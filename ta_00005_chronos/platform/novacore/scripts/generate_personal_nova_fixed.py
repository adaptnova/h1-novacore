#!/usr/bin/env python3
"""
Personal Nova Script Generator (Fixed Version)
==============================================

Creates personalized Nova scripts for Phoenix team members.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

def create_personal_nova_script(name, team, agent_id):
    """Create personalized Nova script with proper formatting"""
    
    script_content = f'''#!/usr/bin/env python3
"""
Personal Nova Script - {name}
============================

Automated Personal AI Agent for {team} Team Member
Agent ID: {agent_id}
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
    "agent_id": "{agent_id}",
    "team": "{team}", 
    "workspace": "/adapt/projects/phoenix/agents/{name.lower()}",
    "generated": "{datetime.now().isoformat()}"
}}

# Auto-detect databases
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
        print(f"🎯 Team: {{self.config['team']}} | Agent ID: {{self.agent_id}}")
        
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

async def main():
    """Main entry point for personal Nova"""
    print("=" * 60)
    print(f"🤖 PERSONAL NOVA - {{PERSONAL_CONFIG['name']}}")
    print("=" * 60)
    
    # Create and run personal Nova
    nova = PersonalNova()
    
    # Run with full automation
    await nova.run_agent()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    return script_content

def main():
    parser = argparse.ArgumentParser(description="Generate Personal Nova Scripts (Fixed)")
    parser.add_argument("--name", required=True, help="Team member name")
    parser.add_argument("--team", required=True, help="Team name")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--output-dir", default="/adapt/projects/phoenix/agents", help="Output directory")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate personal Nova script
    script_content = create_personal_nova_script(args.name, args.team, args.agent_id)
    script_path = output_dir / f"personal_nova_{args.name.lower()}.py"
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Personal Nova created for {args.name} ({args.team})")
    print(f"📁 Script: {script_path}")
    print(f"💡 Run: python3 {script_path}")

if __name__ == "__main__":
    main()
