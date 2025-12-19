"""
File Writer Tool for Vaeris Nova

Provides capabilities to write to files on the file system.
"""

import os
import logging
from typing import Dict, List, Any, Optional

from langchain_core.tools import BaseTool

logger = logging.getLogger("vaeris-nova.tools.file_writer")

class FileWriterTool(BaseTool):
    """Tool for writing content to files in the file system."""
    
    name = "file_writer"
    description = """
    Writes content to a file.
    Input should include the file path and content to write.
    Can append to existing files or create new ones.
    """
    
    def _run(self, file_path: str, content: str, append: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            append: Whether to append to the file or overwrite
            
        Returns:
            Dictionary containing success status and message
        """
        logger.info(f"Writing to file: {file_path} (append={append})")
        
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write to file
            mode = 'a' if append else 'w'
            with open(file_path, mode) as f:
                f.write(content)
            
            # Get file info for response
            file_info = os.stat(file_path)
            
            return {
                "success": True,
                "message": f"Successfully {'appended to' if append else 'wrote'} file: {file_path}",
                "file_path": file_path,
                "file_size": file_info.st_size,
                "append": append
            }
            
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to write to file: {file_path}"
            }
    
    async def _arun(self, file_path: str, content: str, append: bool = False, **kwargs) -> Dict[str, Any]:
        """Asynchronous version of _run"""
        return self._run(file_path, content, append, **kwargs)
    
    def confirm_file_operation(self, file_path: str) -> Dict[str, Any]:
        """
        Confirm whether a file operation should be allowed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary indicating whether the operation is allowed
        """
        try:
            # Check if the path is in a sensitive directory
            sensitive_dirs = [
                "/etc", 
                "/var/log", 
                "/var/spool", 
                "/usr/bin", 
                "/bin", 
                "/usr/sbin", 
                "/sbin", 
                "/boot",
                # Add other sensitive directories as needed
            ]
            
            for sensitive_dir in sensitive_dirs:
                if file_path.startswith(sensitive_dir + "/"):
                    return {
                        "allowed": False,
                        "message": f"Writing to {sensitive_dir} is not allowed for security reasons."
                    }
            
            # Check if the file exists and get info
            file_exists = os.path.exists(file_path)
            
            return {
                "allowed": True,
                "file_exists": file_exists,
                "message": f"File operation on {file_path} is allowed."
            }
            
        except Exception as e:
            logger.error(f"Error confirming file operation: {e}")
            return {
                "allowed": False,
                "error": str(e),
                "message": f"Could not confirm file operation safety: {file_path}"
            }