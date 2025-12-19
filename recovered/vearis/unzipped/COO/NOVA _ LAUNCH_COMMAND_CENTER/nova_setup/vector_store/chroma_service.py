import chromadb
from chromadb.config import Settings
import uvicorn
import os

def init_chroma():
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./data",
    ))
    
    # Create collections for different purposes
    collections = {
        "general_knowledge": client.create_collection(name="general_knowledge", metadata={"type": "general"}),
        "task_context": client.create_collection(name="task_context", metadata={"type": "task"}),
        "agent_memory": client.create_collection(name="agent_memory", metadata={"type": "memory"}),
    }
    
    return client, collections

if __name__ == "__main__":
    # Initialize ChromaDB
    client, collections = init_chroma()
    
    # Start the ChromaDB server
    uvicorn.run(
        "chromadb.app:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )