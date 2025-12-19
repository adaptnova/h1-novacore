"""
Tool Manager - Tool integration and management for Vaeris Nova

This module provides a comprehensive tool management system,
allowing Vaeris to use a wide range of tools with unified interfaces.
"""

import os
import logging
import importlib
import inspect
from typing import Dict, List, Any, Optional, Union, Callable

from langchain_core.tools import BaseTool, StructuredTool, Tool

# File toolkit not available in this environment
# from langchain.agent_toolkits import FileManagementToolkit

# These toolkits may not be available in the current environment
# from langchain_community.agent_toolkits import (
#     GmailToolkit,
#     SQLDatabaseToolkit,
#     VectorStoreToolkit,
#     ZapierToolkit,
#     JiraToolkit,
#     SlackToolkit,
#     OpenAPIToolkit
# )

# Path issue with relative imports, use absolute imports instead
try:
    # Import placeholder classes for custom tools since there may be issues with imports
    class CodeAnalysisTool:
        def __init__(self):
            self.name = "code_analysis"
            self.description = "Analyze code for patterns, issues, and improvements"
            
    class GitTool:
        def __init__(self):
            self.name = "git_tool"
            self.description = "Work with Git repositories"
            
    class DockerTool:
        def __init__(self):
            self.name = "docker_tool"
            self.description = "Work with Docker containers and images"
            
    class WebSearchTool:
        def __init__(self):
            self.name = "web_search"
            self.description = "Search the web for information"
            
    class WikipediaTool:
        def __init__(self):
            self.name = "wikipedia"
            self.description = "Search Wikipedia for information"
            
    class DocumentationTool:
        def __init__(self):
            self.name = "documentation"
            self.description = "Search documentation for information"
            
    class FileReaderTool:
        def __init__(self):
            self.name = "file_reader"
            self.description = "Read files from the filesystem"
            
    class FileWriterTool:
        def __init__(self):
            self.name = "file_writer"
            self.description = "Write to files on the filesystem"
            
    class DirectoryTool:
        def __init__(self):
            self.name = "directory_tool"
            self.description = "Work with directories"
            
    class SystemInfoTool:
        def __init__(self):
            self.name = "system_info"
            self.description = "Get information about the system"
            
    class ProcessManagerTool:
        def __init__(self):
            self.name = "process_manager"
            self.description = "Manage system processes"
            
    class NetworkTool:
        def __init__(self):
            self.name = "network_tool"
            self.description = "Work with networks"
            
    class DataFrameTool:
        def __init__(self):
            self.name = "dataframe_tool"
            self.description = "Work with pandas DataFrames"
            
    class JSONTool:
        def __init__(self):
            self.name = "json_tool"
            self.description = "Work with JSON data"
            
    class CSVTool:
        def __init__(self):
            self.name = "csv_tool"
            self.description = "Work with CSV data"
except Exception as e:
    logging.warning(f"Error importing tool classes: {e}")

logger = logging.getLogger("vaeris-nova.tools")

class ToolManager:
    """
    Tool Manager for Vaeris Nova with comprehensive tool integration.
    """
    
    def __init__(
        self,
        provided_tools: List[BaseTool] = None,
        enable_file_tools: bool = True,
        enable_code_tools: bool = True,
        enable_search_tools: bool = True,
        enable_system_tools: bool = True,
        enable_data_tools: bool = True,
        enable_api_tools: bool = False,
        custom_tools_path: str = None
    ):
        """
        Initialize the tool manager.
        
        Args:
            provided_tools: List of pre-initialized tools to include
            enable_file_tools: Whether to enable file management tools
            enable_code_tools: Whether to enable code analysis tools
            enable_search_tools: Whether to enable search tools
            enable_system_tools: Whether to enable system tools
            enable_data_tools: Whether to enable data manipulation tools
            enable_api_tools: Whether to enable API integration tools
            custom_tools_path: Path to directory containing custom tool definitions
        """
        self.provided_tools = provided_tools or []
        self.enable_file_tools = enable_file_tools
        self.enable_code_tools = enable_code_tools
        self.enable_search_tools = enable_search_tools
        self.enable_system_tools = enable_system_tools
        self.enable_data_tools = enable_data_tools
        self.enable_api_tools = enable_api_tools
        self.custom_tools_path = custom_tools_path
        
        # Tool collections
        self.file_tools = []
        self.code_tools = []
        self.search_tools = []
        self.system_tools = []
        self.data_tools = []
        self.api_tools = []
        self.custom_tools = []
        
        # Initialize tools
        self._initialize_tools()
        
        logger.info(f"ToolManager initialized with {len(self.get_tools())} tools")
    
    def _initialize_tools(self):
        """Initialize all enabled tool categories."""
        try:
            # Initialize file tools if enabled
            if self.enable_file_tools:
                self._initialize_file_tools()
            
            # Initialize code tools if enabled
            if self.enable_code_tools:
                self._initialize_code_tools()
            
            # Initialize search tools if enabled
            if self.enable_search_tools:
                self._initialize_search_tools()
            
            # Initialize system tools if enabled
            if self.enable_system_tools:
                self._initialize_system_tools()
            
            # Initialize data tools if enabled
            if self.enable_data_tools:
                self._initialize_data_tools()
            
            # Initialize API tools if enabled
            if self.enable_api_tools:
                self._initialize_api_tools()
            
            # Load custom tools if path provided
            if self.custom_tools_path:
                self._load_custom_tools()
            
        except Exception as e:
            logger.error(f"Error initializing tools: {e}")
    
    def _initialize_file_tools(self):
        """Initialize file management tools."""
        try:
            # Create individual file tools
            file_reader = FileReaderTool()
            file_writer = FileWriterTool()
            directory_tool = DirectoryTool()
            
            # Add to file tools collection
            self.file_tools.extend([
                file_reader,
                file_writer,
                directory_tool
            ])
            
            # File management toolkit is not available in this environment
            # try:
            #     file_toolkit = FileManagementToolkit(
            #         root_dir=os.getcwd()
            #     )
            #     self.file_tools.extend(file_toolkit.get_tools())
            # except Exception as e:
            #     logger.warning(f"Failed to initialize FileManagementToolkit: {e}")
            
            logger.info("File management toolkit not available")
            
            logger.info(f"Initialized {len(self.file_tools)} file tools")
            
        except Exception as e:
            logger.error(f"Error initializing file tools: {e}")
    
    def _initialize_code_tools(self):
        """Initialize code analysis and management tools."""
        try:
            # Create code tools
            code_analysis = CodeAnalysisTool()
            git_tool = GitTool()
            docker_tool = DockerTool()
            
            # Add to code tools collection
            self.code_tools.extend([
                code_analysis,
                git_tool,
                docker_tool
            ])
            
            logger.info(f"Initialized {len(self.code_tools)} code tools")
            
        except Exception as e:
            logger.error(f"Error initializing code tools: {e}")
    
    def _initialize_search_tools(self):
        """Initialize search and retrieval tools."""
        try:
            # Create search tools
            web_search = WebSearchTool()
            wikipedia_tool = WikipediaTool()
            documentation_tool = DocumentationTool()
            
            # Add to search tools collection
            self.search_tools.extend([
                web_search,
                wikipedia_tool,
                documentation_tool
            ])
            
            logger.info(f"Initialized {len(self.search_tools)} search tools")
            
        except Exception as e:
            logger.error(f"Error initializing search tools: {e}")
    
    def _initialize_system_tools(self):
        """Initialize system information and management tools."""
        try:
            # Create system tools
            system_info = SystemInfoTool()
            process_manager = ProcessManagerTool()
            network_tool = NetworkTool()
            
            # Add to system tools collection
            self.system_tools.extend([
                system_info,
                process_manager,
                network_tool
            ])
            
            logger.info(f"Initialized {len(self.system_tools)} system tools")
            
        except Exception as e:
            logger.error(f"Error initializing system tools: {e}")
    
    def _initialize_data_tools(self):
        """Initialize data manipulation tools."""
        try:
            # Create data tools
            dataframe_tool = DataFrameTool()
            json_tool = JSONTool()
            csv_tool = CSVTool()
            
            # Add to data tools collection
            self.data_tools.extend([
                dataframe_tool,
                json_tool,
                csv_tool
            ])
            
            logger.info(f"Initialized {len(self.data_tools)} data tools")
            
        except Exception as e:
            logger.error(f"Error initializing data tools: {e}")
    
    def _initialize_api_tools(self):
        """Initialize API integration tools."""
        try:
            # Initialize API toolkits if available
            
            # These toolkits are commented out since they're not available in the current environment
            # 
            # # Zapier toolkit
            # try:
            #     if os.environ.get("ZAPIER_NLA_API_KEY"):
            #         zapier_toolkit = ZapierToolkit()
            #         self.api_tools.extend(zapier_toolkit.get_tools())
            # except Exception as e:
            #     logger.warning(f"Failed to initialize ZapierToolkit: {e}")
            # 
            # # Jira toolkit
            # try:
            #     if all(os.environ.get(k) for k in ["JIRA_API_TOKEN", "JIRA_USERNAME", "JIRA_INSTANCE_URL"]):
            #         jira_toolkit = JiraToolkit()
            #         self.api_tools.extend(jira_toolkit.get_tools())
            # except Exception as e:
            #     logger.warning(f"Failed to initialize JiraToolkit: {e}")
            # 
            # # Slack toolkit
            # try:
            #     if os.environ.get("SLACK_BOT_TOKEN"):
            #         slack_toolkit = SlackToolkit()
            #         self.api_tools.extend(slack_toolkit.get_tools())
            # except Exception as e:
            #     logger.warning(f"Failed to initialize SlackToolkit: {e}")
            
            # Use placeholder tool to avoid empty API tools list
            api_info_tool = Tool(
                name="api_info",
                func=lambda x: "API integration is not available in the current environment.",
                description="Provides information about API integration capabilities."
            )
            self.api_tools.append(api_info_tool)
            
            logger.info(f"Initialized {len(self.api_tools)} API tools")
            
        except Exception as e:
            logger.error(f"Error initializing API tools: {e}")
    
    def _load_custom_tools(self):
        """Load custom tools from the specified directory."""
        try:
            if not os.path.exists(self.custom_tools_path):
                logger.warning(f"Custom tools path does not exist: {self.custom_tools_path}")
                return
            
            # Create a list of Python files in the directory
            tool_files = [f for f in os.listdir(self.custom_tools_path) 
                         if f.endswith('.py') and not f.startswith('__')]
            
            for file_name in tool_files:
                try:
                    # Convert file path to module path
                    module_path = os.path.join(self.custom_tools_path, file_name)
                    module_name = file_name[:-3]  # Remove .py extension
                    
                    # Import the module
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find all Tool or BaseTool subclasses in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            (issubclass(obj, BaseTool) or issubclass(obj, Tool)) and
                            obj is not BaseTool and obj is not Tool):
                            
                            # Instantiate the tool
                            try:
                                tool_instance = obj()
                                self.custom_tools.append(tool_instance)
                                logger.info(f"Loaded custom tool: {name}")
                            except Exception as e:
                                logger.warning(f"Failed to instantiate custom tool {name}: {e}")
                    
                except Exception as e:
                    logger.warning(f"Failed to load custom tool from {file_name}: {e}")
            
            logger.info(f"Loaded {len(self.custom_tools)} custom tools")
            
        except Exception as e:
            logger.error(f"Error loading custom tools: {e}")
    
    def get_tools(self) -> List[BaseTool]:
        """
        Get all available tools.
        
        Returns:
            List of all available tools
        """
        all_tools = []
        
        # Add provided tools
        all_tools.extend(self.provided_tools)
        
        # Add all tool categories
        all_tools.extend(self.file_tools)
        all_tools.extend(self.code_tools)
        all_tools.extend(self.search_tools)
        all_tools.extend(self.system_tools)
        all_tools.extend(self.data_tools)
        all_tools.extend(self.api_tools)
        all_tools.extend(self.custom_tools)
        
        # Generate a "help" tool that lists all available tools
        help_tool = StructuredTool.from_function(
            func=lambda: {
                "available_tools": [
                    {"name": tool.name, "description": tool.description}
                    for tool in all_tools
                ]
            },
            name="list_tools",
            description="Lists all available tools with their descriptions"
        )
        
        all_tools.append(help_tool)
        
        return all_tools
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """
        Get tools by category.
        
        Args:
            category: Category of tools to get ('file', 'code', 'search', 'system', 'data', 'api', 'custom')
            
        Returns:
            List of tools in the specified category
        """
        if category == "file":
            return self.file_tools
        elif category == "code":
            return self.code_tools
        elif category == "search":
            return self.search_tools
        elif category == "system":
            return self.system_tools
        elif category == "data":
            return self.data_tools
        elif category == "api":
            return self.api_tools
        elif category == "custom":
            return self.custom_tools
        else:
            logger.warning(f"Unknown tool category: {category}")
            return []
    
    def add_tool(self, tool: BaseTool, category: str = "custom"):
        """
        Add a new tool to the manager.
        
        Args:
            tool: Tool to add
            category: Category to add the tool to
        """
        if category == "file":
            self.file_tools.append(tool)
        elif category == "code":
            self.code_tools.append(tool)
        elif category == "search":
            self.search_tools.append(tool)
        elif category == "system":
            self.system_tools.append(tool)
        elif category == "data":
            self.data_tools.append(tool)
        elif category == "api":
            self.api_tools.append(tool)
        else:
            self.custom_tools.append(tool)
        
        logger.info(f"Added tool {tool.name} to category {category}")
    
    def create_tool_from_function(
        self,
        func: Callable,
        name: str = None,
        description: str = None,
        category: str = "custom"
    ) -> BaseTool:
        """
        Create a tool from a function and add it to the manager.
        
        Args:
            func: Function to create tool from
            name: Name of the tool (defaults to function name)
            description: Description of the tool
            category: Category to add the tool to
            
        Returns:
            Created tool
        """
        if name is None:
            name = func.__name__
        
        if description is None:
            description = func.__doc__ or f"Tool for {name}"
        
        # Create tool from function
        tool = StructuredTool.from_function(
            func=func,
            name=name,
            description=description
        )
        
        # Add to appropriate category
        self.add_tool(tool, category)
        
        return tool
    
    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            name: Name of the tool to get
            
        Returns:
            Tool with the specified name, or None if not found
        """
        for tool in self.get_tools():
            if tool.name == name:
                return tool
        
        logger.warning(f"Tool not found: {name}")
        return None