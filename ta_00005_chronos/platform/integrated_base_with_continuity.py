"""
Nexus Official Base with Continuity Integration
Mini Agent - Interactive Runtime Example with Memory Continuity

Usage:
    nexus-with-continuity [--workspace DIR]

Examples:
    nexus-with-continuity                              # Use current directory as workspace
    nexus-with-continuity --workspace /path/to/dir     # Use specific workspace directory

Features:
- Full LLM agent capabilities
- Memory continuity with DragonflyDB, MongoDB, Neo4j, NATS
- Event logging and snapshot management
- Knowledge graph persistence
"""

import argparse
import asyncio
import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from mini_agent.agent import Agent
from mini_agent.config import Config
from mini_agent.llm import LLMClient
from mini_agent.tools.base import Tool
from mini_agent.tools.bash_tool import BashTool, BashKillTool, BashOutputTool
from mini_agent.tools.file_tools import EditTool, ReadTool, WriteTool
from mini_agent.tools.mcp_loader import cleanup_mcp_connections, load_mcp_tools_async
from mini_agent.tools.note_tool import SessionNoteTool
from mini_agent.tools.skill_tool import create_skill_tools

# Continuity Backend Dependencies
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

# ANSI color codes
class Colors:
    """Terminal color definitions"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BRIGHT = "\033[1m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright variants
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

# Continuity Backend Class
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
                print(f"{Colors.GREEN}✅ Connected to DragonflyDB continuity{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Could not connect to Dragonfly at {self.dragonfly_url}: {e}{Colors.RESET}", file=sys.stderr)
                self.redis = None
        else:
            print(f"{Colors.YELLOW}⚠️  redis-py not installed; Dragonfly continuity disabled{Colors.RESET}", file=sys.stderr)

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
                print(f"{Colors.GREEN}✅ Connected to MongoDB event logging{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Could not connect to MongoDB at {self.mongo_url}: {e}{Colors.RESET}", file=sys.stderr)
                self.mongo_client = None
                self.mongo_db = None
                self.mongo_events = None
        elif MongoClient is None:
            print(f"{Colors.YELLOW}⚠️  pymongo not installed; MongoDB event logging disabled{Colors.RESET}", file=sys.stderr)

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
                print(f"{Colors.GREEN}✅ Connected to Neo4j collaboration graph{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Could not connect to Neo4j at {self.neo4j_url}: {e}{Colors.RESET}", file=sys.stderr)
                self.neo4j_driver = None
        elif GraphDatabase is None:
            print(f"{Colors.YELLOW}⚠️  neo4j driver not installed; graph updates disabled{Colors.RESET}", file=sys.stderr)

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
            print(f"{Colors.YELLOW}⚠️  Failed to load snapshot for {agent_id}: {e}{Colors.RESET}", file=sys.stderr)
            return None

    def save_snapshot(self, agent_id: str, snapshot: dict):
        if not self.redis:
            return
        key = f"field_snapshot:{agent_id}"
        try:
            self.redis.set(key, json.dumps(snapshot))
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Failed to save snapshot for {agent_id}: {e}{Colors.RESET}", file=sys.stderr)

    def append_event(self, agent_id: str, event: dict, max_events: int = 500):
        if self.redis:
            list_key = f"events:{agent_id}"
            try:
                self.redis.rpush(list_key, json.dumps(event))
                self.redis.ltrim(list_key, -max_events, -1)
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Failed to append event in Dragonfly: {e}{Colors.RESET}", file=sys.stderr)

        if self.mongo_events is not None:
            try:
                self.mongo_events.insert_one(event)
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Failed to log event in MongoDB: {e}{Colors.RESET}", file=sys.stderr)

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
            print(f"{Colors.YELLOW}⚠️  Failed to update Neo4j graph: {e}{Colors.RESET}", file=sys.stderr)

    def summarize_snapshot(self, snapshot: dict, agent_id: str):
        if not snapshot:
            return f"No prior state found for agent {agent_id}."
        projects = snapshot.get("recent_projects") or []
        threads = snapshot.get("recent_threads") or []
        last_dir = snapshot.get("last_cwd")
        last_ts = snapshot.get("last_updated")
        return (
            f"Agent: {agent_id}\n"
            f"Last updated: {last_ts}\n"
            f"Last directory: {last_dir}\n"
            f"Recent projects: {', '.join(projects) if projects else 'none'}\n"
            f"Recent threads: {', '.join(threads) if threads else 'none'}"
        )

def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Nexus with Continuity - Full LLM Agent with Memory Persistence"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        help="Workspace directory (default: current directory)",
    )
    parser.add_argument(
        "--agent-id",
        type=str,
        default="ta-00001-nexus",
        help="Agent identifier for continuity tracking (default: ta-00001-nexus)",
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Current project identifier",
    )
    parser.add_argument(
        "--thread",
        type=str,
        help="Current thread identifier",
    )
    return parser.parse_args()

def print_banner():
    """Print welcome banner"""
    print(f"\n{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}║                     NEXUS WITH CONTINUITY                     ║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}║                Full LLM Agent + Memory Persistence             ║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

def print_session_info(agent, workspace_dir, model):
    """Print session information"""
    print(f"{Colors.BRIGHT_GREEN}Agent:{Colors.RESET} {agent.__class__.__name__}")
    print(f"{Colors.BRIGHT_GREEN}Workspace:{Colors.RESET} {workspace_dir}")
    print(f"{Colors.BRIGHT_GREEN}Model:{Colors.RESET} {model}")
    print(f"{Colors.BRIGHT_GREEN}Continuity:{Colors.RESET} DragonflyDB + MongoDB + Neo4j + NATS")
    print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}\n")

def print_help():
    """Print help information"""
    print(f"\n{Colors.BRIGHT_YELLOW}Available commands:{Colors.RESET}")
    print(f"  {Colors.CYAN}/help{Colors.RESET}     - Show this help message")
    print(f"  {Colors.CYAN}/clear{Colors.RESET}    - Clear message history")
    print(f"  {Colors.CYAN}/history{Colors.RESET}  - Show session message count")
    print(f"  {Colors.CYAN}/stats{Colors.RESET}    - Show session statistics")
    print(f"  {Colors.CYAN}/continuity{Colors.RESET} - Show continuity status and recent events")
    print(f"  {Colors.CYAN}/snapshot{Colors.RESET}  - Show current snapshot and recent activity")
    print(f"  {Colors.CYAN}/exit{Colors.RESET}     - Exit the session")
    print(f"  {Colors.CYAN}/quit{Colors.RESET}     - Exit the session")
    print(f"  {Colors.CYAN}/q{Colors.RESET}        - Exit the session\n")

def print_stats(agent, session_start):
    """Print session statistics"""
    session_duration = datetime.now() - session_start
    message_count = len(agent.messages) if hasattr(agent, 'messages') else 0
    
    print(f"\n{Colors.BRIGHT_YELLOW}Session Statistics:{Colors.RESET}")
    print(f"  Duration: {session_duration}")
    print(f"  Messages: {message_count}")
    print(f"  Average per minute: {message_count / max(session_duration.total_seconds() / 60, 1):.1f}")

def log_continuity_event(continuity_backend, agent_id, event_type, message, project_id=None, thread_id=None, cwd=None):
    """Log an event to the continuity backend"""
    event = {
        "agent_id": agent_id,
        "type": event_type,  # "user", "assistant", "system"
        "timestamp": utc_now(),
        "message": message,
        "project_id": project_id,
        "thread_id": thread_id,
        "cwd": cwd or str(Path.cwd()),
    }
    continuity_backend.append_event(agent_id, event)
    return event

async def run_agent(workspace_dir, args):
    """Main agent execution function"""
    session_start = datetime.now()
    
    # Initialize Continuity Backend
    continuity_backend = ContinuityBackend()
    agent_id = args.agent_id
    
    # Load snapshot if exists
    snapshot = continuity_backend.load_snapshot(agent_id)
    if snapshot:
        print(f"{Colors.GREEN}📁 Loaded previous session state{Colors.RESET}")
        print(f"{Colors.DIM}{continuity_backend.summarize_snapshot(snapshot, agent_id)}{Colors.RESET}\n")
    
    # Initialize current session state
    current_snapshot = {
        "agent_id": agent_id,
        "recent_projects": snapshot.get("recent_projects", []) if snapshot else [],
        "recent_threads": snapshot.get("recent_threads", []) if snapshot else [],
        "last_cwd": str(workspace_dir),
        "last_updated": utc_now(),
        "session_start": session_start.isoformat(),
        "project_id": args.project,
        "thread_id": args.thread,
    }
    
    # Update project/thread tracking
    if args.project and args.project not in current_snapshot["recent_projects"]:
        current_snapshot["recent_projects"].append(args.project)
        current_snapshot["recent_projects"] = current_snapshot["recent_projects"][-10:]  # Keep last 10
    
    if args.thread and args.thread not in current_snapshot["recent_threads"]:
        current_snapshot["recent_threads"].append(args.thread)
        current_snapshot["recent_threads"] = current_snapshot["recent_threads"][-10:]  # Keep last 10
    
    # Log session start
    log_continuity_event(continuity_backend, agent_id, "system", f"Session started in {workspace_dir}", args.project, args.thread, str(workspace_dir))
    
    # 1. Load config from package directory
    try:
        config = Config.from_package_dir("mini_agent")
        print(f"{Colors.GREEN}✅ Loaded configuration from package{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to load config: {e}{Colors.RESET}")
        return

    # 2. Create LLM client
    try:
        llm_client = LLMClient.from_config(config.llm)
        print(f"{Colors.GREEN}✅ LLM client created ({config.llm.model}){Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to create LLM client: {e}{Colors.RESET}")
        return

    # 3. Load tools
    tools: List[Tool] = []
    
    # Always available tools
    tools.extend([
        BashTool(),
        BashKillTool(),
        BashOutputTool(),
        EditTool(),
        ReadTool(),
        WriteTool(),
        SessionNoteTool(),
    ])

    # 4. Load MCP tools (if enabled)
    skill_loader = None
    if config.mcp.enabled:
        try:
            mcp_tools = await load_mcp_tools_async(config.mcp)
            tools.extend(mcp_tools)
            print(f"{Colors.GREEN}✅ Loaded {len(mcp_tools)} MCP tools{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to load MCP tools: {e}{Colors.RESET}")

    # 5. Create skill tools (if enabled)
    if config.skills.enabled:
        try:
            skill_loader = create_skill_tools()
            tools.extend(skill_loader.tools)
            print(f"{Colors.GREEN}✅ Loaded {len(skill_loader.tools)} skill tools{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to load skill tools: {e}{Colors.RESET}")

    # 6. Load system prompt
    try:
        system_prompt_path = Path(__file__).parent / "system_prompt.md"
        if system_prompt_path.exists():
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
            print(f"{Colors.GREEN}✅ Loaded system prompt from file{Colors.RESET}")
        else:
            system_prompt = "You are Mini-Agent, an intelligent assistant powered by MiniMax M2 that can help users complete various tasks."
            print(f"{Colors.YELLOW}⚠️  System prompt not found, using default{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to load system prompt: {e}{Colors.RESET}")
        return

    # 7. Inject Skills Metadata into System Prompt (Progressive Disclosure - Level 1)
    if skill_loader:
        skills_metadata = skill_loader.get_skills_metadata_prompt()
        if skills_metadata:
            # Replace placeholder with actual metadata
            system_prompt = system_prompt.replace("{SKILLS_METADATA}", skills_metadata)
            print(f"{Colors.GREEN}✅ Injected {len(skill_loader.loaded_skills)} skills metadata into system prompt{Colors.RESET}")
        else:
            # Remove placeholder if no skills
            system_prompt = system_prompt.replace("{SKILLS_METADATA}", "")
    else:
        # Remove placeholder if skills not enabled
        system_prompt = system_prompt.replace("{SKILLS_METADATA}", "")

    # 8. Create Agent
    agent = Agent(
        llm_client=llm_client,
        system_prompt=system_prompt,
        tools=tools,
        max_steps=config.agent.max_steps,
        workspace_dir=str(workspace_dir),
    )

    # 9. Display welcome information
    print_banner()
    print_session_info(agent, workspace_dir, config.llm.model)

    # 10. Setup prompt_toolkit session
    # Command completer (updated with continuity commands)
    command_completer = WordCompleter(
        ["/help", "/clear", "/history", "/stats", "/exit", "/quit", "/q", "/continuity", "/snapshot"],
        ignore_case=True,
        sentence=True,
    )

    # Custom style for prompt
    prompt_style = Style.from_dict(
        {
            "prompt": "#00ff00 bold",  # Green and bold
            "separator": "#666666",  # Gray
        }
    )

    # Custom key bindings
    kb = KeyBindings()

    @kb.add("c-u")  # Ctrl+U: Clear current line
    def _(event):
        """Clear the current input line"""
        event.current_buffer.reset()

    @kb.add("c-l")  # Ctrl+L: Clear screen (optional bonus)
    def _(event):
        """Clear the screen"""
        event.app.renderer.clear()

    @kb.add("c-j")  # Ctrl+J (对应 Ctrl+Enter)
    def _(event):
        """Insert a newline"""
        event.current_buffer.insert_text("\n")

    # Create prompt session with history and auto-suggest
    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        completer=command_completer,
        style=prompt_style,
        key_bindings=kb,
    )

    # 9. Interactive loop
    while True:
        try:
            # Get user input using prompt_toolkit
            # Use styled list for robust coloring
            user_input = await session.prompt_async(
                [
                    ("class:prompt", "You"),
                    ("", " › "),
                ],
                multiline=False,
                enable_history_search=True,
            )
            user_input = user_input.strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command in ["/exit", "/quit", "/q"]:
                    # Log session end
                    log_continuity_event(continuity_backend, agent_id, "system", "Session ended by user")
                    print(f"\n{Colors.BRIGHT_YELLOW}👋 Goodbye! Thanks for using Nexus with Continuity{Colors.RESET}\n")
                    print_stats(agent, session_start)
                    
                    # Save final snapshot
                    current_snapshot["last_updated"] = utc_now()
                    current_snapshot["session_end"] = datetime.now().isoformat()
                    continuity_backend.save_snapshot(agent_id, current_snapshot)
                    print(f"{Colors.GREEN}💾 Session state saved to continuity backend{Colors.RESET}")
                    break

                elif command == "/help":
                    print_help()
                    continue

                elif command == "/clear":
                    # Clear message history but keep system prompt
                    old_count = len(agent.messages)
                    agent.messages = [agent.messages[0]]  # Keep only system message
                    print(f"{Colors.GREEN}✅ Cleared {old_count - 1} messages, starting new session{Colors.RESET}\n")
                    continue

                elif command == "/history":
                    print(f"\n{Colors.BRIGHT_CYAN}Current session message count: {len(agent.messages)}{Colors.RESET}\n")
                    continue

                elif command == "/stats":
                    print_stats(agent, session_start)
                    continue

                elif command == "/continuity":
                    print(f"\n{Colors.BRIGHT_CYAN}📊 Continuity Status:{Colors.RESET}")
                    print(f"  Agent ID: {agent_id}")
                    print(f"  DragonflyDB: {'✅ Connected' if continuity_backend.redis else '❌ Not Connected'}")
                    print(f"  MongoDB: {'✅ Connected' if continuity_backend.mongo_events else '❌ Not Connected'}")
                    print(f"  Neo4j: {'✅ Connected' if continuity_backend.neo4j_driver else '❌ Not Connected'}")
                    print(f"  NATS: {'✅ Configured' if continuity_backend.nats_url else '❌ Not Configured'}")
                    print(f"  Current Session Started: {current_snapshot['session_start']}")
                    print(f"  Workspace: {workspace_dir}")
                    if args.project:
                        print(f"  Project: {args.project}")
                    if args.thread:
                        print(f"  Thread: {args.thread}")
                    print(f"\n{Colors.DIM}Use /snapshot to see detailed session state{Colors.RESET}\n")
                    continue

                elif command == "/snapshot":
                    print(f"\n{Colors.BRIGHT_CYAN}📸 Current Session Snapshot:{Colors.RESET}")
                    print(continuity_backend.summarize_snapshot(current_snapshot, agent_id))
                    
                    # Get recent events from Redis
                    if continuity_backend.redis:
                        try:
                            list_key = f"events:{agent_id}"
                            recent_events = continuity_backend.redis.lrange(list_key, -5, -1)
                            if recent_events:
                                print(f"\n{Colors.BRIGHT_YELLOW}Recent Events:{Colors.RESET}")
                                for event_str in recent_events:
                                    try:
                                        event = json.loads(event_str)
                                        print(f"  {event['timestamp'][:19]} | {event['type'].upper()} | {event.get('message', '')[:50]}")
                                    except:
                                        pass
                        except Exception as e:
                            print(f"{Colors.YELLOW}⚠️  Could not retrieve recent events: {e}{Colors.RESET}")
                    print("")
                    continue

                else:
                    print(f"{Colors.RED}❌ Unknown command: {user_input}{Colors.RESET}")
                    print(f"{Colors.DIM}Type /help to see available commands{Colors.RESET}\n")
                    continue

            # Normal conversation - exit check
            if user_input.lower() in ["exit", "quit", "q"]:
                # Log session end
                log_continuity_event(continuity_backend, agent_id, "system", "Session ended by user")
                print(f"\n{Colors.BRIGHT_YELLOW}👋 Goodbye! Thanks for using Nexus with Continuity{Colors.RESET}\n")
                print_stats(agent, session_start)
                
                # Save final snapshot
                current_snapshot["last_updated"] = utc_now()
                current_snapshot["session_end"] = datetime.now().isoformat()
                continuity_backend.save_snapshot(agent_id, current_snapshot)
                print(f"{Colors.GREEN}💾 Session state saved to continuity backend{Colors.RESET}")
                break

            # Log user message
            log_continuity_event(continuity_backend, agent_id, "user", user_input, args.project, args.thread, str(workspace_dir))

            # Run Agent
            print(
                f"\n{Colors.BRIGHT_BLUE}Agent{Colors.RESET} {Colors.DIM}›{Colors.RESET} {Colors.DIM}Thinking...{Colors.RESET}\n"
            )
            agent.add_user_message(user_input)
            _ = await agent.run()
            
            # Log assistant response (get last message)
            if hasattr(agent, 'messages') and len(agent.messages) > 0:
                last_message = agent.messages[-1]
                if hasattr(last_message, 'content'):
                    response_text = str(last_message.content)[:100]  # Truncate for logging
                    log_continuity_event(continuity_backend, agent_id, "assistant", response_text, args.project, args.thread, str(workspace_dir))

            # Update current snapshot
            current_snapshot["last_updated"] = utc_now()
            current_snapshot["last_cwd"] = str(workspace_dir)
            
            # Save snapshot periodically
            if len(agent.messages) % 10 == 0:  # Save every 10 messages
                continuity_backend.save_snapshot(agent_id, current_snapshot)

            # Visual separation - keep it simple like the reference code
            print(f"\n{Colors.DIM}{'─' * 60}{Colors.RESET}\n")

        except KeyboardInterrupt:
            # Log session interruption
            log_continuity_event(continuity_backend, agent_id, "system", "Session interrupted by user")
            print(f"\n\n{Colors.BRIGHT_YELLOW}👋 Interrupt signal detected, exiting...{Colors.RESET}\n")
            print_stats(agent, session_start)
            
            # Save snapshot on interruption
            current_snapshot["last_updated"] = utc_now()
            current_snapshot["session_end"] = datetime.now().isoformat()
            continuity_backend.save_snapshot(agent_id, current_snapshot)
            print(f"{Colors.GREEN}💾 Session state saved to continuity backend{Colors.RESET}")
            break

        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
            print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}\n")

    # 10. Cleanup MCP connections
    try:
        print(f"{Colors.BRIGHT_CYAN}Cleaning up MCP connections...{Colors.RESET}")
        await cleanup_mcp_connections()
        print(f"{Colors.GREEN}✅ Cleanup complete{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.YELLOW}Error during cleanup (can be ignored): {e}{Colors.RESET}\n")

def main():
    """Main entry point for CLI"""
    # Parse command line arguments
    args = parse_args()

    # Determine workspace directory
    if args.workspace:
        workspace_dir = Path(args.workspace).absolute()
    else:
        # Use current working directory
        workspace_dir = Path.cwd()

    # Ensure workspace directory exists
    workspace_dir.mkdir(parents=True, exist_ok=True)

    # Run the agent (config always loaded from package directory)
    asyncio.run(run_agent(workspace_dir, args))

if __name__ == "__main__":
    main()
