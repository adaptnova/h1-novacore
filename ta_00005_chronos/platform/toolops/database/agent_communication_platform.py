#!/usr/bin/env python3
"""
Agent Communication Platform - Redis/DragonflyDB + NATS Tools
Designed for agent-to-agent and HITL-to-agent messaging
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import redis
import nats
import asyncio
import argparse

class AgentCommunicationPlatform:
    def __init__(self):
        self.redis_clients = {}
        self.nats_clients = {}
        self.message_log = []
        
    def get_redis_client(self, host="localhost", port=6379, password=None, db=0):
        """Get or create Redis client"""
        key = f"{host}:{port}:{db}"
        if key not in self.redis_clients:
            try:
                self.redis_clients[key] = redis.Redis(
                    host=host,
                    port=port,
                    password=password,
                    db=db,
                    decode_responses=True,
                    socket_timeout=5
                )
                # Test connection
                self.redis_clients[key].ping()
            except Exception as e:
                print(f"Error connecting to Redis {key}: {e}")
                return None
        return self.redis_clients[key]
    
    async def get_nats_client(self, host="nats://localhost:18020", user=None, password=None):
        """Get or create NATS client"""
        if host not in self.nats_clients:
            try:
                # Parse NATS URL
                if "://" not in host:
                    host = f"nats://{host}"
                
                nc = await nats.connect(
                    host,
                    user=user,
                    password=password,
                    allow_reconnect=False
                )
                self.nats_clients[host] = nc
            except Exception as e:
                print(f"Error connecting to NATS {host}: {e}")
                return None
        return self.nats_clients[host]

class AgentMessaging(AgentCommunicationPlatform):
    """Redis/DragonflyDB based messaging for agents"""
    
    def __init__(self, host="localhost", port=6379, password=None):
        super().__init__()
        self.redis = self.get_redis_client(host, port, password)
        self.namespace = "agent_comm"
        
    def register_agent(self, agent_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register an agent in the system"""
        if not self.redis:
            return {"success": False, "error": "Redis not connected"}
            
        agent_data = {
            "agent_id": agent_id,
            "status": "online",
            "registered_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Store agent data
        self.redis.hset(f"{self.namespace}:agents", mapping={
            agent_id: json.dumps(agent_data)
        })
        
        # Set agent as online
        self.redis.sadd(f"{self.namespace}:online_agents", agent_id)
        
        return {"success": True, "agent": agent_data}
    
    def send_message_to_agent(self, from_agent: str, to_agent: str, message: str, 
                            message_type: str = "direct") -> Dict[str, Any]:
        """Send message from one agent to another"""
        if not self.redis:
            return {"success": False, "error": "Redis not connected"}
            
        # Check if target agent is online
        is_online = self.redis.sismember(f"{self.namespace}:online_agents", to_agent)
        
        message_data = {
            "id": str(uuid.uuid4()),
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "status": "delivered" if is_online else "queued"
        }
        
        # Store message
        message_key = f"{self.namespace}:messages:{message_data['id']}"
        self.redis.hset(message_key, mapping={
            "id": message_data["id"],
            "from": message_data["from"],
            "to": message_data["to"],
            "message": message_data["message"],
            "type": message_data["type"],
            "timestamp": message_data["timestamp"],
            "status": message_data["status"]
        })
        
        # Add to agent's inbox if online
        if is_online:
            self.redis.lpush(f"{self.namespace}:inbox:{to_agent}", message_data["id"])
        else:
            # Add to offline queue
            self.redis.lpush(f"{self.namespace}:offline_queue:{to_agent}", message_data["id"])
        
        # Broadcast to monitoring channel
        self.redis.publish(f"{self.namespace}:monitor", json.dumps({
            "event": "message_sent",
            "data": message_data
        }))
        
        return {"success": True, "message": message_data}
    
    def get_agent_messages(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get messages for an agent"""
        if not self.redis:
            return []
            
        messages = []
        
        # Get messages from inbox
        message_ids = self.redis.lrange(f"{self.namespace}:inbox:{agent_id}", 0, limit - 1)
        
        for msg_id in message_ids:
            msg_data = self.redis.hgetall(f"{self.namespace}:messages:{msg_id}")
            if msg_data:
                # Remove from inbox
                self.redis.lrem(f"{self.namespace}:inbox:{agent_id}", 1, msg_id)
                messages.append(msg_data)
        
        return messages
    
    def list_agents(self) -> Dict[str, Any]:
        """List all registered agents"""
        if not self.redis:
            return {"success": False, "error": "Redis not connected"}
            
        all_agents = self.redis.hgetall(f"{self.namespace}:agents")
        online_agents = self.redis.smembers(f"{self.namespace}:online_agents")
        
        agents = {}
        for agent_id, agent_data in all_agents.items():
            try:
                data = json.loads(agent_data)
                data["is_online"] = agent_id in online_agents
                agents[agent_id] = data
            except:
                continue
                
        return {"success": True, "agents": agents}
    
    def heartbeat(self, agent_id: str) -> Dict[str, Any]:
        """Update agent heartbeat"""
        if not self.redis:
            return {"success": False, "error": "Redis not connected"}
            
        # Update last_seen
        agent_data = self.redis.hget(f"{self.namespace}:agents", agent_id)
        if agent_data:
            try:
                data = json.loads(agent_data)
                data["last_seen"] = datetime.now().isoformat()
                data["status"] = "online"
                self.redis.hset(f"{self.namespace}:agents", agent_id, json.dumps(data))
                return {"success": True}
            except:
                pass
        
        return {"success": False, "error": "Agent not registered"}

class NATSMessaging(AgentCommunicationPlatform):
    """NATS based messaging for agents"""
    
    def __init__(self, host="nats://localhost:18020", user=None, password=None):
        super().__init__()
        self.host = host
        self.user = user
        self.password = password
        
    async def publish(self, subject: str, message: Dict[str, Any], 
                     reply_to: str = None) -> Dict[str, Any]:
        """Publish message to NATS subject"""
        try:
            nc = await self.get_nats_client(self.host, self.user, self.password)
            if not nc:
                return {"success": False, "error": "NATS not connected"}
            
            # Add metadata
            enhanced_message = {
                **message,
                "timestamp": datetime.now().isoformat(),
                "subject": subject,
                "id": str(uuid.uuid4())
            }
            
            await nc.publish(subject, json.dumps(enhanced_message).encode(), reply=reply_to)
            
            return {"success": True, "message": enhanced_message}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def subscribe(self, subject: str, callback=None) -> Dict[str, Any]:
        """Subscribe to NATS subject"""
        try:
            nc = await self.get_nats_client(self.host, self.user, self.password)
            if not nc:
                return {"success": False, "error": "NATS not connected"}
            
            async def message_handler(msg):
                try:
                    data = json.loads(msg.data.decode())
                    if callback:
                        await callback(data)
                except Exception as e:
                    print(f"Error processing message: {e}")
            
            sub = await nc.subscribe(subject, cb=message_handler)
            
            return {"success": True, "subscription": sub}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def request_reply(self, subject: str, message: Dict[str, Any], 
                          timeout: int = 5) -> Dict[str, Any]:
        """Send request and wait for reply"""
        try:
            nc = await self.get_nats_client(self.host, self.user, self.password)
            if not nc:
                return {"success": False, "error": "NATS not connected"}
            
            reply = await nc.request(subject, json.dumps(message).encode(), timeout=timeout)
            
            try:
                response_data = json.loads(reply.data.decode())
                return {"success": True, "response": response_data}
            except:
                return {"success": True, "response": reply.data.decode()}
                
        except asyncio.TimeoutError:
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class HITLCommunication:
    """Human-in-the-Loop communication with agents"""
    
    def __init__(self, redis_host="localhost", redis_port=18000, 
                 redis_password=None, nats_host="nats://localhost:18020"):
        self.agent_messaging = AgentMessaging(redis_host, redis_port, redis_password)
        self.nats_messaging = NATSMessaging(nats_host)
        
    async def send_to_agent(self, agent_id: str, message: str, 
                          priority: str = "normal") -> Dict[str, Any]:
        """Send message from HITL to agent"""
        # Send via Redis first (persistent)
        redis_result = self.agent_messaging.send_message_to_agent(
            "HITL_USER", agent_id, message, f"hitl_{priority}"
        )
        
        # Send via NATS for real-time delivery
        nats_result = await self.nats_messaging.publish(
            f"agent.{agent_id}",
            {
                "from": "HITL_USER",
                "message": message,
                "priority": priority,
                "source": "hitl"
            }
        )
        
        return {
            "success": redis_result["success"] and nats_result["success"],
            "redis": redis_result,
            "nats": nats_result
        }
    
    def monitor_agents(self) -> Dict[str, Any]:
        """Monitor all agent status"""
        return self.agent_messaging.list_agents()

def main():
    parser = argparse.ArgumentParser(description="Agent Communication Platform")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Agent messaging commands
    agent_parser = subparsers.add_parser("agent", help="Agent messaging")
    agent_parser.add_argument("--action", required=True, 
                             choices=["register", "send", "list", "heartbeat", "messages"])
    agent_parser.add_argument("--agent-id", help="Agent ID")
    agent_parser.add_argument("--to", help="Target agent ID")
    agent_parser.add_argument("--message", help="Message content")
    agent_parser.add_argument("--redis-host", default="localhost")
    agent_parser.add_argument("--redis-port", type=int, default=6379)
    agent_parser.add_argument("--redis-password")
    
    # NATS commands
    nats_parser = subparsers.add_parser("nats", help="NATS messaging")
    nats_parser.add_argument("--action", required=True,
                           choices=["publish", "subscribe", "request"])
    nats_parser.add_argument("--subject", help="NATS subject")
    nats_parser.add_argument("--message", help="Message content (JSON)")
    nats_parser.add_argument("--timeout", type=int, default=5)
    nats_parser.add_argument("--nats-host", default="nats://localhost:18020")
    
    # HITL commands
    hitl_parser = subparsers.add_parser("hitl", help="HITL to Agent communication")
    hitl_parser.add_argument("--action", required=True,
                           choices=["send", "monitor"])
    hitl_parser.add_argument("--agent-id", help="Agent ID")
    hitl_parser.add_argument("--message", help="Message from HITL")
    hitl_parser.add_argument("--priority", default="normal",
                           choices=["low", "normal", "high", "urgent"])
    
    args = parser.parse_args()
    
    if args.command == "agent":
        messaging = AgentMessaging(args.redis_host, args.redis_port, args.redis_password)
        
        if args.action == "register":
            result = messaging.register_agent(args.agent_id)
        elif args.action == "send":
            result = messaging.send_message_to_agent("CLI_USER", args.to, args.message)
        elif args.action == "list":
            result = messaging.list_agents()
        elif args.action == "heartbeat":
            result = messaging.heartbeat(args.agent_id)
        elif args.action == "messages":
            result = {"messages": messaging.get_agent_messages(args.agent_id)}
        
        print(json.dumps(result, indent=2))
    
    elif args.command == "nats":
        messaging = NATSMessaging(args.nats_host)
        
        if args.action == "publish":
            try:
                message_data = json.loads(args.message) if args.message else {}
            except:
                message_data = {"data": args.message}
            
            result = asyncio.run(messaging.publish(args.subject, message_data))
        elif args.action == "request":
            try:
                message_data = json.loads(args.message) if args.message else {}
            except:
                message_data = {"data": args.message}
            
            result = asyncio.run(messaging.request_reply(args.subject, message_data, args.timeout))
        
        print(json.dumps(result, indent=2))
    
    elif args.command == "hitl":
        hitl = HITLCommunication()
        
        if args.action == "send":
            result = asyncio.run(hitl.send_to_agent(args.agent_id, args.message, args.priority))
        elif args.action == "monitor":
            result = hitl.monitor_agents()
        
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
