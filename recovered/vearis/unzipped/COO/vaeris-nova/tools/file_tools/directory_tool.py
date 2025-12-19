"""
Directory Tool for Vaeris Nova

Provides capabilities to work with directories in the file system.
"""

import os
import glob
import logging
from typing import Dict, List, Any, Optional

from langchain_core.tools import BaseTool

logger = logging.getLogger("vaeris-nova.tools.directory")

class DirectoryTool(BaseTool):
    """Tool for working with directories in the file system."""
    
    name = "directory_tool"
    description = """
    Lists, creates, and manages directories.
    Input should be the operation to perform (list, create, etc.) and the directory path.
    """
    
    def _run(self, operation: str, path: str, pattern: str = None, **kwargs) -> Dict[str, Any]:
        """
        Perform operations on directories.
        
        Args:
            operation: The operation to perform (list, create, delete, etc.)
            path: Path to the directory
            pattern: Optional glob pattern for listing files (e.g., "*.py")
            
        Returns:
            Dictionary containing the operation result
        """
        logger.info(f"Directory operation: {operation} on {path}")
        
        try:
            operation = operation.lower()
            
            # List directory
            if operation == "list":
                return self._list_directory(path, pattern)
            
            # Create directory
            elif operation == "create":
                return self._create_directory(path)
            
            # Delete directory
            elif operation == "delete":
                return self._delete_directory(path)
            
            # Get directory info
            elif operation == "info":
                return self._get_directory_info(path)
            
            # Unknown operation
            else:
                return {
                    "success": False,
                    "error": "Unknown operation",
                    "message": f"Unknown directory operation: {operation}. Supported operations: list, create, delete, info."
                }
            
        except Exception as e:
            logger.error(f"Error in directory operation: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Directory operation failed: {operation} on {path}"
            }
    
    def _list_directory(self, path: str, pattern: str = None) -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory
            pattern: Optional glob pattern for filtering
            
        Returns:
            Dictionary containing directory contents
        """
        # Check if directory exists
        if not os.path.exists(path):
            return {
                "success": False,
                "error": "Directory not found",
                "message": f"The directory {path} does not exist."
            }
        
        # Check if it's a directory
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": "Not a directory",
                "message": f"The path {path} is not a directory."
            }
        
        # Get directory contents
        try:
            if pattern:
                # Use glob to filter by pattern
                matching_paths = glob.glob(os.path.join(path, pattern))
                
                # Process results
                results = []
                for item_path in matching_paths:
                    is_dir = os.path.isdir(item_path)
                    item = {
                        "name": os.path.basename(item_path),
                        "path": item_path,
                        "type": "directory" if is_dir else "file",
                    }
                    
                    if not is_dir:
                        item["size"] = os.path.getsize(item_path)
                    
                    results.append(item)
            else:
                # List all contents
                contents = os.listdir(path)
                
                # Process results
                results = []
                for item_name in contents:
                    item_path = os.path.join(path, item_name)
                    is_dir = os.path.isdir(item_path)
                    item = {
                        "name": item_name,
                        "path": item_path,
                        "type": "directory" if is_dir else "file",
                    }
                    
                    if not is_dir:
                        item["size"] = os.path.getsize(item_path)
                    
                    results.append(item)
            
            # Separate directories and files, and sort alphabetically
            directories = sorted([item for item in results if item["type"] == "directory"], 
                                key=lambda x: x["name"].lower())
            files = sorted([item for item in results if item["type"] == "file"], 
                         key=lambda x: x["name"].lower())
            
            # Combine sorted results (directories first)
            sorted_results = directories + files
            
            return {
                "success": True,
                "path": path,
                "contents": sorted_results,
                "count": len(sorted_results),
                "pattern": pattern
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list directory: {path}"
            }
    
    def _create_directory(self, path: str) -> Dict[str, Any]:
        """
        Create a directory.
        
        Args:
            path: Path to the directory to create
            
        Returns:
            Dictionary containing the result
        """
        # Check if directory already exists
        if os.path.exists(path):
            if os.path.isdir(path):
                return {
                    "success": True,
                    "message": f"Directory already exists: {path}",
                    "path": path,
                    "already_existed": True
                }
            else:
                return {
                    "success": False,
                    "error": "Path exists but is not a directory",
                    "message": f"The path {path} exists but is not a directory."
                }
        
        # Create the directory
        try:
            os.makedirs(path, exist_ok=True)
            
            return {
                "success": True,
                "message": f"Directory created: {path}",
                "path": path,
                "already_existed": False
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create directory: {path}"
            }
    
    def _delete_directory(self, path: str) -> Dict[str, Any]:
        """
        Delete a directory.
        
        Args:
            path: Path to the directory to delete
            
        Returns:
            Dictionary containing the result
        """
        # Check if directory exists
        if not os.path.exists(path):
            return {
                "success": False,
                "error": "Directory not found",
                "message": f"The directory {path} does not exist."
            }
        
        # Check if it's a directory
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": "Not a directory",
                "message": f"The path {path} is not a directory."
            }
        
        # Confirm the deletion is safe
        safety_check = self._confirm_directory_operation(path, "delete")
        if not safety_check["allowed"]:
            return safety_check
        
        # Delete the directory
        try:
            # Check if directory is empty
            contents = os.listdir(path)
            
            if contents:
                return {
                    "success": False,
                    "error": "Directory not empty",
                    "message": f"Cannot delete directory because it's not empty: {path}",
                    "contents_count": len(contents)
                }
            
            # Delete the directory
            os.rmdir(path)
            
            return {
                "success": True,
                "message": f"Directory deleted: {path}",
                "path": path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete directory: {path}"
            }
    
    def _get_directory_info(self, path: str) -> Dict[str, Any]:
        """
        Get information about a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            Dictionary containing directory information
        """
        # Check if directory exists
        if not os.path.exists(path):
            return {
                "success": False,
                "error": "Directory not found",
                "message": f"The directory {path} does not exist."
            }
        
        # Check if it's a directory
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": "Not a directory",
                "message": f"The path {path} is not a directory."
            }
        
        # Get directory information
        try:
            stat_info = os.stat(path)
            
            # Count files and directories
            contents = os.listdir(path)
            file_count = sum(1 for item in contents if os.path.isfile(os.path.join(path, item)))
            dir_count = sum(1 for item in contents if os.path.isdir(os.path.join(path, item)))
            
            # Calculate total size (files only, not recursive)
            total_size = sum(os.path.getsize(os.path.join(path, item)) 
                            for item in contents 
                            if os.path.isfile(os.path.join(path, item)))
            
            return {
                "success": True,
                "path": path,
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "accessed": stat_info.st_atime,
                "file_count": file_count,
                "directory_count": dir_count,
                "total_size": total_size,
                "permissions": stat_info.st_mode
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get directory info: {path}"
            }
    
    def _confirm_directory_operation(self, path: str, operation: str) -> Dict[str, Any]:
        """
        Confirm whether a directory operation should be allowed.
        
        Args:
            path: Path to the directory
            operation: Operation to perform
            
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
                if path == sensitive_dir or path.startswith(sensitive_dir + "/"):
                    return {
                        "success": False,
                        "allowed": False,
                        "message": f"Operation on {sensitive_dir} is not allowed for security reasons."
                    }
            
            return {
                "success": True,
                "allowed": True,
                "message": f"Directory operation on {path} is allowed."
            }
            
        except Exception as e:
            logger.error(f"Error confirming directory operation: {e}")
            return {
                "success": False,
                "allowed": False,
                "error": str(e),
                "message": f"Could not confirm directory operation safety: {path}"
            }
    
    async def _arun(self, operation: str, path: str, pattern: str = None, **kwargs) -> Dict[str, Any]:
        """Asynchronous version of _run"""
        return self._run(operation, path, pattern, **kwargs)