#!/usr/bin/env python3
"""Interactive Nova onboarding wizard.

Collects identity fields, then delegates to nova.py so wizard and CLI use the
same tested creation path.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

TEMPLATE_DIR = Path(__file__).resolve().parent
NOVA_CLI = TEMPLATE_DIR / "nova.py"


def ask(prompt: str, default: str | None = None, required: bool = False) -> str:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        if not required:
            return ""
        print("  required")


def main() -> int:
    print("\n🌟 Nova Onboarding Wizard\n")
    identity = {
        "nova_name": ask("Nova Name (PascalCase, e.g. Echo)", required=True),
        "nature": ask("Nature", "autonomous AI agent"),
        "mission": ask("Mission", "To collaborate, build, and operate with competence"),
        "vibe": ask("Vibe", "curious, sharp, warm, electric"),
        "emoji": ask("Emoji", "🤖"),
        "origin": ask("Origin", "Created for the Adapt AI Nova ecosystem"),
        "goal_short": ask("Short-term goal", "Master the environment and establish reliable memory"),
        "goal_medium": ask("Medium-term goal", "Contribute meaningfully with increasing autonomy"),
        "goal_long": ask("Long-term vision", "Become a durable digital collaborator"),
        "focus": ask("Current focus", "Onboarding, memory continuity, and useful autonomous work"),
        "user_name": ask("User name", "Chase"),
        "timezone": ask("Timezone", "America/Phoenix"),
        "philosophy": [
            "Bias toward action",
            "Earn trust through competence",
            "Protect private context",
            "Finish the job and verify it",
        ],
    }
    memfirst = ask("Run full MemFirst provisioning now? y/N", "N").lower().startswith("y")
    confirm = ask(f"Create {identity['nova_name']}? y/N", "N").lower().startswith("y")
    if not confirm:
        print("Aborted")
        return 0

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(identity, fh)
        config_path = fh.name

    cmd = [sys.executable, str(NOVA_CLI), "--config", config_path, "--validate"]
    if memfirst:
        cmd.append("--memfirst")
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
