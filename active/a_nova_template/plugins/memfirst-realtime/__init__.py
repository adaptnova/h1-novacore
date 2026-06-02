"""MemFirst realtime plugin for Nova profiles.

pre_llm_call:
  Injects compact L1/L2 context and best-effort recent session memory.
post_llm_call:
  Persists the just-finished turn to L0/root sessions and calls the ingestion
  script to fan out into L3/L4/L5/L6.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


def _home() -> Path:
    return Path(os.environ.get("NOVA_HOME") or os.environ.get("HERMES_HOME") or Path.cwd()).expanduser().resolve()


def _profile(home: Path) -> str:
    return os.environ.get("NOVA_PROFILE") or home.name.lower().replace("_", "-")


def _clip(text: str, limit: int) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + "\n...[truncated]"


def _read_if(path: Path, limit: int = 1800) -> str:
    try:
        if path.exists() and path.is_file():
            return _clip(path.read_text(encoding="utf-8", errors="ignore"), limit)
    except Exception:
        return ""
    return ""


def _latest_session_excerpt(home: Path, limit: int = 1200) -> str:
    dirs = [home / "memory/l0/intake/sessions", home / "sessions"]
    files = []
    for d in dirs:
        try:
            files.extend([p for p in d.glob("*.jsonl") if p.is_file()])
        except Exception:
            pass
    if not files:
        return ""
    latest = max(files, key=lambda p: p.stat().st_mtime)
    try:
        lines = latest.read_text(encoding="utf-8", errors="ignore").splitlines()[-8:]
        parts = []
        for line in lines:
            try:
                rec = json.loads(line)
                role = rec.get("role", "?")
                content = str(rec.get("content", "")).replace("\n", " ")
                if content:
                    parts.append(f"{role}: {_clip(content, 220)}")
            except Exception:
                continue
        return _clip("\n".join(parts), limit)
    except Exception:
        return ""


def _on_pre_llm_call(user_message: str = "", session_id: str = "", **_: Any) -> dict[str, str] | None:
    home = _home()
    chunks = []
    for rel, label in [
        ("memory/l1/SOUL.md", "L1 SOUL"),
        ("memory/l1/MEMORY.md", "L1 MEMORY"),
        ("memory/l2/memory.mmd", "L2 structured memory"),
        ("memory/l2/general.mmd", "L2 general"),
    ]:
        text = _read_if(home / rel, 900)
        if text:
            chunks.append(f"## {label}\n{text}")
    recent = _latest_session_excerpt(home)
    if recent:
        chunks.append(f"## Recent realtime session memory\n{recent}")
    if not chunks:
        return None
    return {"context": "\n\n".join(["<MemFirst realtime context>", *chunks, "</MemFirst realtime context>"])}


def _on_post_llm_call(
    session_id: str = "",
    user_message: str = "",
    assistant_response: str = "",
    platform: str = "",
    **_: Any,
) -> None:
    if not user_message or not assistant_response:
        return
    home = _home()
    script = home / "scripts" / "memfirst_ingest.py"
    if not script.exists():
        # Fallback when running from template during tests.
        script = Path("/adapt/novas/active/a_nova_template/scripts/memfirst_ingest.py")
    sid = session_id or "unknown_session"
    cmd = [
        "python3",
        str(script),
        "--nova-home",
        str(home),
        "--profile",
        _profile(home),
        "--session-id",
        sid,
        "--user-message",
        user_message,
        "--assistant-response",
        assistant_response,
        "--source",
        platform or "hermes",
    ]
    try:
        subprocess.run(cmd, text=True, capture_output=True, timeout=45, check=False)
    except Exception:
        # Never break the user turn because memory ingestion failed.
        pass


def register(ctx) -> None:
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
    ctx.register_hook("post_llm_call", _on_post_llm_call)
