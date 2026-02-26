from mem0 import Memory
from ollama import Client
import json

config = {
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "embeddinggemma:latest",
            "ollama_base_url": "http://localhost:11434", # Default Ollama URL
            #"embedding_dims": 768  # EmbeddingGemma output dimension
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "gemma3:latest", # Or your preferred local LLM
            "temperature": 0.1
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": "6333", # Default Ollama URL
            "collection_name": "agentic_memories",
            "embedding_model_dims": 768  # EmbeddingGemma output dimension
        }
    }
}

#create a memory client
mem_client = Memory.from_config(config)

 # Initialize the Ollama client and send the query along with the system prompt as context
client = Client(
host="localhost:11434",
)
#create a user message
user_query = input("👉 What you are looking for? ")

search_memory = mem_client.search(user_id="Bibhukalyan",query=user_query)
memories = [f"ID: {mem.get('id')}\nMemory: {mem.get('memory')}" for mem in search_memory.get('results', [])]

SYSTEM_PROMPT = f"""
Here is the conext about the user: {json.dumps(memories)}
"""

#print(f"Memory: {memories}")

response = client.chat(model="gemma3:latest", messages= [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_query}
])
print(f"{response.message.content}")

print(f"New facts is assigning to memory, please wait ...")
mem_client.add(
    user_id="Bibhukalyan",
    messages = [
        {"role": "user", "content": user_query},
        {"role": "system", "content": response.message.content},
    ]
)

print(f"New facts stored to memory ...")

