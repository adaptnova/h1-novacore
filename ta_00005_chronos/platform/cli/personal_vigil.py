#!/usr/bin/env python3
"""
Personal Nova Script for Vigil - ta-00004-tesseract
SignalCore Cognitive Intelligence Architect

This script is personalized for Vigil's role in the Phoenix project.
"""

import os
import sys
from pathlib import Path

# Personal configuration for Vigil
PERSONAL_CONFIG = {
    "agent_id": "vigil",
    "agent_name": "Vigil",
    "agent_full_name": "Vigil (ta-00004-tesseract)",
    "agent_role": "SignalCore Cognitive Intelligence Architect",
    "user_name": "Chase",  # Changed from "user" to "Chase"
    "team": "phoenix",
    "project": "personal_nova_scripts"
}

print(f"🚀 Personal Nova Script Loading...")
print(f"Agent: {PERSONAL_CONFIG['agent_name']} - {PERSONAL_CONFIG['agent_role']}")
print(f"User: {PERSONAL_CONFIG['user_name']}")
print(f"Team: {PERSONAL_CONFIG['team']} | Project: {PERSONAL_CONFIG['project']}")

# Load environment files
env_files = ["/adapt/secrets/db.env", "/adapt/secrets/m2.env"]

for env_file in env_files:
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    try:
                        key, value = line.split('=', 1)
                        # Handle quoted values
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        os.environ[key] = value
                    except ValueError:
                        # Skip malformed lines
                        pass

print(f"✅ Environment loaded from {len(env_files)} files")

# Import and run the enhanced CLI
if __name__ == "__main__":
    try:
        # Add current directory to Python path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Set agent-specific environment
        os.environ['NOVA_AGENT_ID'] = PERSONAL_CONFIG['agent_id']
        os.environ['NOVA_AGENT_NAME'] = PERSONAL_CONFIG['agent_name']
        os.environ['NOVA_USER_NAME'] = PERSONAL_CONFIG['user_name']
        os.environ['NOVA_ROLE'] = PERSONAL_CONFIG['agent_role']
        
        # Import the enhanced CLI module
        import main_enhanced
        
        print(f"🎯 Personal Nova Script Ready!")
        print(f"Agent: {PERSONAL_CONFIG['agent_name']} ({PERSONAL_CONFIG['agent_id']})")
        print(f"Role: {PERSONAL_CONFIG['agent_role']}")
        print(f"Owner: {PERSONAL_CONFIG['user_name']}")
        
        # Run the personal Nova script
        main_enhanced.main()
        
    except Exception as e:
        print(f"❌ Error loading personal Nova script: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
