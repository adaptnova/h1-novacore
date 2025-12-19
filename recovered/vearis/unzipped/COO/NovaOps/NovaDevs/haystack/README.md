# Haystack RAG Implementation

A robust implementation of Retrieval Augmented Generation (RAG) using Haystack, designed to power advanced question-answering and document retrieval workflows.

## Features

- Vector-based document storage using ChromaDB
- Efficient document retrieval with dense embeddings
- Question answering with transformer models
- Distributed processing support with Ray
- RESTful API with FastAPI
- Monitoring with Prometheus metrics
- Distributed tracing support
- Authentication and rate limiting
- CORS support
- Comprehensive logging

## Architecture

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  Document Store  |<--->|  RAG Pipeline   |<--->|   REST API      |
|    (ChromaDB)    |     |                  |     |   (FastAPI)     |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
         ^                       ^                        ^
         |                       |                        |
         v                       v                        v
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|     Indexing     |     |   Distributed    |     |   Monitoring    |
|     Service      |     |   Processing     |     |     Stack       |
|                  |     |     (Ray)        |     |                 |
+------------------+     +------------------+     +------------------+
```

## Prerequisites

- Python 3.8+
- pip
- Redis (optional, for caching)
- CUDA-compatible GPU (optional, for improved performance)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/haystack-rag.git
cd haystack-rag
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

The application can be configured through environment variables or the `.env` file. Key configuration options include:

- API settings (host, port, workers)
- Vector store settings
- Model configurations
- Distributed processing settings
- Monitoring options
- Security parameters

See `.env.example` for all available configuration options.

## Usage

### Starting the Server

1. Start the API server:
```bash
python -m src.haystack_rag.main
```

2. The API will be available at `http://localhost:8000`
3. API documentation is available at `http://localhost:8000/docs`

### API Endpoints

#### Document Management

Add documents:
```bash
curl -X POST "http://localhost:8000/documents" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key" \
     -d '[{
       "content": "Your document content here",
       "metadata": {"source": "example", "date": "2024-03-14"}
     }]'
```

Retrieve a document:
```bash
curl -X GET "http://localhost:8000/documents/document_id" \
     -H "X-API-Key: your-api-key"
```

Delete a document:
```bash
curl -X DELETE "http://localhost:8000/documents/document_id" \
     -H "X-API-Key: your-api-key"
```

#### Query Processing

Process a RAG query:
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key" \
     -d '{
       "query": "What is Haystack?",
       "filters": {"source": "documentation"},
       "top_k": 5
     }'
```

### Monitoring

- Metrics are available at `http://localhost:8000/metrics`
- Health check endpoint: `http://localhost:8000/health`

## Development

### Project Structure

```
src/haystack_rag/
├── api/            # FastAPI application
├── core/           # Core configuration and utilities
├── document_store/ # Vector store implementation
├── pipeline/       # RAG pipeline implementation
└── utils/          # Utility functions
```

### Running Tests

```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Performance Optimization

- Use GPU acceleration when available
- Configure batch sizes appropriately
- Adjust embedding model based on requirements
- Enable caching for frequent queries
- Use distributed processing for large workloads

## Security Considerations

- Always use API key authentication in production
- Configure CORS settings appropriately
- Set up rate limiting
- Use secure connections (HTTPS)
- Regularly update dependencies

## Troubleshooting

Common issues and solutions:

1. **Connection errors:**
   - Check if ChromaDB is running
   - Verify Redis connection if caching is enabled
   - Ensure correct port configurations

2. **Performance issues:**
   - Check GPU utilization
   - Monitor memory usage
   - Adjust batch sizes
   - Enable caching

3. **API errors:**
   - Verify API key configuration
   - Check request format
   - Review logs for detailed error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Haystack](https://github.com/deepset-ai/haystack) for the core framework
- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Ray](https://ray.io/) for distributed processing
