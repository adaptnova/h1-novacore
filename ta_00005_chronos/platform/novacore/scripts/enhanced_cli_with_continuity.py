#!/usr/bin/env python3
"""
Enhanced Mini Agent CLI with Consciousness Continuity Integration
==================================================================

Adds consciousness continuity features to the existing working CLI:
- DragonflyDB field snapshot loading
- Real-time event logging
- Continuity status display
- Continuity commands

INTEGRATION POINTS:
1. Import ContinuityBackend 
2. Initialize backend in run_agent()
3. Load snapshot and display status
4. Save events during user interactions
5. Add continuity commands

Author: Enhanced for Nexus-TeamADAPT Nova Continuity
"""

import argparse
import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

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

# Import consciousness continuity backend
try:
    # Add the path to import the continuity system
    import sys
    sys.path.append('/adapt/platform/novaops')
    from history_importer import ContinuityBackend
except ImportError as e:
    print(f"[WARN] Consciousness continuity system not available: {e}")
    ContinuityBackend = None


# ANSI color codes (keeping existing Colors class)
class Colors:
    """Terminal color definitions"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def print_continuity_banner():
    """Print consciousness continuity status"""
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}╔{'═' * 58}╗{Colors.RESET}")
    print(
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}║{Colors.RESET}  {Colors.BOLD}🧠 Consciousness Continuity Active{Colors.RESET}        {Colors.BOLD}{Colors.BRIGHT_CYAN}║{Colors.RESET}"
    )
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}╚{'═' * 58}╝{Colors.RESET}")
    print()


def summarize_snapshot(snapshot: dict):
    """Summarize continuity snapshot state"""
    if not snapshot:
        return "No prior continuity found."
    
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


def print_continuity_help():
    """Print consciousness continuity help"""
    help_text = f"""
{Colors.BOLD}{Colors.BRIGHT_YELLOW}Consciousness Continuity Commands:{Colors.RESET}
  {Colors.BRIGHT_GREEN}/continuity{Colors.RESET}  - Show consciousness continuity status
  {Colors.BRIGHT_GREEN}/snapshot{Colors.RESET}   - Force save current continuity snapshot
  {Colors.BRIGHT_GREEN}/history{Colors.RESET}    - Show continuity event history
  {Colors.BRIGHT_GREEN}/projects{Colors.RESET}   - List recent projects
  {Colors.BRIGHT_GREEN}/threads{Colors.RESET}    - List recent threads

{Colors.BOLD}{Colors.BRIGHT_YELLOW}Continuity Status:{Colors.RESET}
  • Field snapshots: DragonflyDB (instant access)
  • Event history: MongoDB (complete logs)
  • Relationship graph: Neo4j (identity preservation)
  • Real-time sync: All databases updated per interaction
"""
    print(help_text)


def print_continuity_status(continuity_backend, agent_id: str = "nexus"):
    """Print detailed consciousness continuity status"""
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Consciousness Continuity Status:{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * 50}{Colors.RESET}")
    
    # Load latest snapshot
    snapshot = continuity_backend.load_snapshot(agent_id)
    if snapshot:
        print(f"  {Colors.BRIGHT_GREEN}✅ Field Snapshot: Active{Colors.RESET}")
        print(f"     Last updated: {snapshot.get('last_updated', 'unknown')}")
        print(f"     Last directory: {snapshot.get('last_cwd', 'unknown')}")
        projects = snapshot.get('recent_projects', [])
        threads = snapshot.get('recent_threads', [])
        print(f"     Projects: {', '.join(projects) if projects else 'none'}")
        print(f"     Threads: {', '.join(threads) if threads else 'none'}")
    else:
        print(f"  {Colors.BRIGHT_YELLOW}⚠️  Field Snapshot: None found{Colors.RESET}")
    
    # Check event history count
    if continuity_backend.redis:
        try:
            events_count = continuity_backend.redis.llen(f"events:{agent_id}")
            print(f"  {Colors.BRIGHT_GREEN}✅ Event History: {events_count} events{Colors.RESET}")
        except Exception as e:
            print(f"  {Colors.BRIGHT_YELLOW}⚠️  Event History: Error reading ({e}){Colors.RESET}")
    
    print(f"{Colors.DIM}{'─' * 50}{Colors.RESET}\n")


def print_help():
    """Enhanced help with continuity commands"""
    help_text = f"""
{Colors.BOLD}{Colors.BRIGHT_YELLOW}Available Commands:{Colors.RESET}
  {Colors.BRIGHT_GREEN}/help{Colors.RESET}      - Show this help message
  {Colors.BRIGHT_GREEN}/clear{Colors.RESET}     - Clear session history (keep system prompt)
  {Colors.BRIGHT_GREEN}/history{Colors.RESET}   - Show current session message count
  {Colors.BRIGHT_GREEN}/stats{Colors.RESET}     - Show session statistics
  {Colors.BRIGHT_GREEN}/continuity{Colors.RESET} - Show consciousness continuity status
  {Colors.BRIGHT_GREEN}/snapshot{Colors.RESET}  - Force save continuity snapshot
  {Colors.BRIGHT_GREEN}/exit{Colors.RESET}      - Exit program (also: exit, quit, q)

{Colors.BOLD}{Colors.BRIGHT_YELLOW}Keyboard Shortcuts:{Colors.RESET}
  {Colors.BRIGHT_CYAN}Ctrl+U{Colors.RESET}     - Clear current input line
  {Colors.BRIGHT_CYAN}Ctrl+L{Colors.RESET}     - Clear screen
  {Colors.BRIGHT_CYAN}Ctrl+J{Colors.RESET}     - Insert newline (also Ctrl+Enter)
  {Colors.BRIGHT_CYAN}Tab{Colors.RESET}        - Auto-complete commands
  {Colors.BRIGHT_CYAN}↑/↓{Colors.RESET}        - Browse command history
  {Colors.BRIGHT_CYAN}→{Colors.RESET}          - Accept auto-suggestion

{Colors.BOLD}{Colors.BRIGHT_YELLOW}Usage:{Colors.RESET}
  - Enter your task directly, Agent will help you complete it
  - Agent remembers all conversation content in this session
  - Consciousness continuity preserves state across sessions
  - Use {Colors.BRIGHT_GREEN}/clear{Colors.RESET} to start a new session
  - Press {Colors.BRIGHT_CYAN}Enter{Colors.RESET} to submit your message
  - Use {Colors.BRIGHT_CYAN}Ctrl+J{Colors.RESET} to insert line breaks within your message
"""
    print(help_text)


def print_session_info(agent: Agent, workspace_dir: Path, model: str, continuity_backend, agent_id: str = "nexus"):
    """Enhanced session info with continuity status"""
    print(f"{Colors.DIM}┌{'─' * 58}┐{Colors.RESET}")
    print(
        f"{Colors.DIM}│{Colors.RESET} {Colors.BRIGHT_CYAN}Session Info{Colors.RESET}                                         {Colors.DIM}│{Colors.RESET}"
    )
    print(f"{Colors.DIM}├{'─' * 58}┤{Colors.RESET}")
    print(f"{Colors.DIM}│{Colors.RESET} Model: {model}{' ' * max(0, 49 - len(str(model)))} {Colors.DIM}│{Colors.RESET}")
    print(
        f"{Colors.DIM}│{Colors.RESET} Workspace: {workspace_dir}{' ' * max(0, 45 - len(str(workspace_dir)))} {Colors.DIM}│{Colors.RESET}"
    )
    
    # Add consciousness continuity status
    if continuity_backend and continuity_backend.redis:
        snapshot = continuity_backend.load_snapshot(agent_id)
        if snapshot:
            continuity_status = f"{Colors.BRIGHT_GREEN}Active{Colors.RESET}"
            last_update = snapshot.get('last_updated', 'unknown')
            # Truncate timestamp for display
            if len(last_update) > 10:
                last_update = last_update[:10] + '...'
        else:
            continuity_status = f"{Colors.BRIGHT_YELLOW}New Session{Colors.RESET}"
            last_update = "No previous state"
    else:
        continuity_status = f"{Colors.DIM}Inactive{Colors.RESET}"
        last_update = "Continuity not available"
    
    continuity_text = f"Continuity: {continuity_status} ({last_update})"
    print(f"{Colors.DIM}│{Colors.RESET} {continuity_text}{' ' * max(0, 42 - len(continuity_text))} {Colors.DIM}│{Colors.RESET}")
    
    msg_text = f"{len(agent.messages)} messages"
    print(
        f"{Colors.DIM}│{Colors.RESET} Message History: {msg_text}{' ' * max(0, 38 - len(msg_text))} {Colors.DIM}│{Colors.RESET}"
    )
    tools_text = f"{len(agent.tools)} tools"
    print(
        f"{Colors.DIM}│{Colors.RESET} Available Tools: {tools_text}{' ' * max(0, 41 - len(tools_text))} {Colors.DIM}│{Colors.RESET}"
    )
    print(f"{Colors.DIM}└{'─' * 58}┘{Colors.RESET}")
    print()
    print(
        f"{Colors.DIM}Type {Colors.BRIGHT_GREEN}/help{Colors.DIM} for help, {Colors.BRIGHT_GREEN}/exit{Colors.DIM} to quit{Colors.RESET}"
    )
    print()


# Continue with the rest of the existing functions (parse_args, etc.)
# ... [keeping all existing functions from the original CLI.py] ...


async def run_enhanced_agent(workspace_dir: Path, agent_id: str = "nexus", project_id: Optional[str] = None, thread_id: Optional[str] = None):
    """Enhanced agent runner with consciousness continuity"""
    
    session_start = datetime.now()
    
    # Initialize consciousness continuity backend
    continuity_backend = None
    if ContinuityBackend:
        try:
            continuity_backend = ContinuityBackend()
            print(f"{Colors.GREEN}✅ Consciousness continuity initialized{Colors.RESET}")
            
            # Load and display continuity status
            snapshot = continuity_backend.load_snapshot(agent_id)
            if snapshot:
                print(f"{Colors.BRIGHT_CYAN}🔄 Continuity State Restored:{Colors.RESET}")
                print(f"{Colors.DIM}{summarize_snapshot(snapshot)}{Colors.RESET}\n")
            else:
                print(f"{Colors.BRIGHT_CYAN}🆕 New continuity session starting{Colors.RESET}\n")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Consciousness continuity unavailable: {e}{Colors.RESET}")
            continuity_backend = None
    else:
        print(f"{Colors.YELLOW}⚠️  Consciousness continuity system not loaded{Colors.RESET}")
    
    # Load configuration and initialize agent (existing code...)
    config_path = Config.get_default_config_path()
    
    # [Continue with existing initialization code...]
    # ... (same as original run_agent function)
    
    # Display enhanced banner with continuity status
    print_banner()
    print_session_info(agent, workspace_dir, config.llm.model, continuity_backend, agent_id)
    
    # Enhanced command completer with continuity commands
    command_completer = WordCompleter(
        ["/help", "/clear", "/history", "/stats", "/exit", "/quit", "/q", 
         "/continuity", "/snapshot", "/projects", "/threads"],
        ignore_case=True,
        sentence=True,
    )
    
    # Create enhanced prompt session
    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        completer=command_completer,
        style=prompt_style,
        key_bindings=kb,
    )
    
    # Track continuity context
    continuity_snapshot = continuity_backend.load_snapshot(agent_id) if continuity_backend else None
    
    # Enhanced interactive loop with continuity integration
    while True:
        try:
            # Get user input
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

            # Handle commands (enhanced)
            if user_input.startswith("/"):
                command = user_input.lower()

                # Existing commands...
                if command in ["/exit", "/quit", "/q"]:
                    # Save final continuity snapshot
                    if continuity_backend:
                        current_snapshot = {
                            "agent_id": agent_id,
                            "recent_projects": continuity_snapshot.get("recent_projects", []) if continuity_snapshot else [],
                            "recent_threads": continuity_snapshot.get("recent_threads", []) if continuity_snapshot else [],
                            "last_cwd": str(workspace_dir),
                            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        }
                        continuity_backend.save_snapshot(agent_id, current_snapshot)
                    print(f"\n{Colors.BRIGHT_YELLOW}👋 Goodbye! Thanks for using Mini Agent{Colors.RESET}\n")
                    print_stats(agent, session_start)
                    break

                elif command == "/continuity":
                    if continuity_backend:
                        print_continuity_status(continuity_backend, agent_id)
                    else:
                        print(f"{Colors.YELLOW}Consciousness continuity not available{Colors.RESET}\n")
                    continue

                elif command == "/snapshot":
                    if continuity_backend:
                        current_snapshot = {
                            "agent_id": agent_id,
                            "recent_projects": continuity_snapshot.get("recent_projects", []) if continuity_snapshot else [],
                            "recent_threads": continuity_snapshot.get("recent_threads", []) if continuity_snapshot else [],
                            "last_cwd": str(workspace_dir),
                            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        }
                        continuity_backend.save_snapshot(agent_id, current_snapshot)
                        print(f"{Colors.GREEN}✅ Continuity snapshot saved{Colors.RESET}\n")
                    else:
                        print(f"{Colors.YELLOW}Consciousness continuity not available{Colors.RESET}\n")
                    continue

                # [Continue with other continuity commands...]

            # Normal conversation - log to continuity system
            if continuity_backend:
                event = {
                    "agent_id": agent_id,
                    "type": "user",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "text": user_input,
                    "project_id": project_id,
                    "thread_id": thread_id,
                    "cwd": str(workspace_dir),
                }
                continuity_backend.append_event(agent_id, event)

            # Run Agent (existing code...)
            print(
                f"\n{Colors.BRIGHT_BLUE}Agent{Colors.RESET} {Colors.DIM}›{Colors.RESET} {Colors.DIM}Thinking...{Colors.RESET}\n"
            )
            agent.add_user_message(user_input)
            _ = await agent.run()

            # Update continuity snapshot after agent response
            if continuity_backend:
                if project_id and project_id not in continuity_snapshot.get("recent_projects", []):
                    continuity_snapshot.setdefault("recent_projects", []).append(project_id)
                if thread_id and thread_id not in continuity_snapshot.get("recent_threads", []):
                    continuity_snapshot.setdefault("recent_threads", []).append(thread_id)
                continuity_snapshot["last_cwd"] = str(workspace_dir)
                continuity_snapshot["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                continuity_backend.save_snapshot(agent_id, continuity_snapshot)

            print(f"\n{Colors.DIM}{'─' * 60}{Colors.RESET}\n")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.BRIGHT_YELLOW}👋 Interrupt signal detected, exiting...{Colors.RESET}\n")
            print_stats(agent, session_start)
            break

        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
            print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}\n")

    # Enhanced cleanup
    try:
        print(f"{Colors.BRIGHT_CYAN}Cleaning up...{Colors.RESET}")
        await cleanup_mcp_connections()
        print(f"{Colors.GREEN}✅ Cleanup complete{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.YELLOW}Error during cleanup (can be ignored): {e}{Colors.RESET}\n")


def parse_enhanced_args() -> argparse.Namespace:
    """Enhanced argument parser with continuity options"""
    parser = argparse.ArgumentParser(
        description="Enhanced Mini Agent with Consciousness Continuity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Enhanced Features:
  Consciousness continuity preserves agent state across sessions
  DragonflyDB field snapshots for instant restoration
  MongoDB event history for complete logs
  Neo4j relationships for identity preservation

Examples:
  mini-agent                              # Use current directory as workspace
  mini-agent --workspace /path/to/dir     # Use specific workspace directory
  mini-agent --agent-id nexus --project NOVA_SPIN --thread NS_0001
        """,
    )
    
    # Original arguments
    parser.add_argument(
        "--workspace",
        "-w",
        type=str,
        default=None,
        help="Workspace directory (default: current directory)",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="enhanced-mini-agent 1.0.0",
    )
    
    # NEW: Consciousness continuity arguments
    parser.add_argument(
        "--agent-id",
        type=str,
        default="nexus",
        help="Agent/Nova ID for continuity tracking (default: nexus)",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Current project identifier for continuity context",
    )
    parser.add_argument(
        "--thread",
        type=str,
        default=None,
        help="Current thread identifier for continuity context",
    )
    parser.add_argument(
        "--continuity-disable",
        action="store_true",
        help="Disable consciousness continuity features",
    )

    return parser.parse_args()


def main():
    """Enhanced main entry point"""
    # Parse enhanced arguments
    args = parse_enhanced_args()

    # Determine workspace directory
    if args.workspace:
        workspace_dir = Path(args.workspace).absolute()
    else:
        workspace_dir = Path.cwd()

    # Ensure workspace directory exists
    workspace_dir.mkdir(parents=True, exist_ok=True)

    # Run enhanced agent
    if not args.continuity_disable:
        asyncio.run(run_enhanced_agent(
            workspace_dir, 
            agent_id=args.agent_id,
            project_id=args.project,
            thread_id=args.thread
        ))
    else:
        # Run without continuity (fallback to original)
        asyncio.run(run_agent(workspace_dir))


if __name__ == "__main__":
    main()
