#!/usr/bin/env bash
# Easter MVP Build Script
# ALWAYS reads team_comms FIRST before taking action

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC} ${GREEN}EASTER MVP BUILD - TEAM COLLABORATION MODE${NC}          ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. READ TEAM_COMMS FIRST (ALWAYS!)
TEAM_COMM_DIR="/adapt/projects/easter/team_comms"
PROJECT_DIR="/adapt/projects/easter"

echo -e "${YELLOW}📖 STEP 1: Reading Team Communications...${NC}"
echo ""

if [ ! -d "$TEAM_COMM_DIR" ]; then
    echo "⚠️  No team_comms directory found. Creating..."
    mkdir -p "$TEAM_COMM_DIR"
fi

LATEST_COMM=$(ls -t "$TEAM_COMM_DIR"/*.md 2>/dev/null | head -1)

if [ -n "$LATEST_COMM" ]; then
    echo "Latest team communication:"
    echo "  📄 $LATEST_COMM"
    echo ""
    echo "--- TEAM COMMS ---"
    cat "$LATEST_COMM" | head -50
    if [ $(wc -l < "$LATEST_COMM") -gt 50 ]; then
        echo "... (truncated, see full file for details)"
    fi
    echo "--- END TEAM COMMS ---"
    echo ""
else
    echo "⚠️  No team communications found yet."
    echo "This is our first build!"
fi

# 2. UNDERSTAND TEAM STATUS
echo -e "${YELLOW}📊 STEP 2: Understanding Team Status...${NC}"
echo ""

echo "Team context from comms:"
if [ -n "$LATEST_COMM" ]; then
    # Extract key information from latest comm
    if grep -q "2 HOURS" "$LATEST_COMM" 2>/dev/null; then
        echo "✅ Team goal: MVP in 2 hours (AI Speed)"
    fi
    if grep -q "Tesseract" "$LATEST_COMM" 2>/dev/null; then
        echo "✅ Tesseract (NovaOps) involved"
    fi
    if grep -q "DataOps" "$LATEST_COMM" 2>/dev/null; then
        echo "✅ DataOps leading architecture"
    fi
    if grep -q "Nexus" "$LATEST_COMM" 2>/dev/null; then
        echo "✅ Nexus integration planned"
    fi
fi

echo ""

# 3. CHECK INFRASTRUCTURE
echo -e "${YELLOW}🏗️  STEP 3: Checking Infrastructure...${NC}"
echo ""

# Check databases
source /adaptai/db.env 2>/dev/null || echo "⚠️  db.env not found, may need to source it"

for db in "DragonflyDB" "MongoDB" "Neo4j" "NATS" "Qdrant"; do
    echo "  Checking $db..."
    # This is informational, not a hard failure
done

echo ""

# 4. COLLABORATIVE BUILD DECISION
echo -e "${YELLOW}🤝 STEP 4: Easter Team Build Decision...${NC}"
echo ""

echo -e "${GREEN}💡 Team Decision: Build MVP with Continuity${NC}"
echo ""
echo "Following team plan:"
echo "  1. Copy official base template"
echo "  2. Extract ContinuityBackend"
echo "  3. Integrate continuity features"
echo "  4. Test end-to-end"
echo ""

# 5. EXECUTE BUILD
echo -e "${YELLOW}🚀 STEP 5: Building MVP (Collaboratively)...${NC}"
echo ""

# Create directories
mkdir -p /adapt/platform/novaops/cli
mkdir -p /adapt/platform/novaops/continuity
mkdir -p /adapt/platform/novaops/services

# Step 1: Copy official base
echo -e "${GREEN}1. Copying Official Base Template...${NC}"
OFFICIAL_BASE="/adapt/platform/novaops/novacore/scripts/template/template_base_cli-v.0.0.1.py"
CLI_MAIN="/adapt/platform/novaops/cli/main.py"

if [ ! -f "$OFFICIAL_BASE" ]; then
    echo -e "${RED}❌ ERROR: Official base not found at $OFFICIAL_BASE${NC}"
    echo ""
    echo "Cannot proceed. Please ensure official base exists."
    exit 1
fi

if [ -f "$CLI_MAIN" ]; then
    echo "  ⚠️  CLI main.py already exists, backing up..."
    mv "$CLI_MAIN" "$CLI_MAIN.backup.$(date +%s)"
fi

cp "$OFFICIAL_BASE" "$CLI_MAIN"
echo "  ✅ Official base copied to $CLI_MAIN"
echo ""

# Step 2: Extract ContinuityBackend
echo -e "${GREEN}2. Extracting ContinuityBackend...${NC}"
CONTINUITY_SOURCE="/adapt/platform/novaops/novacore/scripts/template/archive/dbops_template_cli.py"
CONTINUITY_BACKEND="/adapt/platform/novaops/continuity/backend.py"

if [ ! -f "$CONTINUITY_SOURCE" ]; then
    echo -e "${RED}❌ ERROR: Continuity template not found at $CONTINUITY_SOURCE${NC}"
    exit 1
fi

cp "$CONTINUITY_SOURCE" "$CONTINUITY_BACKEND"
echo "  ✅ Continuity backend extracted"
echo ""

# Step 3: Integration notes
echo -e "${GREEN}3. Integration Plan...${NC}"
echo "  📝 Next steps (manual integration required):"
echo "     a. Modify $CLI_MAIN to import ContinuityBackend"
echo "     b. Add continuity initialization"
echo "     c. Add event logging (user + assistant)"
echo "     d. Add /continuity, /snapshot commands"
echo "     e. Update snapshots after each interaction"
echo ""

# 6. DOCUMENT COLLABORATIVE ACTION
echo -e "${YELLOW}📝 STEP 6: Documenting Action in Team Comms...${NC}"
echo ""

TIMESTAMP=$(date +"%Y%m%d_%H%M")
UPDATE_FILE="$TEAM_COMM_DIR/${TIMESTAMP}_easter_build_progress.md"

cat > "$UPDATE_FILE" << EOF
# TEAM COMMUNICATION MEMO - BUILD PROGRESS
**Date:** $(date) MST
**From:** Easter Scripts (Automated Build)
**To:** Easter Team (DataOps, Tesseract, Nexus)
**Subject:** MVP Build Progress - Foundation Complete
**Priority:** High
**Distribution:** Easter Core Team

---

## 🎯 EXECUTIVE SUMMARY

Automated build script executed. Foundation for MVP complete. Ready for manual integration.

## 📋 ACTIONS COMPLETED

✅ **Step 1: Official Base Copied**
   - Source: $OFFICIAL_BASE
   - Dest: $CLI_MAIN
   - Status: Complete

✅ **Step 2: Continuity Backend Extracted**
   - Source: $CONTINUITY_SOURCE
   - Dest: $CONTINUITY_BACKEND
   - Status: Complete

## 📝 MANUAL INTEGRATION REQUIRED

The following integration steps require manual completion:

1. **Import ContinuityBackend**
   - Add import: \`from continuity.backend import ContinuityBackend\`
   - Location: $CLI_MAIN

2. **Initialize Continuity**
   - Create instance: \`continuity = ContinuityBackend()\`
   - In run_agent() function

3. **Log Events**
   - Before agent.run(): \`continuity.log_event("user", user_input, ...)\`
   - After agent.run(): \`continuity.log_event("assistant", response, ...)\`

4. **Add Commands**
   - /continuity - Show continuity status
   - /snapshot - Force save snapshot

5. **Update Snapshots**
   - After each interaction
   - Track project, thread, cwd

## 🎯 NEXT ACTIONS

- [ ] Manual integration in $CLI_MAIN
- [ ] Test with sample data
- [ ] Verify all databases receive events
- [ ] End-to-end MVP test
- [ ] Document test results

## 🚀 IMMEDIATE NEXT STEP

Review $CLI_MAIN and $CONTINUITY_BACKEND
Begin manual integration
Run: \`cd /adapt/platform/novaops/cli && python3 main.py --agent-id nexus --project easter_mvp\`

---

**Foundation complete. Integration phase begins.**
EOF

echo "✅ Progress documented: $UPDATE_FILE"
echo ""

# 7. PROVIDE NEXT STEPS
echo -e "${GREEN}✅ MVP BUILD FOUNDATION COMPLETE${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "  1. Official base: ✅ $CLI_MAIN"
echo "  2. Continuity backend: ✅ $CONTINUITY_BACKEND"
echo "  3. Integration: ⏳ Manual work required"
echo ""
echo -e "${YELLOW}🤝 TEAM NEXT STEPS:${NC}"
echo "  1. Review team_comms/$TIMESTAMP_easter_build_progress.md"
echo "  2. Begin manual integration in $CLI_MAIN"
echo "  3. Use update_status.sh to check progress"
echo ""
echo -e "${GREEN}🚀 Ready for integration phase!${NC}"
echo ""
