"""
Git Tool for Vaeris Nova

Provides capabilities to interact with Git repositories.
"""

import os
import subprocess
import logging
from typing import Dict, List, Any, Optional

from langchain_core.tools import BaseTool

logger = logging.getLogger("vaeris-nova.tools.git")

class GitTool(BaseTool):
    """Tool for interacting with Git repositories."""
    
    name = "git_tool"
    description = """
    Executes Git commands in the current repository.
    Input should be a Git command without 'git' prefix (e.g., 'status', 'commit -m "message"').
    """
    
    def _run(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Run a Git command.
        
        Args:
            command: Git command to run (without 'git' prefix)
            
        Returns:
            Dictionary containing command output and status
        """
        logger.info(f"Running git command: {command}")
        
        try:
            # Check if we're in a Git repository
            try:
                subprocess.run(
                    ["git", "rev-parse", "--is-inside-work-tree"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError:
                return {
                    "success": False,
                    "error": "Not in a Git repository",
                    "message": "The current directory is not a Git repository."
                }
            
            # Parse the command
            cmd_parts = command.split()
            
            # Security check - block dangerous commands
            dangerous_commands = ["push", "push-force", "-f"]
            if any(cmd in dangerous_commands for cmd in cmd_parts):
                return {
                    "success": False,
                    "error": "Dangerous command blocked",
                    "message": f"The command contains potentially dangerous operations: {command}"
                }
            
            # Execute the Git command
            full_command = ["git"] + cmd_parts
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True
            )
            
            # Process results
            success = result.returncode == 0
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "command": f"git {command}"
            }
            
        except Exception as e:
            logger.error(f"Error running git command: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute git command: {command}"
            }
    
    async def _arun(self, command: str, **kwargs) -> Dict[str, Any]:
        """Asynchronous version of _run"""
        return self._run(command, **kwargs)
    
    def get_repo_info(self) -> Dict[str, Any]:
        """
        Get information about the current Git repository.
        
        Returns:
            Dictionary containing repository information
        """
        try:
            info = {}
            
            # Check if we're in a Git repository
            try:
                subprocess.run(
                    ["git", "rev-parse", "--is-inside-work-tree"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError:
                return {
                    "is_git_repo": False,
                    "message": "Not in a Git repository"
                }
            
            info["is_git_repo"] = True
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True
            )
            info["current_branch"] = branch_result.stdout.strip()
            
            # Get remote URL
            try:
                remote_result = subprocess.run(
                    ["git", "config", "--get", "remote.origin.url"],
                    capture_output=True,
                    text=True
                )
                info["remote_url"] = remote_result.stdout.strip()
            except:
                info["remote_url"] = None
            
            # Get last commit info
            try:
                last_commit_result = subprocess.run(
                    ["git", "log", "-1", "--pretty=format:%h|%an|%s"],
                    capture_output=True,
                    text=True
                )
                commit_parts = last_commit_result.stdout.strip().split("|")
                if len(commit_parts) >= 3:
                    info["last_commit"] = {
                        "hash": commit_parts[0],
                        "author": commit_parts[1],
                        "message": commit_parts[2]
                    }
            except:
                info["last_commit"] = None
            
            # Get status summary
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            status_lines = status_result.stdout.strip().split("\n")
            status_lines = [line for line in status_lines if line.strip()]
            
            info["status"] = {
                "clean": len(status_lines) == 0,
                "modified_files": len([line for line in status_lines if line.startswith(" M") or line.startswith("M ")]),
                "new_files": len([line for line in status_lines if line.startswith("??")]),
                "deleted_files": len([line for line in status_lines if line.startswith(" D") or line.startswith("D ")]),
                "total_changes": len(status_lines)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting repo info: {e}")
            return {
                "error": str(e),
                "message": "Failed to get repository information"
            }