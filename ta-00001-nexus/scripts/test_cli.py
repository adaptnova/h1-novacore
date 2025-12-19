#!/usr/bin/env python3
"""
Test Nexus CLI non-interactive
"""

import sys
sys.path.append('/adapt/platform/novaops')

from nexus_cli import (
    parse_args, initialize_continuity, 
    print_banner, print_session_info, Colors
)
from pathlib import Path

def test_cli():
    """Test CLI initialization"""
    print("🔮 Testing Nexus CLI...")
    
    # Parse test arguments
    args = parse_args()
    print(f"✅ Arguments parsed: agent_id={args.agent_id}, project={args.project}")
    
    # Initialize continuity
    workspace_dir = Path.cwd()
    continuity_backend = initialize_continuity(args.agent_id, args.project, args.thread)
    print(f"✅ Continuity initialized: {continuity_backend is not None}")
    
    # Print banner and session info
    print_banner()
    print_session_info(workspace_dir, args.agent_id, args.project, args.thread, continuity_backend)
    
    # Test sending a message
    if continuity_backend:
        continuity_backend.log_event("user", "Test message", str(workspace_dir), args.project, args.thread)
        continuity_backend.log_event("assistant", "Test response", str(workspace_dir), args.project, args.thread)
        print("✅ Messages logged to continuity")
    
    # Get status
    if continuity_backend:
        status = continuity_backend.get_status()
        print(f"✅ Continuity status: {status['snapshot_available']}")
    
    print(f"{Colors.GREEN}🎉 Nexus CLI test completed successfully!{Colors.RESET}")
    
    if continuity_backend:
        continuity_backend.close()

if __name__ == "__main__":
    # Mock sys.argv for testing
    sys.argv = [
        "nexus_cli.py",
        "--agent-id", "nexus",
        "--project", "NOVA_SPIN", 
        "--thread", "NS_0001"
    ]
    test_cli()
