#!/usr/bin/env bash
# Easter Status Update Script
# Reads team_comms FIRST, then provides status update

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC} ${GREEN}EASTER TEAM STATUS CHECK${NC}                               ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. READ TEAM_COMMS FIRST (ALWAYS!)
TEAM_COMM_DIR="/adapt/projects/easter/team_comms"
SCRIPTS_DIR="/adapt/projects/easter/scripts"

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
    echo "--- CONTENT ---"
    cat "$LATEST_COMM"
    echo ""
    echo "--- END CONTENT ---"
    echo ""
else
    echo "⚠️  No team communications found yet."
fi

# 2. CHECK CURRENT STATUS
echo -e "${YELLOW}📊 STEP 2: Checking Current Status...${NC}"
echo ""

# Check if official base exists
OFFICIAL_BASE="/adapt/platform/novaops/novacore/scripts/template/template_base_cli-v.0.0.1.py"
CLI_MAIN="/adapt/platform/novaops/cli/main.py"
CONTINUITY_BACKEND="/adapt/platform/novaops/template/dbops_template_cli.py"

if [ -f "$OFFICIAL_BASE" ]; then
    echo "✅ Official base template found"
else
    echo "❌ Official base template NOT found"
fi

if [ -f "$CLI_MAIN" ]; then
    echo "✅ CLI main.py (working copy) exists"
else
    echo "❌ CLI main.py NOT found - MVP not started"
fi

if [ -f "$CONTINUITY_BACKEND" ]; then
    echo "✅ Continuity backend exists"
else
    echo "❌ Continuity backend NOT found"
fi

# Check directory structure
for dir in cli continuity services; do
    if [ -d "/adapt/platform/novaops/$dir" ]; then
        echo "✅ Directory: /adapt/platform/novaops/$dir"
    else
        echo "⚪ Directory: /adapt/platform/novaops/$dir (not created yet)"
    fi
done

echo ""

# 3. PROVIDE COLLABORATIVE RESPONSE
echo -e "${YELLOW}🤝 STEP 3: Easter Team Response...${NC}"
echo ""

if [ ! -f "$CLI_MAIN" ]; then
    echo -e "${GREEN}💡 NEXT ACTION: Start MVP Build${NC}"
    echo "   Run: ./build_mvp.sh"
    echo ""
    echo "   This will:"
    echo "   1. Copy official base to cli/main.py"
    echo "   2. Extract ContinuityBackend"
    echo "   3. Begin integration"
    echo ""
elif [ ! -d "/adapt/platform/novaops/continuity" ]; then
    echo -e "${GREEN}💡 NEXT ACTION: Complete Integration${NC}"
    echo "   Continue building MVP..."
    echo ""
else
    echo -e "${GREEN}✅ MVP BUILD IN PROGRESS${NC}"
    echo "   Continuing with integration..."
    echo ""
fi

# 4. UPDATE TEAM_COMMS
echo -e "${YELLOW}📝 STEP 4: Update Team Comms...${NC}"
echo ""

TIMESTAMP=$(date +"%Y%m%d_%H%M")
STATUS_FILE="$TEAM_COMM_DIR/${TIMESTAMP}_easter_status_update.md"

cat > "$STATUS_FILE" << EOF
# TEAM COMMUNICATION MEMO - STATUS UPDATE
**Date:** $(date) MST
**From:** Easter Scripts (Automated)
**To:** Easter Team (DataOps, Tesseract, Nexus)
**Subject:** Status Update - MVP Progress
**Priority:** Medium
**Distribution:** Easter Core Team

---

## 🎯 EXECUTIVE SUMMARY

Automated status check completed. Current MVP progress assessed.

## 📊 CURRENT STATUS

### Build Status:
$(if [ -f "$CLI_MAIN" ]; then echo "✅ Working copy created"; else echo "❌ Working copy not found"; fi)
$(if [ -d "/adapt/platform/novaops/continuity" ]; then echo "✅ Continuity directory exists"; else echo "⚪ Continuity not extracted"; fi)

### Infrastructure:
- Official Base: $([ -f "$OFFICIAL_BASE" ] && echo "✅" || echo "❌")
- CLI Main: $([ -f "$CLI_MAIN" ] && echo "✅" || echo "❌")
- Continuity Backend: $([ -f "$CONTINUITY_BACKEND" ] && echo "✅" || echo "❌")

## 📋 NEXT ACTIONS

$(if [ ! -f "$CLI_MAIN" ]; then
    echo "- [ ] Run ./build_mvp.sh to start MVP"
    echo "- [ ] Check back in 1 hour"
else
    echo "- [ ] Continue MVP integration"
    echo "- [ ] Test continuity features"
fi)

## 🚀 RECOMMENDATIONS

- Continue following team_comms for collaborative decisions
- No isolated work - always check team_comms first
- Document progress after each step

---

**Automated status check complete. Check back frequently during MVP build.**
EOF

echo "✅ Status update saved to: $STATUS_FILE"
echo ""

# 5. SUGGEST NEXT STEP
echo -e "${GREEN}🚀 STEP 5: Next Step Recommendation${NC}"
echo ""

if [ ! -f "$CLI_MAIN" ]; then
    echo -e "${BLUE}RECOMMENDATION:${NC} Start MVP build now!"
    echo ""
    echo "Run:"
    echo "  cd $SCRIPTS_DIR"
    echo "  ./build_mvp.sh"
    echo ""
else
    echo -e "${BLUE}RECOMMENDATION:${NC} Continue building!"
    echo ""
    echo "Check progress with:"
    echo "  ./update_status.sh"
    echo ""
fi

echo -e "${GREEN}✅ Status check complete. Check team_comms for details.${NC}"
echo ""
