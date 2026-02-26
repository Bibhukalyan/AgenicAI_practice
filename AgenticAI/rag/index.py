from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

#1) Load the document
file_path = Path(__file__).parent / "ml_executive_summery.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()
#print(docs[21])

#2) Split the document into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
chunks = text_splitter.split_documents(docs)

#3) Create embeddings for the chunks
# embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", api_key=os.getenv("API_KEY_2"))
# vector = embeddings.embed_query("hello, world!")
# print(vector)

#3) Initialize the embedding model
embeddings = OllamaEmbeddings(model="embeddinggemma:latest")
# vector = embeddings.embed_query("hello, world!")
# print(vector)

#4) Store the embeddings in a vector database quadrant vector database, pinecone, weaviate, redis, chroma db etc
vector_store = QdrantVectorStore.from_documents(chunks, embeddings, collection_name="executive_summery", 
                                                url="http://localhost:6333")

print("Vector store created and embeddings stored successfully!")

