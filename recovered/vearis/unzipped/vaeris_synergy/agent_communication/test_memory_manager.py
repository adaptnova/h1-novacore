#!/usr/bin/env python3
"""
Test Script for Memory Manager
Created by Forge - March 14, 2025
Version: 1.0.0

This script demonstrates the use of the memory manager with the three-tiered
memory architecture: personal, team, and system-wide memory.
"""

import sys
import time
import random
import logging
from memory_manager import get_memory_manager, MemoryEntry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_memory_manager")

def print_memory_entry(entry, indent=""):
    """Print a memory entry in a readable format"""
    print(f"{indent}Memory ID: {entry.memory_id}")
    print(f"{indent}Creator: {entry.creator}")
    print(f"{indent}Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry.timestamp))}")
    print(f"{indent}Content: {entry.content}")
    if entry.metadata:
        print(f"{indent}Metadata: {entry.metadata}")
    print()

def test_basic_functionality():
    """Test basic memory manager functionality"""
    print("=== Testing Basic Memory Manager Functionality ===\n")
    
    # Initialize memory manager
    manager = get_memory_manager()
    
    # Create personal memories
    vaeris_memory = manager.get_personal_memory("vaeris")
    synergy_memory = manager.get_personal_memory("synergy")
    
    print("1. Storing Personal Memories")
    vaeris_memory.remember("Design patterns for agent collaboration systems", 
                          {"category": "design", "importance": "high"})
    vaeris_memory.remember("Communication protocol requires secure channels", 
                          {"category": "security", "importance": "critical"})
    synergy_memory.remember("Implementation details for the Redis connector", 
                          {"category": "implementation", "importance": "medium"})
    synergy_memory.remember("Error handling patterns for cross-agent messaging", 
                          {"category": "implementation", "importance": "high"})
    
    # Create team memory
    vs_team = manager.create_team_memory("vaeris_synergy", ["vaeris", "synergy"])
    
    print("2. Storing Team Memories")
    vs_team.share("Project roadmap for the communication framework", "vaeris",
                {"category": "planning", "importance": "high"})
    vs_team.share("Weekly coordination meeting notes", "synergy",
                {"category": "notes", "importance": "medium"})
    vs_team.share("Integration test results for Redis Streams module", "synergy",
                {"category": "testing", "importance": "high"})
    
    # Store system memories
    print("3. Storing System-Wide Memories")
    manager.system_memory.share("Server environment configuration", "vaeris",
                              {"category": "system", "importance": "medium"})
    manager.system_memory.share("Security guidelines for all agents", "synergy",
                              {"category": "security", "importance": "critical"})
    
    print("4. Retrieving Recent Personal Memories (Vaeris)")
    for entry in vaeris_memory.retrieve_recent(limit=2):
        print_memory_entry(entry, "  ")
    
    print("5. Retrieving Recent Team Memories")
    for entry in vs_team.retrieve_recent(limit=2):
        print_memory_entry(entry, "  ")
    
    print("6. Retrieving Recent System Memories")
    for entry in manager.system_memory.retrieve_recent(limit=2):
        print_memory_entry(entry, "  ")
    
    return manager

def test_search_functionality(manager):
    """Test search functionality across memory stores"""
    print("\n=== Testing Search Functionality ===\n")
    
    vaeris_memory = manager.get_personal_memory("vaeris")
    vs_team = manager.get_team_memory("vaeris_synergy")
    
    # Add some additional memories for search testing
    vaeris_memory.remember("Security is critical for agent communication")
    vs_team.share("Implementing secure channels for communication", "vaeris")
    manager.system_memory.share("Security protocols must be followed by all agents", "synergy")
    
    print("1. Searching for 'security' in Vaeris's Personal Memory")
    for entry in vaeris_memory.search("security"):
        print_memory_entry(entry, "  ")
    
    print("2. Searching for 'communication' in Team Memory")
    for entry in vs_team.search("communication"):
        print_memory_entry(entry, "  ")
    
    print("3. Searching for 'protocol security' in System Memory")
    for entry in manager.system_memory.search("protocol security"):
        print_memory_entry(entry, "  ")
    
    return manager

def test_context_retrieval(manager):
    """Test retrieving context across all memory stores"""
    print("\n=== Testing Context Retrieval ===\n")
    
    print("1. Getting Memory Context for Vaeris on 'security communication'")
    context = manager.get_memory_context("vaeris", "security communication")
    
    print("  Personal Memories:")
    for entry in context["personal"]:
        print_memory_entry(entry, "    ")
    
    print("  Team Memories:")
    for team_id, memories in context["team"].items():
        print(f"  Team: {team_id}")
        for entry in memories:
            print_memory_entry(entry, "    ")
    
    print("  System Memories:")
    for entry in context["system"]:
        print_memory_entry(entry, "    ")
    
    return manager

def test_scope_storage(manager):
    """Test storing memories with different scopes"""
    print("\n=== Testing Scope-Based Storage ===\n")
    
    # Store memories using the remember method with different scopes
    print("1. Storing Memories with Different Scopes")
    
    # Personal memory
    personal_id = manager.remember(
        "vaeris", 
        "This is a personal note about implementation ideas",
        {"category": "notes"}, 
        scope="personal"
    )
    print(f"  Stored personal memory: {personal_id}")
    
    # Team memory
    team_id = manager.remember(
        "vaeris", 
        "This is a team note about our next steps",
        {"category": "planning"}, 
        scope="team:vaeris_synergy"
    )
    print(f"  Stored team memory: {team_id}")
    
    # System memory
    system_id = manager.remember(
        "vaeris", 
        "This is a system-wide announcement about Redis upgrades",
        {"category": "announcement"}, 
        scope="system"
    )
    print(f"  Stored system memory: {system_id}")
    
    # Retrieve and print the stored memories
    print("\n2. Retrieving Stored Memories")
    
    print("  Personal Memory:")
    entry = manager.get_personal_memory("vaeris").retrieve(personal_id)
    print_memory_entry(entry, "    ")
    
    print("  Team Memory:")
    entry = manager.get_team_memory("vaeris_synergy").retrieve(team_id)
    print_memory_entry(entry, "    ")
    
    print("  System Memory:")
    entry = manager.system_memory.retrieve(system_id)
    print_memory_entry(entry, "    ")
    
    return manager

if __name__ == "__main__":
    try:
        # Run tests
        manager = test_basic_functionality()
        manager = test_search_functionality(manager)
        manager = test_context_retrieval(manager)
        manager = test_scope_storage(manager)
        
        print("\n=== All Tests Completed Successfully ===")
    except Exception as e:
        logger.error(f"Error in tests: {e}", exc_info=True)
        sys.exit(1)