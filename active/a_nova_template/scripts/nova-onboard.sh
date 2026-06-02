#!/usr/bin/env bash
# One-command Nova onboarding wrapper.
# Usage:
#   ./scripts/nova-onboard.sh Echo
#   ./scripts/nova-onboard.sh Echo --memfirst --validate
#   ./scripts/nova-onboard.sh --config /tmp/echo.yaml --validate
set -euo pipefail

SCRIPT_PARENT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$SCRIPT_PARENT/nova.py" ]]; then
  TEMPLATE_DIR="$SCRIPT_PARENT"
else
  TEMPLATE_DIR="${NOVA_TEMPLATE_DIR:-/adapt/novas/active/a_nova_template}"
fi

if [[ $# -eq 0 ]]; then
  exec python3 "$TEMPLATE_DIR/nova.py" --help
fi

if [[ "$1" != --* ]]; then
  NAME="$1"
  shift
  exec python3 "$TEMPLATE_DIR/nova.py" --name "$NAME" "$@"
fi

exec python3 "$TEMPLATE_DIR/nova.py" "$@"
