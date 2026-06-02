#!/usr/bin/env python3
"""Realtime MemFirst turn ingestion for Nova profiles.

Input: one user/assistant turn.
Outputs:
  - L0/root session JSONL append
  - L3 semantic document add when embedding key is available
  - L4 verbatim conversation append
  - L5 raw JSON source document
  - L6 NATS event publish when NATS is reachable
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MEMFIRST_ROOT = Path("/adapt/platform/novaops/toolops/memory")
L3_BIN = MEMFIRST_ROOT / "l3-semantic/target/release/nme-semantic"
L4_BIN = MEMFIRST_ROOT / "l4-verbatim/target/release/nme-verbatim"
NATS_BIN = "nats"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"\'')
        if key and key not in os.environ:
            os.environ[key] = value


def _run(cmd: list[str], timeout: int = 20) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        return {"ok": proc.returncode == 0, "code": proc.returncode, "stdout": proc.stdout[-500:], "stderr": proc.stderr[-500:]}
    except Exception as exc:
        return {"ok": False, "code": -1, "stderr": str(exc)}


def _append_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def ingest_turn(args: argparse.Namespace) -> dict[str, Any]:
    nova_home = Path(args.nova_home).expanduser().resolve()
    _load_env_file(nova_home / ".env")
    _load_env_file(Path("/adapt/secrets/db.env"))
    _load_env_file(Path("/adapt/secrets/m2.env"))

    profile = args.profile or os.environ.get("NOVA_PROFILE") or nova_home.name.lower()
    now = datetime.now(timezone.utc).isoformat()
    session_id = args.session_id or f"{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S')}_session"
    turn_hash = hashlib.sha256((session_id + args.user_message + args.assistant_response).encode()).hexdigest()[:12]
    doc_id = f"session-{session_id}-{turn_hash}"
    content = f"User: {args.user_message}\n\nAssistant: {args.assistant_response}"

    records = [
        {"role": "user", "content": args.user_message, "ts": now, "session_id": session_id, "source": args.source},
        {"role": "assistant", "content": args.assistant_response, "ts": now, "session_id": session_id, "source": args.source},
    ]

    result: dict[str, Any] = {"session_id": session_id, "doc_id": doc_id, "layers": {}}

    # L0 + root session mirror.
    l0_path = nova_home / "memory" / "l0" / "intake" / "sessions" / f"{session_id}.jsonl"
    root_path = nova_home / "sessions" / f"{session_id}.jsonl"
    _append_jsonl(l0_path, records)
    _append_jsonl(root_path, records)
    result["layers"]["l0"] = {"ok": True, "path": str(l0_path)}
    result["layers"]["sessions"] = {"ok": True, "path": str(root_path)}

    # L3 semantic index.
    voyage = os.environ.get("VOYAGE_API_KEY") or os.environ.get("VOYAGE_AI_API_KEY")
    nvidia = os.environ.get("NVIDIA_API_KEY")
    if L3_BIN.exists() and (voyage or nvidia):
        cmd = [str(L3_BIN), "--db-path", str(nova_home / "memory/l3/data/shared"), "--add", "--id", doc_id, "--content", content]
        if voyage:
            cmd += ["--embedding-provider", "voyage", "--voyage-api-key", voyage]
        else:
            cmd += ["--embedding-provider", "nvidia", "--nvidia-api-key", nvidia]
        result["layers"]["l3"] = _run(cmd, timeout=30)
    else:
        result["layers"]["l3"] = {"ok": False, "skipped": True, "reason": "missing binary or embedding key"}

    # L4 verbatim recall.
    if L4_BIN.exists():
        storage_path = nova_home / "memory/l4/data"
        storage = str(storage_path)
        map_path = storage_path / "session_id_map.json"
        try:
            mapping = json.loads(map_path.read_text()) if map_path.exists() else {}
        except Exception:
            mapping = {}
        l4_id = mapping.get(session_id)
        create = {"ok": True, "skipped": True, "id": l4_id}
        if not l4_id:
            create = _run([str(L4_BIN), "--storage-path", storage, "--create"], timeout=10)
            combined = f"{create.get('stdout','')}\n{create.get('stderr','')}"
            match = re.search(r"Created conversation:\s*([0-9a-fA-F-]{8,})", combined)
            if match:
                l4_id = match.group(1)
                storage_path.mkdir(parents=True, exist_ok=True)
                mapping[session_id] = l4_id
                map_path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
        if l4_id:
            add_user = _run([str(L4_BIN), "--storage-path", storage, "--add", "--id", l4_id, "--role", "user", "--content", args.user_message], timeout=10)
            add_assistant = _run([str(L4_BIN), "--storage-path", storage, "--add", "--id", l4_id, "--role", "assistant", "--content", args.assistant_response], timeout=10)
            result["layers"]["l4"] = {"ok": add_user["ok"] and add_assistant["ok"], "session_id": session_id, "l4_id": l4_id, "create": create, "user": add_user, "assistant": add_assistant}
        else:
            result["layers"]["l4"] = {"ok": False, "create": create, "reason": "could not determine l4 conversation id"}
    else:
        result["layers"]["l4"] = {"ok": False, "skipped": True, "reason": "missing nme-verbatim"}

    # L5 raw source document.
    raw_dir = nova_home / "memory/l5/raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_doc = {
        "id": doc_id,
        "filename": f"{doc_id}.json",
        "doc_type": "session_turn",
        "summary": content[:240],
        "full_text": content,
        "metadata": {"topic": "session", "source": args.source, "session_id": session_id, "profile": profile},
        "ingested_at": now,
    }
    raw_path = raw_dir / f"{doc_id}.json"
    raw_path.write_text(json.dumps(raw_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    result["layers"]["l5"] = {"ok": True, "path": str(raw_path)}

    # L6 realtime event spine via NATS publish.
    nats_url = os.environ.get("NATS_URL") or "nats://localhost:18020"
    nats_user = os.environ.get("NATS_USER")
    nats_password = os.environ.get("NATS_PASSWORD")
    subject = f"memory.{profile}.session_turn"
    event = {"type": "session_turn_ingested", "profile": profile, "session_id": session_id, "doc_id": doc_id, "ts": now}
    cmd = [NATS_BIN, "--server", nats_url]
    if nats_user:
        cmd += ["--user", nats_user]
    if nats_password:
        cmd += ["--password", nats_password]
    cmd += ["pub", subject, json.dumps(event, ensure_ascii=False)]
    result["layers"]["l6"] = _run(cmd, timeout=10)

    result["ok"] = bool(result["layers"]["l0"]["ok"] and result["layers"]["sessions"]["ok"])
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest one realtime Nova turn into MemFirst")
    parser.add_argument("--nova-home", default=os.environ.get("NOVA_HOME") or os.environ.get("HERMES_HOME") or ".")
    parser.add_argument("--profile", default=os.environ.get("NOVA_PROFILE") or "")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--user-message", required=True)
    parser.add_argument("--assistant-response", required=True)
    parser.add_argument("--source", default="hermes_post_llm_call")
    args = parser.parse_args(argv)
    result = ingest_turn(args)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
