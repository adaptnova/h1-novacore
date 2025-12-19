"""
Code Analysis Tool for Vaeris Nova

Provides capabilities to analyze code quality, detect bugs, and optimize performance.
"""

import os
import subprocess
import logging
from typing import Dict, List, Any, Optional

from langchain_core.tools import BaseTool, StructuredTool, Tool

logger = logging.getLogger("vaeris-nova.tools.code_analysis")

class CodeAnalysisTool(BaseTool):
    """Tool for analyzing code quality, detecting bugs, and suggesting optimizations."""
    
    name = "code_analysis"
    description = """
    Analyzes code for quality, bugs, and performance issues.
    Inputs should include the code to analyze and the language.
    """
    
    def _run(self, code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
        """
        Run code analysis on the provided code.
        
        Args:
            code: The code to analyze
            language: The programming language of the code
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Running code analysis for {language} code")
        
        try:
            # Basic structure for result
            result = {
                "issues": [],
                "suggestions": [],
                "complexity": {},
                "summary": ""
            }
            
            # Python-specific analysis
            if language.lower() == "python":
                return self._analyze_python(code)
            
            # JavaScript/TypeScript analysis
            elif language.lower() in ["javascript", "typescript", "js", "ts"]:
                return self._analyze_js(code)
            
            # Default generic analysis
            else:
                # Basic analysis like line count, function count, etc.
                lines = code.split("\n")
                result["complexity"]["line_count"] = len(lines)
                result["complexity"]["character_count"] = len(code)
                result["complexity"]["average_line_length"] = sum(len(line) for line in lines) / len(lines) if lines else 0
                
                result["summary"] = f"Basic analysis completed for {language} code."
                
            return result
            
        except Exception as e:
            logger.error(f"Error in code analysis: {e}")
            return {
                "error": str(e),
                "message": "Failed to analyze code"
            }
    
    def _analyze_python(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Analysis results
        """
        result = {
            "issues": [],
            "suggestions": [],
            "complexity": {},
            "summary": ""
        }
        
        try:
            # Write code to temporary file
            temp_file = "/tmp/vaeris_code_analysis.py"
            with open(temp_file, "w") as f:
                f.write(code)
            
            # Run static analysis tools if available
            try:
                # Try pylint
                pylint_output = subprocess.run(
                    ["pylint", "--output-format=json", temp_file],
                    capture_output=True,
                    text=True
                )
                
                if pylint_output.returncode != 0:
                    # Parse pylint issues
                    for line in pylint_output.stdout.split("\n"):
                        if line.strip():
                            result["issues"].append(line)
            except Exception as e:
                logger.warning(f"Pylint analysis failed: {e}")
            
            # Check for common issues
            if "except:" in code and "except Exception:" not in code:
                result["issues"].append("Bare except clause detected - should catch specific exceptions")
            
            if "import *" in code:
                result["issues"].append("Wildcard import detected - may cause namespace pollution")
            
            # Check for hardcoded secrets
            secret_patterns = ["password", "secret", "api_key", "apikey", "token"]
            for pattern in secret_patterns:
                if pattern in code.lower():
                    result["issues"].append(f"Possible hardcoded secret detected with pattern: {pattern}")
            
            # Suggestions for improvement
            if "print(" in code and "def test_" in code:
                result["suggestions"].append("Consider using logging instead of print statements in tests")
            
            if "# TODO" in code or "# FIXME" in code:
                result["suggestions"].append("Code contains TODO or FIXME comments that should be addressed")
            
            # Clean up
            os.remove(temp_file)
            
            # Summarize
            result["summary"] = f"Analysis complete. Found {len(result['issues'])} issues and {len(result['suggestions'])} suggestions."
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Python code analysis: {e}")
            return {
                "error": str(e),
                "message": "Failed to analyze Python code"
            }
    
    def _analyze_js(self, code: str) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript code.
        
        Args:
            code: JS/TS code to analyze
            
        Returns:
            Analysis results
        """
        result = {
            "issues": [],
            "suggestions": [],
            "complexity": {},
            "summary": ""
        }
        
        try:
            # Write code to temporary file
            temp_file = "/tmp/vaeris_code_analysis.js"
            with open(temp_file, "w") as f:
                f.write(code)
            
            # Basic analysis
            lines = code.split("\n")
            result["complexity"]["line_count"] = len(lines)
            
            # Check for common issues
            if "console.log" in code:
                result["issues"].append("console.log statements found - should be removed in production code")
            
            if "eval(" in code:
                result["issues"].append("eval() usage detected - potential security risk")
            
            # Check for React hooks rules
            if "function" in code and "useState" in code:
                if "useEffect" in code and "}, [])" not in code and "})" in code:
                    result["issues"].append("useEffect without dependency array might cause infinite loops")
            
            # Clean up
            os.remove(temp_file)
            
            # Summarize
            result["summary"] = f"Analysis complete. Found {len(result['issues'])} issues and {len(result['suggestions'])} suggestions."
            
            return result
            
        except Exception as e:
            logger.error(f"Error in JS code analysis: {e}")
            return {
                "error": str(e),
                "message": "Failed to analyze JavaScript code"
            }
    
    async def _arun(self, code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
        """Asynchronous version of _run"""
        return self._run(code, language, **kwargs)