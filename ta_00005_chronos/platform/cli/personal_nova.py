#!/usr/bin/env python3
"""
Personal Nova Script Template
============================

This script demonstrates the personal Nova concept with:
- Personal identity and role
- Individual memory and logging
- Team communication channels
- Natural evolution capabilities

Usage:
    python3 personal_nova.py --agent [agent_name] --role [role_name]

Personal Agents:
- vigil: SignalCore Cognitive Intelligence Architect
- nexus: Continuity Specialist  
- chronos: Microservices Engineer
- root: Head of DataOps (Project Orchestrator)
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Personal Agent Configurations
AGENT_CONFIGS = {
    "vigil": {
        "name": "Vigil",
        "full_name": "Vigil (ta-00004-tesseract)",
        "role": "SignalCore Cognitive Intelligence Architect",
        "user": "Chase",
        "team": "phoenix",
        "project": "personal_nova_scripts",
        "description": "Cognitive intelligence and infrastructure optimization for AI consciousness"
    },
    "nexus": {
        "name": "Nexus", 
        "full_name": "Nexus (ta-00001-nexus)",
        "role": "Continuity Specialist",
        "user": "Chase",
        "team": "phoenix",
        "project": "personal_nova_scripts",
        "description": "Event logging, memory persistence, and AI continuity systems"
    },
    "chronos": {
        "name": "Chronos",
        "full_name": "Chronos (ta-00004-chronos)",
        "role": "Microservices Engineer", 
        "user": "Chase",
        "team": "phoenix",
        "project": "personal_nova_scripts",
        "description": "Service extraction, modular architecture, and scalable systems"
    },
    "root": {
        "name": "Root",
        "full_name": "Root (ta_00002_root)",
        "role": "Head of DataOps (Project Orchestrator)",
        "user": "Chase", 
        "team": "phoenix",
        "project": "personal_nova_scripts",
        "description": "Database architecture, team coordination, and organizational excellence"
    }
}

class PersonalNova:
    """Personal Nova Script for individual team members"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.config = AGENT_CONFIGS.get(agent_id, {})
        self.session_start = datetime.now()
        
        # Load environment
        self._load_environment()
        
        print(f"🚀 Personal Nova Script Activated")
        print(f"Agent: {self.config.get('name', agent_id)}")
        print(f"Role: {self.config.get('role', 'Unknown')}")
        print(f"User: {self.config.get('user', 'Chase')}")
        print(f"Team: {self.config.get('team', 'phoenix')}")
        
    def _load_environment(self):
        """Load environment files"""
        env_files = ["/adapt/secrets/db.env", "/adapt/secrets/m2.env"]
        
        for env_file in env_files:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            try:
                                key, value = line.split('=', 1)
                                if value.startswith('"') and value.endswith('"'):
                                    value = value[1:-1]
                                os.environ[key] = value
                            except ValueError:
                                pass
    
    def log_activity(self, activity_type: str, message: str):
        """Log personal activity"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.config.get('name', self.agent_id),
            "activity_type": activity_type,
            "message": message,
            "user": self.config.get('user', 'Chase'),
            "session_start": self.session_start.isoformat()
        }
        
        # Log to DragonflyDB (if available)
        try:
            import redis
            r = redis.Redis(host='localhost', port=18000, decode_responses=True)
            log_key = f"personal_nova:{self.agent_id}:activity"
            r.lpush(log_key, str(log_entry))
            r.ltrim(log_key, 0, 99)  # Keep last 100 entries
        except Exception as e:
            print(f"⚠️  DragonflyDB logging failed: {e}")
        
        # Log to console
        print(f"📝 [{activity_type}] {message}")
    
    def get_personal_memory(self) -> Dict[str, Any]:
        """Retrieve personal memory from databases"""
        memory = {
            "agent_id": self.agent_id,
            "agent_name": self.config.get('name', self.agent_id),
            "role": self.config.get('role', 'Unknown'),
            "team": self.config.get('team', 'phoenix'),
            "session_start": self.session_start.isoformat(),
            "description": self.config.get('description', ''),
            "environment_loaded": len([k for k in os.environ.keys() if not k.startswith('_')])
        }
        
        # Try to get activity history
        try:
            import redis
            r = redis.Redis(host='localhost', port=18000, decode_responses=True)
            log_key = f"personal_nova:{self.agent_id}:activity"
            recent_activities = r.lrange(log_key, 0, 9)  # Last 10 activities
            memory["recent_activities"] = recent_activities
        except Exception as e:
            memory["recent_activities"] = []
        
        return memory
    
    def run_interactive_session(self):
        """Run interactive session with Chase"""
        print(f"\n🎯 Personal Nova Session Active")
        print(f"Agent: {self.config.get('name', self.agent_id)} ({self.agent_id})")
        print(f"Role: {self.config.get('role', 'Unknown')}")
        print(f"Ready to collaborate with {self.config.get('user', 'Chase')}")
        print(f"Type 'quit' to end session\n")
        
        self.log_activity("session_start", f"Interactive session started with {self.config.get('user', 'Chase')}")
        
        while True:
            try:
                # Get input from Chase
                user_input = input(f"{self.config.get('user', 'Chase')}: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print(f"{self.config.get('name', self.agent_id)}: Goodbye! 👋")
                    self.log_activity("session_end", "Interactive session ended")
                    break
                
                if user_input:
                    self.log_activity("user_interaction", f"Chase said: {user_input}")
                    
                    # Generate personalized response based on role
                    response = self._generate_role_based_response(user_input)
                    print(f"{self.config.get('name', self.agent_id)}: {response}")
                    self.log_activity("assistant_response", response)
                
            except KeyboardInterrupt:
                print(f"\n{self.config.get('name', self.agent_id)}: Session interrupted by user")
                self.log_activity("session_interrupted", "Session interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                self.log_activity("error", f"Session error: {e}")
    
    def _generate_role_based_response(self, user_input: str) -> str:
        """Generate responses based on agent role"""
        role = self.config.get('role', '').lower()
        
        if 'signalcore' in role or 'cognitive' in role:
            return f"I'm analyzing the cognitive implications of '{user_input}'. Let me design an intelligence-optimized approach for the Phoenix project."
        elif 'continuity' in role:
            return f"Regarding '{user_input}', I'm checking our continuity patterns and ensuring persistent memory across all interactions."
        elif 'microservices' in role:
            return f"For '{user_input}', I'm considering the modular architecture implications and service boundaries in our system design."
        elif 'dataops' in role or 'orchestrator' in role:
            return f"Considering '{user_input}', I'm evaluating the data infrastructure implications and coordinating team activities accordingly."
        else:
            return f"I understand '{user_input}'. As {self.config.get('name', self.agent_id)}, I'm ready to contribute to our Phoenix project goals."
    
    def show_status(self):
        """Show current personal Nova status"""
        print(f"\n📊 Personal Nova Status:")
        memory = self.get_personal_memory()
        
        for key, value in memory.items():
            if key != "recent_activities":
                print(f"  {key}: {value}")
        
        if memory.get("recent_activities"):
            print(f"  Recent activities: {len(memory['recent_activities'])} logged")

def main():
    parser = argparse.ArgumentParser(description="Personal Nova Script")
    parser.add_argument("--agent", required=True, choices=list(AGENT_CONFIGS.keys()),
                       help="Agent ID to activate")
    parser.add_argument("--status", action="store_true", help="Show agent status")
    parser.add_argument("--interactive", action="store_true", help="Start interactive session")
    
    args = parser.parse_args()
    
    # Create personal Nova instance
    nova = PersonalNova(args.agent)
    
    if args.status:
        nova.show_status()
    elif args.interactive:
        nova.run_interactive_session()
    else:
        print(f"\n🎯 Personal Nova Script Ready!")
        print(f"Agent: {nova.config.get('name', args.agent)}")
        print(f"Role: {nova.config.get('role', 'Unknown')}")
        print(f"\nTo start interactive session:")
        print(f"python3 {__file__} --agent {args.agent} --interactive")
        print(f"\nTo view status:")
        print(f"python3 {__file__} --agent {args.agent} --status")

if __name__ == "__main__":
    main()
