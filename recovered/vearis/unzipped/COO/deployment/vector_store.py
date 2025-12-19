#!/usr/bin/env python3
# Nova Vector Store Setup
# Author: V.I. (Vaeris Intelligence)
# Date: February 25, 2025 01:48 MST
# Version: 1.0.0

import os
import sys
import faiss
import numpy as np
import logging
from datetime import datetime
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/data/logs/vector_store.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, dimension: int = 384):
        """Initialize vector store with specified dimension"""
        self.dimension = dimension
        self.index = None
        self.store_path = "/data/models/vector_store.faiss"
        self.config = {
            'nlist': 256,  # Number of clusters
            'nprobe': 16,  # Number of clusters to visit during search
            'metric': faiss.METRIC_INNER_PRODUCT
        }
        
    def initialize(self) -> bool:
        """Initialize and configure the FAISS index"""
        try:
            # Create quantizer
            quantizer = faiss.IndexFlatIP(self.dimension)
            
            # Create IVF index with scalar quantization
            self.index = faiss.IndexIVFScalarQuantizer(
                quantizer,
                self.dimension,
                self.config['nlist'],
                faiss.ScalarQuantizer.QT_8bit
            )
            
            # Set search parameters
            self.index.nprobe = self.config['nprobe']
            
            # Train on random vectors
            logger.info("Training vector store...")
            train_size = 10000
            train_vectors = np.random.random((train_size, self.dimension)).astype('float32')
            self.index.train(train_vectors)
            
            logger.info("Vector store initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            return False
    
    def save(self) -> bool:
        """Save the index to disk"""
        try:
            logger.info(f"Saving vector store to {self.store_path}")
            faiss.write_index(self.index, self.store_path)
            
            # Save configuration
            config_path = self.store_path.replace('.faiss', '_config.txt')
            with open(config_path, 'w') as f:
                f.write(f"timestamp: {datetime.now().isoformat()}\n")
                f.write(f"dimension: {self.dimension}\n")
                f.write(f"nlist: {self.config['nlist']}\n")
                f.write(f"nprobe: {self.config['nprobe']}\n")
                f.write(f"metric: {self.config['metric']}\n")
            
            logger.info("Vector store saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save vector store: {str(e)}")
            return False
    
    def load(self) -> bool:
        """Load the index from disk"""
        try:
            if not os.path.exists(self.store_path):
                logger.error("Vector store file not found")
                return False
                
            logger.info(f"Loading vector store from {self.store_path}")
            self.index = faiss.read_index(self.store_path)
            self.index.nprobe = self.config['nprobe']
            
            logger.info("Vector store loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load vector store: {str(e)}")
            return False
    
    def add_vectors(self, vectors: np.ndarray) -> bool:
        """Add vectors to the index"""
        try:
            if vectors.dtype != np.float32:
                vectors = vectors.astype(np.float32)
            
            if vectors.shape[1] != self.dimension:
                raise ValueError(f"Expected vectors of dimension {self.dimension}, got {vectors.shape[1]}")
            
            self.index.add(vectors)
            logger.info(f"Added {len(vectors)} vectors to store")
            return True
        except Exception as e:
            logger.error(f"Failed to add vectors: {str(e)}")
            return False
    
    def search(self, query: np.ndarray, k: int = 4) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar vectors"""
        try:
            if query.dtype != np.float32:
                query = query.astype(np.float32)
            
            if len(query.shape) == 1:
                query = query.reshape(1, -1)
            
            distances, indices = self.index.search(query, k)
            return distances, indices
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return None, None
    
    def verify_store(self) -> bool:
        """Verify vector store functionality"""
        try:
            # Create test vectors
            test_vectors = np.random.random((100, self.dimension)).astype('float32')
            
            # Add vectors
            if not self.add_vectors(test_vectors):
                return False
            
            # Test search
            query = test_vectors[0].reshape(1, -1)
            distances, indices = self.search(query, k=5)
            
            if distances is None or indices is None:
                return False
            
            # Verify first result is the query vector
            if indices[0][0] != 0:
                logger.error("Search verification failed")
                return False
            
            logger.info("Vector store verification successful")
            return True
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False

def main():
    """Main setup function"""
    logger.info("Starting vector store setup")
    
    # Initialize store
    store = VectorStore()
    
    # Step 1: Initialize
    if not store.initialize():
        logger.error("Vector store initialization failed")
        sys.exit(1)
    
    # Step 2: Verify functionality
    if not store.verify_store():
        logger.error("Vector store verification failed")
        sys.exit(1)
    
    # Step 3: Save to disk
    if not store.save():
        logger.error("Failed to save vector store")
        sys.exit(1)
    
    logger.info("Vector store setup completed successfully")

if __name__ == "__main__":
    main()