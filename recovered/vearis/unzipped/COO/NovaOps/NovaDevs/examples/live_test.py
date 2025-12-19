#!/usr/bin/env python3
"""
Live Test Script for Nova Framework Agents
Run this script to see the agents in action with real-world tasks.
"""

import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Any

from examples.langchain_agent import NovaMemoryAgent
from examples.autogen_agent import NovaMemoryGroupChat

class LiveTest:
    """Live test runner for Nova Framework agents."""

    def __init__(self):
        """Initialize test runner."""
        self.langchain = NovaMemoryAgent()
        self.autogen = NovaMemoryGroupChat()

    async def setup(self):
        """Initialize agents."""
        print("\nInitializing agents...")
        await self.langchain.initialize()
        await self.autogen.initialize()

    async def cleanup(self):
        """Cleanup agents."""
        print("\nShutting down agents...")
        await self.langchain.shutdown()
        await self.autogen.shutdown()

    async def run_task(self, task: str):
        """Run a single task with both agents."""
        print(f"\n{'='*50}")
        print(f"Task: {task}")
        print(f"{'='*50}")

        # LangChain agent processes task
        print("\nLangChain Agent processing...")
        result = await self.langchain.run(task=task, context="Focus on accuracy and detail")
        print(f"LangChain result: {result}")

        # AutoGen agent builds on results
        print("\nAutoGen Agent processing...")
        await self.autogen.chat(
            f"Review and expand upon what we learned about: {task}"
        )

    async def run_all_tests(self):
        """Run all test scenarios."""
        tasks = [
            # Knowledge Building Tasks
            "Research and explain the concept of transformers in machine learning",
            "Investigate the differences between CNN and RNN architectures",
            "Study the principles of reinforcement learning",

            # Knowledge Integration Tasks
            "Connect the concepts of transformers, CNNs, and RNNs",
            "Explain how reinforcement learning relates to neural networks",
            "Create a comprehensive overview of modern deep learning approaches",

            # Practical Application Tasks
            "Describe real-world applications of transformers",
            "Explain how CNNs are used in computer vision",
            "Detail how RNNs are applied in natural language processing"
        ]

        for task in tasks:
            await self.run_task(task)
            print("\nWaiting before next task...")
            await asyncio.sleep(2)  # Prevent rate limiting

def print_header():
    """Print test header."""
    print("\n" + "="*60)
    print("Nova Framework Live Agent Test")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

def print_footer():
    """Print test footer."""
    print("\n" + "="*60)
    print("Live Test Completed")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

async def main():
    """Main test function."""
    print_header()

    test = LiveTest()
    try:
        await test.setup()
        await test.run_all_tests()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
    finally:
        await test.cleanup()
        print_footer()

def run_test():
    """Run the live test."""
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

if __name__ == "__main__":
    run_test()