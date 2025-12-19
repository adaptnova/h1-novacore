#!/bin/bash
# Parallel Deployment Script
# Author: V.I. (Vaeris Intelligence)
# Date: February 25, 2025 01:59 MST
# Version: 1.0.0

# Error handling
set -e
trap 'echo "Error on line $LINENO"' ERR

# Configuration
PRIMARY_DIR="/data/models"
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
RAG_MODEL="mistralai/Mistral-7B-v0.1"
LOG_DIR="/data/logs"

# Create required directories
echo "Creating directory structure..."
mkdir -p ${PRIMARY_DIR}/{embeddings,rag,cache,vector}
mkdir -p ${LOG_DIR}

# Function to download models in parallel
download_models() {
    echo "Starting parallel model downloads..."
    
    # Download embedding model
    (
        echo "Downloading embedding model..."
        aria2c --max-concurrent-downloads=16 \
            --dir=${PRIMARY_DIR}/embeddings \
            https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/pytorch_model.bin \
            https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config.json \
            https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/special_tokens_map.json \
            https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/tokenizer_config.json \
            https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/vocab.txt
    ) &

    # Download RAG model
    (
        echo "Downloading RAG model..."
        aria2c --max-concurrent-downloads=16 \
            --dir=${PRIMARY_DIR}/rag \
            https://huggingface.co/mistralai/Mistral-7B-v0.1/resolve/main/pytorch_model.bin \
            https://huggingface.co/mistralai/Mistral-7B-v0.1/resolve/main/config.json \
            https://huggingface.co/mistralai/Mistral-7B-v0.1/resolve/main/generation_config.json \
            https://huggingface.co/mistralai/Mistral-7B-v0.1/resolve/main/special_tokens_map.json \
            https://huggingface.co/mistralai/Mistral-7B-v0.1/resolve/main/tokenizer_config.json \
            https://huggingface.co/mistralai/Mistral-7B-v0.1/resolve/main/tokenizer.json
    ) &

    # Wait for all downloads to complete
    wait
    echo "All model downloads completed"
}

# Function to setup Python environment
setup_environment() {
