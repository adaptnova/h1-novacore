"""
LangChain Agent with Nova Memory System Integration
Demonstrates using the Nova Memory System with a LangChain agent.
"""

import asyncio
import yaml
from typing import Any, Dict, List
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import AgentAction, AgentFinish

from src.handlers.memory import MemoryManager, MemoryType

class NovaMemoryPromptTemplate(StringPromptTemplate):
    """Custom prompt template that includes memory context."""

    template = """You are an AI assistant with access to a sophisticated memory system.
You can store and retrieve information across different types of memory:
- Short-term memory for temporary data
- Long-term memory for persistent information
- Semantic memory for connected knowledge

Current conversation context:
{context}

Previous relevant memories:
{memories}

Task: {task}

Available tools:
{tools}

Take into account the context and memories to determine the next action.
Format your response as an action using the available tools.

Response: """

    def format(self, **kwargs) -> str:
        """Format the prompt template."""
        # Get memories from the memory system
        memories = kwargs.pop('memories', [])
        formatted_memories = "\n".join(
            f"- {memory['type']}: {memory['content']}"
            for memory in memories
        )

        # Format tools
        tools = kwargs.pop('tools', [])
        formatted_tools = "\n".join(
            f"- {tool.name}: {tool.description}"
            for tool in tools
        )

        return self.template.format(
            memories=formatted_memories,
            tools=formatted_tools,
            **kwargs
        )

class NovaMemoryAgent:
    """Agent that uses Nova Memory System for enhanced reasoning."""

    def __init__(self, config_path: str = "config/memory_config.yaml"):
        """Initialize the agent with memory system."""
        self.llm = ChatOpenAI(temperature=0)
        self.memory_manager = None
        self.config_path = config_path
        self.tools = self._create_tools()
        self.prompt = NovaMemoryPromptTemplate(
            input_variables=["context", "memories", "task", "tools"]
        )

        # Create LangChain agent
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.agent = LLMSingleActionAgent(
            llm_chain=self.llm_chain,
            output_parser=self._parse_output,
            stop=["\nObservation:"],
            allowed_tools=[tool.name for tool in self.tools]
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )

    def _create_tools(self) -> List[Tool]:
        """Create tools for memory operations."""
        return [
            Tool(
                name="store_short_term",
                func=self._store_short_term,
                description="Store temporary information in short-term memory"
            ),
            Tool(
                name="store_long_term",
                func=self._store_long_term,
                description="Store persistent information in long-term memory"
            ),
            Tool(
                name="store_semantic",
                func=self._store_semantic,
                description="Store connected information in semantic memory"
            ),
            Tool(
                name="retrieve_memory",
                func=self._retrieve_memory,
                description="Retrieve information from any memory type"
            ),
            Tool(
                name="search_semantic",
                func=self._search_semantic,
                description="Search for related concepts in semantic memory"
            )
        ]

    async def _store_short_term(self, data: Dict[str, Any]) -> str:
        """Store data in short-term memory."""
        key = data.get('key')
        content = data.get('content')
        ttl = data.get('ttl', 3600)  # 1 hour default

        success = await self.memory_manager.store(
            MemoryType.SHORT_TERM,
            key,
            content,
            ttl=ttl
        )
        return f"Stored in short-term memory: {success}"

    async def _store_long_term(self, data: Dict[str, Any]) -> str:
        """Store data in long-term memory."""
        key = data.get('key')
        content = data.get('content')
        metadata = data.get('metadata', {})

        success = await self.memory_manager.store(
            MemoryType.LONG_TERM,
            key,
            content,
            metadata=metadata
        )
        return f"Stored in long-term memory: {success}"

    async def _store_semantic(self, data: Dict[str, Any]) -> str:
        """Store data in semantic memory."""
        key = data.get('key')
        content = data.get('content')
        relationships = data.get('relationships', [])

        success = await self.memory_manager.store(
            MemoryType.SEMANTIC,
            key,
            content,
            relationships=relationships
        )
        return f"Stored in semantic memory: {success}"

    async def _retrieve_memory(self, data: Dict[str, Any]) -> str:
        """Retrieve data from memory."""
        memory_type = MemoryType(data.get('type'))
        key = data.get('key')
        include_metadata = data.get('include_metadata', False)
        include_relationships = data.get('include_relationships', False)

        result = await self.memory_manager.retrieve(
            memory_type,
            key,
            include_metadata=include_metadata,
            include_relationships=include_relationships
        )
        return f"Retrieved from {memory_type.value}: {result}"

    async def _search_semantic(self, data: Dict[str, Any]) -> str:
        """Search semantic memory for related concepts."""
        pattern = data.get('pattern', '*')
        keys = await self.memory_manager.list_keys(
            MemoryType.SEMANTIC,
            pattern
        )

        results = []
        for key in keys:
            result = await self.memory_manager.retrieve(
                MemoryType.SEMANTIC,
                key,
                include_relationships=True
            )
            results.append(result)

        return f"Found related concepts: {results}"

    def _parse_output(self, llm_output: str) -> AgentAction:
        """Parse LLM output into agent action."""
        # Simple parsing - in practice, you'd want more robust parsing
        try:
            tool_name = llm_output.split()[0]
            tool_input = llm_output[len(tool_name):].strip()
            return AgentAction(tool=tool_name, tool_input=tool_input, log=llm_output)
        except Exception:
            return AgentFinish(return_values={"output": llm_output}, log=llm_output)

    async def initialize(self):
        """Initialize the memory system."""
        # Load configuration
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Initialize memory manager
        self.memory_manager = MemoryManager(config)
        await self.memory_manager.connect()

    async def shutdown(self):
        """Shutdown the memory system."""
        if self.memory_manager:
            await self.memory_manager.disconnect()

    async def run(self, task: str, context: str = "") -> str:
        """Run the agent on a task."""
        try:
            # Get relevant memories
            memories = []
            for memory_type in MemoryType:
                keys = await self.memory_manager.list_keys(memory_type)
                for key in keys:
                    memory = await self.memory_manager.retrieve(
                        memory_type,
                        key,
                        include_metadata=True,
                        include_relationships=True
                    )
                    memories.append({
                        'type': memory_type.value,
                        'content': memory
                    })

            # Execute agent
            result = await self.agent_executor.arun(
                context=context,
                memories=memories,
                task=task,
                tools=self.tools
            )

            return result

        except Exception as e:
            return f"Error executing task: {str(e)}"

async def main():
    """Example usage of the NovaMemoryAgent."""
    agent = NovaMemoryAgent()

    try:
        # Initialize agent
        await agent.initialize()

        # Example task
        task = "Learn about machine learning and store this knowledge"
        context = "User is interested in AI and machine learning concepts"

        # Run agent
        result = await agent.run(task, context)
        print(f"Agent result: {result}")

    finally:
        # Clean up
        await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main())