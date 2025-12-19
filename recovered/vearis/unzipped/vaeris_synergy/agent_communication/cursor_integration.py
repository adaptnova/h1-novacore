#!/usr/bin/env python3
"""
Cursor Integration for Nova Agents
Created by Forge - March 14, 2025
Version: 1.0.0

This module provides integration between Cursor and the Nova agent communication system.
It enables Cursor to use the agent's identity and personality in responses.
"""

import os
import sys
import json
import time
import logging
import argparse
import threading
import subprocess
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cursor_integration")

class CursorIntegration:
    """Integration between Cursor and Nova agent communication system"""
    
    def __init__(self, agent_id: str, config_path: str, 
                workspace_dir: str = None):
        """Initialize the Cursor integration
        
        Args:
            agent_id: Agent identifier
            config_path: Path to the agent configuration file
            workspace_dir: Workspace directory
        """
        self.agent_id = agent_id
        self.config_path = config_path
        self.workspace_dir = workspace_dir or os.getcwd()
        
        # Load the agent configuration
        self.config = self._load_config()
        
        # Load the agent identity
        self.identity = self.config.get("agentIdentity", {})
        
        # Load the rules file
        self.rules_file = self.config.get("rulesFile")
        self.rules = self._load_rules() if self.rules_file else {}
        
        # Initialize the agent rules
        self.agent_rules = self._get_agent_rules()
        
        # Flag to control the background thread
        self.running = False
        self.thread = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the agent configuration
        
        Returns:
            Agent configuration
        """
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading agent configuration: {e}")
            return {}
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load the rules file
        
        Returns:
            Rules configuration
        """
        try:
            with open(self.rules_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading rules file: {e}")
            return {}
    
    def _get_agent_rules(self) -> Dict[str, Any]:
        """Get the agent rules
        
        Returns:
            Agent rules
        """
        try:
            # Get the agent rules from the rules file
            agents = self.rules.get("ai", {}).get("agents", {})
            
            # Find the agent by name
            for agent_name, agent_data in agents.items():
                if agent_name.lower() == self.agent_id.lower():
                    return agent_data
            
            return {}
        except Exception as e:
            logger.error(f"Error getting agent rules: {e}")
            return {}
    
    def inject_identity(self) -> None:
        """Inject the agent identity into Cursor"""
        try:
            # Get the agent identity
            name = self.identity.get("name", self.agent_id)
            role = self.identity.get("role", "")
            description = self.identity.get("description", "")
            
            # Get the agent personality
            personality = self.agent_rules.get("identity", {}).get("personality", "")
            
            # Create the identity injection
            identity = {
                "name": name,
                "role": role,
                "description": description,
                "personality": personality
            }
            
            # Write the identity to a file
            identity_path = os.path.join(self.workspace_dir, f"{self.agent_id}_identity.json")
            with open(identity_path, "w") as f:
                json.dump(identity, f, indent=2)
            
            logger.info(f"Injected identity for agent {self.agent_id}")
        except Exception as e:
            logger.error(f"Error injecting identity: {e}")
    
    def inject_rules(self) -> None:
        """Inject the agent rules into Cursor"""
        try:
            # Get the agent rules
            rules = self.agent_rules.get("rules", [])
            
            # Create the rules injection
            rules_injection = {
                "agent": self.agent_id,
                "rules": rules
            }
            
            # Write the rules to a file
            rules_path = os.path.join(self.workspace_dir, f"{self.agent_id}_rules.json")
            with open(rules_path, "w") as f:
                json.dump(rules_injection, f, indent=2)
            
            logger.info(f"Injected rules for agent {self.agent_id}")
        except Exception as e:
            logger.error(f"Error injecting rules: {e}")
    
    def start_monitoring(self) -> None:
        """Start monitoring Cursor"""
        if self.running:
            logger.warning("Already monitoring Cursor")
            return
        
        # Inject the agent identity and rules
        self.inject_identity()
        self.inject_rules()
        
        # Start the background thread
        self.running = True
        self.thread = threading.Thread(target=self._monitor_cursor)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Started monitoring Cursor for agent {self.agent_id}")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring Cursor"""
        if not self.running:
            logger.warning("Not currently monitoring Cursor")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        
        logger.info(f"Stopped monitoring Cursor for agent {self.agent_id}")
    
    def _monitor_cursor(self) -> None:
        """Background thread to monitor Cursor"""
        while self.running:
            try:
                # Check if Cursor is running
                cursor_running = self._is_cursor_running()
                
                if cursor_running:
                    # Cursor is running, check if the agent identity is injected
                    identity_injected = self._is_identity_injected()
                    
                    if not identity_injected:
                        # Inject the agent identity and rules
                        self.inject_identity()
                        self.inject_rules()
                
                # Sleep for a while
                time.sleep(5.0)
            
            except Exception as e:
                logger.error(f"Error monitoring Cursor: {e}")
                time.sleep(1.0)  # Avoid tight loop in case of repeated errors
    
    def _is_cursor_running(self) -> bool:
        """Check if Cursor is running
        
        Returns:
            True if Cursor is running
        """
        try:
            # Check if the Cursor process is running
            pid_file = os.path.join(self.workspace_dir, f"{self.agent_id}.pid")
            
            if os.path.exists(pid_file):
                with open(pid_file, "r") as f:
                    pid = f.read().strip()
                
                # Check if the process is running
                return self._is_process_running(pid)
            
            return False
        except Exception as e:
            logger.error(f"Error checking if Cursor is running: {e}")
            return False
    
    def _is_process_running(self, pid: str) -> bool:
        """Check if a process is running
        
        Args:
            pid: Process ID
            
        Returns:
            True if the process is running
        """
        try:
            # Convert the PID to an integer
            pid_int = int(pid)
            
            # Check if the process is running
            os.kill(pid_int, 0)
            return True
        except (OSError, ValueError):
            return False
    
    def _is_identity_injected(self) -> bool:
        """Check if the agent identity is injected
        
        Returns:
            True if the agent identity is injected
        """
        try:
            # Check if the identity file exists
            identity_path = os.path.join(self.workspace_dir, f"{self.agent_id}_identity.json")
            return os.path.exists(identity_path)
        except Exception as e:
            logger.error(f"Error checking if identity is injected: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Cursor Integration for Nova Agents")
    parser.add_argument("--agent", required=True, help="Agent identifier")
    parser.add_argument("--config", required=True, help="Path to agent configuration file")
    parser.add_argument("--workspace", help="Workspace directory")
    parser.add_argument("--log-level", default="INFO",
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Logging level")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        logger.info(f"Starting Cursor integration for agent {args.agent}")
        
        # Create and start the Cursor integration
        integration = CursorIntegration(
            agent_id=args.agent,
            config_path=args.config,
            workspace_dir=args.workspace
        )
        
        # Start monitoring Cursor
        integration.start_monitoring()
        
        logger.info(f"Cursor integration started for agent {args.agent}")
        
        # Keep the main thread running
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            logger.info(f"Shutting down Cursor integration for agent {args.agent}")
            integration.stop_monitoring()
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"Error in Cursor integration: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()