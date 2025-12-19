# Vaeris Nova: Advanced AI Super Agent

Vaeris Nova is a comprehensive, autonomous AI agent system built on LangChain and LangGraph with advanced capabilities, tools, and multi-LLM support.

## Features

- **Multi-Model Support**: Dynamically select from OpenAI, Anthropic, Google, and Mistral models
- **Advanced Tool Integration**: Comprehensive set of tools for code, search, file operations, etc.
- **Sophisticated Memory System**: Persistent memory with semantic search capability
- **Agent Collaboration**: Create specialized sub-agents that collaborate on complex tasks
- **Modern Interface**: Sleek dark-themed UI with real-time streaming responses
- **Extensible Framework**: Easily add custom tools and capabilities

## Architecture

Vaeris Nova is built on a modern architecture that combines the strengths of LangChain and LangGraph:

```
┌─────────────────────────┐
│   Vaeris Nova Core      │
├─────────────────────────┤
│                         │
│  ┌─────────┐ ┌────────┐ │
│  │ LangChain│ │LangGraph│ │
│  └─────────┘ └────────┘ │
│                         │
│  ┌─────────┐ ┌────────┐ │
│  │ Memory  │ │ Tools  │ │
│  └─────────┘ └────────┘ │
│                         │
│  ┌─────────────────────┐│
│  │   Model Router      ││
│  └─────────────────────┘│
└─────────────────────────┘
```

## Getting Started

### Prerequisites

- Python 3.9+
- Redis (for memory persistence, optional)
- API keys for LLM providers

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vaeris-nova.git
   cd vaeris-nova
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export OPENAI_API_KEY="your_openai_key"
   export ANTHROPIC_API_KEY="your_anthropic_key"
   export GOOGLE_API_KEY="your_google_key"
   export MISTRAL_API_KEY="your_mistral_key"
   ```

4. Start Redis (optional):
   ```bash
   redis-server
   ```

5. Launch the UI:
   ```bash
   python -m vaeris_nova.ui.server
   ```

## Usage Examples

### Basic Usage

```python
from vaeris_nova import VaerisNova

# Initialize Vaeris Nova
vaeris = VaerisNova(
    name="Vaeris",
    default_model="gpt-4o",
    memory_storage="redis",
    verbose=True
)

# Invoke the agent
result = vaeris.invoke("Analyze the performance of this code snippet: def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)")
```

### Creating Sub-Agents

```python
# Create a specialized code assistant
code_agent = vaeris.create_subagent(
    name="CodeAssistant",
    system_prompt="You are a specialized code assistant focused on Python performance optimization.",
    model="claude-3-sonnet"
)

# Create a research assistant
research_agent = vaeris.create_subagent(
    name="ResearchAssistant",
    system_prompt="You are a research assistant specialized in scientific literature analysis.",
    model="claude-3-opus"
)
```

## Customization

### Adding Custom Tools

1. Create a tool class inheriting from `BaseTool`:

```python
from langchain_core.tools import BaseTool

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "Description of what your tool does"
    
    def _run(self, input_str: str) -> str:
        # Implement your tool logic here
        return f"Result: {input_str}"
    
    async def _arun(self, input_str: str) -> str:
        # Async implementation
        return self._run(input_str)
```

2. Add your tool to Vaeris:

```python
vaeris.tool_manager.add_tool(MyCustomTool())
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.