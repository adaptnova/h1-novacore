import chromadb
from chromadb.config import Settings
import logging
import os
import json
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = "./data"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )
        self.collections = {}
        self._setup_collections()
        logger.info("Vector store initialized")

    def _setup_collections(self):
        """Initialize default collections"""
        collection_configs = {
            "general_knowledge": {"description": "General knowledge embeddings"},
            "task_context": {"description": "Task-specific context embeddings"},
            "agent_memory": {"description": "Agent memory embeddings"}
        }
        
        for name, metadata in collection_configs.items():
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata=metadata
            )

    def add_vectors(self, collection_name: str, texts: List[str], 
                   metadata: Optional[List[Dict[str, Any]]] = None,
                   ids: Optional[List[str]] = None) -> List[str]:
        """Add vectors to a collection"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} does not exist")
            
            collection = self.collections[collection_name]
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"{collection_name}_{i}_{os.urandom(4).hex()}" 
                      for i in range(len(texts))]
            
            # Ensure metadata exists for each text
            if metadata is None:
                metadata = [{"source": "unknown"} for _ in texts]
            
            # Add to collection
            collection.add(
                documents=texts,
                metadatas=metadata,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} vectors to {collection_name}")
            return ids
        except Exception as e:
            logger.error(f"Error adding vectors: {str(e)}")
            raise

    def query(self, collection_name: str, query_text: str, n_results: int = 5,
             metadata_filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query vectors from a collection"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} does not exist")
            
            collection = self.collections[collection_name]
            
            # Perform query
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=metadata_filter
            )
            
            logger.info(f"Query performed on {collection_name}")
            return results
        except Exception as e:
            logger.error(f"Error querying vectors: {str(e)}")
            raise

    def delete_vectors(self, collection_name: str, ids: List[str]) -> None:
        """Delete vectors from a collection"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} does not exist")
            
            collection = self.collections[collection_name]
            collection.delete(ids=ids)
            
            logger.info(f"Deleted {len(ids)} vectors from {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            raise

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics about a collection"""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} does not exist")
            
            collection = self.collections[collection_name]
            
            count = collection.count()
            peek = collection.peek()
            
            return {
                "name": collection_name,
                "count": count,
                "sample_ids": peek["ids"] if peek else [],
                "metadata": collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise

    def list_collections(self) -> List[str]:
        """List all available collections"""
        return list(self.collections.keys())

    def get_health(self) -> Dict[str, Any]:
        """Get health status of the vector store"""
        try:
            stats = {name: self.get_collection_stats(name) 
                    for name in self.list_collections()}
            return {
                "status": "healthy",
                "collection_stats": stats,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global instance
vector_store = VectorStore()

if __name__ == "__main__":
    try:
        # Keep the main thread running and periodically check health
        import time
        while True:
            health = vector_store.get_health()
            logger.info(f"Health check: {json.dumps(health, indent=2)}")
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down vector store")