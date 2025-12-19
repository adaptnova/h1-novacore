#!/usr/bin/env python3
# Nova Embedding Model Setup
# Author: V.I. (Vaeris Intelligence)
# Date: February 25, 2025 01:47 MST
# Version: 1.0.0

import os
import sys
import torch
import logging
from sentence_transformers import SentenceTransformer
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/data/logs/embedding_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EmbeddingSetup:
    def __init__(self):
        self.model = None
        self.device = 'cpu'
        self.model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        self.max_seq_length = 512
        self.batch_size = 64
        
    def configure_environment(self):
        """Configure system environment for optimal performance"""
        try:
            # Set thread count for PyTorch
            torch.set_num_threads(32)
            os.environ['TORCH_THREADS'] = '32'
            
            # Verify CPU resources
            logger.info(f"CPU Thread Count: {torch.get_num_threads()}")
            logger.info(f"PyTorch Version: {torch.__version__}")
            
            return True
        except Exception as e:
            logger.error(f"Environment configuration failed: {str(e)}")
            return False

    def load_model(self):
        """Load and configure the embedding model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.model.max_seq_length = self.max_seq_length
            self.model.to(self.device)
            
            logger.info("Model loaded successfully")
            logger.info(f"Model max sequence length: {self.model.max_seq_length}")
            return True
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            return False

    def verify_setup(self):
        """Verify model setup and performance"""
        try:
            # Test basic embedding
            test_texts = [
                "Verifying embedding model setup",
                "Testing batch processing capability",
                "Checking embedding dimensions"
            ]
            
            # Single embedding test
            single_embedding = self.model.encode(test_texts[0])
            logger.info(f"Single embedding shape: {single_embedding.shape}")
            
            # Batch embedding test
            batch_embeddings = self.model.encode(test_texts, batch_size=self.batch_size)
            logger.info(f"Batch embeddings shape: {batch_embeddings.shape}")
            
            # Verify embedding dimension
            if batch_embeddings.shape[1] != 384:
                raise ValueError(f"Unexpected embedding dimension: {batch_embeddings.shape[1]}")
            
            # Memory usage check
            memory_usage = torch.cuda.max_memory_allocated() if torch.cuda.is_available() else "N/A"
            logger.info(f"Peak memory usage: {memory_usage}")
            
            return True
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False

    def save_model_info(self):
        """Save model configuration and status"""
        try:
            info = {
                'timestamp': datetime.now().isoformat(),
                'model_name': self.model_name,
                'max_seq_length': self.max_seq_length,
                'batch_size': self.batch_size,
                'device': self.device,
                'torch_threads': torch.get_num_threads(),
                'torch_version': torch.__version__
            }
            
            with open('/data/models/embeddings/model_info.txt', 'w') as f:
                for key, value in info.items():
                    f.write(f"{key}: {value}\n")
            
            logger.info("Model information saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save model information: {str(e)}")
            return False

def main():
    logger.info("Starting embedding model setup")
    setup = EmbeddingSetup()
    
    # Step 1: Configure environment
    if not setup.configure_environment():
        logger.error("Environment configuration failed")
        sys.exit(1)
    
    # Step 2: Load model
    if not setup.load_model():
        logger.error("Model loading failed")
        sys.exit(1)
    
    # Step 3: Verify setup
    if not setup.verify_setup():
        logger.error("Setup verification failed")
        sys.exit(1)
    
    # Step 4: Save configuration
    if not setup.save_model_info():
        logger.error("Failed to save model information")
        sys.exit(1)
    
    logger.info("Embedding model setup completed successfully")

if __name__ == "__main__":
    main()