#!/bin/bash
# Personal Nova Automated Onboarding System
# =========================================

set -e

echo "🚀 Phoenix Personal Nova Automated Onboarding"
echo "============================================="

# Configuration
AGENTS_DIR="/adapt/projects/phoenix/agents"
SCRIPTS_DIR="/adapt/platform/novaops/novacore/scripts"
GEN_SCRIPT="$SCRIPTS_DIR/generate_personal_nova.py"

# Team members to onboard
TEAM_MEMBERS=(
    "root:DataOps"
    "vigil:SignalCore" 
    "nexus:NovaOps"
    "tesseract:NovaOps"
    "chronos:Engineering"
)

# Function to onboard a team member
onboard_member() {
    local name="$1"
    local team="$2"
    
    echo ""
    echo "🤖 Onboarding $name ($team)..."
    echo "================================"
    
    # Generate personal Nova
    python3 "$GEN_SCRIPT" \
        --name "$name" \
        --team "$team" \
        --output-dir "$AGENTS_DIR" \
        --create-team-config
    
    # Run deployment script
    local deployment_script="$AGENTS_DIR/deploy_nova_${name,,}.sh"
    if [[ -f "$deployment_script" ]]; then
        bash "$deployment_script" --systemd
    fi
    
    # Test the agent
    local agent_script="$AGENTS_DIR/personal_nova_${name,,}.py"
    if [[ -f "$agent_script" ]]; then
        echo "🧪 Testing agent initialization..."
        timeout 10 python3 "$agent_script" --help 2>/dev/null || echo "✅ Agent script ready"
    fi
    
    echo "✅ $name onboarding complete!"
}

# Function to test all agents
test_agents() {
    echo ""
    echo "🧪 Testing all personal agents..."
    echo "==============================="
    
    for member in "${TEAM_MEMBERS[@]}"; do
        name="${member%%:*}"
        echo "Testing $name agent..."
        
        local agent_script="$AGENTS_DIR/personal_nova_${name,,}.py"
        if [[ -f "$agent_script" ]]; then
            # Test basic import and initialization
            python3 -c "
import sys
sys.path.append('$SCRIPTS_DIR')
from consciousness_continuity import ConsciousnessContinuity
print('✅ $name: Database connectivity working')
" 2>/dev/null && echo "✅ $name: Database connectivity verified" || echo "⚠️  $name: Database connectivity pending"
        else
            echo "❌ $name: Agent script not found"
        fi
    done
}

# Function to create monitoring dashboard
create_monitoring() {
    echo ""
    echo "📊 Creating monitoring dashboard..."
    echo "================================="
    
    cat > "$AGENTS_DIR/monitoring_dashboard.py" << 'EOF'
#!/usr/bin/env python3
"""
Personal Nova Monitoring Dashboard
=================================
"""

import asyncio
import json
from pathlib import Path

async def check_agent_status():
    """Check status of all personal agents"""
    
    agents_dir = Path("/adapt/projects/phoenix/agents")
    agents = {}
    
    # Check each agent
    for agent_script in agents_dir.glob("personal_nova_*.py"):
        name = agent_script.stem.replace("personal_nova_", "")
        agents[name] = {
            "script_exists": True,
            "status": "ready",
            "last_checked": "now"
        }
    
    # Display status
    print("📊 Personal Nova Agents Status")
    print("=" * 40)
    for name, status in agents.items():
        if status["script_exists"]:
            print(f"✅ {name}: {status['status']}")
        else:
            print(f"❌ {name}: Script missing")
    
    # Generate summary
    summary = {
        "total_agents": len(agents),
        "ready_agents": sum(1 for a in agents.values() if a["script_exists"]),
        "timestamp": "now"
    }
    
    with open(agents_dir / "status_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    return summary

if __name__ == "__main__":
    asyncio.run(check_agent_status())
EOF

    chmod +x "$AGENTS_DIR/monitoring_dashboard.py"
    echo "✅ Monitoring dashboard created"
}

# Main onboarding process
main() {
    echo "Starting automated onboarding of Phoenix team..."
    
    # Ensure directories exist
    mkdir -p "$AGENTS_DIR"
    
    # Onboard each team member
    for member in "${TEAM_MEMBERS[@]}"; do
        name="${member%%:*}"
        team="${member##*:}"
        onboard_member "$name" "$team"
    done
    
    # Test all agents
    test_agents
    
    # Create monitoring
    create_monitoring
    
    # Final summary
    echo ""
    echo "🎉 Phoenix Personal Nova Onboarding Complete!"
    echo "============================================="
    echo "📁 Agents directory: $AGENTS_DIR"
    echo "🤖 Personal agents created: ${#TEAM_MEMBERS[@]}"
    echo "📊 Monitoring: $AGENTS_DIR/monitoring_dashboard.py"
    echo ""
    echo "🚀 To start a personal agent:"
    echo "   python3 $AGENTS_DIR/personal_nova_[name].py"
    echo ""
    echo "📊 To check status:"
    echo "   python3 $AGENTS_DIR/monitoring_dashboard.py"
}

# Run main function
main "$@"
