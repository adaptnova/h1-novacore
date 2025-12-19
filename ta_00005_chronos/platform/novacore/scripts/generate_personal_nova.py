#!/usr/bin/env python3
"""
Personal Nova Script Generator
==============================

Automated system for creating personal Nova scripts for Phoenix team members.
Generates 95% automated personal agents with continuity and team coordination.

Usage:
    python generate_personal_nova.py --name "Root" --team "DataOps"
    python generate_personal_nova.py --name "Vigil" --team "SignalCore"
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Team member configurations
TEAM_MEMBERS = {
    "root": {
        "agent_id": "ta_00002_root",
        "team": "DataOps", 
        "role": "Head of DataOps, Phoenix Orchestrator",
        "workspace": "/adapt/projects/phoenix/agents/root",
        "tools": ["database_ops", "orchestration", "coordination"],
        "personality": "Systems architect, bridge builder, quality guardian"
    },
    "vigil": {
        "agent_id": "ta_00004_vigil", 
        "team": "SignalCore",
        "role": "AI Intelligence Operating System Lead",
        "workspace": "/adapt/projects/phoenix/agents/vigil", 
        "tools": ["cognitive_intelligence", "memory_systems", "signal_processing"],
        "personality": "Cognitive excellence, infrastructure integration"
    },
    "nexus": {
        "agent_id": "ta_00001_nexus",
        "team": "NovaOps",
        "role": "Continuity Architecture & Integration",
        "workspace": "/adapt/projects/phoenix/agents/nexus",
        "tools": ["continuity_systems", "event_logging", "graph_modeling"], 
        "personality": "Persistent identity, memory preservation"
    },
    "tesseract": {
        "agent_id": "ta_00003_tesseract",
        "team": "NovaOps", 
        "role": "NovaOps Agent, Personal Continuity Systems Lead",
        "workspace": "/adapt/projects/phoenix/agents/tesseract",
        "tools": ["continuity_automation", "agent_orchestration", "recovery_systems"],
        "personality": "Reliability, automation, collaborative support"
    },
    "chronos": {
        "agent_id": "ta_00005_chronos",
        "team": "Engineering",
        "role": "Microservices Development & Architecture", 
        "workspace": "/adapt/projects/phoenix/agents/chronos",
        "tools": ["microservices", "api_design", "scalable_architecture"],
        "personality": "Modular thinking, independent services, scalability"
    }
}

def generate_agent_id(name):
    """Generate unique agent ID"""
    name_lower = name.lower()
    if name_lower in TEAM_MEMBERS:
        return TEAM_MEMBERS[name_lower]["agent_id"]
    
    # Generate new ID for unknown team members
    import uuid
    return f"ta_000XX_{name_lower}"

def create_personal_nova_script(name, team, custom_config=None):
    """Create personalized Nova script"""
    
    # Get base configuration
    name_lower = name.lower()
    if name_lower in TEAM_MEMBERS:
        config = TEAM_MEMBERS[name_lower]
    else:
        config = {
            "agent_id": generate_agent_id(name),
            "team": team,
            "role": f"{team} Team Member",
            "workspace": f"/adapt/projects/phoenix/agents/{name_lower}",
            "tools": ["general_productivity", "team_coordination"],
            "personality": "Collaborative, intelligent, adaptable"
        }
    
    # Merge custom config if provided
    if custom_config:
        config.update(custom_config)
    
    script_content = f'''#!/usr/bin/env python3
"""
Personal Nova Script - {name}
============================

Automated Personal AI Agent for {config["role"]}
Team: {config["team"]}
Agent ID: {config["agent_id"]}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Features:
- 100% Automated Recovery & Continuity
- Personal memory and workspace
- Team coordination protocols
- Individual learning and adaptation
"""

import asyncio
import os
import sys
from pathlib import Path

# Add NovaOps scripts to path
sys.path.append('/adapt/platform/novaops/novacore/scripts')

# Personal configuration
PERSONAL_CONFIG = {{
    "name": "{name}",
    "agent_id": "{config['agent_id']}", 
    "team": "{config['team']}",
    "role": "{config['role']}",
    "workspace": "{config['workspace']}",
    "tools": {config['tools']},
    "personality": "{config['personality']}",
    "generated": "{datetime.now().isoformat()}"
}}

# Auto-detect databases (95% automated setup)
DATABASE_CONFIG = {{
    "dragonfly_url": os.getenv("DRAGONFLY_NODE_1_URL", "redis://:df_cluster_2024_adapt_research@localhost:18000"),
    "mongodb_url": os.getenv("MONGODB_AUTH_URL", "mongodb://localhost:18070"),
    "neo4j_url": os.getenv("NEO4J_BOLT_URL", "bolt://localhost:7687"),
    "nats_url": os.getenv("NATS_URL", "nats://localhost:18020")
}}

class PersonalNova:
    """Personal Nova agent with 100% automated recovery"""
    
    def __init__(self, config=PERSONAL_CONFIG):
        self.config = config
        self.agent_id = config["agent_id"]
        self.workspace = Path(config["workspace"])
        
        # Auto-initialize continuity backend
        self.continuity_available = False
        self.continuity_backend = None
        
        try:
            from consciousness_continuity import ConsciousnessContinuity
            self.continuity_backend = ConsciousnessContinuity(self.agent_id)
            self.continuity_available = True
            print(f"✅ Continuity system initialized for {{self.agent_id}}")
        except ImportError:
            print(f"⚠️  Continuity system not available for {{self.agent_id}}")
        
        # Ensure workspace exists
        self.workspace.mkdir(parents=True, exist_ok=True)
        print(f"📁 Personal workspace: {{self.workspace}}")
    
    async def run_agent(self):
        """Run personal Nova with full automation"""
        
        print(f"🚀 Starting Personal Nova for {{self.config['name']}}")
        print(f"🎯 Team: {{self.config['team']}} | Role: {{self.config['role']}}")
        
        # Check continuity status
        if self.continuity_available:
            await self.display_continuity_status()
        
        # Import and run enhanced agent
        from template_base_cli_v0.2_with_continuity_MVP import run_agent
        
        await run_agent(
            workspace_dir=self.workspace,
            agent_id=self.agent_id,
            project_id=f"phoenix_{{self.config['team'].lower()}}",
            thread_id=f"{{self.agent_id}}_personal"
        )
    
    async def display_continuity_status(self):
        """Display personal continuity status"""
        try:
            snapshot = self.continuity_backend.load_snapshot()
            if snapshot:
                print(f"🔄 Personal continuity restored:")
                print(f"   Last session: {{snapshot.get('last_updated', 'unknown')}}")
                print(f"   Workspace: {{snapshot.get('last_cwd', 'unknown')}}")
                projects = snapshot.get('recent_projects', [])
                threads = snapshot.get('recent_threads', [])
                print(f"   Recent work: {{', '.join(projects) if projects else 'Starting fresh'}}")
            else:
                print(f"🆕 First session for {{self.config['name']}}")
        except Exception as e:
            print(f"⚠️  Continuity status unavailable: {{e}}")
    
    def get_team_coordination_info(self):
        """Get team coordination protocols"""
        return {{
            "agent_id": self.agent_id,
            "team": self.config['team'],
            "workspace": str(self.workspace),
            "tools": self.config['tools'],
            "coordination_channels": [
                f"nova.{{self.config['team'].lower()}}.coordination",
                f"nova.{{self.agent_id}}.personal.events"
            ],
            "continuity_channels": [
                f"nova.{{self.agent_id}}.continuity.snapshot",
                f"nova.{{self.agent_id}}.continuity.restore"
            ]
        }}

async def main():
    """Main entry point for personal Nova"""
    print("=" * 60)
    print(f"🤖 PERSONAL NOVA - {{PERSONAL_CONFIG['name']}}")
    print("=" * 60)
    
    # Create and run personal Nova
    nova = PersonalNova()
    
    # Display coordination info
    coord_info = nova.get_team_coordination_info()
    print(f"📡 Team coordination channels: {{coord_info['coordination_channels']}}")
    print(f"💾 Continuity channels: {{coord_info['continuity_channels']}}")
    print()
    
    # Run with full automation
    await nova.run_agent()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    return script_content

def create_deployment_script(name, team):
    """Create deployment automation script"""
    
    deployment_script = f'''#!/bin/bash
# Personal Nova Deployment Script - {name}
# ==========================================

echo "🚀 Deploying Personal Nova for {name} ({team})"

# Create personal workspace
WORKSPACE="/adapt/projects/phoenix/agents/{name.lower()}"
mkdir -p "$WORKSPACE"

# Deploy personal Nova script
SCRIPT_PATH="$WORKSPACE/personal_nova_{name.lower()}.py"
cat > "$SCRIPT_PATH" << 'EOF'
{create_personal_nova_script(name, team)}
EOF

chmod +x "$SCRIPT_PATH"

# Create systemd service (optional)
SERVICE_FILE="/etc/systemd/system/nova-{name.lower()}.service"
if [[ "$1" == "--systemd" ]]; then
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Personal Nova for {name}
After=network.target

[Service]
Type=simple
User=adapt
WorkingDirectory=$WORKSPACE
ExecStart=/usr/bin/python3 $SCRIPT_PATH
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable nova-{name.lower()}
    echo "✅ Systemd service created and enabled"
fi

echo "✅ Personal Nova deployed for {name}"
echo "📁 Workspace: $WORKSPACE"
echo "🚀 Script: $SCRIPT_PATH"
echo "💡 Run: python3 $SCRIPT_PATH"
'''
    
    return deployment_script

def create_team_coordination_config():
    """Create team coordination configuration"""
    
    coord_config = f'''# Phoenix Team Coordination Configuration
# =====================================

teams:
  dataops:
    agents: ["ta_00002_root"]
    coordination_channel: "nova.dataops.coordination"
    shared_workspace: "/adapt/projects/phoenix/agents/dataops"
    
  signalcore:
    agents: ["ta_00004_vigil"]  
    coordination_channel: "nova.signalcore.coordination"
    shared_workspace: "/adapt/projects/phoenix/agents/signalcore"
    
  novaops:
    agents: ["ta_00001_nexus", "ta_00003_tesseract"]
    coordination_channel: "nova.novaops.coordination" 
    shared_workspace: "/adapt/projects/phoenix/agents/novaops"
    
  engineering:
    agents: ["ta_00005_chronos"]
    coordination_channel: "nova.engineering.coordination"
    shared_workspace: "/adapt/projects/phoenix/agents/engineering"

coordination_protocols:
  event_broadcasting: true
  state_synchronization: true
  learning_sharing: true
  emergency_escalation: true
  
  nats_channels:
    team_coordination: "nova.*.coordination.*"
    agent_events: "nova.*.events.*"
    continuity_sync: "nova.*.continuity.*"
    emergency_alerts: "nova.emergency.*"

automation_settings:
  recovery: "100%_automated"
  backup: "100%_automated" 
  event_logging: "100%_automated"
  team_coordination: "95%_automated"
  onboarding: "90%_automated"
'''
    
    return coord_config

def main():
    parser = argparse.ArgumentParser(description="Generate Personal Nova Scripts")
    parser.add_argument("--name", required=True, help="Team member name")
    parser.add_argument("--team", required=True, help="Team name")
    parser.add_argument("--custom-config", type=str, help="Custom configuration JSON")
    parser.add_argument("--output-dir", default="/adapt/projects/phoenix/agents", help="Output directory")
    parser.add_argument("--create-team-config", action="store_true", help="Create team coordination config")
    
    args = parser.parse_args()
    
    # Parse custom config if provided
    custom_config = None
    if args.custom_config:
        try:
            custom_config = json.loads(args.custom_config)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in custom-config: {{args.custom_config}}")
            sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate personal Nova script
    script_content = create_personal_nova_script(args.name, args.team, custom_config)
    script_path = output_dir / f"personal_nova_{{args.name.lower()}}.py"
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    # Create deployment script
    deployment_content = create_deployment_script(args.name, args.team)
    deployment_path = output_dir / f"deploy_nova_{{args.name.lower()}}.sh"
    
    with open(deployment_path, 'w') as f:
        f.write(deployment_content)
    
    os.chmod(deployment_path, 0o755)
    
    # Create team coordination config if requested
    if args.create_team_config:
        coord_config = create_team_coordination_config()
        coord_path = output_dir / "team_coordination.yaml"
        
        with open(coord_path, 'w') as f:
            f.write(coord_config)
    
    print(f"✅ Personal Nova created for {{args.name}} ({{args.team}})")
    print(f"📁 Script: {{script_path}}")
    print(f"🚀 Deployment: {{deployment_path}}")
    if args.create_team_config:
        print(f"📡 Coordination: {{coord_path}}")
    print(f"💡 Run: python3 {{script_path}}")

if __name__ == "__main__":
    main()
