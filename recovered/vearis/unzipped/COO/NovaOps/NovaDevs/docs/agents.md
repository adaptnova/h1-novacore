# Nova Framework Test Agents

This document describes the test agents implemented to demonstrate the Nova Framework's memory system capabilities using different AI frameworks.

## Overview

We provide two different agent implementations:

1. LangChain Agent - Uses LangChain's agent framework
2. AutoGen Agent - Uses Microsoft's AutoGen framework

Both agents are integrated with the Nova Memory System, demonstrating how different frameworks can utilize our three-tier memory architecture.

## Prerequisites

1. Install required dependencies:

```bash
pip install langchain autogen openai
```

2. Set up environment variables:

```bash
export OPENAI_API_KEY=your_api_key
```

3. Ensure the memory system is running:

```bash
python scripts/setup_memory_system.py
```

## Agent Capabilities

### LangChain Agent (`examples/langchain_agent.py`)

- Direct memory operations through tools
- Single-agent architecture
- Task-focused interactions
- Structured memory access

Features:

- Memory-aware prompting
- Tool-based memory operations
- Async memory access
- Error handling

Example usage:

```python
from examples.langchain_agent import NovaMemoryAgent

async def main():
    agent = NovaMemoryAgent()
    await agent.initialize()

    try:
        result = await agent.run(
            task="Learn about neural networks",
            context="Focus on basic concepts"
        )
        print(result)
    finally:
        await agent.shutdown()
```

### AutoGen Agent (`examples/autogen_agent.py`)

- Multi-agent group chat
- Memory-enhanced conversations
- Collaborative learning
- Context-aware responses

Features:

- Group chat architecture
- Memory context integration
- Automatic memory retrieval
- Relationship exploration

Example usage:

```python
from examples.autogen_agent import NovaMemoryGroupChat

async def main():
    chat = NovaMemoryGroupChat()
    await chat.initialize()

    try:
        await chat.chat(
            "Research deep learning and its applications"
        )
    finally:
        await chat.shutdown()
```

## Testing Both Agents

The `examples/test_agents.py` script demonstrates how both agents can work together:

```python
from examples.test_agents import test_memory_sharing, test_memory_types

async def main():
    # Test memory sharing between agents
    await test_memory_sharing()

    # Test different memory types
    await test_memory_types()
```

### Test Scenarios

1. Memory Sharing Test:

   - LangChain agent learns about neural networks
   - AutoGen agent expands on that knowledge
   - LangChain agent creates relationships
   - AutoGen agent explores the knowledge graph
   - Collaborative learning about deep learning
   - Knowledge verification by both agents

2. Memory Types Test:
   - Short-term memory tests with TTL
   - Long-term memory persistence
   - Semantic memory relationships
   - Cross-agent memory access
   - Memory type-specific operations

## Best Practices

1. Memory Usage:

   - Use short-term memory for temporary context
   - Use long-term memory for persistent knowledge
   - Use semantic memory for connected concepts

2. Agent Interaction:

   - Initialize agents before use
   - Always clean up with shutdown
   - Handle errors appropriately
   - Verify memory operations

3. Performance:
   - Reuse agent instances when possible
   - Clean up expired memories
   - Use appropriate TTLs
   - Monitor memory usage

## Common Patterns

1. Knowledge Building:

```python
# First agent learns
await langchain_agent.run(
    task="Learn about topic X",
    context="Focus on basics"
)

# Second agent expands
await autogen_agent.chat(
    "Expand on what we know about topic X"
)
```

2. Memory Verification:

```python
# Store information
await agent.store_memory(
    MemoryType.LONG_TERM,
    "concept:x",
    {"data": "information"}
)

# Verify storage
result = await agent.retrieve_memory(
    MemoryType.LONG_TERM,
    "concept:x"
)
```

3. Relationship Creation:

```python
# Create semantic relationships
await agent.store_memory(
    MemoryType.SEMANTIC,
    "concept:a",
    {"data": "A"},
    relationships=[{
        "target_key": "concept:b",
        "properties": {"type": "related_to"}
    }]
)
```

## Troubleshooting

1. Memory Access Issues:

   - Verify memory system is running
   - Check connection configurations
   - Ensure proper initialization
   - Verify key formats

2. Agent Communication:

   - Check OpenAI API key
   - Verify prompt formats
   - Monitor token usage
   - Check error logs

3. Performance Issues:
   - Monitor memory usage
   - Check database connections
   - Verify TTL settings
   - Review task complexity

## Contributing

1. Adding New Features:

   - Follow existing patterns
   - Add appropriate tests
   - Update documentation
   - Maintain async patterns

2. Testing:
   - Run existing test suite
   - Add new test cases
   - Verify memory cleanup
   - Test error conditions

## License

MIT License - See LICENSE file for details
