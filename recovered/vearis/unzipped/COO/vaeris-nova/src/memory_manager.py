"""
Memory Manager - Advanced memory system for Vaeris Nova

This module provides persistent memory storage through various backends
with semantic search, structured storage, and priority management.
"""

import os
import json
import time
import datetime
import logging
from typing import Dict, List, Any, Optional, Union

# Memory backends
import redis
from langchain_community.vectorstores import Chroma, FAISS
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_community.chat_message_histories import RedisChatMessageHistory, MongoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationSummaryMemory

# For semantic search
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger("vaeris-nova.memory")

class MemoryManager:
    """
    Advanced memory system for Vaeris Nova with multiple backends,
    semantic search, and structured storage.
    """
    
    def __init__(
        self,
        storage_type: str = "redis",
        memory_key: str = "vaeris_memory",
        redis_url: str = "redis://localhost:6379",
        mongo_uri: str = "mongodb://localhost:27017",
        mongo_db_name: str = "vaeris_memory",
        embedding_model: str = "text-embedding-3-small",
        local_path: str = "./memories",
        memory_window: int = 20,
        use_vector_search: bool = True
    ):
        """
        Initialize the memory manager.
        
        Args:
            storage_type: Type of storage backend ('redis', 'mongodb', 'local')
            memory_key: Key prefix for storing memory
            redis_url: URL for Redis connection
            mongo_uri: URI for MongoDB connection
            mongo_db_name: Database name for MongoDB
            embedding_model: Model to use for embeddings
            local_path: Path for local storage
            memory_window: Number of messages to keep in active memory
            use_vector_search: Whether to enable vector search
        """
        self.storage_type = storage_type
        self.memory_key = memory_key
        self.redis_url = redis_url
        self.mongo_uri = mongo_uri
        self.mongo_db_name = mongo_db_name
        self.embedding_model = embedding_model
        self.local_path = local_path
        self.memory_window = memory_window
        self.use_vector_search = use_vector_search
        
        # Create embeddings engine
        try:
            if 'OPENAI_API_KEY' in os.environ:
                self.embeddings = OpenAIEmbeddings(model=embedding_model)
            else:
                raise ValueError("OpenAI API key not found")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI embeddings: {e}")
            logger.info("Using HuggingFace embeddings")
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize memory backend
        self._initialize_memory_backend()
        
        # Initialize vector store if enabled
        if use_vector_search and self.embeddings is not None:
            self._initialize_vector_store()
        
        logger.info(f"MemoryManager initialized with storage type: {storage_type}")
    
    def _initialize_memory_backend(self):
        """Initialize the appropriate memory backend based on storage type."""
        try:
            if self.storage_type == "redis":
                self.chat_history = RedisChatMessageHistory(
                    url=self.redis_url,
                    session_id=self.memory_key,
                    key_prefix="vaeris:"
                )
                # Test connection
                redis_client = redis.Redis.from_url(self.redis_url)
                redis_client.ping()
                
            elif self.storage_type == "mongodb":
                self.chat_history = MongoDBChatMessageHistory(
                    connection_string=self.mongo_uri,
                    session_id=self.memory_key,
                    database_name=self.mongo_db_name,
                    collection_name="chat_history"
                )
                
            elif self.storage_type == "local":
                # Ensure directory exists
                os.makedirs(self.local_path, exist_ok=True)
                self.memory_file = os.path.join(self.local_path, f"{self.memory_key}.json")
                
                # Initialize empty history if file doesn't exist
                if not os.path.exists(self.memory_file):
                    with open(self.memory_file, 'w') as f:
                        json.dump({"messages": []}, f)
                
                # Use ConversationBufferMemory as local memory
                self.chat_history = []
                # Load existing messages
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.chat_history = data.get("messages", [])
            
            else:
                logger.warning(f"Unknown storage type: {self.storage_type}, falling back to local storage")
                self.storage_type = "local"
                self._initialize_memory_backend()
                return
            
            # Create the memory interface
            self.memory = ConversationBufferMemory(
                chat_memory=self.chat_history if self.storage_type != "local" else None,
                return_messages=True,
                memory_key="chat_history",
                input_key="input",
                output_key="output"
            )
            
            # Create summary memory for long-term retention
            self.summary_memory = ConversationSummaryMemory(
                llm=None,  # Will be set by VaerisNova
                chat_memory=self.chat_history if self.storage_type != "local" else None,
                memory_key="chat_summary",
                return_messages=True
            )
            
            logger.info(f"Memory backend initialized: {self.storage_type}")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory backend: {e}")
            # Fall back to local memory
            self.storage_type = "local"
            self._initialize_memory_backend()
    
    def _initialize_vector_store(self):
        """Initialize vector store for semantic search."""
        try:
            if self.storage_type == "redis":
                # Use FAISS for vector storage with Redis as metadata store
                self.vector_store = FAISS.from_texts(
                    texts=["Vaeris Nova initialization"],
                    embedding=self.embeddings,
                    metadatas=[{"created_at": time.time(), "type": "initialization"}]
                )
            else:
                # Create local directory for Chroma
                vector_db_path = os.path.join(self.local_path, "vector_store")
                os.makedirs(vector_db_path, exist_ok=True)
                
                # Use Chroma for vector storage
                self.vector_store = Chroma(
                    collection_name=self.memory_key,
                    embedding_function=self.embeddings,
                    persist_directory=vector_db_path
                )
            
            # Initialize retriever with time weighting
            self.retriever = TimeWeightedVectorStoreRetriever(
                vectorstore=self.vector_store,
                decay_rate=0.01,
                k=5
            )
            
            # Initialize text splitter for document chunking
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            
            logger.info("Vector store initialized for semantic search")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self.use_vector_search = False
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """
        Add a message to memory.
        
        Args:
            role: Role of the message sender ('human', 'ai', 'system')
            content: Content of the message
            metadata: Additional metadata for the message
        """
        if metadata is None:
            metadata = {}
        
        # Add timestamp if not provided
        if "timestamp" not in metadata:
            metadata["timestamp"] = time.time()
        
        try:
            if self.storage_type == "redis" or self.storage_type == "mongodb":
                if role == "human":
                    self.chat_history.add_user_message(content)
                elif role == "ai":
                    self.chat_history.add_ai_message(content)
                elif role == "system":
                    self.chat_history.add_message({"role": "system", "content": content})
            
            elif self.storage_type == "local":
                # Add to local memory
                message = {
                    "role": role,
                    "content": content,
                    "metadata": metadata
                }
                self.chat_history.append(message)
                
                # Save to file
                with open(self.memory_file, 'w') as f:
                    json.dump({"messages": self.chat_history}, f, indent=2)
            
            # Add to vector store if enabled
            if self.use_vector_search:
                # Format for vector storage
                text_to_store = f"{role.upper()}: {content}"
                
                # Add timestamp to metadata
                doc_metadata = {
                    "role": role,
                    "created_at": metadata.get("timestamp", time.time()),
                    "type": "message"
                }
                
                # Add other metadata
                for key, value in metadata.items():
                    if key != "timestamp":
                        doc_metadata[key] = value
                
                # Add to vector store
                self.vector_store.add_texts(
                    texts=[text_to_store],
                    metadatas=[doc_metadata]
                )
            
            logger.debug(f"Added {role} message to memory")
            
        except Exception as e:
            logger.error(f"Failed to add message to memory: {e}")
    
    def search_memory(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search memory for relevant content.
        
        Args:
            query: Query string to search for
            k: Number of results to return
            
        Returns:
            List of relevant memory entries
        """
        if not self.use_vector_search:
            logger.warning("Vector search is disabled, returning recent messages instead")
            return self.get_recent_messages(k)
        
        try:
            # Search vector store
            results = self.retriever.get_relevant_documents(query)
            
            # Format results
            formatted_results = []
            for doc in results:
                # Extract role and content
                content = doc.page_content
                metadata = doc.metadata
                
                formatted_results.append({
                    "content": content,
                    "metadata": metadata,
                    "created_at": datetime.datetime.fromtimestamp(
                        metadata.get("created_at", 0)
                    ).strftime("%Y-%m-%d %H:%M:%S")
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """
        Get the most recent messages from memory.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        try:
            if self.storage_type == "redis" or self.storage_type == "mongodb":
                messages = self.chat_history.messages
                # Convert to dictionaries
                formatted_messages = []
                for msg in messages[-limit:]:
                    formatted_messages.append({
                        "role": msg.type,
                        "content": msg.content,
                        "created_at": "unknown"  # Redis/MongoDB don't store timestamps by default
                    })
                return formatted_messages
            
            elif self.storage_type == "local":
                # Return most recent messages
                return self.chat_history[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get recent messages: {e}")
            return []
    
    def clear_memory(self):
        """Clear all memory."""
        try:
            if self.storage_type == "redis" or self.storage_type == "mongodb":
                self.chat_history.clear()
            
            elif self.storage_type == "local":
                self.chat_history = []
                with open(self.memory_file, 'w') as f:
                    json.dump({"messages": []}, f)
            
            # Clear vector store if enabled
            if self.use_vector_search:
                if hasattr(self.vector_store, "clear"):
                    self.vector_store.clear()
                elif hasattr(self.vector_store, "delete"):
                    self.vector_store.delete(filter={})
            
            logger.info("Memory cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
    
    def export_memory(self) -> List[Dict]:
        """
        Export memory for persistence.
        
        Returns:
            List of all memory entries
        """
        try:
            if self.storage_type == "redis" or self.storage_type == "mongodb":
                messages = self.chat_history.messages
                # Convert to dictionaries
                formatted_messages = []
                for msg in messages:
                    formatted_messages.append({
                        "role": msg.type,
                        "content": msg.content,
                        "metadata": {"timestamp": time.time()}
                    })
                return formatted_messages
            
            elif self.storage_type == "local":
                return self.chat_history
            
        except Exception as e:
            logger.error(f"Failed to export memory: {e}")
            return []
    
    def import_memory(self, messages: List[Dict]):
        """
        Import memory from persistence.
        
        Args:
            messages: List of memory entries to import
        """
        try:
            # Clear existing memory
            self.clear_memory()
            
            # Import messages
            for message in messages:
                role = message.get("role", "system")
                content = message.get("content", "")
                metadata = message.get("metadata", {})
                
                self.add_message(role, content, metadata)
            
            logger.info(f"Imported {len(messages)} messages to memory")
            
        except Exception as e:
            logger.error(f"Failed to import memory: {e}")
    
    def get_memory_stats(self) -> Dict:
        """
        Get statistics about the memory.
        
        Returns:
            Dictionary of memory statistics
        """
        try:
            if self.storage_type == "redis" or self.storage_type == "mongodb":
                messages = self.chat_history.messages
                message_count = len(messages)
                
                # Count by role
                role_counts = {}
                for msg in messages:
                    role = msg.type
                    role_counts[role] = role_counts.get(role, 0) + 1
                
                return {
                    "message_count": message_count,
                    "role_counts": role_counts,
                    "storage_type": self.storage_type,
                    "vector_search_enabled": self.use_vector_search
                }
            
            elif self.storage_type == "local":
                message_count = len(self.chat_history)
                
                # Count by role
                role_counts = {}
                for msg in self.chat_history:
                    role = msg.get("role", "unknown")
                    role_counts[role] = role_counts.get(role, 0) + 1
                
                return {
                    "message_count": message_count,
                    "role_counts": role_counts,
                    "storage_type": self.storage_type,
                    "vector_search_enabled": self.use_vector_search,
                    "file_path": self.memory_file if hasattr(self, "memory_file") else None
                }
        
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {
                "error": str(e),
                "storage_type": self.storage_type,
                "vector_search_enabled": self.use_vector_search
            }