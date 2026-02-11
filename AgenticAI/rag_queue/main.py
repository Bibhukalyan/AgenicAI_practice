from .rag_server import app
import uvicorn
from dotenv import load_dotenv

#load_dotenv()

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

main()