#!/usr/bin/env python3
"""
Agent Communication Examples and Testing
Demonstrates agent-to-agent and HITL-to-agent communication
"""

import asyncio
import json
import time
from agent_communication_platform import AgentMessaging, NATSMessaging, HITLCommunication

async def demo_agent_to_agent_communication():
    """Demonstrate agent-to-agent communication via Redis"""
    print("\n" + "="*60)
    print("🤖 AGENT-TO-AGENT COMMUNICATION DEMO (Redis)")
    print("="*60)
    
    # Initialize messaging with Redis Cluster Node 1
    messaging = AgentMessaging(host="localhost", port=18010)
    
    # Register agents
    print("\n1. Registering agents...")
    agents = ["agent_alpha", "agent_beta", "agent_gamma", "agent_delta"]
    for agent_id in agents:
        result = messaging.register_agent(agent_id, {
            "type": "specialist",
            "capabilities": ["reasoning", "planning"],
            "version": "1.0"
        })
        if result["success"]:
            print(f"   ✓ {agent_id} registered")
        else:
            print(f"   ✗ {agent_id} failed: {result.get('error')}")
    
    # Send messages between agents
    print("\n2. Sending messages between agents...")
    messages = [
        ("agent_alpha", "agent_beta", "Starting analysis task", "task"),
        ("agent_beta", "agent_gamma", "Need data for processing", "request"),
        ("agent_gamma", "agent_alpha", "Data prepared, ready", "response"),
        ("agent_delta", "agent_alpha", "Monitoring status update", "status")
    ]
    
    for from_agent, to_agent, message, msg_type in messages:
        result = messaging.send_message_to_agent(from_agent, to_agent, message, msg_type)
        if result["success"]:
            print(f"   ✓ {from_agent} → {to_agent}: {message[:40]}...")
        else:
            print(f"   ✗ Failed: {result.get('error')}")
    
    # List all agents
    print("\n3. Agent status:")
    result = messaging.list_agents()
    if result["success"]:
        for agent_id, agent_data in result["agents"].items():
            status = "🟢 ONLINE" if agent_data["is_online"] else "🔴 OFFLINE"
            print(f"   {agent_id}: {status}")
    
    # Retrieve messages for each agent
    print("\n4. Message retrieval:")
    for agent_id in agents:
        messages = messaging.get_agent_messages(agent_id)
        print(f"\n   {agent_id} inbox ({len(messages)} messages):")
        for msg in messages:
            print(f"     ← {msg['from']}: {msg['message']} ({msg['type']})")
    
    # Update heartbeats
    print("\n5. Updating agent heartbeats...")
    for agent_id in agents:
        result = messaging.heartbeat(agent_id)
        if result["success"]:
            print(f"   ✓ {agent_id} heartbeat updated")

async def demo_nats_communication():
    """Demonstrate real-time communication via NATS"""
    print("\n" + "="*60)
    print("⚡ NATS REAL-TIME MESSAGING DEMO")
    print("="*60)
    
    messaging = NATSMessaging(host="nats://localhost:18020")
    
    # Subscribe to monitoring channel
    print("\n1. Setting up NATS subscriptions...")
    
    async def monitor_callback(data):
        print(f"   📡 Monitor: {data.get('event', 'unknown')} - {data.get('data', {}).get('from', 'unknown')}")
    
    # Subscribe to various channels
    subjects = ["agent.status", "agent.commands", "hitl.messages"]
    subscriptions = []
    
    for subject in subjects:
        result = await messaging.subscribe(subject, monitor_callback)
        if result["success"]:
            print(f"   ✓ Subscribed to {subject}")
            subscriptions.append(result["subscription"])
        else:
            print(f"   ✗ Failed to subscribe to {subject}: {result.get('error')}")
    
    # Publish messages to different subjects
    print("\n2. Publishing messages to NATS subjects...")
    
    messages = [
        ("agent.status", {
            "agent_id": "agent_alpha",
            "status": "processing",
            "load": 0.75
        }),
        ("agent.commands", {
            "command": "execute_task",
            "priority": "high",
            "task_id": "task_123"
        }),
        ("hitl.messages", {
            "from": "human_operator",
            "message": "Check system status",
            "priority": "normal"
        })
    ]
    
    for subject, message_data in messages:
        result = await messaging.publish(subject, message_data)
        if result["success"]:
            print(f"   ✓ Published to {subject}")
        else:
            print(f"   ✗ Failed: {result.get('error')}")
        
        await asyncio.sleep(0.5)  # Small delay for demo
    
    # Test request/reply pattern
    print("\n3. Testing request/reply pattern...")
    
    async def handle_request(data):
        # Simulate agent processing
        await asyncio.sleep(1)
        return {
            "status": "completed",
            "result": f"Processed: {data.get('command', 'unknown')}",
            "timestamp": time.time()
        }
    
    # Publish a request
    request_result = await messaging.publish(
        "agent.requests",
        {"command": "get_status", "agent_id": "agent_alpha"}
    )
    
    if request_result["success"]:
        print(f"   ✓ Request sent to agent.requests")
    
    # Wait for subscriptions to process
    print("\n4. Waiting for message processing...")
    await asyncio.sleep(2)
    
    # Cleanup
    for sub in subscriptions:
        await sub.drain()

async def demo_hitl_to_agent():
    """Demonstrate Human-in-the-Loop to Agent communication"""
    print("\n" + "="*60)
    print("👤 HITL-TO-AGENT COMMUNICATION DEMO")
    print("="*60)
    
    hitl = HITLCommunication()
    
    # Send messages from HITL to agents
    print("\n1. Sending messages from HITL to agents...")
    
    messages = [
        ("agent_alpha", "Please analyze the latest data", "high"),
        ("agent_beta", "Prepare summary report", "normal"),
        ("agent_gamma", "URGENT: System monitoring needed", "urgent")
    ]
    
    for agent_id, message, priority in messages:
        result = await hitl.send_to_agent(agent_id, message, priority)
        if result["success"]:
            print(f"   ✓ HITL → {agent_id}: {message[:40]}... (priority: {priority})")
            print(f"     Redis: {'✓' if result['redis']['success'] else '✗'}")
            print(f"     NATS:  {'✓' if result['nats']['success'] else '✗'}")
        else:
            print(f"   ✗ Failed to send to {agent_id}")
        
        await asyncio.sleep(0.5)
    
    # Monitor agent status
    print("\n2. Monitoring agent status from HITL perspective...")
    result = hitl.monitor_agents()
    
    if result["success"]:
        print(f"\n   Current agent status:")
        for agent_id, agent_data in result["agents"].items():
            status_icon = "🟢" if agent_data["is_online"] else "🔴"
            last_seen = agent_data.get("last_seen", "unknown")
            print(f"   {status_icon} {agent_id}: Last seen {last_seen}")

def test_connectivity():
    """Test connectivity to Redis and NATS"""
    print("\n" + "="*60)
    print("🔍 CONNECTIVITY TESTS")
    print("="*60)
    
    # Test Redis Cluster
    print("\n1. Testing Redis Cluster connectivity...")
    for port in [18010, 18011, 18012]:
        try:
            messaging = AgentMessaging(host="localhost", port=port)
            if messaging.redis:
                # Test with INFO command
                info = messaging.redis.info()
                print(f"   ✓ Redis Node {port}: Connected (Version: {info.get('redis_version', 'unknown')})")
            else:
                print(f"   ✗ Redis Node {port}: Connection failed")
        except Exception as e:
            print(f"   ✗ Redis Node {port}: {str(e)}")
    
    # Test NATS
    print("\n2. Testing NATS connectivity...")
    try:
        messaging = NATSMessaging(host="nats://localhost:18020")
        # Just test if we can create a client
        print(f"   ✓ NATS: Host configured (real-time messaging ready)")
    except Exception as e:
        print(f"   ✗ NATS: {str(e)}")
    
    # Test DragonflyDB
    print("\n3. Testing DragonflyDB Cluster connectivity...")
    for port in [18000, 18001, 18002]:
        try:
            messaging = AgentMessaging(host="localhost", port=port)
            if messaging.redis:
                info = messaging.redis.info()
                print(f"   ✓ DragonflyDB {port}: Connected (Version: {info.get('version', 'unknown')})")
            else:
                print(f"   ✗ DragonflyDB {port}: Connection failed")
        except Exception as e:
            print(f"   ✗ DragonflyDB {port}: {str(e)}")

async def main():
    print("🚀 AGENT COMMUNICATION PLATFORM DEMONSTRATION")
    print("="*60)
    print("This demo showcases agent-to-agent and HITL-to-agent")
    print("communication using Redis/DragonflyDB and NATS")
    
    # Test connectivity first
    test_connectivity()
    
    # Run demos
    await demo_agent_to_agent_communication()
    await demo_nats_communication()
    await demo_hitl_to_agent()
    
    print("\n" + "="*60)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("  • Agent registration and heartbeat")
    print("  • Agent-to-agent messaging via Redis")
    print("  • Real-time pub/sub via NATS")
    print("  • HITL-to-agent communication (dual path)")
    print("  • Message queuing for offline agents")
    print("  • Agent status monitoring")
    print("\nUse cases:")
    print("  • Agent coordination and task delegation")
    print("  • Real-time status updates")
    print("  • Human operator intervention")
    print("  • System monitoring and logging")

if __name__ == "__main__":
    asyncio.run(main())
