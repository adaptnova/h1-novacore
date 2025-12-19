"""
Vaeris Nova CLI - Command line interface for the Vaeris Nova agent

This module provides a command-line interface for interacting with the Vaeris Nova agent.
"""

import os
import sys
import argparse
import logging
from typing import Dict, List, Any, Optional

from .core import VaerisNova
from .server import main as start_server

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vaeris-nova.cli")

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Vaeris Nova - Advanced Autonomous AI Super Agent")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat session")
    chat_parser.add_argument("--model", "-m", type=str, default="gpt-4o", help="Model to use")
    chat_parser.add_argument("--memory", type=str, default="local", help="Memory storage type (local, redis, mongodb)")
    chat_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the web server")
    server_parser.add_argument("--port", "-p", type=int, default=5000, help="Port to listen on")
    server_parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a single command")
    run_parser.add_argument("command", type=str, help="Command to run")
    run_parser.add_argument("--model", "-m", type=str, default="gpt-4o", help="Model to use")
    run_parser.add_argument("--memory", type=str, default="local", help="Memory storage type (local, redis, mongodb)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Default to server if no command specified
    if args.command is None:
        args.command = "server"
        args.port = 5000
        args.debug = False
    
    # Run the appropriate command
    if args.command == "chat":
        start_chat(args)
    elif args.command == "server":
        start_server()
    elif args.command == "run":
        run_command(args)
    else:
        parser.print_help()

def start_chat(args):
    """
    Start an interactive chat session.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Initialize Vaeris Nova
        vaeris = VaerisNova(
            default_model=args.model,
            memory_storage=args.memory,
            verbose=args.verbose
        )
        
        print(f"Vaeris Nova Chat (Model: {args.model})")
        print("Type 'exit' or 'quit' to end the session")
        print("Type 'clear' to clear the conversation history")
        print("-" * 50)
        
        # Start chat loop
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Check for clear command
            if user_input.lower() == "clear":
                vaeris.memory_manager.clear_memory()
                print("Conversation history cleared")
                continue
            
            # Process input
            print("\nVaeris: ", end="", flush=True)
            
            try:
                # Invoke the agent
                result = vaeris.invoke(user_input)
                
                # Print the response
                print(result.get("output", "No response"))
            except Exception as e:
                print(f"Error: {e}")
    
    except Exception as e:
        logger.error(f"Error in chat session: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def run_command(args):
    """
    Run a single command.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Initialize Vaeris Nova
        vaeris = VaerisNova(
            default_model=args.model,
            memory_storage=args.memory
        )
        
        # Process command
        try:
            # Invoke the agent
            result = vaeris.invoke(args.command)
            
            # Print the response
            print(result.get("output", "No response"))
        except Exception as e:
            print(f"Error: {e}")
    
    except Exception as e:
        logger.error(f"Error running command: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()