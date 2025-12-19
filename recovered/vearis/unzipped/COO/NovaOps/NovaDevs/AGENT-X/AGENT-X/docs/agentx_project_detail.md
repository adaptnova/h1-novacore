# AGENT-X Project Detail

## Project Overview

AGENT-X is a full-stack application featuring a dark-themed GUI and a multi-agent system (MAS) architecture. The application is built using React for the frontend and FastAPI for the backend. It integrates LangChain and LangGraph for managing autonomous AI agents and orchestrators.

## Technical Implementation Details

- **Frontend**: Built with React and Material-UI, featuring a dark theme.
- **Backend**: Implemented with FastAPI, running as a systemd service.
- **Multi-Agent System**: Utilizes LangChain and LangGraph for agent and orchestrator management.

## Messaging and API Integrations

- **RabbitMQ**: Integrated using Pika for message queuing.
- **Kafka**: Integrated using Confluent Kafka for distributed streaming.
- **Kong API**: Interacted with using HTTP requests for API management.
- **Istio**: Set up for service mesh management.

## LLM Integrations

- **OpenAI GPT-4**: Integrated for advanced language processing.
- **Cohere, Llama, Mistral, AIS**: Various models integrated for specific tasks.

- **Neo4j**: Connected using the Neo4j Python driver.
- **Milvus**: Integrated with PyMilvus for vector similarity search.
- **PostgreSQL with TimescaleDB**: Connected using psycopg2.
- **FAISS**: Utilized for efficient similarity search.
- **MongoDB**: Connected using PyMongo.
- **Weaviate**: Integrated with the Weaviate Python client.
- **ArangoDB**: Connected using PyArango.
- **Redis**: Connected using the Redis Python client.
- **Couchbase**: Connected using the Couchbase Python SDK.
- **ChromaDB**: Integrated with the ChromaDB client.

## Agent Enhancements

- **Memory Management**: Agents have short and long-term memory capabilities.
- **Reasoning**: Agents can simulate reasoning and task execution.
- **Tool Creation**: Agents can create their own tools dynamically.

- **API Communication**: The frontend communicates with the backend via RESTful API endpoints.
- **Systemd Service**: The backend is managed as a systemd service for reliability and ease of deployment.

## Migration Guides

- **Frontend**: Ensure Node.js and npm are installed. Run `npm install` in the `frontend` directory.
- **Backend**: Set up a Python virtual environment and install dependencies with `pip install -r requirements.txt`.

## API Documentation

- **GET /agents**: Retrieves a list of agent tasks.
- **GET /orchestrators**: Retrieves a list of orchestrator tasks.

## Integration Points

- **Frontend and Backend**: Integrated via RESTful API calls.

## Suggested Future Enhancements

- Implement additional agent roles and tasks.
- Enhance the UI with more interactive elements and animations.
- Add authentication and authorization for secure access.

## Files Touched

- `frontend/src/App.tsx`: Updated to fetch and display data from the backend.
- `backend/main.py`: Added endpoints for agents and orchestrators.
- `backend/agents.py`: Defined classes for agents and orchestrators.
- `backend/agentx.service`: Created systemd service file for the backend.

## Challenges and Solutions

- **Dependency Conflicts**: Resolved by using `--legacy-peer-deps` during installation.
- **Systemd Configuration**: Ensured proper setup for running the backend as a service.

## Steps Complete

- Project structure created.
- Dark theme implemented.
- Backend and frontend integrated.
- Systemd service configured.
- Documentation created.
