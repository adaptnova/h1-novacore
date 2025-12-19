import pytest
from datetime import datetime
from typing import Dict, Any

from src.bridges.autogen_bridge import AutoGenBridge
from src.core.message import NovaMessage, BridgeMetadata

@pytest.fixture
def bridge_config() -> Dict[str, Any]:
    """Create sample bridge configuration for testing."""
    return {
        "agent_configuration": {
            "max_agents": 100,
            "collaboration_threshold": 0.8,
            "adaptation_rate": 0.1
        },
        "task_execution": {
            "max_concurrent_tasks": 50,
            "task_timeout": 600,
            "retry_limit": 3
        }
    }

@pytest.fixture
def autogen_bridge(bridge_config: Dict[str, Any]) -> AutoGenBridge:
    """Create an AutoGen bridge instance for testing."""
    return AutoGenBridge(bridge_config)

@pytest.fixture
def sample_message() -> NovaMessage:
    """Create a sample message for testing."""
    metadata = BridgeMetadata(
        framework="autogen",
        version="1.0.0",
        timestamp=datetime.now(),
        operation_id="test_op_123",
        source_agent="agent_1",
        target_agent="agent_2"
    )
    return NovaMessage(
        content={"test": "content"},
        metadata=metadata,
        message_type="test_message"
    )

class TestAutoGenBridge:
    """Test suite for AutoGenBridge class."""

    @pytest.mark.asyncio
    async def test_bridge_initialization(
        self,
        autogen_bridge: AutoGenBridge,
        bridge_config: Dict[str, Any]
    ):
        """Test bridge initialization."""
        assert autogen_bridge.name == "autogen"
        assert autogen_bridge.version == "1.0.0"
        assert autogen_bridge.config == bridge_config
        assert not autogen_bridge.connected
        assert autogen_bridge.last_heartbeat is None
        assert len(autogen_bridge.capabilities) > 0
        assert len(autogen_bridge.supported_operations) > 0

    @pytest.mark.asyncio
    async def test_bridge_connection(self, autogen_bridge: AutoGenBridge):
        """Test bridge connection."""
        success = await autogen_bridge.connect()
        assert success
        assert autogen_bridge.connected
        assert autogen_bridge.last_heartbeat is not None
        assert len(autogen_bridge.learning_patterns) > 0

    @pytest.mark.asyncio
    async def test_bridge_disconnection(self, autogen_bridge: AutoGenBridge):
        """Test bridge disconnection."""
        await autogen_bridge.connect()
        success = await autogen_bridge.disconnect()
        assert success
        assert not autogen_bridge.connected

    @pytest.mark.asyncio
    async def test_langchain_conversion(
        self,
        autogen_bridge: AutoGenBridge,
        sample_message: NovaMessage
    ):
        """Test conversion to and from LangChain format."""
        # Test agent data conversion
        agent_data = {
            "agent_data": {
                "type": "autonomous",
                "capabilities": ["code", "plan", "execute"],
                "state": {"task_count": 0}
            }
        }

        # Convert to LangChain
        lc_format = await autogen_bridge.to_langchain(agent_data)
        assert isinstance(lc_format, dict)
        assert "agent_data" in lc_format

        # Convert back
        nova_format = await autogen_bridge.from_langchain(lc_format)
        assert isinstance(nova_format, dict)
        assert "agent_data" in nova_format

    @pytest.mark.asyncio
    async def test_agent_registration(self, autogen_bridge: AutoGenBridge):
        """Test agent registration."""
        agent_id = "test_agent_1"
        agent_config = {
            "type": "autonomous",
            "capabilities": ["code", "plan", "execute"],
            "learning_rate": 0.1
        }

        success = await autogen_bridge.register_agent(agent_id, agent_config)
        assert success
        assert agent_id in autogen_bridge.active_agents
        assert autogen_bridge.active_agents[agent_id]["config"] == agent_config

    @pytest.mark.asyncio
    async def test_task_execution_registration(self, autogen_bridge: AutoGenBridge):
        """Test task execution registration."""
        task_id = "test_task_1"
        task_config = {
            "type": "code_generation",
            "requirements": ["python", "web"],
            "constraints": {"max_time": 300}
        }

        success = await autogen_bridge.register_task_execution(task_id, task_config)
        assert success
        assert task_id in autogen_bridge.task_executions
        assert autogen_bridge.task_executions[task_id]["config"] == task_config

    @pytest.mark.asyncio
    async def test_learning_pattern_update(self, autogen_bridge: AutoGenBridge):
        """Test learning pattern updates."""
        pattern_type = "behavior"
        pattern_data = {
            "action": "code_generation",
            "success_rate": 0.85,
            "adaptation": {"learning_rate": 0.1}
        }

        success = await autogen_bridge.update_learning_pattern(
            pattern_type,
            pattern_data
        )
        assert success
        assert len(autogen_bridge.learning_patterns[pattern_type]) > 0
        latest_pattern = autogen_bridge.learning_patterns[pattern_type][-1]
        assert "action" in latest_pattern
        assert "success_rate" in latest_pattern

    @pytest.mark.asyncio
    async def test_collaboration_network_creation(
        self,
        autogen_bridge: AutoGenBridge
    ):
        """Test collaboration network creation."""
        network_id = "test_network_1"
        network_config = {
            "type": "task_oriented",
            "max_agents": 10,
            "collaboration_threshold": 0.7
        }

        success = await autogen_bridge.create_collaboration_network(
            network_id,
            network_config
        )
        assert success
        assert network_id in autogen_bridge.collaboration_networks
        assert autogen_bridge.collaboration_networks[network_id]["config"] == network_config

    @pytest.mark.asyncio
    async def test_active_agents_retrieval(self, autogen_bridge: AutoGenBridge):
        """Test retrieving active agents."""
        # Register some agents
        agents = [
            ("agent_1", {"type": "coder"}),
            ("agent_2", {"type": "planner"}),
            ("agent_3", {"type": "executor"})
        ]

        for agent_id, agent_config in agents:
            await autogen_bridge.register_agent(agent_id, agent_config)

        active_agents = await autogen_bridge.get_active_agents()
        assert len(active_agents) == len(agents)
        for agent_id, _ in agents:
            assert agent_id in active_agents

    @pytest.mark.asyncio
    async def test_task_executions_retrieval(self, autogen_bridge: AutoGenBridge):
        """Test retrieving task executions."""
        # Register some tasks
        tasks = [
            ("task_1", {"type": "code"}),
            ("task_2", {"type": "plan"}),
            ("task_3", {"type": "execute"})
        ]

        for task_id, task_config in tasks:
            await autogen_bridge.register_task_execution(task_id, task_config)

        task_executions = await autogen_bridge.get_task_executions()
        assert len(task_executions) == len(tasks)
        for task_id, _ in tasks:
            assert task_id in task_executions

    @pytest.mark.asyncio
    async def test_learning_patterns_retrieval(self, autogen_bridge: AutoGenBridge):
        """Test retrieving learning patterns."""
        learning_patterns = await autogen_bridge.get_learning_patterns()
        assert isinstance(learning_patterns, dict)
        assert "behavior" in learning_patterns
        assert "performance" in learning_patterns
        assert "adaptation" in learning_patterns

    @pytest.mark.asyncio
    async def test_collaboration_networks_retrieval(
        self,
        autogen_bridge: AutoGenBridge
    ):
        """Test retrieving collaboration networks."""
        # Create some networks
        networks = [
            ("network_1", {"type": "task"}),
            ("network_2", {"type": "learning"}),
            ("network_3", {"type": "adaptation"})
        ]

        for network_id, network_config in networks:
            await autogen_bridge.create_collaboration_network(
                network_id,
                network_config
            )

        collaboration_networks = await autogen_bridge.get_collaboration_networks()
        assert len(collaboration_networks) == len(networks)
        for network_id, _ in networks:
            assert network_id in collaboration_networks

    @pytest.mark.asyncio
    async def test_complex_agent_interaction(self, autogen_bridge: AutoGenBridge):
        """Test complex agent interactions and task execution."""
        # Register agents
        agent_configs = {
            "coder": {"type": "code_generation", "skills": ["python", "web"]},
            "planner": {"type": "task_planning", "skills": ["architecture", "design"]},
            "reviewer": {"type": "code_review", "skills": ["testing", "quality"]}
        }

        for agent_id, config in agent_configs.items():
            await autogen_bridge.register_agent(agent_id, config)

        # Create collaboration network
        network_id = "dev_team"
        await autogen_bridge.create_collaboration_network(
            network_id,
            {
                "type": "development",
                "agents": list(agent_configs.keys()),
                "workflow": "agile"
            }
        )

        # Register task
        task_id = "feature_development"
        await autogen_bridge.register_task_execution(
            task_id,
            {
                "type": "feature",
                "steps": ["plan", "code", "review"],
                "assignees": list(agent_configs.keys())
            }
        )

        # Verify state
        active_agents = await autogen_bridge.get_active_agents()
        assert len(active_agents) == len(agent_configs)

        networks = await autogen_bridge.get_collaboration_networks()
        assert network_id in networks

        tasks = await autogen_bridge.get_task_executions()
        assert task_id in tasks

    @pytest.mark.asyncio
    async def test_error_handling(self, autogen_bridge: AutoGenBridge):
        """Test error handling in bridge operations."""
        # Test invalid pattern type
        success = await autogen_bridge.update_learning_pattern(
            "invalid_pattern",
            {"data": "test"}
        )
        assert not success

        # Test invalid agent registration
        with pytest.raises(Exception):
            await autogen_bridge.register_agent(None, None)

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, autogen_bridge: AutoGenBridge):
        """Test concurrent bridge operations."""
        import asyncio

        # Create multiple concurrent operations
        operations = []

        # Agent registrations
        for i in range(5):
            operations.append(
                autogen_bridge.register_agent(
                    f"agent_{i}",
                    {"type": f"type_{i}"}
                )
            )

        # Task registrations
        for i in range(5):
            operations.append(
                autogen_bridge.register_task_execution(
                    f"task_{i}",
                    {"type": f"task_type_{i}"}
                )
            )

        # Execute operations concurrently
        results = await asyncio.gather(*operations)
        assert all(results)

        # Verify results
        active_agents = await autogen_bridge.get_active_agents()
        assert len(active_agents) == 5

        tasks = await autogen_bridge.get_task_executions()
        assert len(tasks) == 5