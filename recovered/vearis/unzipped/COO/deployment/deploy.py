#!/usr/bin/env python3
# Nova Deployment Runner
# Author: V.I. (Vaeris Intelligence)
# Date: February 25, 2025 01:48 MST
# Version: 1.0.0

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/data/logs/deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DeploymentRunner:
    def __init__(self):
        self.base_dir = "/data/ax/NovaOps/deployment"
        self.status = {
            'environment': False,
            'embedding': False,
            'vector_store': False
        }
        self.start_time = datetime.now()
        
    def execute_script(self, script: str, timeout: int = 600) -> bool:
        """Execute a deployment script with timeout"""
        try:
            script_path = os.path.join(self.base_dir, script)
            if not os.path.exists(script_path):
                logger.error(f"Script not found: {script_path}")
                return False
            
            if script.endswith('.py'):
                cmd = ['python3', script_path]
            else:
                cmd = ['bash', script_path]
            
            logger.info(f"Executing: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            
            if process.returncode != 0:
                logger.error(f"Script failed with code {process.returncode}")
                logger.error(f"Error output: {stderr}")
                return False
            
            logger.info(f"Script output: {stdout}")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"Script timed out after {timeout} seconds")
            process.kill()
            return False
        except Exception as e:
            logger.error(f"Script execution failed: {str(e)}")
            return False
    
    def verify_environment(self) -> bool:
        """Verify the deployment environment"""
        try:
            required_dirs = [
                '/data/models',
                '/data/models/embeddings',
                '/data/models/rag',
                '/data/models/cache',
                '/data/logs',
                '/data/nova_env'
            ]
            
            for directory in required_dirs:
                if not os.path.exists(directory):
                    logger.error(f"Required directory missing: {directory}")
                    return False
            
            # Check Python environment
            result = subprocess.run(
                ['python3', '-c', 'import torch, sentence_transformers, faiss'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error("Required Python packages not installed")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Environment verification failed: {str(e)}")
            return False
    
    def deploy(self) -> bool:
        """Run the deployment process"""
        try:
            # Step 1: Environment Setup
            logger.info("Setting up environment...")
            if not self.execute_script('setup_env.sh'):
                return False
            
            if not self.verify_environment():
                return False
            
            self.status['environment'] = True
            logger.info("Environment setup complete")
            
            # Step 2: Embedding Model Setup
            logger.info("Setting up embedding model...")
            if not self.execute_script('embedding_setup.py'):
                return False
            
            self.status['embedding'] = True
            logger.info("Embedding model setup complete")
            
            # Step 3: Vector Store Setup
            logger.info("Setting up vector store...")
            if not self.execute_script('vector_store.py'):
                return False
            
            self.status['vector_store'] = True
            logger.info("Vector store setup complete")
            
            return True
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            return False
        
    def print_status(self):
        """Print deployment status"""
        duration = datetime.now() - self.start_time
        print("\nDeployment Status:")
        print("=" * 50)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        print("\nComponents:")
        print("-" * 50)
        for component, status in self.status.items():
            status_str = "✓" if status else "✗"
            print(f"{component:20} [{status_str}]")
        print("=" * 50)

def main():
    """Main deployment function"""
    logger.info("Starting deployment process")
    runner = DeploymentRunner()
    
    success = runner.deploy()
    runner.print_status()
    
    if success:
        logger.info("Deployment completed successfully")
        sys.exit(0)
    else:
        logger.error("Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()