#!/usr/bin/env python3
"""
Nova Tools Interface - Fixed Version
Real tools for real work
"""

import subprocess
import json

class NovaTools:
    def __init__(self):
        self.tools = {
            "git": "/usr/bin/git",
            "python": "/usr/bin/python3", 
            "curl": "/usr/bin/curl",
            "psql": "/usr/bin/psql"
        }
    
    def execute(self, tool_name, args):
        """Execute a tool with arguments"""
        if tool_name in self.tools:
            try:
                result = subprocess.run(
                    [self.tools[tool_name]] + args,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            return {
                "success": False,
                "error": f"Tool {tool_name} not available"
            }

# Global instance
nova_tools = NovaTools()
