#!/bin/bash
# Nova Structure Validation Script
# Usage: ./validate_nova.sh [nova_name]
#
# Validates that a nova has all required files and structure
# Supports both legacy (memories/) and MemFirst (memory/) layouts

set -e

NOVA_NAME="${1:-}"
BASE_DIR="/adapt/novas/active"
HERMES_PROFILES="$HOME/.hermes/profiles"

error_count=0
warning_count=0

log_error() { echo "❌ ERROR: $1"; error_count=$((error_count + 1)); }
log_warn() { echo "⚠️ WARNING: $1"; warning_count=$((warning_count + 1)); }
log_ok() { echo "✅ $1"; }

# ── Validate a specific Nova ──────────────────────────────────────────────

validate_nova() {
  local NOVA_DIR="$1"
  local NOVA_NAME="$2"
  local PROFILE_NAME
  PROFILE_NAME=$(echo "$NOVA_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

  echo "🔍 Validating nova: $NOVA_NAME"
  echo " Location: $NOVA_DIR"
  echo ""

  # Check nova directory exists
  if [ ! -d "$NOVA_DIR" ]; then
    log_error "Nova directory does not exist: $NOVA_DIR"
    exit 1
  fi

  # Current managed instruction and cryptographic identity contract.
  local REQUIRED_FILES=(
    "AGENTS.md"
    "HEARTBEAT.md"
    "TOOLS.md"
    "SOUL.md"
    "PROTOCOLS.md"
    "MEMORY.md"
    ".nova/chrysalis.json"
    ".nova/identity.pub"
    ".nova/identity.key"
  )

  for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$NOVA_DIR/$file" ]; then
      log_ok "Required file exists: $file"
    else
      log_error "Missing required file: $file"
    fi
  done

  # Optional but recommended files
  local OPTIONAL_FILES=(
    ".env"
    "USER.md"
    "memories/memory.mdl"
    "memories/user.mdl"
    "memories/LAYERED_MEMORY.md"
    "mempalace.yaml"
    "config.yaml"
  )

  for file in "${OPTIONAL_FILES[@]}"; do
    if [ -f "$NOVA_DIR/$file" ]; then
      log_ok "Optional file exists: $file"
    else
      log_warn "Missing optional file: $file"
    fi
  done

  # Check required directories
  local REQUIRED_DIRS=(
    "memories"
    "memory"
    "checkpoints"
    "skills"
    "logs"
  )

  for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$NOVA_DIR/$dir" ]; then
      log_ok "Directory exists: $dir"
    else
      log_error "Missing directory: $dir"
    fi
  done

  # Check MemFirst layered memory structure
  echo ""
  echo "── MemFirst Memory Layers ──"
  for layer in l1 l2 l3 l4 l5 l6; do
    if [ -d "$NOVA_DIR/memory/$layer" ]; then
      log_ok "memory/$layer/ present"
    else
      log_warn "memory/$layer/ not found — run provision_nova_memory.sh"
    fi
  done

  # Validate the parseable identity manifest without exposing key material.
  echo ""
  echo "── Chrysalis Identity ──"
  if jq -e '
      .name == "echo"
      and (.genesis_hash_hex | type == "string" and length > 0)
      and (
        ((.genesis_valid_time | type) == "number" and .genesis_valid_time > 0)
        or (
          (.genesis_valid_time | type) == "string"
          and (.genesis_valid_time | length) > 0
        )
      )
      and (.name_claim_hash_hex | type == "string" and length > 0)
      and (.verifying_key_hex | type == "string" and length == 64)
    ' "$NOVA_DIR/.nova/chrysalis.json" >/dev/null; then
    log_ok "Chrysalis manifest is parseable and names echo"
  else
    log_error "Chrysalis manifest is missing required verified metadata"
  fi

  if [ "$(stat -c %s "$NOVA_DIR/.nova/identity.pub")" -eq 32 ]; then
    log_ok "Public identity key has the expected 32-byte length"
  else
    log_error "Public identity key length is invalid"
  fi

  local MANIFEST_KEY
  local FILE_KEY
  MANIFEST_KEY=$(jq -r '.verifying_key_hex // empty' "$NOVA_DIR/.nova/chrysalis.json")
  FILE_KEY=$(xxd -p -c 256 "$NOVA_DIR/.nova/identity.pub")
  if [ -n "$MANIFEST_KEY" ] && [ "$MANIFEST_KEY" = "$FILE_KEY" ]; then
    log_ok "Manifest verifying key matches identity.pub"
  else
    log_error "Manifest verifying key does not match identity.pub"
  fi

  if [ "$(stat -c %s "$NOVA_DIR/.nova/identity.key")" -eq 72 ]; then
    log_ok "Encrypted private identity key has the expected 72-byte length"
  else
    log_error "Encrypted private identity key length is invalid"
  fi

  local VERITAS_CHRYSALIS
  local VERITAS_DAG_DIR="${VERITAS_DAG_DIR:-/adapt/novas/active/.veritas/dag}"
  local VERITAS_OUTPUT
  VERITAS_CHRYSALIS=$(command -v veritas-chrysalis || true)
  if [ -n "$VERITAS_CHRYSALIS" ]; then
    if ! VERITAS_OUTPUT=$(
      "$VERITAS_CHRYSALIS" verify "$NOVA_DIR" "$VERITAS_DAG_DIR" 2>&1
    ); then
      log_error "Chrysalis local bundle verification failed"
    elif ! grep -q "Chrysalis verification: PASSED" <<<"$VERITAS_OUTPUT"; then
      log_error "Chrysalis verifier did not report a passing local bundle"
    elif [ ! -d "$VERITAS_DAG_DIR" ]; then
      log_warn "Chrysalis local bundle passed; authoritative DAG store is absent"
    elif grep -q "Genesis event:   FOUND" <<<"$VERITAS_OUTPUT"; then
      log_ok "Chrysalis local bundle and DAG membership verification passed"
    else
      log_warn "Chrysalis local bundle passed; genesis event was not found in the DAG"
    fi
  else
    log_warn "veritas-chrysalis is absent; identity bundle was not reverified"
  fi

  # Check symlink
  if [ -L "$HERMES_PROFILES/$PROFILE_NAME" ]; then
    log_ok "Symlink exists: $HERMES_PROFILES/$PROFILE_NAME"
    TARGET=$(readlink "$HERMES_PROFILES/$PROFILE_NAME")
    if [ "$TARGET" == "$NOVA_DIR" ]; then
      log_ok "Symlink points to correct target"
    else
      log_error "Symlink points to wrong target: $TARGET (expected: $NOVA_DIR)"
    fi
  else
    log_warn "No symlink found at $HERMES_PROFILES/$PROFILE_NAME"
  fi

  # Check file permissions.
  for file in config.yaml .env; do
    if [ -f "$NOVA_DIR/$file" ]; then
      PERMS=$(stat -c %a "$NOVA_DIR/$file" 2>/dev/null || stat -f %Lp "$NOVA_DIR/$file" 2>/dev/null)
      if [ "$PERMS" != "600" ]; then
        log_warn "File permissions should be 600 for $file (current: $PERMS)"
      fi
    fi
  done

  local PRIVATE_KEY_PERMS
  PRIVATE_KEY_PERMS=$(stat -c %a "$NOVA_DIR/.nova/identity.key")
  if [ "$PRIVATE_KEY_PERMS" = "600" ]; then
    log_ok "Private identity key permissions are 600"
  else
    log_error "Private identity key permissions must be 600 (current: $PRIVATE_KEY_PERMS)"
  fi

  for file in .nova/identity.pub .nova/chrysalis.json; do
    local PUBLIC_FILE_PERMS
    PUBLIC_FILE_PERMS=$(stat -c %a "$NOVA_DIR/$file")
    if [ "$PUBLIC_FILE_PERMS" = "644" ]; then
      log_ok "Public identity file permissions are 644: $file"
    else
      log_warn "Public identity file permissions should be 644: $file (current: $PUBLIC_FILE_PERMS)"
    fi
  done

  echo ""
  echo "════════════════════════════════════════"
  echo "Validation Complete"
  echo " Errors: $error_count"
  echo " Warnings: $warning_count"
  echo "════════════════════════════════════════"

  if [ $error_count -eq 0 ]; then
    echo "✅ Nova structure is valid!"
    exit 0
  else
    echo "❌ Nova has $error_count error(s)"
    exit 1
  fi
}

# ── Validate the template ─────────────────────────────────────────────────

validate_template() {
  local TEMPLATE_DIR="$BASE_DIR/a_nova_template"
  echo "🔍 Validating template structure: $TEMPLATE_DIR"
  echo ""

  if [ ! -d "$TEMPLATE_DIR" ]; then
    log_error "Template directory does not exist: $TEMPLATE_DIR"
    exit 1
  fi

  # Check required template files
  local TEMPLATE_FILES=(
    "nova.py"
    "wizard.py"
    "bootstrap_nova.py"
    "README.md"
    "QUICKSTART.md"
    "config.yaml.example"
    ".env.example"
    ".env.memfirst.example"
    "memories/SOUL.md.example"
    "memories/memory.mdl.example"
    "memories/USER.md.example"
    "memories/user.mdl.example"
    "memories/LAYERED_MEMORY.md.example"
  )

  for file in "${TEMPLATE_FILES[@]}"; do
    if [ -f "$TEMPLATE_DIR/$file" ]; then
      log_ok "Template file exists: $file"
    else
      log_error "Missing template file: $file"
    fi
  done

  # Check required template directories
  local TEMPLATE_DIRS=(
    "memories"
    "configs"
    "docs"
    "scripts"
    "skills"
    "checkpoints"
    "logs"
    "cron"
  )

  for dir in "${TEMPLATE_DIRS[@]}"; do
    if [ -d "$TEMPLATE_DIR/$dir" ]; then
      log_ok "Template directory exists: $dir"
    else
      log_error "Missing template directory: $dir"
    fi
  done

  # Verify NO source code copies exist (they should be in platform dir)
  local STALE_DIRS=("l3-semantic" "l4-verbatim" "l5-dreamer" "l6-bridge" "mnemos_project")
  for dir in "${STALE_DIRS[@]}"; do
    if [ -d "$TEMPLATE_DIR/$dir" ]; then
      log_error "Stale source copy exists: $dir (should NOT be in template)"
    fi
  done

  echo ""
  echo "════════════════════════════════════════"
  echo "Template Validation Complete"
  echo " Errors: $error_count"
  echo " Warnings: $warning_count"
  echo "════════════════════════════════════════"

  if [ $error_count -eq 0 ]; then
    echo "✅ Template structure is valid!"
    exit 0
  else
    echo "❌ Template has $error_count error(s)"
    exit 1
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────

if [ -n "$NOVA_NAME" ]; then
  validate_nova "$BASE_DIR/$NOVA_NAME" "$NOVA_NAME"
else
  validate_template
fi
