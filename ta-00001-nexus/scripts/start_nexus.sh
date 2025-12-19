#!/bin/bash
# Nexus-TeamADAPT Nova Launcher
# Simple script to start the CLI with proper arguments

cd /adapt/novas/ta-00001-nexus

# Default values
AGENT_ID="nexus"
PROJECT="NOVA_SPIN"
THREAD="NS_0001"
WORKSPACE="/adapt/novas/ta-00001-nexus"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent-id)
            AGENT_ID="$2"
            shift 2
            ;;
        --project)
            PROJECT="$2"
            shift 2
            ;;
        --thread)
            THREAD="$2"
            shift 2
            ;;
        --workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

echo "🚀 Starting Nexus-TeamADAPT Nova CLI..."
echo "   Agent ID: $AGENT_ID"
echo "   Project: $PROJECT"
echo "   Thread: $THREAD"
echo "   Workspace: $WORKSPACE"
echo ""

# Run the CLI
python3 nexus_cli.py \
    --agent-id "$AGENT_ID" \
    --project "$PROJECT" \
    --thread "$THREAD" \
    --workspace "$WORKSPACE"
