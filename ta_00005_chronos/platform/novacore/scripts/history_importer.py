#!/usr/bin/env python3
"""Nova History Importer

One-shot importer to backfill historical chat logs into the new continuity stack:
- MongoDB (event history)
- Dragonfly (snapshot + recent events)
- Neo4j (relationship graph)

Usage example:

  python3 /adapt/platform/novaops/history_importer.py \
    --agent-id nexus \
    --history-file /adapt/novas/ta-00001-nexus/chat_history/ta_00001_nexus_chat_1.md \
    --project NOVA_SPIN \
    --thread NS_0001 \
    --default-cwd /adapt/novas/ta-00001-nexus

Notes:
  - This script assumes a simple markdown/chat-style log with lines that can be
    grouped into messages; it falls back to treating paragraphs as messages.
  - Timestamps are synthetic (ordered) unless you later extend the parser.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

# Auto-load environment from /adaptai/db.env so you don't need to `source` it
ENV_FILE = "/adaptai/db.env"
if Path(ENV_FILE).is_file():
    load_dotenv(ENV_FILE)

# Optional dependencies
try:
    import redis  # Dragonfly
except ImportError:
    redis = None

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

ISO_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime(ISO_FMT)


def parse_history_markdown(path: Path):
    """Very simple parser for a chat-style markdown log.

    Strategy:
      - Split on blank lines into blocks.
      - Within each block, treat the first line as 'role' if it looks like
        'User:' or 'Assistant:'; otherwise default based on markers or use 'unknown'.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.split(r"\n\s*\n", text.strip())

    messages = []
    for block in blocks:
        lines = [l for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        first = lines[0].strip()
        role = "unknown"
        content_lines = lines

        # Crude role detection
        m = re.match(r"^(User|Assistant|System|Nexus)[:\-]", first, re.IGNORECASE)
        if m:
            role_raw = m.group(1).lower()
            if role_raw in {"user", "assistant", "system"}:
                role = role_raw
            elif role_raw == "nexus":
                role = "assistant"
            content_lines = lines[1:] if len(lines) > 1 else []

        content = "\n".join(content_lines).strip()
        if not content:
            continue

        messages.append(
            {
                "role": role,
                "text": content,
            }
        )

    return messages


def compute_event_hash(agent_id: str, role: str, text: str) -> str:
    h = hashlib.sha256()
    key = f"{agent_id}|{role}|{text[:200]}"
    h.update(key.encode("utf-8", errors="ignore"))
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Nova History Importer")
    parser.add_argument("--agent-id", required=True, help="Agent/Nova ID (e.g. nexus, vaeris)")
    parser.add_argument("--history-file", required=True, help="Path to markdown chat history file")
    parser.add_argument("--project", help="Project ID to tag events with", default=None)
    parser.add_argument("--thread", help="Thread ID to tag events with", default=None)
    parser.add_argument("--default-cwd", help="Default workspace path to tag events with", default=None)
    parser.add_argument(
        "--max-dragonfly-events",
        type=int,
        default=500,
        help="Max recent events to keep in Dragonfly list",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and show counts, but do not write to DBs",
    )
    args = parser.parse_args()

    agent_id = args.agent_id
    history_path = Path(args.history_file)
    if not history_path.is_file():
        print(f"[ERROR] History file not found: {history_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Parsing history from {history_path} for agent '{agent_id}'...")
    messages = parse_history_markdown(history_path)
    if not messages:
        print("[ERROR] No messages parsed from history file.", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Parsed {len(messages)} messages.")

    # Set up DB connections unless dry-run
    redis_client = None
    mongo_events = None
    neo4j_driver = None

    if not args.dry_run:
        # Dragonfly
        if redis is not None:
            dragonfly_url = os.getenv(
                "DRAGONFLY_NODE_1_URL",
                "redis://:df_cluster_2024_adapt_research@localhost:18000",
            )
            try:
                redis_client = redis.from_url(dragonfly_url)
                redis_client.ping()
                print(f"[INFO] Connected to Dragonfly at {dragonfly_url}")
            except Exception as e:
                print(f"[WARN] Could not connect to Dragonfly: {e}", file=sys.stderr)
                redis_client = None
        else:
            print("[WARN] redis-py not installed; Dragonfly continuity will be skipped", file=sys.stderr)

        # MongoDB
        if MongoClient is not None:
            mongo_url = os.getenv("MONGODB_AUTH_URL")
            if mongo_url:
                try:
                    client = MongoClient(mongo_url)
                    db_name = os.getenv("MONGODB_DATABASE", "teamadapt")
                    db = client[db_name]
                    collection_name = f"{agent_id}_events"
                    mongo_events = db[collection_name]
                    print(f"[INFO] Connected to MongoDB collection {db_name}.{collection_name}")
                except Exception as e:
                    print(f"[WARN] Could not connect to MongoDB: {e}", file=sys.stderr)
                    mongo_events = None
            else:
                print("[WARN] MONGODB_AUTH_URL not set; MongoDB will be skipped", file=sys.stderr)
        else:
            print("[WARN] pymongo not installed; MongoDB will be skipped", file=sys.stderr)

        # Neo4j
        if GraphDatabase is not None:
            neo4j_url = os.getenv("NEO4J_BOLT_URL")
            if neo4j_url:
                neo4j_user = os.getenv("NEO4J_USER", "neo4j")
                neo4j_pass = os.getenv("NEO4J_PASSWORD", os.getenv("NEO4J_AUTH", "changeme"))
                try:
                    neo4j_driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_pass))
                    print(f"[INFO] Connected to Neo4j at {neo4j_url}")
                except Exception as e:
                    print(f"[WARN] Could not connect to Neo4j: {e}", file=sys.stderr)
                    neo4j_driver = None
            else:
                print("[WARN] NEO4J_BOLT_URL not set; Neo4j will be skipped", file=sys.stderr)
        else:
            print("[WARN] neo4j driver not installed; Neo4j will be skipped", file=sys.stderr)

    # Assign synthetic timestamps in order
    start_time = utc_now() - timedelta(minutes=len(messages))
    events = []
    for idx, msg in enumerate(messages):
        ts = start_time + timedelta(minutes=idx)
        event = {
            "agent_id": agent_id,
            "type": msg.get("role", "unknown"),
            "timestamp": isoformat(ts),
            "text": msg.get("text", ""),
            "project_id": args.project,
            "thread_id": args.thread,
            "cwd": args.default_cwd,
            "source": "imported_history",
        }
        event["event_hash"] = compute_event_hash(agent_id, event["type"], event["text"])
        events.append(event)

    print(f"[INFO] Prepared {len(events)} events for import.")

    if args.dry_run:
        print("[DRY RUN] First 3 events:")
        for e in events[:3]:
            print(json.dumps(e, indent=2))
        print("[DRY RUN] No writes performed.")
        sys.exit(0)

    # Write to MongoDB
    if mongo_events is not None:
        try:
            mongo_events.insert_many(events)
            print(f"[INFO] Inserted {len(events)} events into MongoDB.")
        except Exception as e:
            print(f"[WARN] Failed to insert events into MongoDB: {e}", file=sys.stderr)

    # Seed Dragonfly
    if redis_client is not None:
        list_key = f"events:{agent_id}"
        snap_key = f"field_snapshot:{agent_id}"

        # Keep only the last N events in the list
        last_events = events[-args.max_dragonfly_events :]
        try:
            redis_client.delete(list_key)
            for ev in last_events:
                redis_client.rpush(list_key, json.dumps(ev))
            print(f"[INFO] Seeded Dragonfly list {list_key} with {len(last_events)} events.")
        except Exception as e:
            print(f"[WARN] Failed to seed Dragonfly events list: {e}", file=sys.stderr)

        # Snapshot
        last_event = events[-1]
        recent_projects = []
        recent_threads = []
        if args.project:
            recent_projects.append(args.project)
        if args.thread:
            recent_threads.append(args.thread)

        snapshot = {
            "agent_id": agent_id,
            "recent_projects": recent_projects,
            "recent_threads": recent_threads,
            "last_cwd": args.default_cwd,
            "last_updated": last_event["timestamp"],
        }
        try:
            redis_client.set(snap_key, json.dumps(snapshot))
            print(f"[INFO] Wrote snapshot to {snap_key} in Dragonfly.")
        except Exception as e:
            print(f"[WARN] Failed to write snapshot to Dragonfly: {e}", file=sys.stderr)

    # Update Neo4j
    if neo4j_driver is not None:

        def _tx(tx, ev):
            tx.run(
                """
                MERGE (a:Agent {id: $agent_id})
                  ON CREATE SET a.created_at = $ts
                  SET a.last_seen_at = $ts
                WITH a
                FOREACH (p IN CASE WHEN $project_id IS NULL THEN [] ELSE [1] END |
                  MERGE (pr:Project {id: $project_id})
                    ON CREATE SET pr.created_at = $ts
                    SET pr.last_seen_at = $ts
                  MERGE (a)-[r:WORKS_ON]->(pr)
                    ON CREATE SET r.since = $ts
                    SET r.last_active = $ts
                )
                WITH a
                FOREACH (t IN CASE WHEN $thread_id IS NULL THEN [] ELSE [1] END |
                  MERGE (th:Thread {id: $thread_id})
                    ON CREATE SET th.created_at = $ts
                    SET th.last_seen_at = $ts
                  MERGE (a)-[rt:PARTICIPATES_IN]->(th)
                    ON CREATE SET rt.since = $ts
                    SET rt.last_active = $ts
                )
                WITH a
                FOREACH (d IN CASE WHEN $cwd IS NULL THEN [] ELSE [1] END |
                  MERGE (w:Workspace {path: $cwd})
                    ON CREATE SET w.created_at = $ts
                    SET w.last_seen_at = $ts
                  MERGE (a)-[rw:WORKS_IN]->(w)
                    ON CREATE SET rw.since = $ts
                    SET rw.last_active = $ts
                )
                """,
                agent_id=ev["agent_id"],
                project_id=ev.get("project_id"),
                thread_id=ev.get("thread_id"),
                cwd=ev.get("cwd"),
                ts=ev["timestamp"],
            )

        try:
            with neo4j_driver.session() as session:
                for ev in events:
                    session.execute_write(_tx, ev)
            print("[INFO] Neo4j graph updated for imported events.")
        except Exception as e:
            print(f"[WARN] Failed to update Neo4j: {e}", file=sys.stderr)

    print("[INFO] Import completed.")


if __name__ == "__main__":
    main()
