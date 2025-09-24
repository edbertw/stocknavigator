from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from .models import ChatSession, ChatMessage
from django.contrib.auth.models import User
import os
import uuid
from datetime import datetime, timedelta
from collections import OrderedDict
import time
import torch
from dotenv import load_dotenv
import requests


class MemoryAwareFinancialChatbotRAG:
    def __init__(self):
        self.file_paths = [
            "Knowledge_Base/candlestick.txt",
            "Knowledge_Base/ma.txt",
            "Knowledge_Base/momentum.txt",
            "Knowledge_Base/rsi.txt",
            "Knowledge_Base/bollinger.txt",
            "Knowledge_Base/corr.txt",
            "Knowledge_Base/cumul.txt",
            "Knowledge_Base/macd.txt"
        ]
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.faiss_index_path = "faiss"
        self.vectorstore = None
        self.retriever = None
        self.llm = None
        self.rag_pipeline = None
        self.session_memories = {}  # Store memories for each session
        # Simple in-memory cache: {(session_id, normalized_question): (answer, expire_epoch)}
        self.response_cache = OrderedDict()
        self.cache_ttl_seconds = 300  # 5 minutes
        # Simple keyword routing to decide when to enforce RAG-only answers
        self.rag_keywords = {
            'ma','moving average','sma','ema','wma','rsi','macd','bollinger','band','bands',
            'candlestick','candle','doji','hammer','engulfing','shooting star','harami',
            'momentum','correlation','cumulative','return','chart pattern','pattern','volume',
            'vwap','obv','adx','parabolic sar','keltner','donchian','support','resistance', 'stock'
        }
        self.strict_rag_prompt = PromptTemplate(
            input_variables=["context","question"],
            template=(
                "You are a precise financial assistant.") +
                " Answer ONLY using the provided context.\n"
                "- If the answer is not fully supported by the context, reply: 'I don't know based on the provided knowledge base.'\n"
                "- Do not make up facts.\n"
                "- Keep answers concise and focused.\n\n"
                "Context:\n{context}\n\n"
                "Question: {question}\n"
            )
        
    def initialize(self):
        # Load environment variables
        try:
            load_dotenv()
        except Exception:
            pass

        # Load and process documents
        documents = []
        for file_path in self.file_paths:
            loader = TextLoader(file_path)
            documents.extend(loader.load())
        
        # Slightly larger chunks reduce number of embeddings and retrieval cost
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        
        # Initialize vector store
        if os.path.exists(self.faiss_index_path):
            self.vectorstore = FAISS.load_local(
                self.faiss_index_path, 
                self.embedding_model, 
                allow_dangerous_deserialization=True
            )
        else:
            self.vectorstore = FAISS.from_documents(
                documents=chunks, 
                embedding=self.embedding_model
            )
            self.vectorstore.save_local(self.faiss_index_path)
        # Configure a retriever once with MMR for diversity and better relevance
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3, "fetch_k": 15, "lambda_mult": 0.8, "score_threshold": 0.85}
        )
        
        # Initialize LLM pipeline
        model_name = "edbertw/tuned_flanT5"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        hf_pipeline = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=1000,
            device=0 if device == "cuda" else -1,
            # Faster decoding settings; reduce beams and sampling complexity
            num_beams=1,
            do_sample=False
        )
        
        self.llm = HuggingFacePipeline(pipeline=hf_pipeline)
        # Configure OpenRouter base LLM
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = "deepseek/deepseek-chat-v3.1:free"
        self.openrouter_base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def get_or_create_session_memory(self, session_id):
        """Get or create memory for a specific session"""
        if session_id not in self.session_memories:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                output_key="answer",
                return_messages=True
            )
            self.session_memories[session_id] = memory
        return self.session_memories[session_id]
    
    def load_session_history(self, session_id):
        """Load conversation history from database for a session"""
        try:
            session = ChatSession.objects.get(id=session_id)
            messages = session.messages.all().order_by('timestamp')
            
            memory = self.get_or_create_session_memory(session_id)
            
            # Clear existing memory and load from database
            memory.clear()
            
            for message in messages:
                if message.message_type == 'user':
                    memory.chat_memory.add_user_message(message.content)
                elif message.message_type == 'assistant':
                    memory.chat_memory.add_ai_message(message.content)
            
            return memory
        except ChatSession.DoesNotExist:
            return self.get_or_create_session_memory(session_id)

    def _render_memory_for_system(self, memory, max_chars=2000):
        """Render recent conversation turns for inclusion in a system prompt.
        Keeps it compact to avoid token bloat.
        """
        try:
            messages = getattr(memory, "chat_memory", None)
            if not messages or not getattr(messages, "messages", None):
                return ""
            rendered = []
            for m in messages.messages[-20:]:
                role = getattr(m, "type", "") or ("human" if m.__class__.__name__.lower().startswith("human") else "ai")
                content = getattr(m, "content", "")
                prefix = "User" if role in ("human", "user") else "Assistant"
                rendered.append(f"{prefix}: {content}")
            text = "\n".join(rendered)
            if len(text) > max_chars:
                return text[-max_chars:]
            return text
        except Exception:
            return ""

    def _call_openrouter_chat(self, system_prompt, user_prompt, temperature=0.2, max_tokens=800):
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        resp = requests.post(self.openrouter_base_url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return str(data)

    def _normalize_question(self, question: str) -> str:
        return (question or "").strip().lower()

    def _prune_cache(self):
        now = time.time()
        # Remove expired entries and keep cache size bounded
        keys_to_delete = []
        for key, (_, expire_ts) in self.response_cache.items():
            if expire_ts <= now:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del self.response_cache[key]
        # Optional: bound size to last 200 items
        while len(self.response_cache) > 200:
            self.response_cache.popitem(last=False)

    def _get_cached_response(self, session_id, question):
        self._prune_cache()
        key = (str(session_id), self._normalize_question(question))
        if key in self.response_cache:
            answer, expire_ts = self.response_cache[key]
            if expire_ts > time.time():
                return answer
            else:
                del self.response_cache[key]
        return None

    def _set_cached_response(self, session_id, question, answer):
        expire_ts = time.time() + self.cache_ttl_seconds
        key = (str(session_id), self._normalize_question(question))
        self.response_cache[key] = (answer, expire_ts)
    
    def _is_rag_topic(self, question: str) -> bool:
        q = (question or "").lower()
        return any(k in q for k in self.rag_keywords)
    
    def ask_question(self, question, session_id, user_id):
        """Process a question through the memory-aware RAG pipeline"""
        if not question:
            raise ValueError("No question provided")
        
        if not session_id:
            raise ValueError("Session ID is required")
        
        # Load session history
        memory = self.load_session_history(session_id)
        
        # Cache check to short-circuit repeated queries in the same session
        cached = self._get_cached_response(session_id, question)
        if cached is not None:
            # Still record to DB for continuity
            self.save_conversation(session_id, user_id, question, cached)
            return cached

        # Route: if topic is RAG-relevant, enforce context-only answering
        if self._is_rag_topic(question):
            retriever = self.retriever or self.vectorstore.as_retriever(search_kwargs={"k": 3})
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=False,
                verbose=False,
                combine_docs_chain_kwargs={"prompt": self.strict_rag_prompt}
            )
            response = qa_chain({"question": question})
            final_answer = response['answer']
        else:
            # Non-RAG topic: answer directly with base LLM (no retrieval)
            system_prompt = (
                f"""You are a formal and helpful assistant. Answer clearly, concisely and make it consistent with the provided chat history below.\n\n
                For any stock or finance-related questions, answer it to the best of your ability. Please do not hallucinate or make up any information.
                If you don't know the answer, please say "I don't know" or "I don't have that information".
                Chat History:
                {self._render_memory_for_system(memory)}
                """
            )
            final_answer = self._call_openrouter_chat(system_prompt, question)
        # Save the conversation to database and cache
        self.save_conversation(session_id, user_id, question, final_answer)
        self._set_cached_response(session_id, question, final_answer)
        
        return final_answer
    
    def save_conversation(self, session_id, user_id, question, answer):
        """Save user question and assistant answer to database"""
        try:
            session = ChatSession.objects.get(id=session_id)
            
            # Save user message
            ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=question
            )
            
            # Save assistant message
            ChatMessage.objects.create(
                session=session,
                message_type='assistant',
                content=answer
            )
            
            # Update session timestamp
            session.updated_at = datetime.now()
            session.save()
            
        except ChatSession.DoesNotExist:
            raise ValueError("Session not found")
    
    def clear_session_memory(self, session_id):
        """Clear memory for a specific session"""
        if session_id in self.session_memories:
            del self.session_memories[session_id]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions and their memories"""
        # Delete sessions older than 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        expired_sessions = ChatSession.objects.filter(
            updated_at__lt=cutoff_time,
            is_active=True
        )
        
        for session in expired_sessions:
            # Clear memory
            self.clear_session_memory(session.id)
            # Mark session as inactive
            session.is_active = False
            session.save()

# Initialize the chatbot instance
chatbot = MemoryAwareFinancialChatbotRAG()
chatbot.initialize()

@csrf_exempt
@api_view(['POST'])
def ask_chatbot(request):
    try:
        question = request.data.get("question")
        session_id = request.data.get("session_id")
        user_id = request.data.get("user_id")
        
        if not question:
            return Response({'error': 'No question provided.'}, status=400)
        
        if not session_id:
            return Response({'error': 'Session ID is required.'}, status=400)
        
        if not user_id:
            return Response({'error': 'User ID is required.'}, status=400)
        
        print("Running memory-aware RAG.....")
        response_bot = chatbot.ask_question(question, session_id, user_id)
        print("Success response!")
        print(response_bot)
        return Response({'response': response_bot}, status=200)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def create_chat_session(request):
    """Create a new chat session"""
    try:
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({'error': 'User ID is required.'}, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)
        
        session = ChatSession.objects.create(user=user)
        return Response({
            'session_id': str(session.id),
            'created_at': session.created_at,
            'message': 'Chat session created successfully'
        }, status=201)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
def get_chat_session(request, session_id):
    """Get chat session details and messages"""
    try:
        session = ChatSession.objects.get(id=session_id)
        messages = session.messages.all().order_by('timestamp')
        
        session_data = {
            'session_id': str(session.id),
            'created_at': session.created_at,
            'updated_at': session.updated_at,
            'is_active': session.is_active,
            'messages': [
                {
                    'id': msg.id,
                    'message_type': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.timestamp
                }
                for msg in messages
            ]
        }
        
        return Response(session_data, status=200)
        
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['DELETE'])
def end_chat_session(request, session_id):
    """End a chat session and clear its memory"""
    try:
        session = ChatSession.objects.get(id=session_id)
        session.is_active = False
        session.save()
        
        # Clear session memory
        chatbot.clear_session_memory(session_id)
        
        return Response({'message': 'Chat session ended successfully'}, status=200)
        
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
def get_user_sessions(request, user_id):
    """Get all chat sessions for a user"""
    try:
        user = User.objects.get(id=user_id)
        sessions = ChatSession.objects.filter(user=user, is_active=True).order_by('-updated_at')
        
        sessions_data = []
        for session in sessions:
            message_count = session.messages.count()
            sessions_data.append({
                'session_id': str(session.id),
                'created_at': session.created_at,
                'updated_at': session.updated_at,
                'message_count': message_count
            })
        
        return Response({'sessions': sessions_data}, status=200)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def cleanup_expired_sessions(request):
    """Clean up expired sessions (admin endpoint)"""
    try:
        chatbot.cleanup_expired_sessions()
        return Response({'message': 'Expired sessions cleaned up successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)