"""
Test Script for Memory-Enhanced Agents
Demonstrates using both LangChain and AutoGen agents with the Nova Memory System.
"""

import asyncio
import yaml
from typing import Dict, Any
from datetime import datetime

from examples.langchain_agent import NovaMemoryAgent as LangChainAgent
from examples.autogen_agent import NovaMemoryGroupChat as AutoGenAgent

async def test_memory_sharing():
    """Test sharing memory between different framework agents."""
    # Initialize agents
    langchain_agent = LangChainAgent()
    autogen_agent = AutoGenAgent()

    try:
        # Initialize memory systems
        print("\nInitializing agents...")
        await langchain_agent.initialize()
        await autogen_agent.initialize()

        print("\n=== Testing Memory Sharing Between Agents ===")

        # Step 1: LangChain agent learns about neural networks
        print("\n1. LangChain Agent: Learning about neural networks")
        result = await langchain_agent.run(
            task="Research neural networks and store a comprehensive overview",
            context="Focus on fundamental concepts and architecture"
        )
        print(f"LangChain result: {result}")

        # Step 2: AutoGen agent builds on that knowledge
        print("\n2. AutoGen Agent: Expanding neural network knowledge")
        await autogen_agent.chat(
            "Read the existing information about neural networks and expand it "
            "with details about different types of neural networks"
        )

        # Step 3: LangChain agent creates relationships
        print("\n3. LangChain Agent: Creating knowledge relationships")
        result = await langchain_agent.run(
            task="Create semantic relationships between neural network concepts",
            context="Use the existing knowledge to build connections"
        )
        print(f"LangChain result: {result}")

        # Step 4: AutoGen agent explores the knowledge graph
        print("\n4. AutoGen Agent: Exploring and explaining relationships")
        await autogen_agent.chat(
            "Analyze the semantic relationships between neural network concepts "
            "and explain how they are connected"
        )

        # Step 5: Collaborative learning task
        print("\n5. Collaborative Learning Task")

        # LangChain agent researches deep learning
        print("\nLangChain Agent: Researching deep learning")
        result = await langchain_agent.run(
            task="Research deep learning and its relationship to neural networks",
            context="Focus on how deep learning extends neural network concepts"
        )
        print(f"LangChain result: {result}")

        # AutoGen agent builds on deep learning knowledge
        print("\nAutoGen Agent: Expanding deep learning knowledge")
        await autogen_agent.chat(
            "Read the deep learning information and expand it with practical "
            "applications and frameworks"
        )

        # Step 6: Knowledge verification
        print("\n6. Knowledge Verification")

        # LangChain agent verifies stored information
        print("\nLangChain Agent: Verifying stored knowledge")
        result = await langchain_agent.run(
            task="Verify and summarize all stored information about neural networks and deep learning",
            context="Check for consistency and completeness"
        )
        print(f"LangChain result: {result}")

        # AutoGen agent provides final analysis
        print("\nAutoGen Agent: Final analysis")
        await autogen_agent.chat(
            "Analyze all the stored information and provide a comprehensive "
            "summary of what we've learned about neural networks and deep learning"
        )

    finally:
        # Cleanup
        print("\nShutting down agents...")
        await langchain_agent.shutdown()
        await autogen_agent.shutdown()

async def test_memory_types():
    """Test different memory types with both agents."""
    # Initialize agents
    langchain_agent = LangChainAgent()
    autogen_agent = AutoGenAgent()

    try:
        # Initialize memory systems
        print("\nInitializing agents...")
        await langchain_agent.initialize()
        await autogen_agent.initialize()

        print("\n=== Testing Different Memory Types ===")

        # Test short-term memory
        print("\n1. Testing Short-term Memory")

        # LangChain agent stores temporary data
        print("\nLangChain Agent: Storing temporary information")
        result = await langchain_agent.run(
            task="Store current time and some temporary notes in short-term memory",
            context="Use TTL of 60 seconds"
        )
        print(f"LangChain result: {result}")

        # AutoGen agent tries to access it quickly
        print("\nAutoGen Agent: Accessing temporary information")
        await autogen_agent.chat(
            "Try to read the temporary information that was just stored"
        )

        # Wait for TTL
        print("\nWaiting for TTL expiration (5 seconds)...")
        await asyncio.sleep(5)

        # Try to access expired data
        print("\nAutoGen Agent: Trying to access expired information")
        await autogen_agent.chat(
            "Try to read the temporary information again after TTL expiration"
        )

        # Test long-term memory
        print("\n2. Testing Long-term Memory")

        # LangChain agent stores persistent data
        print("\nLangChain Agent: Storing persistent information")
        result = await langchain_agent.run(
            task="Store important concepts about machine learning in long-term memory",
            context="Include metadata about the source and timestamp"
        )
        print(f"LangChain result: {result}")

        # AutoGen agent accesses and builds on it
        print("\nAutoGen Agent: Building on stored information")
        await autogen_agent.chat(
            "Read the machine learning concepts and add your own insights"
        )

        # Test semantic memory
        print("\n3. Testing Semantic Memory")

        # LangChain agent creates knowledge graph
        print("\nLangChain Agent: Creating knowledge graph")
        result = await langchain_agent.run(
            task="Create a semantic network of AI concepts with relationships",
            context="Include machine learning, deep learning, and neural networks"
        )
        print(f"LangChain result: {result}")

        # AutoGen agent explores relationships
        print("\nAutoGen Agent: Exploring concept relationships")
        await autogen_agent.chat(
            "Analyze the relationships between AI concepts and explain the connections"
        )

    finally:
        # Cleanup
        print("\nShutting down agents...")
        await langchain_agent.shutdown()
        await autogen_agent.shutdown()

async def main():
    """Run all tests."""
    print("=== Starting Agent Tests ===")

    print("\nTest 1: Memory Sharing")
    await test_memory_sharing()

    print("\nTest 2: Memory Types")
    await test_memory_types()

    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    asyncio.run(main())