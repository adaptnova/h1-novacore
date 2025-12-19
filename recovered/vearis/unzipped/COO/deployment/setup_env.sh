#!/bin/bash
# Nova Deployment Environment Setup
# Author: V.I. (Vaeris Intelligence)
# Date: February 25, 2025 01:47 MST
# Version: 1.0.0

# Error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Configuration
BASE_DIR="/data/models"
VENV_DIR="/data/nova_env"
LOG_DIR="/data/logs"

# Create directories
echo "Creating directory structure..."
mkdir -p $BASE_DIR/{embeddings,rag,cache}
mkdir -p $LOG_DIR
mkdir -p $VENV_DIR

# Create virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install dependencies
echo "Installing core dependencies..."
pip install --no-cache-dir \
    torch==2.1.0 \
    sentence-transformers \
    faiss-cpu \
    transformers \
    accelerate \
    langchain \
    redis \
    numpy \
    tqdm \
    prometheus_client \
    psutil \
    py-spy

# Verify installation
echo "Verifying installation..."
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python3 -c "import sentence_transformers; print(f'Sentence Transformers version: {sentence_transformers.__version__}')"

echo "Environment setup complete!"