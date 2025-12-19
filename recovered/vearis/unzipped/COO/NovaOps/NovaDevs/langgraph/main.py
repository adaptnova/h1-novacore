"""
Main entry point for the ADAPT AI Agent System.
"""
import asyncio
import logging
import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from fastapi import FastAPI
from prometheus_client import start_http_server

# Core imports
from core.base_agent import BaseAgent
from core.config.config import config
from core.messaging.message import Message

# Executive agents
from agents.executive.supervisor_agent import SupervisorAgent
from agents.executive.compliance_agent import ComplianceAgent
from agents.executive.security_oversight_agent import SecurityOversightAgent
from agents.executive.quality_assurance_agent import QualityAssuranceAgent
from agents.executive.resource_manager_agent import ResourceManagerAgent

# Knowledge agents
from agents.knowledge.knowledge_graph_agent import KnowledgeGraphAgent
from agents.knowledge.data_analytics_agent import DataAnalyticsAgent
from agents.knowledge.research_agent import ResearchAgent
from agents.knowledge.memory_management_agent import MemoryManagementAgent
from agents.knowledge.document_processing_agent import DocumentProcessingAgent

# Integration agents
from agents.integration.atlassian_integration_agent import AtlassianIntegrationAgent
from agents.integration.slack_integration_agent import SlackIntegrationAgent
from agents.integration.github_integration_agent import GitHubIntegrationAgent
from agents.integration.database_integration_agent import DatabaseIntegrationAgent
from agents.integration.api_integration_agent import APIIntegrationAgent

# Specialized agents
from agents.specialized.llm_integration_agent import LLMIntegrationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ADAPTSystem:
    """Main ADAPT AI System coordinator."""
    
    def __init__(self):
        """Initialize the ADAPT system."""
        self.agents: Dict[str, BaseAgent] = {}
        self.app = FastAPI(title="ADAPT AI System")
        self.setup_complete = False

    async def initialize(self) -> None:
        """Initialize all system components."""
        try:
            logger.info("Initializing ADAPT AI System...")
            
            # Initialize metrics server
            if config.METRICS_ENABLED:
                start_http_server(config.PROMETHEUS_PORT)
            
            # Initialize agents
            await self._initialize_agents()
            
            # Setup API routes
            self._setup_routes()
            
            # Mark setup as complete
            self.setup_complete = True
            
            logger.info("ADAPT AI System initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ADAPT AI System: {str(e)}")
            raise

    async def _initialize_agents(self) -> None:
        """Initialize all agents in the system."""
        try:
            # Initialize executive agents
            self.agents["supervisor"] = await self._init_agent(SupervisorAgent())
            self.agents["compliance"] = await self._init_agent(ComplianceAgent())
            self.agents["security"] = await self._init_agent(SecurityOversightAgent())
            self.agents["quality"] = await self._init_agent(QualityAssuranceAgent())
            self.agents["resource"] = await self._init_agent(ResourceManagerAgent())

            # Initialize knowledge agents
            self.agents["knowledge_graph"] = await self._init_agent(KnowledgeGraphAgent())
            self.agents["data_analytics"] = await self._init_agent(DataAnalyticsAgent())
            self.agents["research"] = await self._init_agent(ResearchAgent())
            self.agents["memory"] = await self._init_agent(MemoryManagementAgent())
            self.agents["document"] = await self._init_agent(DocumentProcessingAgent())

            # Initialize integration agents
            self.agents["atlassian"] = await self._init_agent(AtlassianIntegrationAgent())
            self.agents["slack"] = await self._init_agent(SlackIntegrationAgent())
            self.agents["github"] = await self._init_agent(GitHubIntegrationAgent())
            self.agents["database"] = await self._init_agent(DatabaseIntegrationAgent())
            self.agents["api"] = await self._init_agent(APIIntegrationAgent())

            # Initialize specialized agents
            self.agents["llm"] = await self._init_agent(LLMIntegrationAgent())

            logger.info(f"Initialized {len(self.agents)} agents")

        except Exception as e:
            logger.error(f"Error initializing agents: {str(e)}")
            raise

    async def _init_agent(self, agent: BaseAgent) -> BaseAgent:
        """Initialize a single agent."""
        try:
            await agent.initialize()
            logger.info(f"Initialized agent: {agent.name}")
            return agent
        except Exception as e:
            logger.error(f"Error initializing agent {agent.name}: {str(e)}")
            raise

    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""
        @self.app.get("/")
        async def root():
            return {
                "name": "ADAPT AI System",
                "status": "operational" if self.setup_complete else "initializing",
                "agents": len(self.agents)
            }

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "agents": {
                    name: "active" 
                    for name in self.agents
                }
            }

        @self.app.get("/agents")
        async def list_agents():
            return {
                name: {
                    "capabilities": agent.capabilities,
                    "status": "active"
                }
                for name, agent in self.agents.items()
            }

        @self.app.post("/process")
        async def process_message(message: Dict[str, Any]):
            try:
                # Create message object
                msg = Message(
                    content=message.get("content"),
                    message_type=message.get("type"),
                    sender_id=message.get("sender", "api"),
                    recipient_id=message.get("recipient", "supervisor")
                )
                
                # Route message to appropriate agent
                if msg.recipient_id in self.agents:
                    response = await self.agents[msg.recipient_id].process(msg)
                    return response.content if response else {"error": "No response"}
                else:
                    return {"error": f"Unknown agent: {msg.recipient_id}"}
                    
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                return {"error": str(e)}

    async def start(self) -> None:
        """Start the ADAPT system."""
        try:
            # Initialize system
            await self.initialize()
            
            # Start background tasks
            asyncio.create_task(self._monitor_system())
            
            logger.info("ADAPT AI System started successfully")
            
        except Exception as e:
            logger.error(f"Error starting ADAPT AI System: {str(e)}")
            raise

    async def _monitor_system(self) -> None:
        """Monitor system health and performance."""
        while True:
            try:
                # Check agent health
                for name, agent in self.agents.items():
                    try:
                        status_msg = Message(
                            content={},
                            message_type="status_request",
                            sender_id="system",
                            recipient_id=name
                        )
                        response = await agent.process(status_msg)
                        if not response or "error" in response.content:
                            logger.warning(f"Agent {name} health check failed")
                    except Exception as e:
                        logger.error(f"Error checking agent {name} health: {str(e)}")

                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {str(e)}")
                await asyncio.sleep(60)

    async def shutdown(self) -> None:
        """Shutdown the ADAPT system."""
        try:
            logger.info("Shutting down ADAPT AI System...")
            
            # Shutdown agents
            for name, agent in self.agents.items():
                try:
                    logger.info(f"Shutting down agent: {name}")
                    # Add agent shutdown logic here
                except Exception as e:
                    logger.error(f"Error shutting down agent {name}: {str(e)}")
            
            logger.info("ADAPT AI System shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during system shutdown: {str(e)}")
            raise

# Create system instance
adapt_system = ADAPTSystem()

# FastAPI startup event
@adapt_system.app.on_event("startup")
async def startup_event():
    await adapt_system.start()

# FastAPI shutdown event
@adapt_system.app.on_event("shutdown")
async def shutdown_event():
    await adapt_system.shutdown()

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("API_WORKERS", "1"))
    
    # Start server
    uvicorn.run(
        "main:adapt_system.app",
        host=host,
        port=port,
        workers=workers,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
