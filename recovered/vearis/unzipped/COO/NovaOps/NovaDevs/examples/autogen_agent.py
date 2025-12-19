"""
AutoGen Agent with Nova Memory System Integration
Demonstrates using the Nova Memory System with AutoGen agents.
"""

import asyncio
import yaml
import autogen
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.handlers.memory import MemoryManager, MemoryType

class NovaMemoryAssistant:
    """Assistant agent with Nova Memory System integration."""

    def __init__(
        self,
        name: str,
        config_path: str = "config/memory_config.yaml",
        llm_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the assistant."""
        self.name = name
        self.config_path = config_path
        self.memory_manager = None

        # Default LLM config if none provided
        self.llm_config = llm_config or {
            "temperature": 0,
            "config_list": autogen.config_list_from_json(
                "OAI_CONFIG_LIST",
                filter_dict={"model": ["gpt-4"]}
            )
        }

        # Create AutoGen agent
        self.agent = autogen.AssistantAgent(
            name=name,
            system_message=self._create_system_message(),
            llm_config=self.llm_config
        )

    def _create_system_message(self) -> str:
        """Create system message for the agent."""
        return f"""You are {self.name}, an AI assistant with access to a sophisticated memory system.
You can store and retrieve information across different types of memory:

1. Short-term Memory (Redis):
   - Use for temporary data and caching
   - Automatically expires after TTL
   - Fast access and storage

2. Long-term Memory (MongoDB):
   - Use for persistent information
   - Structured data storage
   - Supports complex queries

3. Semantic Memory (Neo4j):
   - Use for connected knowledge
   - Graph-based relationships
   - Concept mapping and traversal

Memory Operations Available:
- store_short_term(key, content, ttl)
- store_long_term(key, content, metadata)
- store_semantic(key, content, relationships)
- retrieve_memory(memory_type, key)
- search_semantic(pattern)

Always consider what information should be stored in which type of memory.
Maintain context across conversations using the memory system."""

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

    async def store_memory(
        self,
        memory_type: MemoryType,
        key: str,
        content: Any,
        **kwargs
    ) -> bool:
        """Store information in memory."""
        try:
            return await self.memory_manager.store(
                memory_type,
                key,
                content,
                **kwargs
            )
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False

    async def retrieve_memory(
        self,
        memory_type: MemoryType,
        key: str,
        **kwargs
    ) -> Optional[Any]:
        """Retrieve information from memory."""
        try:
            return await self.memory_manager.retrieve(
                memory_type,
                key,
                **kwargs
            )
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return None

    async def search_memories(
        self,
        memory_type: MemoryType,
        pattern: str = "*"
    ) -> List[str]:
        """Search for memories matching pattern."""
        try:
            return await self.memory_manager.list_keys(memory_type, pattern)
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

class NovaMemoryUserProxy:
    """User proxy agent with memory system access."""

    def __init__(
        self,
        name: str = "user_proxy",
        code_execution_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the user proxy."""
        self.name = name

        # Default code execution config if none provided
        self.code_execution_config = code_execution_config or {
            "work_dir": "workspace",
            "use_docker": False
        }

        # Create AutoGen agent
        self.agent = autogen.UserProxyAgent(
            name=name,
            system_message="Human user proxy with access to code execution.",
            code_execution_config=self.code_execution_config,
            human_input_mode="NEVER"
        )

class NovaMemoryGroupChat:
    """Group chat with memory-enhanced agents."""

    def __init__(
        self,
        assistant_name: str = "assistant",
        user_name: str = "user",
        config_path: str = "config/memory_config.yaml"
    ):
        """Initialize the group chat."""
        # Create agents
        self.assistant = NovaMemoryAssistant(
            name=assistant_name,
            config_path=config_path
        )
        self.user_proxy = NovaMemoryUserProxy(name=user_name)

        # Create group chat
        self.group_chat = autogen.GroupChat(
            agents=[self.assistant.agent, self.user_proxy.agent],
            messages=[],
            max_round=50
        )

        # Create manager
        self.manager = autogen.GroupChatManager(
            groupchat=self.group_chat,
            llm_config=self.assistant.llm_config
        )

    async def initialize(self):
        """Initialize the memory system."""
        await self.assistant.initialize()

    async def shutdown(self):
        """Shutdown the memory system."""
        await self.assistant.shutdown()

    async def chat(self, message: str):
        """Start a group chat."""
        try:
            # Retrieve relevant memories
            memories = []
            for memory_type in MemoryType:
                keys = await self.assistant.memory_manager.list_keys(memory_type)
                for key in keys:
                    memory = await self.assistant.memory_manager.retrieve(
                        memory_type,
                        key,
                        include_metadata=True,
                        include_relationships=True
                    )
                    memories.append({
                        'type': memory_type.value,
                        'content': memory
                    })

            # Add memories to message context
            context = "Previous memories:\n" + "\n".join(
                f"- {memory['type']}: {memory['content']}"
                for memory in memories
            )

            # Start chat with context
            self.group_chat.messages = []
            await self.manager.run(f"{context}\n\nHuman: {message}")

        except Exception as e:
            print(f"Error in group chat: {e}")

async def main():
    """Example usage of AutoGen agents with Nova Memory System."""
    chat = NovaMemoryGroupChat()

    try:
        # Initialize
        await chat.initialize()

        # Example tasks
        tasks = [
            "Research the basics of neural networks and store this information",
            "What do you remember about neural networks? Can you explain the concept?",
            "Learn about deep learning frameworks and their relationships to neural networks",
            "Create a knowledge graph of AI concepts we've discussed"
        ]

        # Run tasks
        for task in tasks:
            print(f"\nTask: {task}")
            await chat.chat(task)
            print("\n" + "="*50)

    finally:
        # Clean up
        await chat.shutdown()

if __name__ == "__main__":
    asyncio.run(main())