from dotenv import load_dotenv
import os
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from ollama import Client

# Initialize the embedding model
embeddings = OllamaEmbeddings(model="embeddinggemma:latest")

#4) Store the embeddings in a vector database quadrant vector database, pinecone, weaviate, redis, chroma db etc
vector_store = QdrantVectorStore.from_existing_collection(embedding=embeddings, collection_name="executive_summery",
                                                url="http://localhost:6333")

#5) Now we can perform similarity search on the vector database to get relevant chunks for a query
#query = "What are the key takeaways from the executive summary?"
query = input("👉 what information are you looking for? ")
similar_chunks = vector_store.similarity_search(query)

context = "\n\n\n".join([f"Page number: {chunk.metadata['page_label']}\nPage content:{chunk.page_content}\nFile location: {chunk.metadata['source']}" for chunk in similar_chunks])

#6) system prompt to provide context to the model
SYSTEM_PROMPT = f"""You are a helpful AI assistant. Use the following context to answer the user's question along with page number.
If the context does not contain the answer, say "I don't know".
Context:
{context}
"""

#7) Initialize the Ollama client and send the query along with the system prompt as context
client = Client(
   host="localhost:11434",
)
final_response = client.chat(model="gemma3:latest", messages=[{"role": "system", "content": SYSTEM_PROMPT},
                                                              {"role": "user", "content": query}])
print(f"Response from RAG system:{final_response.message.content}")
