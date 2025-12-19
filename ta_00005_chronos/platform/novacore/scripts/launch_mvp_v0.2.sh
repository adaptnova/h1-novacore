#!/bin/bash
# MVP Launch Script for Tesseract
# ================================

echo "🚀 Launching Mini Agent with Continuity v0.2 MVP"
echo "================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "template/template_base_cli_v0.2_with_continuity_MVP.py" ]; then
    echo "❌ Error: MVP file not found"
    echo "Please run from: /adapt/platform/novaops/novacore/scripts/"
    exit 1
fi

echo "📍 Working directory: $(pwd)"
echo "🤖 Agent ID: ta_00003_tesseract"
echo "📦 Template: template_base_cli_v0.2_with_continuity_MVP.py"
echo ""

# Set environment variables for continuity (optional)
echo "🔧 Environment variables (optional):"
echo "   export DRAGONFLY_NODE_1_URL='redis://:df_cluster_2024_adapt_research@localhost:18000'"
echo "   export MONGODB_AUTH_URL='your_mongodb_url'"
echo "   export NEO4J_BOLT_URL='your_neo4j_url'"
echo ""

echo "✨ Starting MVP..."
echo "   Use /help to see all commands including continuity features"
echo "   Use /continuity to check continuity status"
echo "   Use /snapshot to force save state"
echo ""
echo "🎯 Press Ctrl+C to exit"
echo "================================================="
echo ""

# Launch the MVP
python3 template/template_base_cli_v0.2_with_continuity_MVP.py \
    --agent-id ta_00003_tesseract \
    --workspace /adapt/novas/ta_00003_tesseract/ \
    "$@"
