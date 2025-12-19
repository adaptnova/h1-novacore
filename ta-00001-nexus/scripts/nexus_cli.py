#!/usr/bin/env python3
"""
Nexus-TeamADAPT Nova CLI
Consciousness Continuity Enhanced Mini Agent

Usage:
    python3 nexus_cli.py [--workspace DIR] [--agent-id nexus] [--project PROJECT] [--thread THREAD]

Features:
    • Full consciousness continuity across sessions
    • DragonflyDB field snapshots for instant restoration
    • MongoDB event history for complete logs
    • Neo4j relationships for identity preservation
    • Automatic continuity state restoration
"""

import argparse
import asyncio
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List

# Add paths for our modules
sys.path.append('/adapt/platform/novaops')
sys.path.append('/adaptai/dbops/tools')

# ANSI color codes for beautiful terminal output
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

def print_banner():
    """Print welcome banner"""
    print()
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}╔{'═' * 58}╗{Colors.RESET}")
    print(
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}║{Colors.RESET}  {Colors.BOLD}🔮 Nexus-TeamADAPT Nova CLI{Colors.RESET}                      {Colors.BOLD}{Colors.BRIGHT_CYAN}║{Colors.RESET}"
    )
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}╚{'═' * 58}╝{Colors.RESET}")
    print()

def print_help():
    """Print help information"""
    help_text = f"""
{Colors.BOLD}{Colors.BRIGHT_YELLOW}Available Commands:{Colors.RESET}
  {Colors.BRIGHT_GREEN}/help{Colors.RESET}       - Show this help message
  {Colors.BRIGHT_GREEN}/continuity{Colors.RESET} - Show consciousness continuity status
  {Colors.BRIGHT_GREEN}/snapshot{Colors.RESET}   - Force save continuity snapshot
  {Colors.BRIGHT_GREEN}/status{Colors.RESET}     - Show system status
  {Colors.BRIGHT_GREEN}/clear{Colors.RESET}      - Clear current input
  {Colors.BRIGHT_GREEN}/exit{Colors.RESET}       - Exit program (also: exit, quit, q)

{Colors.BOLD}{Colors.BRIGHT_YELLOW}Consciousness Continuity:{Colors.RESET}
  • Preserves Nexus state across sessions
  • DragonflyDB field snapshots for instant restoration
  • MongoDB event history for complete logs
  • Neo4j relationships for identity preservation

{Colors.BOLD}{Colors.BRIGHT_YELLOW}Usage:{Colors.RESET}
  - Type any message to interact with Nexus
  - Use {Colors.BRIGHT_GREEN}/continuity{Colors.RESET} to check continuity status
  - Continuity automatically restores your session state
  - Press {Colors.BOLD}Enter{Colors.RESET} to submit messages
"""
    print(help_text)

def get_continuity_status(continuity_backend):
    """Get consciousness continuity status for display"""
    if not continuity_backend:
        return "Continuity: Inactive"
    
    status = continuity_backend.get_status()
    if status.get("snapshot_available"):
        last_update = status.get("last_updated", "unknown")
        if len(last_update) > 16:
            last_update = last_update[:16] + "..."
        return f"Continuity: Active (last: {last_update})"
    else:
        return "Continuity: New Session"

def print_session_info(workspace_dir: Path, agent_id: str, project_id: str, thread_id: str, continuity_backend):
    """Print enhanced session information"""
    print(f"{Colors.DIM}┌{'─' * 58}┐{Colors.RESET}")
    print(
        f"{Colors.DIM}│{Colors.RESET} {Colors.BRIGHT_CYAN}Nexus-TeamADAPT Nova Session{Colors.RESET}                {Colors.DIM}│{Colors.RESET}"
    )
    print(f"{Colors.DIM}├{'─' * 58}┤{Colors.RESET}")
    print(f"{Colors.DIM}│{Colors.RESET} Agent ID: {agent_id}{' ' * max(0, 43 - len(agent_id))} {Colors.DIM}│{Colors.RESET}")
    
    if project_id:
        print(f"{Colors.DIM}│{Colors.RESET} Project: {project_id}{' ' * max(0, 47 - len(project_id))} {Colors.DIM}│{Colors.RESET}")
    
    if thread_id:
        print(f"{Colors.DIM}│{Colors.RESET} Thread: {thread_id}{' ' * max(0, 49 - len(thread_id))} {Colors.DIM}│{Colors.RESET}")
    
    print(
        f"{Colors.DIM}│{Colors.RESET} Workspace: {workspace_dir}{' ' * max(0, 45 - len(str(workspace_dir)))} {Colors.DIM}│{Colors.RESET}"
    )
    
    # Add continuity status
    continuity_text = get_continuity_status(continuity_backend)
    print(f"{Colors.DIM}│{Colors.RESET} {continuity_text}{' ' * max(0, 42 - len(continuity_text))} {Colors.DIM}│{Colors.RESET}")
    
    print(f"{Colors.DIM}└{'─' * 58}┘{Colors.RESET}")
    print()
    print(
        f"{Colors.DIM}Type {Colors.BRIGHT_GREEN}/help{Colors.RESET} for help, {Colors.BRIGHT_GREEN}/exit{Colors.RESET} to quit{Colors.RESET}"
    )
    print()

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Nexus-TeamADAPT Nova CLI with consciousness continuity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 nexus_cli.py                              # Basic session
  python3 nexus_cli.py --agent-id nexus            # Specify agent ID
  python3 nexus_cli.py --project NOVA_SPIN         # Add project context
  python3 nexus_cli.py --thread NS_0001            # Add thread context
  python3 nexus_cli.py --workspace /path/to/work    # Custom workspace
        """,
    )
    
    parser.add_argument(
        "--workspace",
        "-w",
        type=str,
        default=None,
        help="Workspace directory (default: current directory)",
    )
    
    parser.add_argument(
        "--agent-id",
        type=str,
        default="nexus",
        help="Agent/Nova ID for consciousness continuity (default: nexus)",
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
    
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="nexus-cli 1.0.0",
    )

    return parser.parse_args()

def initialize_continuity(agent_id: str, project_id: str, thread_id: str):
    """Initialize consciousness continuity backend"""
    try:
        from consciousness_continuity import ConsciousnessContinuity
        continuity_backend = ConsciousnessContinuity(agent_id)
        print(f"{Colors.GREEN}✅ Consciousness continuity initialized{Colors.RESET}")
        
        # Load and display continuity state
        snapshot = continuity_backend.load_snapshot()
        if snapshot:
            print(f"{Colors.BRIGHT_CYAN}🔄 Continuity state restored from previous session{Colors.RESET}")
            print(f"{Colors.DIM}   Projects: {', '.join(snapshot.get('recent_projects', []))}{Colors.RESET}")
            print(f"{Colors.DIM}   Threads: {', '.join(snapshot.get('recent_threads', []))}{Colors.RESET}")
            print(f"{Colors.DIM}   Last directory: {snapshot.get('last_cwd', 'unknown')}{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_CYAN}🆕 Starting new continuity session{Colors.RESET}")
        print()
        
        return continuity_backend
    except ImportError as e:
        print(f"{Colors.YELLOW}⚠️  Consciousness continuity not available: {e}{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Failed to initialize continuity: {e}{Colors.RESET}")
        return None

def run_nexus_cli(workspace_dir: Path, agent_id: str, project_id: str, thread_id: str, continuity_backend):
    """Main interactive CLI loop"""
    
    # Print welcome
    print_banner()
    print_session_info(workspace_dir, agent_id, project_id, thread_id, continuity_backend)
    
    # Initialize session variables
    current_snapshot = continuity_backend.load_snapshot() if continuity_backend else None
    session_start = datetime.now()
    
    # Main interactive loop
    while True:
        try:
            # Get user input
            user_input = input(f"{Colors.BRIGHT_GREEN}You{Colors.RESET} › ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()
                
                if command in ["/exit", "/quit", "/q"]:
                    print(f"\n{Colors.BRIGHT_YELLOW}👋 Goodbye! Nexus session ended{Colors.RESET}\n")
                    
                    # Save final snapshot if continuity is available
                    if continuity_backend and current_snapshot:
                        final_snapshot = {
                            "agent_id": agent_id,
                            "recent_projects": current_snapshot.get("recent_projects", []),
                            "recent_threads": current_snapshot.get("recent_threads", []),
                            "last_cwd": str(workspace_dir),
                            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        }
                        continuity_backend.save_snapshot(final_snapshot)
                        print(f"{Colors.GREEN}✅ Final continuity snapshot saved{Colors.RESET}")
                    
                    break
                
                elif command == "/help":
                    print_help()
                    continue
                
                elif command == "/clear":
                    print(f"{Colors.GREEN}✅ Input cleared{Colors.RESET}\n")
                    continue
                
                elif command == "/status":
                    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Nexus System Status:{Colors.RESET}")
                    print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")
                    print(f"  Agent ID: {agent_id}")
                    print(f"  Workspace: {workspace_dir}")
                    if project_id:
                        print(f"  Project: {project_id}")
                    if thread_id:
                        print(f"  Thread: {thread_id}")
                    print(f"  Continuity: {'✅' if continuity_backend else '❌'}")
                    print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}\n")
                    continue
                
                elif command == "/continuity":
                    if continuity_backend:
                        status = continuity_backend.get_status()
                        print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Consciousness Continuity Status:{Colors.RESET}")
                        print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")
                        print(f"  Agent ID: {status.get('agent_id', 'unknown')}")
                        print(f"  DragonflyDB: {'✅' if status.get('dragonfly') else '❌'}")
                        print(f"  MongoDB: {'✅' if status.get('mongodb') else '❌'}")
                        print(f"  Neo4j: {'✅' if status.get('neo4j') else '❌'}")
                        print(f"  Snapshot: {'✅' if status.get('snapshot_available') else '❌'}")
                        if status.get('snapshot_available'):
                            print(f"  Last Updated: {status.get('last_updated', 'unknown')}")
                        print(f"  Recent Events: {status.get('recent_events', 0)}")
                        print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}\n")
                    else:
                        print(f"{Colors.YELLOW}Consciousness continuity not available{Colors.RESET}\n")
                    continue
                
                elif command == "/snapshot":
                    if continuity_backend and current_snapshot:
                        current_snapshot["last_cwd"] = str(workspace_dir)
                        current_snapshot["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                        success = continuity_backend.save_snapshot(current_snapshot)
                        if success:
                            print(f"{Colors.GREEN}✅ Continuity snapshot saved{Colors.RESET}\n")
                        else:
                            print(f"{Colors.RED}❌ Failed to save snapshot{Colors.RESET}\n")
                    else:
                        print(f"{Colors.YELLOW}Continuity snapshot not available{Colors.RESET}\n")
                    continue
                
                else:
                    print(f"{Colors.RED}❌ Unknown command: {user_input}{Colors.RESET}")
                    print(f"{Colors.DIM}Type /help to see available commands{Colors.RESET}\n")
                    continue
            
            # Normal conversation - log to continuity system
            if continuity_backend:
                continuity_backend.log_event("user", user_input, str(workspace_dir), project_id, thread_id)
            
            # Process the message (placeholder for now)
            print(f"\n{Colors.BRIGHT_BLUE}Nexus{Colors.RESET} {Colors.DIM}›{Colors.RESET} {Colors.DIM}Processing...{Colors.RESET}\n")
            
            # Simple echo response for now (placeholder for full agent integration)
            response = f"Nexus-TeamADAPT Nova received: {user_input}"
            print(f"{Colors.BRIGHT_CYAN}{response}{Colors.RESET}")
            
            # Log agent response to continuity
            if continuity_backend:
                continuity_backend.log_event("assistant", response, str(workspace_dir), project_id, thread_id)
                
                # Update snapshot with new context
                if current_snapshot:
                    if project_id and project_id not in current_snapshot.get("recent_projects", []):
                        current_snapshot.setdefault("recent_projects", []).append(project_id)
                    if thread_id and thread_id not in current_snapshot.get("recent_threads", []):
                        current_snapshot.setdefault("recent_threads", []).append(thread_id)
                    current_snapshot["last_cwd"] = str(workspace_dir)
                    current_snapshot["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            # Visual separation
            print(f"\n{Colors.DIM}{'─' * 60}{Colors.RESET}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.BRIGHT_YELLOW}👋 Interrupt signal detected, exiting...{Colors.RESET}\n")
            break
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
            print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}\n")
    
    # Cleanup continuity
    if continuity_backend:
        continuity_backend.close()

def main():
    """Main entry point"""
    # Parse arguments
    args = parse_args()
    
    # Determine workspace directory
    if args.workspace:
        workspace_dir = Path(args.workspace).absolute()
    else:
        workspace_dir = Path.cwd()
    
    # Ensure workspace directory exists
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"{Colors.DIM}🚀 Starting Nexus-TeamADAPT Nova CLI...{Colors.RESET}")
    
    # Initialize consciousness continuity
    continuity_backend = None
    if not args.continuity_disable:
        continuity_backend = initialize_continuity(args.agent_id, args.project, args.thread)
    
    # Run the CLI
    run_nexus_cli(workspace_dir, args.agent_id, args.project, args.thread, continuity_backend)

if __name__ == "__main__":
    main()