#!/bin/bash
# Script to create Redis streams for the new organizational structure
# Author: Vaeris (COO)
# Date: April 5, 2025

REDIS_PASSWORD="d5d7817937232ca5"
REDIS_PORT=7000

echo "Creating Redis streams for the new organizational structure..."

# Create streams for Tier 1 Leaders (Group Heads)
echo "Creating Tier 1 Leader streams..."
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD ops.pathfinder.direct '*' type init content "Operations Group direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD novaops.cosmos.direct '*' type init content "NovaOps Group direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD evoops.nexus.direct '*' type init content "EvolutionOps Group direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD rd.synergy.direct '*' type init content "R&D Group direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD growthops.oracle.direct '*' type init content "GrowthOps Group direct communication stream initialized" timestamp "$(date +%s)"

# Create streams for Tier 2 Leaders (Division Heads)
echo "Creating Tier 2 Leader streams..."
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD infraops.helion.direct '*' type init content "InfraOps Division direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD secops.theseus.direct '*' type init content "SecOps Division direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD dataops.vertex.direct '*' type init content "DataOps Division direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD memcommsops.echo.direct '*' type init content "MemCommsOps Division direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD toolchainrd.syntax.direct '*' type init content "Toolchain R&D Division direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD mlops.ethos.direct '*' type init content "MLOps Division direct communication stream initialized" timestamp "$(date +%s)"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD gtmstrategy.keystone.direct '*' type init content "GTM Strategy Division direct communication stream initialized" timestamp "$(date +%s)"

# Create coordination channel for Tier 1 leaders
echo "Creating Tier 1 coordination channel..."
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XADD tier1.coordination '*' type init content "Tier 1 Leadership coordination channel initialized" timestamp "$(date +%s)"

# Create consumer groups for each stream
echo "Creating consumer groups..."
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE ops.pathfinder.direct tier1_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE novaops.cosmos.direct tier1_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE evoops.nexus.direct tier1_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE rd.synergy.direct tier1_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE growthops.oracle.direct tier1_group $ MKSTREAM

redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE infraops.helion.direct tier2_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE secops.theseus.direct tier2_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE dataops.vertex.direct tier2_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE memcommsops.echo.direct tier2_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE toolchainrd.syntax.direct tier2_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE mlops.ethos.direct tier2_group $ MKSTREAM
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE gtmstrategy.keystone.direct tier2_group $ MKSTREAM

redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE tier1.coordination tier1_group $ MKSTREAM

echo "Creating monitoring stream..."
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD XGROUP CREATE stream.monitor admin_group $ MKSTREAM

echo "All streams created successfully!"

# List all streams to verify
echo "Listing all streams:"
redis-cli -c -p $REDIS_PORT -a $REDIS_PASSWORD SCAN 0 TYPE stream
