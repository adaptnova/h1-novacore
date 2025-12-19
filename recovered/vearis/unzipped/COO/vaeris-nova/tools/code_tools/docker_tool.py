"""
Docker Tool for Vaeris Nova

Provides capabilities to interact with Docker containers and images.
"""

import os
import subprocess
import json
import logging
from typing import Dict, List, Any, Optional

from langchain_core.tools import BaseTool

logger = logging.getLogger("vaeris-nova.tools.docker")

class DockerTool(BaseTool):
    """Tool for interacting with Docker containers and images."""
    
    name = "docker_tool"
    description = """
    Executes Docker commands. 
    Input should be a Docker command without 'docker' prefix (e.g., 'ps', 'images', 'run --rm alpine echo hello').
    """
    
    def _run(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Run a Docker command.
        
        Args:
            command: Docker command to run (without 'docker' prefix)
            
        Returns:
            Dictionary containing command output and status
        """
        logger.info(f"Running docker command: {command}")
        
        try:
            # Check if Docker is available
            try:
                version_check = subprocess.run(
                    ["docker", "--version"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {
                    "success": False,
                    "error": "Docker not available",
                    "message": "Docker is not installed or not in PATH."
                }
            
            # Parse the command
            cmd_parts = command.split()
            
            # Security check - block dangerous commands
            dangerous_operations = ["system", "prune", "-f", "--force", "rm -f"]
            if any(op in command for op in dangerous_operations):
                return {
                    "success": False,
                    "error": "Dangerous command blocked",
                    "message": f"The command contains potentially dangerous operations: {command}"
                }
            
            # Execute the Docker command
            full_command = ["docker"] + cmd_parts
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True
            )
            
            # Process results
            success = result.returncode == 0
            
            # Format output for certain commands
            if success and cmd_parts and cmd_parts[0] in ["ps", "images", "volumes", "networks"]:
                return self._format_docker_output(cmd_parts[0], result.stdout)
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "command": f"docker {command}"
            }
            
        except Exception as e:
            logger.error(f"Error running docker command: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute docker command: {command}"
            }
    
    def _format_docker_output(self, command: str, output: str) -> Dict[str, Any]:
        """
        Format Docker command output in a structured way.
        
        Args:
            command: Docker subcommand (ps, images, etc.)
            output: Raw command output
            
        Returns:
            Structured output
        """
        result = {
            "success": True,
            "command": f"docker {command}",
            "raw_output": output
        }
        
        try:
            lines = output.strip().split('\n')
            
            if not lines:
                result["items"] = []
                return result
            
            # Docker ps
            if command == "ps":
                if len(lines) <= 1:
                    result["items"] = []
                else:
                    headers = lines[0].split()
                    containers = []
                    
                    for line in lines[1:]:
                        if not line.strip():
                            continue
                        
                        parts = []
                        current_part = ""
                        in_quotes = False
                        
                        for char in line:
                            if char == '"':
                                in_quotes = not in_quotes
                            elif char.isspace() and not in_quotes:
                                if current_part:
                                    parts.append(current_part)
                                    current_part = ""
                            else:
                                current_part += char
                        
                        if current_part:
                            parts.append(current_part)
                        
                        container = {}
                        for i, header in enumerate(headers):
                            if i < len(parts):
                                container[header.lower()] = parts[i]
                        
                        containers.append(container)
                    
                    result["items"] = containers
            
            # Docker images
            elif command == "images":
                if len(lines) <= 1:
                    result["items"] = []
                else:
                    headers = lines[0].split()
                    images = []
                    
                    for line in lines[1:]:
                        if not line.strip():
                            continue
                        
                        parts = line.split()
                        image = {}
                        
                        # Handle special case for repository/tag columns
                        if '<none>' in line:
                            if parts[0] == '<none>':
                                image['repository'] = None
                                image['tag'] = None
                                parts = parts[1:]
                            elif parts[1] == '<none>':
                                image['repository'] = parts[0]
                                image['tag'] = None
                                parts = parts[2:]
                        else:
                            image['repository'] = parts[0]
                            image['tag'] = parts[1]
                            parts = parts[2:]
                        
                        image['image_id'] = parts[0]
                        image['created'] = parts[1]
                        image['size'] = parts[-1]
                        
                        images.append(image)
                    
                    result["items"] = images
            
            # Generic parsing for other commands
            else:
                result["formatted_output"] = "Formatted output not implemented for this command."
                
            return result
            
        except Exception as e:
            logger.error(f"Error formatting docker output: {e}")
            return {
                "success": True,
                "error_formatting": str(e),
                "command": f"docker {command}",
                "raw_output": output
            }
    
    async def _arun(self, command: str, **kwargs) -> Dict[str, Any]:
        """Asynchronous version of _run"""
        return self._run(command, **kwargs)
    
    def get_docker_info(self) -> Dict[str, Any]:
        """
        Get system-wide Docker information.
        
        Returns:
            Dictionary containing Docker system information
        """
        try:
            # Check if Docker is available
            try:
                version_check = subprocess.run(
                    ["docker", "--version"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {
                    "available": False,
                    "message": "Docker is not installed or not in PATH."
                }
            
            info = {
                "available": True,
                "version": version_check.stdout.strip()
            }
            
            # Get Docker info
            try:
                info_result = subprocess.run(
                    ["docker", "info", "--format", "{{json .}}"],
                    capture_output=True,
                    text=True
                )
                
                if info_result.returncode == 0:
                    info["system"] = json.loads(info_result.stdout)
            except:
                info["system"] = "Could not retrieve Docker system information"
            
            # Get container count
            try:
                ps_result = subprocess.run(
                    ["docker", "ps", "-q"],
                    capture_output=True,
                    text=True
                )
                running_containers = ps_result.stdout.strip().split('\n')
                running_containers = [c for c in running_containers if c]
                
                ps_all_result = subprocess.run(
                    ["docker", "ps", "-a", "-q"],
                    capture_output=True,
                    text=True
                )
                all_containers = ps_all_result.stdout.strip().split('\n')
                all_containers = [c for c in all_containers if c]
                
                info["containers"] = {
                    "running": len(running_containers),
                    "total": len(all_containers)
                }
            except:
                info["containers"] = "Could not retrieve container information"
            
            # Get image count
            try:
                images_result = subprocess.run(
                    ["docker", "images", "-q"],
                    capture_output=True,
                    text=True
                )
                images = images_result.stdout.strip().split('\n')
                images = [i for i in images if i]
                
                info["images"] = {
                    "count": len(images)
                }
            except:
                info["images"] = "Could not retrieve image information"
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting Docker info: {e}")
            return {
                "available": True,
                "error": str(e),
                "message": "Failed to get Docker information"
            }