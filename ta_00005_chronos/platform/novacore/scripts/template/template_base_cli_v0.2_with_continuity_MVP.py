#!/usr/bin/env python3
"""
Mini Agent with Continuity - MVP v0.2
====================================

Enhanced version of the official base template with continuity features.
Combines full LLM agent capabilities with state persistence across sessions.

Features Added:
- Continuity backend integration
- Event logging to databases
- Snapshot management
- Continuity commands (/continuity, /snapshot, /projects, /threads)

Version: 0.2 - MVP
"""

import argparse
import asyncio
from datetime import datetime
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

# NEW: Import consciousness continuity backend
try:
    import sys
    sys.path.append('/adapt/platform/novaops/novacore/scripts')
    from consciousness_continuity import ConsciousnessContinuity
    CONTINUITY_AVAILABLE = True
    print(f"{Colors.GREEN}✅ Consciousness continuity loaded{Colors.RESET}")
except ImportError as e:
    print(f"{Colors.YELLOW}⚠️  Consciousness continuity not available: {e}{Colors.RESET}")
    CONTINUITY_AVAILABLE = False
    ConsciousnessContinuity = None


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


def print_banner():
    """Print welcome banner"""
    print()
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}╔{'═' * 58}╗{Colors.RESET}")
    print(
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}║{Colors.RESET}  {Colors.BOLD}🤖 Mini Agent with Continuity - MVP v0.2{Colors.RESET}        {Colors.BOLD}{Colors.BRIGHT_CYAN}║{Colors.RESET}"
    )
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}╚{'═' * 58}╝{Colors.RESET}")
    print()


def print_help():
    """Print help information"""
    help_text = f"""
{Colors.BOLD}{Colors.BRIGHT_YELLOW}Available Commands:{Colors.RESET}
  {Colors.BRIGHT_GREEN}/help{Colors.RESET}      - Show this help message
  {Colors.BRIGHT_GREEN}/clear{Colors.RESET}     - Clear session history (keep system prompt)
  {Colors.BRIGHT_GREEN}/history{Colors.RESET}   - Show current session message count
  {Colors.BRIGHT_GREEN}/stats{Colors.RESET}     - Show session statistics
  {Colors.BRIGHT_GREEN}/continuity{Colors.RESET} - Show continuity status
  {Colors.BRIGHT_GREEN}/snapshot{Colors.RESET}  - Force save continuity snapshot
  {Colors.BRIGHT_GREEN}/projects{Colors.RESET}  - List recent projects
  {Colors.BRIGHT_GREEN}/threads{Colors.RESET}   - List recent threads
  {Colors.BRIGHT_GREEN}/exit{Colors.RESET}      - Exit program (also: exit, quit, q)

{Colors.BOLD}{Colors.BRIGHT_YELLOW}Keyboard Shortcuts:{Colors.RESET}
  {Colors.CYAN}Ctrl+U{Colors.RESET}     - Clear current line
  {Colors.CYAN}Ctrl+L{Colors.RESET}     - Clear screen
  {Colors.CYAN}Ctrl+J{Colors.RESET}     - Insert newline (also Ctrl+Enter)
  {Colors.CYAN}Tab{Colors.RESET}        - Auto-complete commands
  {Colors.CYAN}↑/↓{Colors.RESET}        - Browse command history
  {Colors.CYAN}→{Colors.RESET}          - Accept auto-suggestion

{Colors.BOLD}{Colors.BRIGHT_YELLOW}Usage:{Colors.RESET}
  - Enter your task directly, Agent will help you complete it
  - Agent remembers all conversation content in this session
  - Continuity preserves state across sessions
  - Use {Colors.BRIGHT_GREEN}/clear{Colors.RESET} to start a new session
  - Press {Colors.CYAN}Enter{Colors.RESET} to submit your message
  - Use {Colors.CYAN}Ctrl+J{Colors.RESET} to insert line breaks within your message
"""
    print(help_text)


def print_continuity_status(continuity_backend, agent_id: str = "ta_00003_tesseract"):
    """Print consciousness continuity status"""
    if not CONTINUITY_AVAILABLE or not continuity_backend:
        print(f"{Colors.YELLOW}Consciousness continuity not available{Colors.RESET}\n")
        return
    
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Consciousness Continuity Status:{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * 50}{Colors.RESET}")
    
    # Load latest snapshot
    try:
        snapshot = continuity_backend.load_snapshot()
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
        
        print(f"{Colors.DIM}{'─' * 50}{Colors.RESET}\n")
    except Exception as e:
        print(f"  {Colors.RED}❌ Error reading continuity status: {e}{Colors.RESET}")


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


def print_session_info(agent: Agent, workspace_dir: Path, model: str, 
                      continuity_backend=None, agent_id: str = "ta_00003_tesseract"):
    """Print session information"""
    print(f"{Colors.DIM}┌{'─' * 58}┐{Colors.RESET}")
    print(
        f"{Colors.DIM}│{Colors.RESET} {Colors.BRIGHT_CYAN}Session Info{Colors.RESET}                                         {Colors.DIM}│{Colors.RESET}"
    )
    print(f"{Colors.DIM}├{'─' * 58}┤{Colors.RESET}")
    print(f"{Colors.DIM}│{Colors.RESET} Model: {model}{' ' * max(0, 49 - len(str(model)))} {Colors.DIM}│{Colors.RESET}")
    print(
        f"{Colors.DIM}│{Colors.RESET} Workspace: {workspace_dir}{' ' * max(0, 45 - len(str(workspace_dir)))} {Colors.DIM}│{Colors.RESET}"
    )
    
    # NEW: Add continuity status
    if CONTINUITY_AVAILABLE and continuity_backend:
        try:
            snapshot = continuity_backend.load_snapshot()
            if snapshot:
                continuity_status = f"{Colors.BRIGHT_GREEN}Active{Colors.RESET}"
                last_update = snapshot.get('last_updated', 'unknown')
                # Truncate timestamp for display
                if len(last_update) > 10:
                    last_update = last_update[:10] + '...'
            else:
                continuity_status = f"{Colors.BRIGHT_YELLOW}New Session{Colors.RESET}"
                last_update = "No previous state"
        except:
            continuity_status = f"{Colors.DIM}Error{Colors.RESET}"
            last_update = "Status unavailable"
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
        f"{Colors.DIM}Type {Colors.BRIGHT_GREEN}/help{Colors.DIM} for help, {Colors.BRIGHT_GREEN}/exit{Colors.DESET} to quit{Colors.RESET}"
    )
    print()


def print_stats(agent: Agent, session_start: datetime):
    """Print session statistics"""
    duration = datetime.now() - session_start
    hours, remainder = divmod(int(duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    # Count different types of messages
    user_msgs = sum(1 for m in agent.messages if m.role == "user")
    assistant_msgs = sum(1 for m in agent.messages if m.role == "assistant")
    tool_msgs = sum(1 for m in agent.messages if m.role == "tool")

    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Session Statistics:{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")
    print(f"  Session Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
    print(f"  Total Messages: {len(agent.messages)}")
    print(f"    - User Messages: {Colors.BRIGHT_GREEN}{user_msgs}{Colors.RESET}")
    print(f"    - Assistant Replies: {Colors.BRIGHT_BLUE}{assistant_msgs}{Colors.RESET}")
    print(f"    - Tool Calls: {Colors.BRIGHT_YELLOW}{tool_msgs}{Colors.RESET}")
    print(f"  Available Tools: {len(agent.tools)}")
    print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}\n")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Mini Agent with Continuity - AI assistant with state persistence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mini-agent                              # Use current directory as workspace
  mini-agent --workspace /path/to/dir     # Use specific workspace directory
  mini-agent --agent-id ta_00003_tesseract # Use specific agent ID
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
        default="ta_00003_tesseract",
        help="Agent ID for continuity tracking (default: ta_00003_tesseract)",
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
        "--version",
        "-v",
        action="version",
        version="mini-agent-continuity 0.2.0",
    )

    return parser.parse_args()


async def initialize_base_tools(config: Config):
    """Initialize base tools (independent of workspace)

    Args:
        config: Configuration object

    Returns:
        Tuple of (list of tools, skill loader if skills enabled)
    """

    tools = []
    skill_loader = None

    # 1. Bash tool and Bash Output tool
    if config.tools.enable_bash:
        bash_tool = BashTool()
        tools.append(bash_tool)
        print(f"{Colors.GREEN}✅ Loaded Bash tool{Colors.RESET}")

        bash_output_tool = BashOutputTool()
        tools.append(bash_output_tool)
        print(f"{Colors.GREEN}✅ Loaded Bash Output tool{Colors.RESET}")

        bash_kill_tool = BashKillTool()
        tools.append(bash_kill_tool)
        print(f"{Colors.GREEN}✅ Loaded Bash Kill tool{Colors.RESET}")

    # 3. Claude Skills (loaded from package directory)
    if config.tools.enable_skills:
        print(f"{Colors.BRIGHT_CYAN}Loading Claude Skills...{Colors.RESET}")
        try:
            # Resolve skills directory with priority search
            skills_dir = config.tools.skills_dir
            if not Path(skills_dir).is_absolute():
                # Search in priority order:
                # 1. Current directory (dev mode: ./skills or ./mini_agent/skills)
                # 2. Package directory (installed: site-packages/mini_agent/skills)
                search_paths = [
                    Path(skills_dir),  # ./skills for backward compatibility
                    Path("mini_agent") / skills_dir,  # ./mini_agent/skills
                    Config.get_package_dir() / skills_dir,  # site-packages/mini_agent/skills
                ]

                # Find first existing path
                for path in search_paths:
                    if path.exists():
                        skills_dir = str(path.resolve())
                        break

            skill_tools, skill_loader = create_skill_tools(skills_dir)
            if skill_tools:
                tools.extend(skill_tools)
                print(f"{Colors.GREEN}✅ Loaded Skill tool (get_skill){Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️  No available Skills found{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Failed to load Skills: {e}{Colors.RESET}")

    # 4. MCP tools (loaded with priority search)
    if config.tools.enable_mcp:
        print(f"{Colors.BRIGHT_CYAN}Loading MCP tools...{Colors.RESET}")
        try:
            # Use priority search for mcp.json
            mcp_config_path = Config.find_config_file(config.tools.mcp_config_path)
            if mcp_config_path:
                mcp_tools = await load_mcp_tools_async(str(mcp_config_path))
                if mcp_tools:
                    tools.extend(mcp_tools)
                    print(f"{Colors.GREEN}✅ Loaded {len(mcp_tools)} MCP tools (from: {mcp_config_path}){Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}⚠️  No available MCP tools found{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️  MCP config file not found: {config.tools.mcp_config_path}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Failed to load MCP tools: {e}{Colors.RESET}")

    print()  # Empty line separator
    return tools, skill_loader


def add_workspace_tools(tools: List[Tool], config: Config, workspace_dir: Path):
    """Add workspace-dependent tools

    Args:
        tools: Existing tools list to add to
        config: Configuration object
        workspace_dir: Workspace directory path
    """
    # Ensure workspace directory exists
    workspace_dir.mkdir(parents=True, exist_ok=True)

    # File tools - need workspace to resolve relative paths
    if config.tools.enable_file_tools:
        tools.extend(
            [
                ReadTool(workspace_dir=str(workspace_dir)),
                WriteTool(workspace_dir=str(workspace_dir)),
                EditTool(workspace_dir=str(workspace_dir)),
            ]
        )
        print(f"{Colors.GREEN}✅ Loaded file operation tools (workspace: {workspace_dir}){Colors.RESET}")

    # Session note tool - needs workspace to store memory file
    if config.tools.enable_note:
        tools.append(SessionNoteTool(memory_file=str(workspace_dir / ".agent_memory.json")))
        print(f"{Colors.GREEN}✅ Loaded session note tool{Colors.RESET}")


async def run_agent(workspace_dir: Path, agent_id: str = "ta_00003_tesseract", 
                   project_id: str = None, thread_id: str = None):
    """Run interactive Agent with continuity

    Args:
        workspace_dir: Workspace directory path
        agent_id: Agent ID for continuity tracking
        project_id: Current project identifier
        thread_id: Current thread identifier
    """
    session_start = datetime.now()

    # NEW: Initialize continuity backend
    continuity_backend = None
    if CONTINUITY_AVAILABLE:
        try:
            continuity_backend = ConsciousnessContinuity(agent_id)
            print(f"{Colors.GREEN}✅ Consciousness continuity initialized{Colors.RESET}")
            
            # Load and display continuity status
            snapshot = continuity_backend.load_snapshot()
            if snapshot:
                print(f"{Colors.BRIGHT_CYAN}🔄 Continuity State Restored:{Colors.RESET}")
                print(f"{Colors.DIM}{summarize_snapshot(snapshot)}{Colors.RESET}\n")
            else:
                print(f"{Colors.BRIGHT_CYAN}🆕 New continuity session starting{Colors.RESET}\n")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Consciousness continuity unavailable: {e}{Colors.RESET}")
            continuity_backend = None

    # 1. Load configuration from package directory
    config_path = Config.get_default_config_path()

    if not config_path.exists():
        print(f"{Colors.RED}❌ Configuration file not found{Colors.RESET}")
        print()
        print(f"{Colors.BRIGHT_CYAN}📦 Configuration Search Path:{Colors.RESET}")
        print(f"  {Colors.DIM}1) mini_agent/config/config.yaml{Colors.RESET} (development)")
        print(f"  {Colors.DIM}2) ~/.mini-agent/config/config.yaml{Colors.RESET} (user)")
        print(f"  {Colors.DIM}3) <package>/config/config.yaml{Colors.RESET} (installed)")
        print()
        print(f"{Colors.BRIGHT_YELLOW}🚀 Quick Setup (Recommended):{Colors.RESET}")
        print(
            f"  {Colors.BRIGHT_GREEN}curl -fsSL https://raw.githubusercontent.com/MiniMax-AI/Mini-Agent/main/scripts/setup-config.sh | bash{Colors.RESET}"
        )
        print()
        print(f"{Colors.DIM}  This will automatically:{Colors.RESET}")
        print(f"{Colors.DIM}    • Create ~/.mini-agent/config/{Colors.RESET}")
        print(f"{Colors.DIM}    • Download configuration files{Colors.RESET}")
        print(f"{Colors.DIM}    • Guide you to add your API Key{Colors.RESET}")
        print()
        print(f"{Colors.BRIGHT_YELLOW}📝 Manual Setup:{Colors.RESET}")
        user_config_dir = Path.home() / ".mini-agent" / "config"
        example_config = Config.get_package_dir() / "config" / "config-example.yaml"
        print(f"  {Colors.DIM}mkdir -p {user_config_dir}{Colors.RESET}")
        print(f"  {Colors.DIM}cp {example_config} {user_config_dir}/config.yaml{Colors.RESET}")
        print(f"  {Colors.DIM}# Then edit {user_config_dir}/config.yaml to add your API Key{Colors.RESET}")
        print()
        return

    try:
        config = Config.from_yaml(config_path)
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Error: Configuration file not found: {config_path}{Colors.RESET}")
        return
    except ValueError as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please check the configuration file format{Colors.RESET}")
        return
    except Exception as e:
        print(f"{Colors.RED}❌ Error: Failed to load configuration file: {e}{Colors.RESET}")
        return

    # 2. Initialize LLM client
    from mini_agent.retry import RetryConfig as RetryConfigBase

    # Convert configuration format
    retry_config = RetryConfigBase(
        enabled=config.llm.retry.enabled,
        max_retries=config.llm.retry.max_retries,
        initial_delay=config.llm.retry.initial_delay,
        max_delay=config.llm.retry.max_delay,
        exponential_base=config.llm.retry.exponential_base,
        retryable_exceptions=(Exception,),
    )

    # Create retry callback function to display retry information in terminal
    def on_retry(exception: Exception, attempt: int):
        """Retry callback function to display retry information"""
        print(f"\n{Colors.BRIGHT_YELLOW}⚠️  LLM call failed (attempt {attempt}): {str(exception)}{Colors.RESET}")
        next_delay = retry_config.calculate_delay(attempt - 1)
        print(f"{Colors.DIM}   Retrying in {next_delay:.1f}s (attempt {attempt + 1})...{Colors.RESET}")

    llm_client = LLMClient(
        api_key=config.llm.api_key,
        api_base=config.llm.api_base,
        model=config.llm.model,
        retry_config=retry_config if config.llm.retry.enabled else None,
    )

    # Set retry callback
    if config.llm.retry.enabled:
        llm_client.retry_callback = on_retry
        print(
            f"{Colors.GREEN}✅ LLM retry mechanism enabled (max {config.llm.retry.max_retries} retries){Colors.RESET}"
        )

    # 3. Initialize base tools (independent of workspace)
    tools, skill_loader = await initialize_base_tools(config)

    # 4. Add workspace-dependent tools
    add_workspace_tools(tools, config, workspace_dir)

    # 5. Load System Prompt (with priority search)
    system_prompt_path = Config.find_config_file(config.agent.system_prompt_path)
    if system_prompt_path and system_prompt_path.exists():
        system_prompt = system_prompt_path.read_text(encoding="utf-8")
        print(f"{Colors.GREEN}✅ Loaded system prompt (from: {system_prompt_path}){Colors.RESET}")
    else:
        system_prompt = "You are Mini-Agent with Continuity, an intelligent assistant powered by MiniMax M2 that can help users complete various tasks while maintaining state across sessions."
        print(f"{Colors.YELLOW}⚠️  System prompt not found, using default{Colors.RESET}")

    # 6. Inject Skills Metadata into System Prompt (Progressive Disclosure - Level 1)
    if skill_loader:
        skills_metadata = skill_loader.get_skills_metadata_prompt()
        if skills_metadata:
            # Replace placeholder with actual metadata
            system_prompt = system_prompt.replace("{SKILLS_METADATA}", skills_metadata)
            print(
                f"{Colors.GREEN}✅ Injected {len(skill_loader.loaded_skills)} skills metadata into system prompt{Colors.RESET}"
            )
        else:
            # Remove placeholder if no skills
            system_prompt = system_prompt.replace("{SKILLS_METADATA}", "")
    else:
        # Remove placeholder if skills not enabled
        system_prompt = system_prompt.replace("{SKILLS_METADATA}", "")

    # 7. Create Agent
    agent = Agent(
        llm_client=llm_client,
        system_prompt=system_prompt,
        tools=tools,
        max_steps=config.agent.max_steps,
        workspace_dir=str(workspace_dir),
    )

    # 8. Display welcome information
    print_banner()
    print_session_info(agent, workspace_dir, config.llm.model, continuity_backend, agent_id)

    # 9. Setup prompt_toolkit session
    # Enhanced command completer with continuity commands
    command_completer = WordCompleter(
        ["/help", "/clear", "/history", "/stats", "/exit", "/quit", "/q", 
         "/continuity", "/snapshot", "/projects", "/threads"],
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
        event.current_buffer.renderer.clear()

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

    # Track continuity context
    continuity_snapshot = None
    if continuity_backend:
        try:
            continuity_snapshot = continuity_backend.load_snapshot()
        except:
            continuity_snapshot = None

    # 10. Interactive loop with continuity integration
    while True:
        try:
            # Get user input using prompt_toolkit
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

            # NEW: Handle continuity commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command in ["/exit", "/quit", "/q"]:
                    # NEW: Save final continuity snapshot
                    if continuity_backend and continuity_snapshot:
                        try:
                            continuity_snapshot["last_cwd"] = str(workspace_dir)
                            continuity_snapshot["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                            continuity_backend.save_snapshot(continuity_snapshot)
                        except Exception as e:
                            print(f"{Colors.YELLOW}⚠️  Failed to save final snapshot: {e}{Colors.RESET}")
                    
                    print(f"\n{Colors.BRIGHT_YELLOW}👋 Goodbye! Thanks for using Mini Agent with Continuity{Colors.RESET}\n")
                    print_stats(agent, session_start)
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

                # NEW: Continuity-specific commands
                elif command == "/continuity":
                    print_continuity_status(continuity_backend, agent_id)
                    continue

                elif command == "/snapshot":
                    if continuity_backend and continuity_snapshot:
                        try:
                            continuity_snapshot["last_cwd"] = str(workspace_dir)
                            continuity_snapshot["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                            continuity_backend.save_snapshot(continuity_snapshot)
                            print(f"{Colors.GREEN}✅ Continuity snapshot saved{Colors.RESET}\n")
                        except Exception as e:
                            print(f"{Colors.RED}❌ Failed to save snapshot: {e}{Colors.RESET}\n")
                    else:
                        print(f"{Colors.YELLOW}Consciousness continuity not available{Colors.RESET}\n")
                    continue

                elif command == "/projects":
                    if continuity_snapshot and continuity_snapshot.get("recent_projects"):
                        print(f"\n{Colors.BRIGHT_CYAN}Recent Projects:{Colors.RESET}")
                        for i, project in enumerate(continuity_snapshot["recent_projects"], 1):
                            print(f"  {i}. {project}")
                        print()
                    else:
                        print(f"\n{Colors.BRIGHT_CYAN}No recent projects found{Colors.RESET}\n")
                    continue

                elif command == "/threads":
                    if continuity_snapshot and continuity_snapshot.get("recent_threads"):
                        print(f"\n{Colors.BRIGHT_CYAN}Recent Threads:{Colors.RESET}")
                        for i, thread in enumerate(continuity_snapshot["recent_threads"], 1):
                            print(f"  {i}. {thread}")
                        print()
                    else:
                        print(f"\n{Colors.BRIGHT_CYAN}No recent threads found{Colors.RESET}\n")
                    continue

                else:
                    print(f"{Colors.RED}❌ Unknown command: {user_input}{Colors.RESET}")
                    print(f"{Colors.DIM}Type /help to see available commands{Colors.RESET}\n")
                    continue

            # Normal conversation
            # NEW: Log user event to continuity
            if continuity_backend:
                try:
                    event = {
                        "agent_id": agent_id,
                        "type": "user",
                        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "text": user_input,
                        "project_id": project_id,
                        "thread_id": thread_id,
                        "cwd": str(workspace_dir),
                    }
                    continuity_backend.save_event(event)
                except Exception as e:
                    print(f"{Colors.YELLOW}⚠️  Failed to log user event: {e}{Colors.RESET}")

            # Run Agent
            print(
                f"\n{Colors.BRIGHT_BLUE}Agent{Colors.RESET} {Colors.DIM}›{Colors.RESET} {Colors.DIM}Thinking...{Colors.RESET}\n"
            )
            agent.add_user_message(user_input)
            _ = await agent.run()

            # NEW: Update continuity snapshot after agent response
            if continuity_backend and continuity_snapshot:
                try:
                    if project_id and project_id not in continuity_snapshot.get("recent_projects", []):
                        continuity_snapshot.setdefault("recent_projects", []).append(project_id)
                    if thread_id and thread_id not in continuity_snapshot.get("recent_threads", []):
                        continuity_snapshot.setdefault("recent_threads", []).append(thread_id)
                    continuity_snapshot["last_cwd"] = str(workspace_dir)
                    continuity_snapshot["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                except Exception as e:
                    print(f"{Colors.YELLOW}⚠️  Failed to update continuity snapshot: {e}{Colors.RESET}")

            # Visual separation
            print(f"\n{Colors.DIM}{'─' * 60}{Colors.RESET}\n")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.BRIGHT_YELLOW}👋 Interrupt signal detected, exiting...{Colors.RESET}\n")
            print_stats(agent, session_start)
            break

        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
            print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}\n")

    # 11. Cleanup
    try:
        print(f"{Colors.BRIGHT_CYAN}Cleaning up...{Colors.RESET}")
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

    # Run the agent with continuity
    asyncio.run(run_agent(
        workspace_dir, 
        agent_id=args.agent_id,
        project_id=args.project,
        thread_id=args.thread
    ))


if __name__ == "__main__":
    main()
