from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
import os
'''
file_paths = [
        "/Users/edbertwidjaja/Downloads/Stock-Navigator-main/Knowledge_Base/candlestick.txt",
        "/Users/edbertwidjaja/Downloads/Stock-Navigator-main/Knowledge_Base/ma.txt",
        "/Users/edbertwidjaja/Downloads/Stock-Navigator-main/Knowledge_Base/momentum.txt",
        "/Users/edbertwidjaja/Downloads/Stock-Navigator-main/Knowledge_Base/rsi.txt",
        "/Users/edbertwidjaja/Downloads/Stock-Navigator-main/Knowledge_Base/bollinger.txt",
        "/Users/edbertwidjaja/Downloads/Stock-Navigator-main/Knowledge_Base/corr.txt",
        "/Users/edbertwidjaja/Downloads/Stock-Navigator-main/Knowledge_Base/cumul.txt",
        "/Users/edbertwidjaja/Downloads/Stock-Navigator-main/Knowledge_Base/macd.txt"]
'''
file_paths = [
        "Knowledge_Base/candlestick.txt",
        "Knowledge_Base/ma.txt",
        "Knowledge_Base/momentum.txt",
        "Knowledge_Base/rsi.txt",
        "Knowledge_Base/bollinger.txt",
        "Knowledge_Base/corr.txt",
        "Knowledge_Base/cumul.txt",
        "Knowledge_Base/macd.txt"]

documents = []
for file_path in file_paths:
    loader = TextLoader(file_path)
    documents.extend(loader.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)
        
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
faiss_index_path = "faiss"

# Check if FAISS index exists
if os.path.exists(faiss_index_path):
    # Load the persisted FAISS index
    vectorstore = FAISS.load_local(faiss_index_path, embedding_model, allow_dangerous_deserialization=True)
else:
    # Create the FAISS index and persist it
    embeddings = embedding_model.embed_documents([chunk.page_content for chunk in chunks])
    vectorstore = FAISS.from_documents(documents=chunks, embedding=embedding_model)
    vectorstore.save_local(faiss_index_path)
    
model_name = "google/flan-t5-base"  # You can choose other models
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cpu")
tokenizer = AutoTokenizer.from_pretrained(model_name)
hf_pipeline = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=512,  # Max token length for output
    device = -1,
    num_beams=5,     # Beam search for better answers, change from 3
    temperature = 0.5,
    do_sample = True,
    top_p = 0.9 #nucleus sampling
)

        # Wrap the pipeline for LangChain
llm = HuggingFacePipeline(pipeline=hf_pipeline)
retriever = vectorstore.as_retriever()

        # Create a RetrievalQA chain
rag_pipeline = RetrievalQA.from_chain_type(
llm=llm,
chain_type="refine",  # "map_reduce", "refine", "map_rerank", etc.
retriever=retriever
)
@csrf_exempt
@api_view(['POST'])
def ask_chatbot(request):
    
    try:
        question = request.data.get("question")
        if not question:
            return Response({'error': 'No question provided.'}, status=400)
        print("Running.....")
        response_bot = rag_pipeline.run(question)
        print("Success response!")
        print(response_bot)
        return Response({'response': response_bot}, status=200)
        
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
        
        
        
        
    