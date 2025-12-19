#!/bin/bash

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install required packages
pip install chromadb
pip install sentence-transformers
pip install fastapi
pip install uvicorn
pip install typing-extensions
pip install numpy
pip install pydantic

# Create necessary directories
mkdir -p chroma_store
mkdir -p logs

# Initialize log files
touch logs/chroma.log
touch logs/vector_service.log

echo "Setup completed successfully!"