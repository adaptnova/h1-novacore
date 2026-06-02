#!/usr/bin/env python3
"""Compatibility entrypoint for Nova onboarding.

The old bootstrap_nova.py had divergent creation logic. It now delegates to the
canonical nova.py implementation so every path uses the same tested automation.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

NOVA_CLI = Path(__file__).resolve().parent / "nova.py"


def main() -> int:
    if not NOVA_CLI.exists():
        print(f"ERROR: missing canonical onboarding CLI: {NOVA_CLI}", file=sys.stderr)
        return 1
    return subprocess.run([sys.executable, str(NOVA_CLI), *sys.argv[1:]]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
