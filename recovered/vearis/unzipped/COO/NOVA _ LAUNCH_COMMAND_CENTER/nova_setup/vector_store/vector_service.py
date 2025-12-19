"""
FastAPI service for Vector Store operations
Provides REST API endpoints for ChromaDB integration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import logging
from chroma_setup import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vector_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ADAPT Vector Store Service",
    description="Vector storage and semantic search service for ADAPT platform",
    version="1.0.0"
)

# Initialize VectorStore
vector_store = VectorStore()

# Pydantic models
class EmbeddingRequest(BaseModel):
    texts: List[str]
    metadatas: Optional[List[Dict]] = None
    ids: Optional[List[str]] = None

class QueryRequest(BaseModel):
    query_texts: List[str]
    n_results: int = 5
    where: Optional[Dict] = None

class DeleteRequest(BaseModel):
    ids: List[str]

# API endpoints
@app.post("/embeddings/{collection_name}")
async def add_embeddings(collection_name: str, request: EmbeddingRequest):
    """Add embeddings to specified collection."""
    try:
        vector_store.add_embeddings(
            collection_name=collection_name,
            texts=request.texts,
            metadatas=request.metadatas,
            ids=request.ids
        )
        return {"status": "success", "message": f"Added {len(request.texts)} embeddings"}
    except Exception as e:
        logger.error(f"Error adding embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/{collection_name}")
async def query_similar(collection_name: str, request: QueryRequest):
    """Query collection for similar embeddings."""
    try:
        results = vector_store.query_similar(
            collection_name=collection_name,
            query_texts=request.query_texts,
            n_results=request.n_results,
            where=request.where
        )
        return {"status": "success", "results": results}
    except Exception as e:
        logger.error(f"Error querying embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/embeddings/{collection_name}")
async def delete_embeddings(collection_name: str, request: DeleteRequest):
    """Delete embeddings from specified collection."""
    try:
        vector_store.delete_embeddings(
            collection_name=collection_name,
            ids=request.ids
        )
        return {"status": "success", "message": f"Deleted {len(request.ids)} embeddings"}
    except Exception as e:
        logger.error(f"Error deleting embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/{collection_name}")
async def get_stats(collection_name: str):
    """Get statistics for specified collection."""
    try:
        stats = vector_store.get_collection_stats(collection_name)
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/collection/{collection_name}")
async def clear_collection(collection_name: str):
    """Clear all embeddings from specified collection."""
    try:
        vector_store.clear_collection(collection_name)
        return {"status": "success", "message": f"Cleared collection {collection_name}"}
    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/persist")
async def persist_collections():
    """Persist all collections to disk."""
    try:
        vector_store.persist()
        return {"status": "success", "message": "Persisted all collections"}
    except Exception as e:
        logger.error(f"Error persisting collections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check service health."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "vector_store"
    }

if __name__ == "__main__":
    uvicorn.run(
        "vector_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )