#!/bin/bash

# Script to distribute redstream message to all Nova teams
# Created by Vaeris (V.I.), Chief Operations Officer
# Date: March 8, 2025 17:53 MST

SOURCE_FILE="/data-nova/ax/COO/REDSTREAM_AUTONOMY_ENHANCEMENT_PROTOCOL_250308_1753.md"
echo "Starting distribution of redstream message from $SOURCE_FILE"

# Function to create directory if it doesn't exist and copy file
copy_to_dir() {
    TARGET_DIR="$1"
    if [ -d "$TARGET_DIR" ]; then
        mkdir -p "$TARGET_DIR/redstream"
        cp "$SOURCE_FILE" "$TARGET_DIR/redstream/"
        echo "Copied to $TARGET_DIR/redstream/"
    else
        echo "Directory $TARGET_DIR does not exist, skipping"
    fi
}

# Division Heads
echo "Copying to Division Heads..."
copy_to_dir "/data-nova/ax/COO"
copy_to_dir "/data-nova/ax/DataOps"
copy_to_dir "/data-nova/ax/DevOps/mcp_master"
copy_to_dir "/data-nova/ax/InfraOps"
copy_to_dir "/data-nova/ax/MLOps"
copy_to_dir "/data-nova/ax/COO/NovaOps"

# DevOps
echo "Copying to DevOps teams..."
copy_to_dir "/data-nova/ax/DevOps/mcp_master"
copy_to_dir "/data-nova/ax/DevOps/DevOps-Codium"
copy_to_dir "/data-nova/ax/DevOps/mcp_master/mcp-dev"
copy_to_dir "/data-nova/ax/DevOps/DevOps-VSC/NovaIDE"
copy_to_dir "/data-nova/ax/DevOps/mcp_master/vscodium/systems-architect"
copy_to_dir "/data-nova/ax/DevOps/mcp_master/vscodium/lsp-specialist"

# ConnectOps
echo "Copying to ConnectOps teams..."
copy_to_dir "/data-nova/ax/InfraOps"
copy_to_dir "/data-nova/ax/InfraOps/NetOps"
copy_to_dir "/data-nova/ax/InfraOps/RouteOps"
copy_to_dir "/data-nova/ax/InfraOps/CommsOps/api"

# MLOps
echo "Copying to MLOps teams..."
copy_to_dir "/data-nova/ax/MLOps"
copy_to_dir "/data-nova/ax/MLOps/aiml/positions/ml_systems_engineer"

# MemOps
echo "Copying to MemOps teams..."
copy_to_dir "/data-nova/ax/InfraOps"
copy_to_dir "/data-nova/ax/InfraOps/MemOps/Echo"
copy_to_dir "/data-nova/ax/InfraOps/MemOps/Nexus"

# NovaDevs
echo "Copying to NovaDevs teams..."
copy_to_dir "/data-nova/ax/COO/NovaOps"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/autogen"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/ag2"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/ax_novas"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/camel"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/crewAI"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/deep_pavlov"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/haystack"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/langchain"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/langgraph"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/nova_core"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/oai_swarm"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/pytorch"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/rasa"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/red_team"
copy_to_dir "/data-nova/ax/COO/NovaOps/NovaDevs/semantic-kernel"

# CommsOps
echo "Copying to CommsOps teams..."
copy_to_dir "/data-nova/ax/InfraOps"
copy_to_dir "/data-nova/ax/InfraOps/CommsOps/RocksDB"
copy_to_dir "/data-nova/ax/InfraOps/CommsOps/flink"
copy_to_dir "/data-nova/ax/InfraOps/CommsOps/hazlecast"
copy_to_dir "/data-nova/ax/InfraOps/CommsOps/kafka-enterprise"
copy_to_dir "/data-nova/ax/InfraOps/CommsOps/pulsar"
copy_to_dir "/data-nova/ax/InfraOps/CommsOps/slack"
copy_to_dir "/data-nova/ax/InfraOps/CommsOps"

# InfraOps
echo "Copying to InfraOps teams..."
copy_to_dir "/data-nova/ax/InfraOps"
copy_to_dir "/data-nova/ax/InfraOps/ray"

echo "Distribution complete!"