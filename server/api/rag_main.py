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
import os

class FinancialChatbotRAG:
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
        self.llm = None
        self.rag_pipeline = None
        
    def initialize(self):
        # Load and process documents
        documents = []
        for file_path in self.file_paths:
            loader = TextLoader(file_path)
            documents.extend(loader.load())
        
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
        
        # Initialize LLM pipeline
        model_name = "edbertw/tuned_flanT5"
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cpu")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        hf_pipeline = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=128,
            device="cpu",
            num_beams=5,
            temperature=0.5,
            do_sample=True,
            top_p=0.9,
            early_stopping=True
        )
        
        self.llm = HuggingFacePipeline(pipeline=hf_pipeline)
        retriever = self.vectorstore.as_retriever()
        
        # Create RAG pipeline
        self.rag_pipeline = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            verbose=True
        )
    
    def ask_question(self, question):
        """Process a question through the RAG pipeline"""
        if not question:
            raise ValueError("No question provided")
        
        question = "answer the question: " + question
        response = self.rag_pipeline.invoke(question)
        return response['result']

# Initialize the chatbot instance
chatbot = FinancialChatbotRAG()
chatbot.initialize()

@csrf_exempt
@api_view(['POST'])
def ask_chatbot(request):
    try:
        question = request.data.get("question")
        if not question:
            return Response({'error': 'No question provided.'}, status=400)
        
        print("Running.....")
        response_bot = chatbot.ask_question(question)
        print("Success response!")
        print(response_bot)
        return Response({'response': response_bot}, status=200)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)