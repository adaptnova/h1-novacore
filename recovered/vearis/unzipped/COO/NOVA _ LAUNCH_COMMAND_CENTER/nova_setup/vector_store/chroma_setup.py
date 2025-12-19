"""
ChromaDB Setup and Configuration for ADAPT Platform
This module implements vector storage capabilities for semantic understanding and cross-Nova knowledge sharing.
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chroma.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = "chroma_store"):
        """Initialize ChromaDB with persistence and monitoring."""
        self.persist_directory = persist_directory
        
        # Ensure persistence directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        
        # Initialize default embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create collections for different types of data
        self.collections = {
            "semantic_memory": self.client.get_or_create_collection(
                name="semantic_memory",
                embedding_function=self.embedding_function,
                metadata={"description": "Long-term semantic understanding"}
            ),
            "knowledge_base": self.client.get_or_create_collection(
                name="knowledge_base",
                embedding_function=self.embedding_function,
                metadata={"description": "Shared knowledge across Novas"}
            ),
            "context_store": self.client.get_or_create_collection(
                name="context_store",
                embedding_function=self.embedding_function,
                metadata={"description": "Context preservation"}
            )
        }
        
        logger.info("VectorStore initialized successfully")

    def add_embeddings(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """Add embeddings to specified collection."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} not found")
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"{collection_name}_{datetime.now().timestamp()}_{i}" 
                      for i in range(len(texts))]
            
            # Add default metadata if not provided
            if metadatas is None:
                metadatas = [{"timestamp": datetime.now().isoformat()} 
                           for _ in texts]
            
            self.collections[collection_name].add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} embeddings to {collection_name}")
            
        except Exception as e:
            logger.error(f"Error adding embeddings: {str(e)}")
            raise

    def query_similar(
        self,
        collection_name: str,
        query_texts: Union[str, List[str]],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """Query collection for similar embeddings."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} not found")
            
            # Convert single query to list
            if isinstance(query_texts, str):
                query_texts = [query_texts]
            
            results = self.collections[collection_name].query(
                query_texts=query_texts,
                n_results=n_results,
                where=where
            )
            
            logger.info(f"Successfully queried {collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error querying embeddings: {str(e)}")
            raise

    def delete_embeddings(
        self,
        collection_name: str,
        ids: List[str]
    ) -> None:
        """Delete embeddings from specified collection."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} not found")
            
            self.collections[collection_name].delete(ids=ids)
            logger.info(f"Deleted {len(ids)} embeddings from {collection_name}")
            
        except Exception as e:
            logger.error(f"Error deleting embeddings: {str(e)}")
            raise

    def get_collection_stats(self, collection_name: str) -> Dict:
        """Get statistics for specified collection."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} not found")
            
            collection = self.collections[collection_name]
            count = collection.count()
            
            stats = {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
            
            logger.info(f"Retrieved stats for {collection_name}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise

    def clear_collection(self, collection_name: str) -> None:
        """Clear all embeddings from specified collection."""
        try:
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} not found")
            
            self.collections[collection_name].delete()
            logger.info(f"Cleared all embeddings from {collection_name}")
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise

    def persist(self) -> None:
        """Persist all collections to disk."""
        try:
            self.client.persist()
            logger.info("Successfully persisted all collections")
            
        except Exception as e:
            logger.error(f"Error persisting collections: {str(e)}")
            raise

# Add test function
def run_tests():
    """Run basic tests for VectorStore functionality."""
    try:
        # Initialize VectorStore
        vs = VectorStore()
        logger.info("Starting VectorStore tests...")

        # Test data
        test_texts = [
            "The quick brown fox jumps over the lazy dog",
            "A fast auburn canine leaps across a sleepy hound",
            "The lazy dog sleeps while the quick fox runs"
        ]
        test_metadata = [
            {"source": "test1", "timestamp": datetime.now().isoformat()},
            {"source": "test2", "timestamp": datetime.now().isoformat()},
            {"source": "test3", "timestamp": datetime.now().isoformat()}
        ]
        test_ids = ["test1", "test2", "test3"]

        # Test adding embeddings
        vs.add_embeddings(
            "semantic_memory",
            test_texts,
            test_metadata,
            test_ids
        )

        # Test querying
        results = vs.query_similar(
            "semantic_memory",
            "A quick animal jumps",
            n_results=2
        )

        # Test collection stats
        stats = vs.get_collection_stats("semantic_memory")
        
        # Log results
        logger.info("Test Results:")
        logger.info(f"Collection Stats: {stats}")
        logger.info(f"Query Results: {results}")
        
        # Clean up
        vs.delete_embeddings("semantic_memory", test_ids)
        logger.info("Tests completed successfully")
        
        return True

    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        return False

if __name__ == "__main__":
    run_tests()