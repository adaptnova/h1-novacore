# Quick Start Guide: Live Testing Nova Framework Agents

This guide will help you quickly get started with testing the Nova Framework agents.

## 1. Setup Environment

First, set up your environment and install dependencies:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/your-repo/NovaOps.git
cd NovaOps

# Install required packages
pip install redis motor neo4j-driver pyyaml langchain autogen openai pytest pytest-asyncio

# Set your OpenAI API key
export OPENAI_API_KEY=your_api_key
```

## 2. Start Memory System

Initialize the memory system databases:

```bash
# Run the setup script
python scripts/setup_memory_system.py

# This will:
# 1. Start Redis (short-term memory)
# 2. Start MongoDB (long-term memory)
# 3. Start Neo4j (semantic memory)
# 4. Create default configuration
# 5. Test all connections
```

## 3. Run Live Tests

### Basic Test

Test both agents working together:

```bash
# Run the test script
python examples/test_agents.py

# This will:
# 1. Initialize both agents
# 2. Run memory sharing tests
# 3. Test different memory types
# 4. Show interaction between agents
```

### Interactive Testing

For interactive testing, use Python's REPL:

```python
import asyncio
from examples.langchain_agent import NovaMemoryAgent
from examples.autogen_agent import NovaMemoryGroupChat

async def test_agents():
    # Initialize agents
    langchain = NovaMemoryAgent()
    autogen = NovaMemoryGroupChat()

    await langchain.initialize()
    await autogen.initialize()

    try:
        # Test LangChain agent
        print("\nTesting LangChain agent...")
        result = await langchain.run(
            task="Research quantum computing",
            context="Focus on basic concepts"
        )
        print(f"Result: {result}")

        # Test AutoGen agent
        print("\nTesting AutoGen agent...")
        await autogen.chat(
            "Read what we know about quantum computing and expand it"
        )

    finally:
        await langchain.shutdown()
        await autogen.shutdown()

# Run the test
asyncio.run(test_agents())
```

## 4. Monitor Results

Check what's stored in each memory type:

```bash
# Short-term memory (Redis)
redis-cli keys "nova:memory:short_term:*"

# Long-term memory (MongoDB)
mongosh --eval "use nova_memory; db.long_term.find()"

# Semantic memory (Neo4j)
cypher-shell -u neo4j -p password "MATCH (n:Memory) RETURN n"
```

## 5. Example Test Cases

Here are some test cases you can try:

1. Knowledge Building:

```python
# Have agents learn about a topic
await langchain.run("Learn about machine learning")
await autogen.chat("What do you know about machine learning?")
```

2. Memory Persistence:

```python
# Store information
await langchain.run("Store facts about AI")

# Retrieve in new session
await autogen.chat("What do we know about AI?")
```

3. Knowledge Relationships:

```python
# Create connections
await langchain.run("Connect AI concepts")

# Explore relationships
await autogen.chat("How are AI concepts related?")
```

## 6. Troubleshooting

If you encounter issues:

1. Check database connections:

```bash
docker ps  # Verify containers are running
docker logs nova-memory-redis  # Check Redis logs
docker logs nova-memory-mongodb  # Check MongoDB logs
docker logs nova-memory-neo4j  # Check Neo4j logs
```

2. Verify OpenAI API:

```python
import openai
openai.api_key = "your_key"
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Test"}]
)
print(response)
```

3. Reset memory system:

```bash
# Stop containers
docker stop nova-memory-redis nova-memory-mongodb nova-memory-neo4j

# Remove containers
docker rm nova-memory-redis nova-memory-mongodb nova-memory-neo4j

# Run setup again
python scripts/setup_memory_system.py
```

## Next Steps

- Check `docs/memory_system.md` for memory system details
- See `docs/agents.md` for complete agent documentation
- Explore example scripts in `examples/` directory
- Try the test suite in `tests/` directory

For more complex scenarios and advanced usage, refer to the full documentation.
