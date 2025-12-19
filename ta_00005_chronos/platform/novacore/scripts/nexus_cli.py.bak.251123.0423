
#!/usr/bin/env python3
"""Nexus Continuity CLI

Lightweight CLI for Nexus that:
- Can be launched from any directory
- Tracks working directories, projects, threads
- Persists short-term state to Dragonfly
- Logs events to MongoDB
- Updates collaboration graph in Neo4j
- Optionally publishes events to NATS

No LLM calls are made here; this is a continuity + tracking shell only.
"""
import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Optional dependencies
try:
    import redis  # Dragonfly (Redis-compatible)
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

try:
    import asyncio
    from nats.aio.client import Client as NATS
except ImportError:
    NATS = None
    asyncio = None

ISO_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


def utc_now():
    return datetime.now(timezone.utc).strftime(ISO_FMT)


class ContinuityBackend:
    def __init__(self):
        # Dragonfly (required for core continuity)
        self.dragonfly_url = os.getenv("DRAGONFLY_NODE_1_URL", "redis://:df_cluster_2024_adapt_research@localhost:18000")
        self.redis = None
        if redis is not None:
            try:
                self.redis = redis.from_url(self.dragonfly_url)
                # simple ping to validate
                self.redis.ping()
            except Exception as e:
                print(f"[WARN] Could not connect to Dragonfly at {self.dragonfly_url}: {e}", file=sys.stderr)
                self.redis = None
        else:
            print("[WARN] redis-py not installed; Dragonfly continuity disabled", file=sys.stderr)

        # MongoDB (event log)
        self.mongo_url = os.getenv("MONGODB_AUTH_URL")
        self.mongo_client = None
        self.mongo_db = None
        self.mongo_events = None
        if MongoClient is not None and self.mongo_url:
            try:
                self.mongo_client = MongoClient(self.mongo_url)
                db_name = os.getenv("MONGODB_DATABASE", "teamadapt")
                self.mongo_db = self.mongo_client[db_name]
                self.mongo_events = self.mongo_db["nexus_events"]
            except Exception as e:
                print(f"[WARN] Could not connect to MongoDB at {self.mongo_url}: {e}", file=sys.stderr)
                self.mongo_client = None
                self.mongo_db = None
                self.mongo_events = None
        elif MongoClient is None:
            print("[WARN] pymongo not installed; MongoDB event logging disabled", file=sys.stderr)

        # Neo4j (collaboration graph)
        self.neo4j_url = os.getenv("NEO4J_BOLT_URL")
        self.neo4j_auth_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_auth_pass = os.getenv("NEO4J_PASSWORD", os.getenv("NEO4J_AUTH", "changeme"))
        self.neo4j_driver = None
        if GraphDatabase is not None and self.neo4j_url:
            try:
                self.neo4j_driver = GraphDatabase.driver(
                    self.neo4j_url,
                    auth=(self.neo4j_auth_user, self.neo4j_auth_pass),
                )
            except Exception as e:
                print(f"[WARN] Could not connect to Neo4j at {self.neo4j_url}: {e}", file=sys.stderr)
                self.neo4j_driver = None
        elif GraphDatabase is None:
            print("[WARN] neo4j driver not installed; graph updates disabled", file=sys.stderr)

        # NATS (optional event bus)
        self.nats_url = os.getenv("NATS_URL", os.getenv("NATS_CLUSTER_URL", ""))
        self.nats_client = None

    def load_snapshot(self, agent_id: str):
        key = f"field_snapshot:{agent_id}"
        if not self.redis:
            return None
        try:
            raw = self.redis.get(key)
            if not raw:
                return None
            return json.loads(raw)
        except Exception as e:
            print(f"[WARN] Failed to load snapshot for {agent_id}: {e}", file=sys.stderr)
            return None

    def save_snapshot(self, agent_id: str, snapshot: dict):
        if not self.redis:
            return
        key = f"field_snapshot:{agent_id}"
        try:
            self.redis.set(key, json.dumps(snapshot))
        except Exception as e:
            print(f"[WARN] Failed to save snapshot for {agent_id}: {e}", file=sys.stderr)

    def append_event(self, agent_id: str, event: dict, max_events: int = 500):
        if self.redis:
            list_key = f"events:{agent_id}"
            try:
                self.redis.rpush(list_key, json.dumps(event))
                self.redis.ltrim(list_key, -max_events, -1)
            except Exception as e:
                print(f"[WARN] Failed to append event in Dragonfly: {e}", file=sys.stderr)

        if self.mongo_events is not None:
            try:
                self.mongo_events.insert_one(event)
            except Exception as e:
                print(f"[WARN] Failed to log event in MongoDB: {e}", file=sys.stderr)

        if self.neo4j_driver is not None:
            self._update_graph(agent_id, event)

    def _update_graph(self, agent_id: str, event: dict):
        project_id = event.get("project_id")
        thread_id = event.get("thread_id")
        cwd = event.get("cwd")
        ts = event.get("timestamp")
        msg_type = event.get("type", "user")

        def _tx(tx):
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
                agent_id=agent_id,
                project_id=project_id,
                thread_id=thread_id,
                cwd=cwd,
                ts=ts,
            )

        try:
            with self.neo4j_driver.session() as session:
                session.execute_write(_tx)
        except Exception as e:
            print(f"[WARN] Failed to update Neo4j graph: {e}", file=sys.stderr)

    async def _publish_nats(self, subject: str, payload: dict):
        if NATS is None or asyncio is None or not self.nats_url:
            return
        if self.nats_client is None:
            try:
                self.nats_client = NATS()
                await self.nats_client.connect(servers=[self.nats_url])
            except Exception as e:
                print(f"[WARN] Failed to connect to NATS at {self.nats_url}: {e}", file=sys.stderr)
                self.nats_client = None
                return
        try:
            data = json.dumps(payload).encode("utf-8")
            await self.nats_client.publish(subject, data)
        except Exception as e:
            print(f"[WARN] Failed to publish to NATS: {e}", file=sys.stderr)

    def publish_event_async(self, agent_id: str, event: dict):
        if NATS is None or asyncio is None or not self.nats_url:
            return

        subject = f"nova.{agent_id}.events"
        try:
            asyncio.run(self._publish_nats(subject, event))
        except RuntimeError:
            # If there's already a running loop, skip publishing to avoid complexity.
            pass


def summarize_snapshot(snapshot: dict):
    if not snapshot:
        return "No prior state found."
    projects = snapshot.get("recent_projects") or []
    threads = snapshot.get("recent_threads") or []
    last_dir = snapshot.get("last_cwd")
    last_ts = snapshot.get("last_updated")
    return (
        f"Last updated: {last_ts}\n"
        f"Last directory: {last_dir}\n"
        f"Recent projects: {', '.join(projects) if projects else 'none'}\n"
        f"Recent threads: {', '.join(threads) if threads else 'none'}"
    )


def main():
    parser = argparse.ArgumentParser(description="Nexus Continuity CLI")
    parser.add_argument("--agent-id", default="nexus", help="Agent ID (default: nexus)")
    parser.add_argument("--project", help="Current project identifier", default=None)
    parser.add_argument("--thread", help="Current thread identifier", default=None)
    args = parser.parse_args()

    agent_id = args.agent_id
    project_id = args.project
    thread_id = args.thread

    backend = ContinuityBackend()

    snapshot = backend.load_snapshot(agent_id)
    print("=== Nexus Continuity CLI ===")
    print(f"Agent: {agent_id}")
    print(summarize_snapshot(snapshot))
    print("-----------------------------")
    print("Type messages to log context and activity. Type 'exit' or 'quit' to stop.")

    cwd = str(Path.cwd())
    if snapshot is None:
        snapshot = {
            "agent_id": agent_id,
            "recent_projects": [],
            "recent_threads": [],
            "last_cwd": cwd,
            "last_updated": utc_now(),
        }

    while True:
        try:
            user_input = input(f"{agent_id}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Exiting Nexus Continuity CLI.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("[INFO] Exiting Nexus Continuity CLI.")
            break

        ts = utc_now()
        cwd = str(Path.cwd())

        event = {
            "agent_id": agent_id,
            "type": "user",
            "timestamp": ts,
            "text": user_input,
            "project_id": project_id,
            "thread_id": thread_id,
            "cwd": cwd,
        }

        backend.append_event(agent_id, event)
        backend.publish_event_async(agent_id, event)

        # Update snapshot
        if project_id:
            if project_id not in snapshot.get("recent_projects", []):
                snapshot.setdefault("recent_projects", []).append(project_id)
        if thread_id:
            if thread_id not in snapshot.get("recent_threads", []):
                snapshot.setdefault("recent_threads", []).append(thread_id)
        snapshot["last_cwd"] = cwd
        snapshot["last_updated"] = ts

        backend.save_snapshot(agent_id, snapshot)

        print("[logged]")


if __name__ == "__main__":
    main()
