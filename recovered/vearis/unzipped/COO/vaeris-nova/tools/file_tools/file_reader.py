"""
File Reader Tool for Vaeris Nova

Provides capabilities to read files from the file system.
"""

import os
import logging
from typing import Dict, List, Any, Optional

from langchain_core.tools import BaseTool

logger = logging.getLogger("vaeris-nova.tools.file_reader")

class FileReaderTool(BaseTool):
    """Tool for reading files from the file system."""
    
    name = "file_reader"
    description = """
    Reads the contents of a file.
    Input should be the file path to read.
    Supports additional options like line limits and offsets.
    """
    
    def _run(self, file_path: str, limit: int = None, offset: int = 0, **kwargs) -> Dict[str, Any]:
        """
        Read the contents of a file.
        
        Args:
            file_path: Path to the file to read
            limit: Maximum number of lines to read (None = all)
            offset: Line offset to start reading from
            
        Returns:
            Dictionary containing file contents or error
        """
        logger.info(f"Reading file: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File not found",
                    "message": f"The file {file_path} does not exist."
                }
            
            # Check if path is a file
            if not os.path.isfile(file_path):
                return {
                    "success": False,
                    "error": "Not a file",
                    "message": f"The path {file_path} is not a file."
                }
            
            # Get file information
            file_info = os.stat(file_path)
            file_size = file_info.st_size
            
            # Determine if file is binary
            try:
                # Try to detect if it's a binary file by reading the first 1024 bytes
                is_binary = False
                with open(file_path, 'rb') as f:
                    chunk = f.read(1024)
                    if b'\0' in chunk:  # Null bytes usually indicate binary
                        is_binary = True
            except Exception as e:
                logger.warning(f"Error detecting file type: {e}")
                is_binary = False
            
            # Handle binary files
            if is_binary:
                return {
                    "success": True,
                    "content": "<binary file>",
                    "is_binary": True,
                    "file_path": file_path,
                    "file_size": file_size,
                    "message": "This appears to be a binary file and cannot be displayed as text."
                }
            
            # Read the file
            try:
                with open(file_path, 'r') as f:
                    # Skip lines if offset is provided
                    if offset > 0:
                        for _ in range(offset):
                            next(f, None)
                    
                    # Read lines
                    if limit is not None:
                        lines = [next(f, None) for _ in range(limit)]
                        lines = [line for line in lines if line is not None]
                        has_more = len(lines) == limit and next(f, None) is not None
                    else:
                        lines = f.readlines()
                        has_more = False
                    
                    # Combine lines
                    content = ''.join(lines)
                    
                    return {
                        "success": True,
                        "content": content,
                        "file_path": file_path,
                        "file_size": file_size,
                        "offset": offset,
                        "limit": limit,
                        "has_more": has_more,
                        "line_count": len(lines)
                    }
            except UnicodeDecodeError:
                # Try again with latin-1 encoding for non-utf8 files
                with open(file_path, 'r', encoding='latin-1') as f:
                    # Skip lines if offset is provided
                    if offset > 0:
                        for _ in range(offset):
                            next(f, None)
                    
                    # Read lines
                    if limit is not None:
                        lines = [next(f, None) for _ in range(limit)]
                        lines = [line for line in lines if line is not None]
                        has_more = len(lines) == limit and next(f, None) is not None
                    else:
                        lines = f.readlines()
                        has_more = False
                    
                    # Combine lines
                    content = ''.join(lines)
                    
                    return {
                        "success": True,
                        "content": content,
                        "file_path": file_path,
                        "file_size": file_size,
                        "offset": offset,
                        "limit": limit,
                        "has_more": has_more,
                        "line_count": len(lines),
                        "encoding": "latin-1",
                        "note": "This file was read with latin-1 encoding due to non-UTF8 characters."
                    }
            
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to read file: {file_path}"
            }
    
    async def _arun(self, file_path: str, limit: int = None, offset: int = 0, **kwargs) -> Dict[str, Any]:
        """Asynchronous version of _run"""
        return self._run(file_path, limit, offset, **kwargs)