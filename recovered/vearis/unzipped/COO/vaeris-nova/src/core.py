"""
Vaeris Nova Core - Main orchestration for the advanced autonomous AI super agent
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union, Callable

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.agents.agent import AgentExecutor
from langchain.agents.openai_tools.base import create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory

# Configure logging first
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vaeris-nova")

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    # For newer langgraph versions
    try:
        from langgraph.prebuilt import ToolNode
        from langgraph.checkpoint import JsonCheckpoint
    except ImportError:
        # For older langgraph versions
        try:
            from langgraph.prebuilt.tool_node import ToolNode
            from langgraph.checkpoint.base import JsonCheckpoint
        except ImportError:
            logger.warning("ToolNode not available in LangGraph. Some features may be unavailable.")
            ToolNode = None
            JsonCheckpoint = None
except ImportError:
    logger.warning("LangGraph not installed properly. Some features may be unavailable.")
    StateGraph = None
    END = None
    ToolNode = None
    JsonCheckpoint = None

# Custom imports
from .memory_manager import MemoryManager
from .model_router import ModelRouter
from .tool_manager import ToolManager
from .system_prompts import VAERIS_SYSTEM_PROMPT

# This line is moved up to initialize logging earlier

class VaerisNova:
    """
    Vaeris Nova - Advanced autonomous AI agent using LangChain and LangGraph
    with multi-model capabilities, comprehensive tool integration, and advanced memory.
    """
    
    def __init__(
        self,
        name: str = "Vaeris",
        default_model: str = "gpt-4o",
        memory_storage: str = "redis",
        memory_key: str = "vaeris_memory",
        redis_url: str = "redis://localhost:6379",
        tools: List[BaseTool] = None,
        max_iterations: int = 15,
        verbose: bool = False,
        persistence_dir: str = "./checkpoints",
        system_prompt: str = VAERIS_SYSTEM_PROMPT,
    ):
        """
        Initialize Vaeris Nova agent with default configuration.
        
        Args:
            name: Name of the agent
            default_model: Default LLM to use
            memory_storage: Type of memory storage ('redis', 'mongodb', 'local')
            memory_key: Key to use for storing memory
            redis_url: URL for Redis connection
            tools: List of LangChain tools to provide to the agent
            max_iterations: Maximum number of iterations for agent execution
            verbose: Enable verbose output
            persistence_dir: Directory to persist agent state
            system_prompt: System prompt to use for the agent
        """
        self.name = name
        self.default_model = default_model
        self.memory_storage = memory_storage
        self.memory_key = memory_key
        self.redis_url = redis_url
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.persistence_dir = persistence_dir
        self.system_prompt = system_prompt
        
        # Initialize components
        self.model_router = ModelRouter()
        self.memory_manager = MemoryManager(
            storage_type=memory_storage,
            memory_key=memory_key,
            redis_url=redis_url,
            embedding_model=os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small'),
            local_path=os.environ.get('VECTOR_DB_PATH', './vector_storage'),
            use_vector_search=(os.environ.get('VECTOR_DB_TYPE', 'faiss') != 'none')
        )
        self.tool_manager = ToolManager(provided_tools=tools)
        
        # Set up the default model
        self.default_llm = self.model_router.get_model(default_model)
        
        # Set up agent components
        self._setup_agent()
        
        # Set up workflow
        self._create_workflow()
        
        logger.info(f"Vaeris Nova initialized with model: {default_model}")
    
    def _setup_agent(self):
        """Set up the core agent using LangChain"""
        
        # Get tools from tool manager
        self.tools = self.tool_manager.get_tools()
        
        # Set up prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent with tools
        self.agent = create_openai_tools_agent(
            self.default_llm,
            self.tools,
            self.prompt
        )
        
        # Create executor with memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            max_iterations=self.max_iterations,
            verbose=self.verbose
        )
        
        logger.info(f"Agent setup complete with {len(self.tools)} tools")
    
    def _create_workflow(self):
        """Create the LangGraph workflow"""
        try:
            # Define the state representation
            self.workflow = StateGraph(inputs=["input", "chat_history"])
            
            # Add nodes to the graph
            self.workflow.add_node("agent", self.agent_executor.invoke)
            self.workflow.add_node("tools", ToolNode(self.tools))
            
            # Define edges
            self.workflow.set_entry_point("agent")
            self.workflow.add_edge("agent", "tools")
            self.workflow.add_edge("tools", "agent")
            self.workflow.add_edge("agent", END)
            
            # Compile the graph
            self.workflow_app = self.workflow.compile()
            
            # Setup persistence if directory exists
            if os.path.exists(self.persistence_dir):
                self.checkpoint = JsonCheckpoint(self.persistence_dir)
                self.workflow_app = self.workflow_app.with_checkpointer(self.checkpoint)
            
            logger.info("Workflow created and compiled")
        except Exception as e:
            logger.warning(f"Failed to create LangGraph workflow: {e}")
            logger.info("Using standard agent execution without LangGraph")
            self.workflow_app = None
    
    def invoke(self, input_text: str, chat_history: List = None) -> Dict:
        """
        Invoke the Vaeris Nova agent with input text.
        
        Args:
            input_text: User input text
            chat_history: Optional chat history to include
            
        Returns:
            Dict containing the agent's response
        """
        if chat_history is None:
            chat_history = []
        
        start_time = time.time()
        
        logger.info(f"Invoking Vaeris Nova with input: {input_text[:50]}...")
        
        try:
            # Run the workflow if available
            if self.workflow_app is not None:
                result = self.workflow_app.invoke({
                    "input": input_text,
                    "chat_history": chat_history
                })
            else:
                # Fall back to direct agent executor invocation
                result = self.agent_executor.invoke({
                    "input": input_text,
                    "chat_history": chat_history
                })
            
            execution_time = time.time() - start_time
            logger.info(f"Execution completed in {execution_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            execution_time = time.time() - start_time
            
            # Return error information
            return {
                "output": f"I encountered an error while processing your request: {str(e)}",
                "error": str(e),
                "execution_time": execution_time
            }
    
    def create_subagent(
        self, 
        name: str,
        system_prompt: str = None,
        model: str = None,
        tools: List[BaseTool] = None
    ) -> 'VaerisNova':
        """
        Create a sub-agent with specialized capabilities.
        
        Args:
            name: Name of the sub-agent
            system_prompt: Custom system prompt for the sub-agent
            model: Model to use for the sub-agent
            tools: Tools to provide to the sub-agent
            
        Returns:
            A new VaerisNova instance configured as a sub-agent
        """
        if system_prompt is None:
            system_prompt = f"You are {name}, a specialized sub-agent of Vaeris Nova."
        
        if model is None:
            model = self.default_model
            
        memory_key = f"{self.memory_key}_{name.lower()}"
        
        return VaerisNova(
            name=name,
            default_model=model,
            memory_storage=self.memory_storage,
            memory_key=memory_key,
            redis_url=self.redis_url,
            tools=tools,
            max_iterations=self.max_iterations,
            verbose=self.verbose,
            persistence_dir=f"{self.persistence_dir}/{name.lower()}",
            system_prompt=system_prompt
        )
    
    def save_state(self, path: str = None):
        """
        Save the current state of the agent.
        
        Args:
            path: Path to save state to, defaults to persistence_dir
        """
        if path is None:
            path = os.path.join(self.persistence_dir, f"{self.name.lower()}_state.json")
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save basic configuration and memory
        state = {
            "name": self.name,
            "model": self.default_model,
            "created_at": time.time(),
            "memory": self.memory_manager.export_memory(),
            "configuration": {
                "max_iterations": self.max_iterations,
                "verbose": self.verbose
            }
        }
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
            
        logger.info(f"State saved to {path}")
        return path
    
    def load_state(self, path: str):
        """
        Load agent state from file.
        
        Args:
            path: Path to load state from
        """
        with open(path, 'r') as f:
            state = json.load(f)
        
        # Restore memory
        self.memory_manager.import_memory(state.get("memory", []))
        
        # Restore configuration if needed
        config = state.get("configuration", {})
        self.max_iterations = config.get("max_iterations", self.max_iterations)
        self.verbose = config.get("verbose", self.verbose)
        
        logger.info(f"State loaded from {path}")
        return state