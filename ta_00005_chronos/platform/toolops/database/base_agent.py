#!/usr/bin/env python3
"""
Base Agent Class for Communication Platform
Agents inherit from this to participate in agent-to-agent communication
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from agent_communication_platform import AgentMessaging, NATSMessaging

class BaseAgent:
    """Base class for all agents in the communication platform"""
    
    def __init__(self, agent_id: str, 
                 redis_host: str = "localhost", 
                 redis_port: int = 18010,
                 nats_host: str = "nats://localhost:18020"):
        
        self.agent_id = agent_id
        self.agent_messaging = AgentMessaging(redis_host, redis_port)
        self.nats_messaging = NATSMessaging(nats_host)
        self.is_running = False
        self.subscriptions = []
        self.message_handlers = {}
        
        # Agent metadata
        self.metadata = {
            "type": self.__class__.__name__,
            "version": "1.0",
            "capabilities": [],
            "status": "offline"
        }
    
    async def register(self) -> bool:
        """Register agent in the communication platform"""
        print(f"🤖 {self.agent_id} registering...")
        
        result = self.agent_messaging.register_agent(self.agent_id, self.metadata)
        
        if result["success"]:
            print(f"✅ {self.agent_id} registered successfully")
            return True
        else:
            print(f"❌ {self.agent_id} registration failed: {result.get('error')}")
            return False
    
    async def start(self):
        """Start the agent (register, setup subscriptions, etc.)"""
        if not await self.register():
            return False
        
        self.is_running = True
        self.metadata["status"] = "online"
        
        # Setup subscriptions
        await self.setup_subscriptions()
        
        # Start heartbeat loop
        asyncio.create_task(self.heartbeat_loop())
        
        print(f"🚀 {self.agent_id} started successfully")
        return True
    
    async def stop(self):
        """Stop the agent"""
        self.is_running = False
        self.metadata["status"] = "offline"
        
        # Cleanup subscriptions
        for sub in self.subscriptions:
            try:
                await sub.drain()
            except:
                pass
        
        # Update status
        self.agent_messaging.send_message_to_agent(
            self.agent_id, self.agent_id, "Agent shutting down", "shutdown"
        )
        
        print(f"🛑 {self.agent_id} stopped")
    
    async def setup_subscriptions(self):
        """Setup NATS subscriptions for incoming messages"""
        subjects = [
            f"agent.{self.agent_id}",
            "agent.broadcast",
            f"agent.commands.{self.agent_id}"
        ]
        
        for subject in subjects:
            result = await self.nats_messaging.subscribe(subject, self.handle_message)
            if result["success"]:
                self.subscriptions.append(result["subscription"])
                print(f"   ✓ Subscribed to {subject}")
    
    async def handle_message(self, message_data: Dict[str, Any]):
        """Handle incoming messages (override in subclass)"""
        print(f"📨 {self.agent_id} received: {message_data}")
        
        # Default message handler - override in subclass
        pass
    
    async def send_message(self, to_agent: str, message: str, msg_type: str = "direct") -> bool:
        """Send message to another agent"""
        if not self.is_running:
            return False
        
        result = self.agent_messaging.send_message_to_agent(
            self.agent_id, to_agent, message, msg_type
        )
        
        return result["success"]
    
    async def broadcast(self, message: str, msg_type: str = "broadcast") -> bool:
        """Broadcast message to all agents"""
        if not self.is_running:
            return False
        
        result = await self.nats_messaging.publish("agent.broadcast", {
            "from": self.agent_id,
            "message": message,
            "type": msg_type
        })
        
        return result["success"]
    
    async def request(self, to_agent: str, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send request and wait for reply"""
        if not self.is_running:
            return None
        
        result = await self.nats_messaging.request_reply(
            f"agent.{to_agent}",
            {
                "from": self.agent_id,
                "type": "request",
                "data": request_data
            }
        )
        
        return result if result["success"] else None
    
    async def heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.is_running:
            try:
                self.agent_messaging.heartbeat(self.agent_id)
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
            except Exception as e:
                print(f"❌ Heartbeat error for {self.agent_id}: {e}")
                await asyncio.sleep(30)

class ExampleAgent(BaseAgent):
    """Example agent implementation"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        
        self.metadata.update({
            "type": "ExampleAgent",
            "capabilities": ["processing", "analysis"],
            "description": "Example agent for demonstration"
        })
        
        # Register message handlers
        self.message_handlers = {
            "task": self.handle_task,
            "query": self.handle_query,
            "status": self.handle_status
        }
    
    async def handle_message(self, message_data: Dict[str, Any]):
        """Handle incoming messages"""
        msg_type = message_data.get("type", "unknown")
        from_agent = message_data.get("from", "unknown")
        
        print(f"📨 {self.agent_id} handling {msg_type} from {from_agent}")
        
        if msg_type in self.message_handlers:
            await self.message_handlers[msg_type](message_data)
        else:
            print(f"   Unknown message type: {msg_type}")
    
    async def handle_task(self, message_data: Dict[str, Any]):
        """Handle task messages"""
        task = message_data.get("message", "")
        from_agent = message_data.get("from", "unknown")
        
        print(f"   📋 Processing task: {task}")
        
        # Simulate task processing
        await asyncio.sleep(2)
        
        # Send completion message
        await self.send_message(from_agent, f"Task completed: {task}", "task_complete")
    
    async def handle_query(self, message_data: Dict[str, Any]):
        """Handle query messages"""
        query = message_data.get("message", "")
        from_agent = message_data.get("from", "unknown")
        
        print(f"   🔍 Processing query: {query}")
        
        # Simulate query processing
        await asyncio.sleep(1)
        
        # Send response
        response = f"Query result for '{query}': Processing complete"
        await self.send_message(from_agent, response, "query_response")
    
    async def handle_status(self, message_data: Dict[str, Any]):
        """Handle status request messages"""
        from_agent = message_data.get("from", "unknown")
        
        status_info = {
            "agent_id": self.agent_id,
            "status": "active",
            "uptime": time.time(),
            "capabilities": self.metadata["capabilities"]
        }
        
        await self.send_message(from_agent, json.dumps(status_info), "status_response")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Base Agent for Communication Platform")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--redis-port", type=int, default=18010, help="Redis port")
    parser.add_argument("--nats-host", default="nats://localhost:18020", help="NATS host")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    # Create agent
    agent = ExampleAgent(args.agent_id)
    agent.redis_port = args.redis_port
    agent.nats_host = args.nats_host
    
    try:
        # Start agent
        if await agent.start():
            if args.daemon:
                # Run as daemon
                while agent.is_running:
                    await asyncio.sleep(1)
            else:
                # Interactive mode
                print(f"\n🤖 {args.agent_id} is running...")
                print("Commands:")
                print("  send <agent> <message> - Send message to agent")
                print("  broadcast <message>     - Broadcast message")
                print("  status                  - Show agent status")
                print("  quit                    - Exit")
                
                while agent.is_running:
                    try:
                        cmd = input(f"\n{args.agent_id}> ").strip().split()
                        
                        if not cmd:
                            continue
                            
                        command = cmd[0].lower()
                        
                        if command == "quit":
                            break
                        elif command == "send" and len(cmd) >= 3:
                            target = cmd[1]
                            message = " ".join(cmd[2:])
                            success = await agent.send_message(target, message)
                            print(f"   {'✓' if success else '✗'} Message sent")
                        elif command == "broadcast" and len(cmd) >= 2:
                            message = " ".join(cmd[1:])
                            success = await agent.broadcast(message)
                            print(f"   {'✓' if success else '✗'} Broadcast sent")
                        elif command == "status":
                            result = agent.agent_messaging.list_agents()
                            if result["success"]:
                                agent_data = result["agents"].get(args.agent_id, {})
                                print(f"   Status: {agent_data.get('status', 'unknown')}")
                                print(f"   Online: {agent_data.get('is_online', False)}")
                        else:
                            print("❌ Invalid command")
                            
                    except KeyboardInterrupt:
                        break
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
