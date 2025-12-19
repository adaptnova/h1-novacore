#!/usr/bin/env python3
"""
Memory Manager for Tiered Agent Memory
Created by Forge - March 14, 2025
Version: 1.0.0

This module implements a three-tiered memory architecture for Nova agents:
1. Personal Memory: Agent-specific private memory
2. Team Memory: Shared memory between specific agents (e.g., Vaeris and Synergy)
3. System Memory: Global memory accessible to all agents
"""

import json
import time
import uuid
import logging
import redis
from typing import Dict, List, Any, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory_manager")

class MemoryEntry:
    """Representation of a single memory entry"""
    
    def __init__(self, content: Any, creator: str, timestamp: float = None, 
                memory_id: str = None, metadata: Dict[str, Any] = None):
        """Initialize a memory entry
        
        Args:
            content: The content of the memory
            creator: The agent that created this memory
            timestamp: Creation time (default: current time)
            memory_id: Unique identifier (default: generated UUID)
            metadata: Additional metadata for the memory
        """
        self.memory_id = memory_id or str(uuid.uuid4())
        self.content = content
        self.creator = creator
        self.timestamp = timestamp or time.time()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the memory entry to a dictionary"""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "creator": self.creator,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Serialize the memory entry to JSON"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create a memory entry from a dictionary"""
        return cls(
            content=data["content"],
            creator=data["creator"],
            timestamp=data["timestamp"],
            memory_id=data["memory_id"],
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MemoryEntry':
        """Create a memory entry from a JSON string"""
        return cls.from_dict(json.loads(json_str))


class MemoryStore:
    """Base class for memory stores"""
    
    def __init__(self, redis_client: redis.Redis, prefix: str):
        """Initialize a memory store
        
        Args:
            redis_client: Redis client for storage
            prefix: Prefix for Redis keys
        """
        self.redis = redis_client
        self.prefix = prefix
    
    def _get_key(self, memory_id: str) -> str:
        """Get the Redis key for a memory ID"""
        return f"{self.prefix}:{memory_id}"
    
    def store(self, entry: Union[MemoryEntry, Dict, Any], creator: str = None) -> str:
        """Store a memory entry
        
        Args:
            entry: Memory entry, dictionary, or raw content
            creator: Agent creating the memory (required if entry is raw content)
            
        Returns:
            Memory ID
        """
        if isinstance(entry, MemoryEntry):
            memory_entry = entry
        elif isinstance(entry, dict) and "memory_id" in entry and "content" in entry:
            memory_entry = MemoryEntry.from_dict(entry)
        else:
            if creator is None:
                raise ValueError("Creator must be specified for raw content")
            memory_entry = MemoryEntry(content=entry, creator=creator)
        
        self.redis.set(
            self._get_key(memory_entry.memory_id),
            memory_entry.to_json()
        )
        
        # Add to time index
        self.redis.zadd(
            f"{self.prefix}:time_index",
            {memory_entry.memory_id: memory_entry.timestamp}
        )
        
        # Add to creator index
        self.redis.sadd(
            f"{self.prefix}:creator:{memory_entry.creator}",
            memory_entry.memory_id
        )
        
        # Add to full-text search index if content is string
        if isinstance(memory_entry.content, str):
            # This is a simplistic approach - in a real system, you might use
            # Redis Search or another search engine
            words = set(memory_entry.content.lower().split())
            for word in words:
                if len(word) > 2:  # Skip very short words
                    self.redis.sadd(
                        f"{self.prefix}:word:{word}",
                        memory_entry.memory_id
                    )
        
        logger.debug(f"Stored memory {memory_entry.memory_id} in {self.prefix}")
        return memory_entry.memory_id
    
    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Memory entry or None if not found
        """
        json_data = self.redis.get(self._get_key(memory_id))
        if json_data:
            return MemoryEntry.from_json(json_data)
        return None
    
    def retrieve_by_creator(self, creator: str, 
                           limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories by creator
        
        Args:
            creator: Creator identifier
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory entries
        """
        memory_ids = self.redis.smembers(f"{self.prefix}:creator:{creator}")
        if not memory_ids:
            return []
        
        memory_ids = list(memory_ids)[:limit]
        memories = []
        
        for memory_id in memory_ids:
            memory = self.retrieve(memory_id.decode('utf-8'))
            if memory:
                memories.append(memory)
        
        return memories
    
    def retrieve_recent(self, limit: int = 10) -> List[MemoryEntry]:
        """Retrieve recent memories
        
        Args:
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory entries in recency order
        """
        memory_ids = self.redis.zrevrange(
            f"{self.prefix}:time_index",
            0,
            limit - 1
        )
        
        memories = []
        for memory_id in memory_ids:
            memory = self.retrieve(memory_id.decode('utf-8'))
            if memory:
                memories.append(memory)
        
        return memories
    
    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memories by text
        
        Args:
            query: Search query
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory entries matching the query
        """
        # Split query into words and find memories containing those words
        words = [w.lower() for w in query.split() if len(w) > 2]
        if not words:
            return []
        
        # Start with memories matching the first word
        memory_ids = self.redis.smembers(f"{self.prefix}:word:{words[0]}")
        
        # Intersect with memories matching other words
        for word in words[1:]:
            word_memories = self.redis.smembers(f"{self.prefix}:word:{word}")
            memory_ids = set(memory_ids) & set(word_memories)
        
        # Convert to list and limit
        memory_ids = list(memory_ids)[:limit]
        
        # Retrieve memory entries
        memories = []
        for memory_id in memory_ids:
            memory = self.retrieve(memory_id.decode('utf-8'))
            if memory:
                memories.append(memory)
        
        return memories


class PersonalMemory(MemoryStore):
    """Personal memory for an individual agent"""
    
    def __init__(self, redis_client: redis.Redis, agent_id: str):
        """Initialize a personal memory store
        
        Args:
            redis_client: Redis client for storage
            agent_id: Agent identifier
        """
        super().__init__(redis_client, f"personal_memory:{agent_id}")
        self.agent_id = agent_id
    
    def remember(self, content: Any, metadata: Dict[str, Any] = None) -> str:
        """Store a memory for this agent
        
        Args:
            content: Memory content
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        entry = MemoryEntry(
            content=content,
            creator=self.agent_id,
            metadata=metadata or {}
        )
        return self.store(entry)
    
    def retrieve_relevant(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Retrieve memories relevant to a query
        
        Args:
            query: Search query
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memory entries
        """
        # Combine search results and recent memories for relevance
        search_results = self.search(query, limit=limit)
        search_ids = {m.memory_id for m in search_results}
        
        recent = [m for m in self.retrieve_recent(limit=limit) 
                if m.memory_id not in search_ids]
        
        # Combine both sets, prioritizing search results
        combined = search_results + recent
        return combined[:limit]


class TeamMemory(MemoryStore):
    """Shared memory for a team of agents"""
    
    def __init__(self, redis_client: redis.Redis, team_id: str, 
                 members: List[str]):
        """Initialize a team memory store
        
        Args:
            redis_client: Redis client for storage
            team_id: Team identifier
            members: List of team member agent IDs
        """
        super().__init__(redis_client, f"team_memory:{team_id}")
        self.team_id = team_id
        self.members = set(members)
        
        # Store team membership
        redis_client.delete(f"team:{team_id}:members")
        for member in members:
            redis_client.sadd(f"team:{team_id}:members", member)
            # Add to agent's team index
            redis_client.sadd(f"agent:{member}:teams", team_id)
    
    def add_member(self, agent_id: str) -> None:
        """Add a member to the team
        
        Args:
            agent_id: Agent identifier
        """
        if agent_id not in self.members:
            self.members.add(agent_id)
            self.redis.sadd(f"team:{self.team_id}:members", agent_id)
            self.redis.sadd(f"agent:{agent_id}:teams", self.team_id)
    
    def remove_member(self, agent_id: str) -> None:
        """Remove a member from the team
        
        Args:
            agent_id: Agent identifier
        """
        if agent_id in self.members:
            self.members.remove(agent_id)
            self.redis.srem(f"team:{self.team_id}:members", agent_id)
            self.redis.srem(f"agent:{agent_id}:teams", self.team_id)
    
    def is_member(self, agent_id: str) -> bool:
        """Check if an agent is a team member
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if the agent is a member
        """
        return agent_id in self.members
    
    def share(self, content: Any, creator: str, 
              metadata: Dict[str, Any] = None) -> str:
        """Share a memory with the team
        
        Args:
            content: Memory content
            creator: Agent sharing the memory
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        if not self.is_member(creator):
            raise ValueError(f"Agent {creator} is not a member of team {self.team_id}")
        
        entry = MemoryEntry(
            content=content,
            creator=creator,
            metadata=metadata or {}
        )
        return self.store(entry)
    
    def retrieve_relevant(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Retrieve memories relevant to a query
        
        Args:
            query: Search query
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memory entries
        """
        # Combine search results and recent memories for relevance
        search_results = self.search(query, limit=limit)
        search_ids = {m.memory_id for m in search_results}
        
        recent = [m for m in self.retrieve_recent(limit=limit) 
                if m.memory_id not in search_ids]
        
        # Combine both sets, prioritizing search results
        combined = search_results + recent
        return combined[:limit]


class SystemMemory(MemoryStore):
    """System-wide memory accessible to all agents"""
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize the system memory store
        
        Args:
            redis_client: Redis client for storage
        """
        super().__init__(redis_client, "system_memory")
    
    def share(self, content: Any, creator: str, 
              metadata: Dict[str, Any] = None) -> str:
        """Share a memory system-wide
        
        Args:
            content: Memory content
            creator: Agent sharing the memory
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        entry = MemoryEntry(
            content=content,
            creator=creator,
            metadata=metadata or {}
        )
        return self.store(entry)
    
    def retrieve_relevant(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Retrieve memories relevant to a query
        
        Args:
            query: Search query
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memory entries
        """
        # Combine search results and recent memories for relevance
        search_results = self.search(query, limit=limit)
        search_ids = {m.memory_id for m in search_results}
        
        recent = [m for m in self.retrieve_recent(limit=limit) 
                if m.memory_id not in search_ids]
        
        # Combine both sets, prioritizing search results
        combined = search_results + recent
        return combined[:limit]


class MemoryManager:
    """Manager for the three-tiered memory architecture"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize the memory manager
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis = redis.from_url(redis_url)
        self.system_memory = SystemMemory(self.redis)
        self.team_memories: Dict[str, TeamMemory] = {}
        self.personal_memories: Dict[str, PersonalMemory] = {}
        
        # Load existing teams from Redis
        self._load_teams()
    
    def _load_teams(self) -> None:
        """Load existing teams from Redis"""
        team_keys = self.redis.keys("team:*:members")
        for key in team_keys:
            team_id = key.decode('utf-8').split(':')[1]
            members = [m.decode('utf-8') for m in self.redis.smembers(key)]
            self.team_memories[team_id] = TeamMemory(self.redis, team_id, members)
    
    def get_personal_memory(self, agent_id: str) -> PersonalMemory:
        """Get or create personal memory for an agent
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Personal memory store
        """
        if agent_id not in self.personal_memories:
            self.personal_memories[agent_id] = PersonalMemory(self.redis, agent_id)
        return self.personal_memories[agent_id]
    
    def create_team_memory(self, team_id: str, members: List[str]) -> TeamMemory:
        """Create a team memory
        
        Args:
            team_id: Team identifier
            members: Team member agent IDs
            
        Returns:
            Team memory store
        """
        team_memory = TeamMemory(self.redis, team_id, members)
        self.team_memories[team_id] = team_memory
        return team_memory
    
    def get_team_memory(self, team_id: str) -> Optional[TeamMemory]:
        """Get a team memory
        
        Args:
            team_id: Team identifier
            
        Returns:
            Team memory store or None if not found
        """
        return self.team_memories.get(team_id)
    
    def get_agent_teams(self, agent_id: str) -> List[str]:
        """Get teams an agent belongs to
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            List of team IDs
        """
        team_ids = self.redis.smembers(f"agent:{agent_id}:teams")
        return [t.decode('utf-8') for t in team_ids]
    
    def get_memory_context(self, agent_id: str, query: str, 
                          limit_per_store: int = 3) -> Dict[str, List[MemoryEntry]]:
        """Get memory context from all stores accessible to an agent
        
        Args:
            agent_id: Agent identifier
            query: Query for retrieving relevant memories
            limit_per_store: Maximum number of memories per store
            
        Returns:
            Dictionary mapping store types to lists of memories
        """
        context = {}
        
        # Get personal memory
        personal_memory = self.get_personal_memory(agent_id)
        context["personal"] = personal_memory.retrieve_relevant(query, limit=limit_per_store)
        
        # Get team memories
        team_ids = self.get_agent_teams(agent_id)
        context["team"] = {}
        for team_id in team_ids:
            team_memory = self.get_team_memory(team_id)
            if team_memory:
                context["team"][team_id] = team_memory.retrieve_relevant(
                    query, limit=limit_per_store
                )
        
        # Get system memory
        context["system"] = self.system_memory.retrieve_relevant(query, limit=limit_per_store)
        
        return context
    
    def remember(self, agent_id: str, content: Any, 
                metadata: Dict[str, Any] = None, scope: str = "personal") -> str:
        """Store a memory with the specified scope
        
        Args:
            agent_id: Agent identifier
            content: Memory content
            metadata: Additional metadata
            scope: Memory scope ("personal", "team:<team_id>", or "system")
            
        Returns:
            Memory ID
        """
        if scope == "personal":
            personal_memory = self.get_personal_memory(agent_id)
            return personal_memory.remember(content, metadata)
        elif scope == "system":
            return self.system_memory.share(content, agent_id, metadata)
        elif scope.startswith("team:"):
            team_id = scope[5:]  # Remove "team:" prefix
            team_memory = self.get_team_memory(team_id)
            if not team_memory:
                raise ValueError(f"Team {team_id} does not exist")
            return team_memory.share(content, agent_id, metadata)
        else:
            raise ValueError(f"Invalid memory scope: {scope}")


# Initialize the global memory manager
memory_manager = None

def get_memory_manager(redis_url: str = "redis://localhost:6379/0") -> MemoryManager:
    """Get the global memory manager instance
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        Memory manager instance
    """
    global memory_manager
    if memory_manager is None:
        memory_manager = MemoryManager(redis_url)
    return memory_manager


if __name__ == "__main__":
    # Example usage
    manager = get_memory_manager()
    
    # Create/get personal memories
    vaeris_memory = manager.get_personal_memory("vaeris")
    synergy_memory = manager.get_personal_memory("synergy")
    
    # Store personal memories
    vaeris_memory.remember("This is a personal note only for Vaeris")
    synergy_memory.remember("Synergy's private implementation details")
    
    # Create team memory
    team_memory = manager.create_team_memory("vaeris_synergy", ["vaeris", "synergy"])
    
    # Share with team
    team_memory.share("Team shared knowledge about the project structure", "vaeris")
    team_memory.share("Notes on our integration patterns", "synergy")
    
    # System-wide knowledge
    manager.system_memory.share("System documentation available to all agents", "vaeris")
    
    # Get combined context
    context = manager.get_memory_context("vaeris", "integration patterns")
    
    print("Retrieved Memory Context:")
    print(f"- Personal: {len(context['personal'])} memories")
    print(f"- Team: {len(context['team'].get('vaeris_synergy', []))} memories")
    print(f"- System: {len(context['system'])} memories")