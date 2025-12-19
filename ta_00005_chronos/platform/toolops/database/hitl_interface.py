#!/usr/bin/env python3
"""
HITL (Human-in-the-Loop) Command Interface
Simple CLI for human operators to communicate with agents
"""

import asyncio
import json
import sys
import argparse
from datetime import datetime
from agent_communication_platform import AgentMessaging, NATSMessaging, HITLCommunication

class HITLInterface:
    def __init__(self):
        self.hitl = HITLCommunication(
            redis_host="localhost", 
            redis_port=18000,
            redis_password="df_cluster_2024_adapt_research"
        )
        self.agent_messaging = AgentMessaging(
            host="localhost", 
            port=18000,
            password="df_cluster_2024_adapt_research"
        )
        
    def list_agents(self):
        """List all agents and their status"""
        result = self.hitl.monitor_agents()
        
        if not result["success"]:
            print(f"❌ Error: {result.get('error')}")
            return
            
        print("\n🤖 REGISTERED AGENTS:")
        print("-" * 60)
        
        agents = result["agents"]
        if not agents:
            print("   No agents registered")
            return
            
        for agent_id, agent_data in agents.items():
            status = "🟢 ONLINE" if agent_data["is_online"] else "🔴 OFFLINE"
            registered = agent_data.get("registered_at", "unknown")
            last_seen = agent_data.get("last_seen", "unknown")
            
            print(f"\n   Agent ID: {agent_id}")
            print(f"   Status: {status}")
            print(f"   Registered: {registered}")
            print(f"   Last Seen: {last_seen}")
            
            metadata = agent_data.get("metadata", {})
            if metadata:
                print(f"   Metadata: {json.dumps(metadata, indent=8)}")
    
    async def send_message(self, agent_id, message, priority="normal"):
        """Send message to specific agent"""
        print(f"\n📤 Sending message to {agent_id}...")
        print(f"   Priority: {priority}")
        print(f"   Message: {message}")
        
        result = await self.hitl.send_to_agent(agent_id, message, priority)
        
        if result["success"]:
            print("✅ Message sent successfully")
            print(f"   Redis delivery: {'✓' if result['redis']['success'] else '✗'}")
            print(f"   NATS delivery: {'✓' if result['nats']['success'] else '✗'}")
            
            # Show message ID
            if result['redis']['success']:
                msg_id = result['redis']['message']['id']
                print(f"   Message ID: {msg_id}")
        else:
            print("❌ Failed to send message")
            print(f"   Error: {result}")
    
    def check_messages(self, agent_id=None):
        """Check messages for an agent"""
        if agent_id:
            print(f"\n📬 Messages for {agent_id}:")
            messages = self.agent_messaging.get_agent_messages(agent_id, limit=20)
            
            if not messages:
                print("   No messages in inbox")
                return
                
            print(f"   Found {len(messages)} messages:")
            for msg in messages:
                timestamp = msg.get('timestamp', 'unknown')
                from_agent = msg.get('from', 'unknown')
                message_text = msg.get('message', '')
                msg_type = msg.get('type', 'unknown')
                msg_id = msg.get('id', 'unknown')
                
                print(f"\n   📨 Message ID: {msg_id}")
                print(f"   From: {from_agent}")
                print(f"   Type: {msg_type}")
                print(f"   Time: {timestamp}")
                print(f"   Content: {message_text}")
        else:
            # List all agents with unread counts
            print("\n📭 MESSAGE SUMMARY:")
            result = self.agent_messaging.list_agents()
            
            if result["success"]:
                for agent_id, agent_data in result["agents"].items():
                    # Count messages in Redis
                    msg_count = 0
                    try:
                        inbox_key = f"agent_comm:inbox:{agent_id}"
                        msg_count = self.agent_messaging.redis.llen(inbox_key)
                    except:
                        msg_count = 0
                    
                    status = "🟢" if agent_data["is_online"] else "🔴"
                    print(f"   {status} {agent_id}: {msg_count} messages")
    
    async def broadcast_message(self, message, priority="normal"):
        """Broadcast message to all online agents"""
        result = self.agent_messaging.list_agents()
        
        if not result["success"]:
            print(f"❌ Error: {result.get('error')}")
            return
            
        online_agents = [
            agent_id for agent_id, data in result["agents"].items() 
            if data["is_online"]
        ]
        
        if not online_agents:
            print("❌ No online agents to broadcast to")
            return
        
        print(f"\n📢 Broadcasting to {len(online_agents)} agents...")
        print(f"   Message: {message}")
        print(f"   Priority: {priority}")
        
        for agent_id in online_agents:
            await self.send_message(agent_id, message, priority)
            await asyncio.sleep(0.1)  # Small delay between sends
    
    def send_heartbeat(self, agent_id=None):
        """Send heartbeat to update agent status"""
        if agent_id:
            print(f"\n💓 Sending heartbeat for {agent_id}...")
            result = self.agent_messaging.heartbeat(agent_id)
            
            if result["success"]:
                print(f"✅ Heartbeat sent for {agent_id}")
            else:
                print(f"❌ Failed to send heartbeat: {result.get('error')}")
        else:
            print("\n💓 Updating all agent heartbeats...")
            result = self.agent_messaging.list_agents()
            
            if result["success"]:
                for agent_id in result["agents"].keys():
                    self.agent_messaging.heartbeat(agent_id)
                    print(f"   ✓ {agent_id}")
    
    async def run_interactive(self):
        """Run interactive HITL session"""
        print("\n" + "="*60)
        print("👤 HITL (Human-in-the-Loop) INTERFACE")
        print("="*60)
        print("Commands:")
        print("  list          - List all agents")
        print("  send <id>     - Send message to agent")
        print("  messages [id] - Check messages (all or specific agent)")
        print("  broadcast     - Broadcast to all agents")
        print("  heartbeat     - Update agent heartbeats")
        print("  quit          - Exit")
        print("="*60)
        
        while True:
            try:
                cmd = input("\n🤖 HITL> ").strip().split()
                
                if not cmd:
                    continue
                    
                command = cmd[0].lower()
                
                if command == "quit":
                    print("👋 Goodbye!")
                    break
                elif command == "list":
                    self.list_agents()
                elif command == "send":
                    if len(cmd) < 2:
                        print("❌ Usage: send <agent_id> [message]")
                        continue
                    agent_id = cmd[1]
                    message = " ".join(cmd[2:]) if len(cmd) > 2 else ""
                    if not message:
                        message = input(f"   Message to {agent_id}: ")
                    await self.send_message(agent_id, message)
                elif command == "messages":
                    agent_id = cmd[1] if len(cmd) > 1 else None
                    self.check_messages(agent_id)
                elif command == "broadcast":
                    message = " ".join(cmd[1:]) if len(cmd) > 1 else ""
                    if not message:
                        message = input("   Broadcast message: ")
                    await self.broadcast_message(message)
                elif command == "heartbeat":
                    agent_id = cmd[1] if len(cmd) > 1 else None
                    self.send_heartbeat(agent_id)
                else:
                    print(f"❌ Unknown command: {command}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="HITL Command Interface")
    parser.add_argument("--action", choices=[
        "list", "send", "messages", "broadcast", "heartbeat", "interactive"
    ], help="Action to perform")
    parser.add_argument("--agent-id", help="Agent ID")
    parser.add_argument("--message", help="Message content")
    parser.add_argument("--priority", default="normal",
                       choices=["low", "normal", "high", "urgent"],
                       help="Message priority")
    
    args = parser.parse_args()
    
    hitl = HITLInterface()
    
    if args.action == "list":
        hitl.list_agents()
    elif args.action == "send":
        if not args.agent_id or not args.message:
            print("❌ --agent-id and --message required for send action")
            sys.exit(1)
        asyncio.run(hitl.send_message(args.agent_id, args.message, args.priority))
    elif args.action == "messages":
        hitl.check_messages(args.agent_id)
    elif args.action == "broadcast":
        if not args.message:
            print("❌ --message required for broadcast action")
            sys.exit(1)
        asyncio.run(hitl.broadcast_message(args.message, args.priority))
    elif args.action == "heartbeat":
        hitl.send_heartbeat(args.agent_id)
    elif args.action == "interactive":
        asyncio.run(hitl.run_interactive())
    else:
        print("🤖 HITL Interface for Agent Communication")
        print("\nUsage Examples:")
        print("  python3 hitl_interface.py --action list")
        print("  python3 hitl_interface.py --action send --agent-id agent_alpha --message 'Start analysis'")
        print("  python3 hitl_interface.py --action messages --agent-id agent_alpha")
        print("  python3 hitl_interface.py --action broadcast --message 'System update needed'")
        print("  python3 hitl_interface.py --action interactive")
        print("\nFor interactive mode:")
        print("  python3 hitl_interface.py --action interactive")

if __name__ == "__main__":
    main()
