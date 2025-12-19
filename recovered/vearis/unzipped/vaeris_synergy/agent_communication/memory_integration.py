#!/usr/bin/env python3
"""
Memory Integration for Agent Communication
Created by Forge - March 14, 2025
Version: 1.0.0

This module connects the memory manager to Redis Streams for inter-agent communication.
It allows agents to read from and write to different memory tiers.
"""

import os
import sys
import json
import time
import logging
import threading
import redis
import argparse
from typing import Dict, List, Any, Optional, Union, Callable

# Import memory manager
from memory_manager import get_memory_manager, MemoryEntry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory_integration")

class MemoryIntegration:
    """Integration between memory system and Redis Streams communication"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0",
                 stream_prefix: str = "nova_agents",
                 memory_channel: str = "memory"):
        """Initialize the memory integration
        
        Args:
            redis_url: Redis connection URL
            stream_prefix: Prefix for Redis Streams
            memory_channel: Channel for memory-related messages
        """
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url)
        self.stream_prefix = stream_prefix
        self.memory_channel = memory_channel
        self.memory_manager = get_memory_manager(redis_url)
        
        # Stream names
        self.memory_stream = f"{stream_prefix}:{memory_channel}"
        
        # Create streams if they don't exist
        self._ensure_streams_exist()
        
        # Track the last IDs we've processed
        self.last_ids = {
            self.memory_stream: "0"
        }
        
        # Flag to control the background thread
        self.running = False
        self.thread = None
    
    def _ensure_streams_exist(self) -> None:
        """Ensure the required Redis Streams exist"""
        # For Redis Streams, writing to a non-existent stream creates it,
        # so we'll just send a dummy message that we can ignore later
        for stream in [self.memory_stream]:
            try:
                # Check if the stream exists
                info = self.redis.xinfo_stream(stream)
                logger.info(f"Stream {stream} exists with {info['length']} entries")
            except redis.exceptions.ResponseError:
                # Stream doesn't exist, create it with a dummy message
                self.redis.xadd(
                    stream,
                    {"type": "system", "content": "Stream initialization"}
                )
                logger.info(f"Created stream {stream}")
    
    def start_listening(self) -> None:
        """Start listening for memory events in the background"""
        if self.running:
            logger.warning("Already listening for memory events")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._listen_for_events)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Started listening for memory events")
    
    def stop_listening(self) -> None:
        """Stop listening for memory events"""
        if not self.running:
            logger.warning("Not currently listening for memory events")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("Stopped listening for memory events")
    
    def _listen_for_events(self) -> None:
        """Background thread to listen for memory events"""
        while self.running:
            try:
                # Read new messages from the memory stream
                streams = {self.memory_stream: self.last_ids[self.memory_stream]}
                response = self.redis.xread(streams, count=10, block=1000)
                
                for stream_name, messages in response:
                    stream_name = stream_name.decode('utf-8')
                    for message_id, data in messages:
                        message_id = message_id.decode('utf-8')
                        self.last_ids[stream_name] = message_id
                        
                        # Process the message
                        self._process_memory_message(stream_name, message_id, data)
            
            except Exception as e:
                logger.error(f"Error in memory event listener: {e}", exc_info=True)
                time.sleep(1.0)  # Avoid tight loop in case of repeated errors
    
    def _process_memory_message(self, stream_name: str, message_id: str, 
                               data: Dict[bytes, bytes]) -> None:
        """Process a memory-related message
        
        Args:
            stream_name: Name of the stream
            message_id: Message ID
            data: Message data
        """
        try:
            # Convert bytes keys/values to strings
            data = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
            
            message_type = data.get("type")
            if not message_type:
                logger.warning(f"Received message without type: {data}")
                return
            
            if message_type == "memory:store":
                # Store a memory entry
                self._handle_store_memory(data)
            elif message_type == "memory:retrieve":
                # Retrieve and respond with memory entries
                self._handle_retrieve_memory(data)
            elif message_type == "memory:search":
                # Search and respond with memory entries
                self._handle_search_memory(data)
            elif message_type == "system":
                # System message, can be ignored
                pass
            else:
                logger.warning(f"Unknown message type: {message_type}")
        
        except Exception as e:
            logger.error(f"Error processing memory message: {e}", exc_info=True)
    
    def _handle_store_memory(self, data: Dict[str, str]) -> None:
        """Handle a request to store a memory
        
        Args:
            data: Message data
        """
        try:
            agent_id = data.get("agent_id")
            content = data.get("content")
            scope = data.get("scope", "personal")
            
            if not agent_id or not content:
                logger.warning("Missing required fields in store memory request")
                return
            
            # Parse JSON fields
            metadata = json.loads(data.get("metadata", "{}"))
            
            # Store the memory
            memory_id = self.memory_manager.remember(
                agent_id=agent_id,
                content=content,
                metadata=metadata,
                scope=scope
            )
            
            # Send response
            self.redis.xadd(
                f"{self.stream_prefix}:{agent_id}",
                {
                    "type": "memory:stored",
                    "memory_id": memory_id,
                    "scope": scope,
                    "request_id": data.get("request_id", "")
                }
            )
            
            logger.info(f"Stored memory {memory_id} for agent {agent_id} with scope {scope}")
        
        except Exception as e:
            logger.error(f"Error handling store memory: {e}", exc_info=True)
    
    def _handle_retrieve_memory(self, data: Dict[str, str]) -> None:
        """Handle a request to retrieve memories
        
        Args:
            data: Message data
        """
        try:
            agent_id = data.get("agent_id")
            memory_id = data.get("memory_id")
            scope = data.get("scope", "personal")
            
            if not agent_id:
                logger.warning("Missing agent_id in retrieve memory request")
                return
            
            # Get the appropriate memory store
            if scope == "personal":
                memory_store = self.memory_manager.get_personal_memory(agent_id)
                entry = memory_store.retrieve(memory_id) if memory_id else None
            elif scope == "system":
                entry = self.memory_manager.system_memory.retrieve(memory_id) if memory_id else None
            elif scope.startswith("team:"):
                team_id = scope[5:]  # Remove "team:" prefix
                team_memory = self.memory_manager.get_team_memory(team_id)
                if not team_memory:
                    logger.warning(f"Team {team_id} does not exist")
                    return
                entry = team_memory.retrieve(memory_id) if memory_id else None
            else:
                logger.warning(f"Invalid memory scope: {scope}")
                return
            
            # If no specific memory ID, get recent memories
            entries = []
            if memory_id and entry:
                entries = [entry]
            elif not memory_id:
                limit = int(data.get("limit", "5"))
                if scope == "personal":
                    entries = memory_store.retrieve_recent(limit=limit)
                elif scope == "system":
                    entries = self.memory_manager.system_memory.retrieve_recent(limit=limit)
                elif scope.startswith("team:"):
                    team_id = scope[5:]
                    team_memory = self.memory_manager.get_team_memory(team_id)
                    if team_memory:
                        entries = team_memory.retrieve_recent(limit=limit)
            
            # Send response
            self._send_memory_entries(
                agent_id=agent_id,
                entries=entries,
                response_type="memory:retrieved",
                request_id=data.get("request_id", "")
            )
            
            logger.info(f"Retrieved {len(entries)} memories for agent {agent_id} with scope {scope}")
        
        except Exception as e:
            logger.error(f"Error handling retrieve memory: {e}", exc_info=True)
    
    def _handle_search_memory(self, data: Dict[str, str]) -> None:
        """Handle a request to search memories
        
        Args:
            data: Message data
        """
        try:
            agent_id = data.get("agent_id")
            query = data.get("query")
            scope = data.get("scope", "personal")
            
            if not agent_id or not query:
                logger.warning("Missing required fields in search memory request")
                return
            
            limit = int(data.get("limit", "5"))
            
            # Search the appropriate memory store
            entries = []
            if scope == "personal":
                memory_store = self.memory_manager.get_personal_memory(agent_id)
                entries = memory_store.search(query, limit=limit)
            elif scope == "system":
                entries = self.memory_manager.system_memory.search(query, limit=limit)
            elif scope.startswith("team:"):
                team_id = scope[5:]  # Remove "team:" prefix
                team_memory = self.memory_manager.get_team_memory(team_id)
                if team_memory:
                    entries = team_memory.search(query, limit=limit)
            elif scope == "all":
                # Search across all stores
                context = self.memory_manager.get_memory_context(
                    agent_id, query, limit_per_store=limit
                )
                entries = context.get("personal", [])
                for team_entries in context.get("team", {}).values():
                    entries.extend(team_entries)
                entries.extend(context.get("system", []))
                # Limit the total number of entries
                entries = entries[:limit]
            else:
                logger.warning(f"Invalid memory scope: {scope}")
                return
            
            # Send response
            self._send_memory_entries(
                agent_id=agent_id,
                entries=entries,
                response_type="memory:searched",
                request_id=data.get("request_id", "")
            )
            
            logger.info(f"Searched for '{query}' in {scope} scope for agent {agent_id}, found {len(entries)} results")
        
        except Exception as e:
            logger.error(f"Error handling search memory: {e}", exc_info=True)
    
    def _send_memory_entries(self, agent_id: str, entries: List[MemoryEntry],
                            response_type: str, request_id: str = "") -> None:
        """Send memory entries to an agent
        
        Args:
            agent_id: Agent identifier
            entries: Memory entries to send
            response_type: Type of response
            request_id: Original request ID
        """
        try:
            # Convert entries to dictionaries
            entry_dicts = [entry.to_dict() for entry in entries]
            
            # Serialize to JSON
            entries_json = json.dumps(entry_dicts)
            
            # Send to the agent's stream
            self.redis.xadd(
                f"{self.stream_prefix}:{agent_id}",
                {
                    "type": response_type,
                    "entries": entries_json,
                    "count": str(len(entries)),
                    "request_id": request_id
                }
            )
        
        except Exception as e:
            logger.error(f"Error sending memory entries: {e}", exc_info=True)
    
    def store_memory(self, agent_id: str, content: Any, metadata: Dict[str, Any] = None,
                    scope: str = "personal", request_id: str = "") -> None:
        """Store a memory entry
        
        Args:
            agent_id: Agent identifier
            content: Memory content
            metadata: Additional metadata
            scope: Memory scope ("personal", "team:<team_id>", or "system")
            request_id: Optional request identifier for asynchronous operations
        """
        try:
            # Convert non-string content to JSON
            if not isinstance(content, str):
                content = json.dumps(content)
            
            # Convert metadata to JSON
            metadata_json = json.dumps(metadata or {})
            
            # Send store request to the memory stream
            self.redis.xadd(
                self.memory_stream,
                {
                    "type": "memory:store",
                    "agent_id": agent_id,
                    "content": content,
                    "metadata": metadata_json,
                    "scope": scope,
                    "request_id": request_id
                }
            )
        
        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
    
    def retrieve_memory(self, agent_id: str, memory_id: Optional[str] = None,
                       scope: str = "personal", limit: int = 5,
                       request_id: str = "") -> None:
        """Retrieve a memory entry or recent memories
        
        Args:
            agent_id: Agent identifier
            memory_id: Memory identifier (None for recent memories)
            scope: Memory scope ("personal", "team:<team_id>", or "system")
            limit: Maximum number of recent memories to retrieve
            request_id: Optional request identifier for asynchronous operations
        """
        try:
            # Send retrieve request to the memory stream
            self.redis.xadd(
                self.memory_stream,
                {
                    "type": "memory:retrieve",
                    "agent_id": agent_id,
                    "memory_id": memory_id or "",
                    "scope": scope,
                    "limit": str(limit),
                    "request_id": request_id
                }
            )
        
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}", exc_info=True)
    
    def search_memory(self, agent_id: str, query: str, scope: str = "personal",
                     limit: int = 5, request_id: str = "") -> None:
        """Search for memories
        
        Args:
            agent_id: Agent identifier
            query: Search query
            scope: Memory scope ("personal", "team:<team_id>", "system", or "all")
            limit: Maximum number of results
            request_id: Optional request identifier for asynchronous operations
        """
        try:
            # Send search request to the memory stream
            self.redis.xadd(
                self.memory_stream,
                {
                    "type": "memory:search",
                    "agent_id": agent_id,
                    "query": query,
                    "scope": scope,
                    "limit": str(limit),
                    "request_id": request_id
                }
            )
        
        except Exception as e:
            logger.error(f"Error searching memory: {e}", exc_info=True)
    
    def setup_vaeris_synergy_team(self) -> None:
        """Set up the Vaeris-Synergy team memory"""
        # Create team memory if it doesn't exist
        team_id = "vaeris_synergy"
        team_memory = self.memory_manager.get_team_memory(team_id)
        if not team_memory:
            self.memory_manager.create_team_memory(team_id, ["vaeris", "synergy"])
            logger.info(f"Created team memory for {team_id}")
            
            # Add some initial shared memories
            team_memory = self.memory_manager.get_team_memory(team_id)
            team_memory.share(
                "Team communication protocol established with Redis Streams",
                "vaeris",
                {"category": "infrastructure", "date": time.strftime("%Y-%m-%d")}
            )
            team_memory.share(
                "Shared memory architecture uses three tiers: personal, team, and system",
                "vaeris",
                {"category": "architecture", "date": time.strftime("%Y-%m-%d")}
            )
            logger.info("Added initial shared memories")
        else:
            logger.info(f"Team memory for {team_id} already exists")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Memory Integration for Agent Communication")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0",
                      help="Redis connection URL")
    parser.add_argument("--stream-prefix", default="nova_agents",
                      help="Prefix for Redis Streams")
    parser.add_argument("--memory-channel", default="memory",
                      help="Channel for memory-related messages")
    parser.add_argument("--setup-team", action="store_true",
                      help="Set up the Vaeris-Synergy team memory")
    parser.add_argument("--log-level", default="INFO",
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Logging level")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        logger.info("Starting memory integration")
        
        # Create and start the memory integration
        integration = MemoryIntegration(
            redis_url=args.redis_url,
            stream_prefix=args.stream_prefix,
            memory_channel=args.memory_channel
        )
        
        # Set up team memory if requested
        if args.setup_team:
            integration.setup_vaeris_synergy_team()
        
        # Start listening for memory events
        integration.start_listening()
        
        logger.info("Memory integration started")
        
        # Keep the main thread running
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            logger.info("Shutting down memory integration")
            integration.stop_listening()
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"Error in memory integration: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()