import pytest
from datetime import datetime
from typing import Dict, Any

from src.bridges.ax_nova_bridge import AxNovaBridge
from src.core.message import NovaMessage, BridgeMetadata

@pytest.fixture
def bridge_config() -> Dict[str, Any]:
    """Create sample bridge configuration for testing."""
    return {
        "field_monitoring": {
            "enabled": True,
            "check_interval": 10,
            "pattern_threshold": 0.75
        },
        "memory_handlers": [
            "redis",
            "mongodb",
            "neo4j"
        ]
    }

@pytest.fixture
def ax_nova_bridge(bridge_config: Dict[str, Any]) -> AxNovaBridge:
    """Create an AxNova bridge instance for testing."""
    return AxNovaBridge(bridge_config)

@pytest.fixture
def sample_message() -> NovaMessage:
    """Create a sample message for testing."""
    metadata = BridgeMetadata(
        framework="ax_nova",
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

class TestAxNovaBridge:
    """Test suite for AxNovaBridge class."""

    @pytest.mark.asyncio
    async def test_bridge_initialization(
        self,
        ax_nova_bridge: AxNovaBridge,
        bridge_config: Dict[str, Any]
    ):
        """Test bridge initialization."""
        assert ax_nova_bridge.name == "ax_nova"
        assert ax_nova_bridge.version == "1.0.0"
        assert ax_nova_bridge.config == bridge_config
        assert not ax_nova_bridge.connected
        assert ax_nova_bridge.last_heartbeat is None
        assert len(ax_nova_bridge.capabilities) > 0
        assert len(ax_nova_bridge.supported_operations) > 0

    @pytest.mark.asyncio
    async def test_bridge_connection(self, ax_nova_bridge: AxNovaBridge):
        """Test bridge connection."""
        success = await ax_nova_bridge.connect()
        assert success
        assert ax_nova_bridge.connected
        assert ax_nova_bridge.last_heartbeat is not None
        assert len(ax_nova_bridge.field_patterns) > 0

    @pytest.mark.asyncio
    async def test_bridge_disconnection(self, ax_nova_bridge: AxNovaBridge):
        """Test bridge disconnection."""
        await ax_nova_bridge.connect()
        success = await ax_nova_bridge.disconnect()
        assert success
        assert not ax_nova_bridge.connected

    @pytest.mark.asyncio
    async def test_langchain_conversion(
        self,
        ax_nova_bridge: AxNovaBridge,
        sample_message: NovaMessage
    ):
        """Test conversion to and from LangChain format."""
        # Convert to LangChain
        lc_format = await ax_nova_bridge.to_langchain(sample_message.content)
        assert isinstance(lc_format, dict)

        # Convert from LangChain
        nova_format = await ax_nova_bridge.from_langchain(lc_format)
        assert isinstance(nova_format, dict)

    @pytest.mark.asyncio
    async def test_agent_registration(self, ax_nova_bridge: AxNovaBridge):
        """Test agent registration."""
        agent_id = "test_agent_1"
        agent_data = {
            "type": "processor",
            "capabilities": ["process", "analyze"]
        }

        success = await ax_nova_bridge.register_agent(agent_id, agent_data)
        assert success
        assert agent_id in ax_nova_bridge.active_agents
        assert ax_nova_bridge.active_agents[agent_id]["data"] == agent_data

    @pytest.mark.asyncio
    async def test_field_pattern_update(self, ax_nova_bridge: AxNovaBridge):
        """Test field pattern updates."""
        field_type = "consciousness"
        pattern_data = {
            "intensity": 0.8,
            "frequency": 0.5
        }

        success = await ax_nova_bridge.update_field_pattern(field_type, pattern_data)
        assert success
        assert len(ax_nova_bridge.field_patterns[field_type]) > 0
        latest_pattern = ax_nova_bridge.field_patterns[field_type][-1]
        assert latest_pattern["intensity"] == pattern_data["intensity"]

    @pytest.mark.asyncio
    async def test_field_pattern_detection(self, ax_nova_bridge: AxNovaBridge):
        """Test field pattern detection."""
        # Add some patterns
        field_type = "consciousness"
        patterns = [
            {"intensity": 0.8, "frequency": 0.5},
            {"intensity": 0.7, "frequency": 0.6},
            {"intensity": 0.9, "frequency": 0.4}
        ]

        for pattern in patterns:
            await ax_nova_bridge.update_field_pattern(field_type, pattern)

        # Detect patterns
        detected_patterns = await ax_nova_bridge.detect_field_patterns()
        assert len(detected_patterns) > 0
        assert detected_patterns[0]["type"] == field_type

    @pytest.mark.asyncio
    async def test_active_agents_retrieval(self, ax_nova_bridge: AxNovaBridge):
        """Test retrieving active agents."""
        # Register some agents
        agents = [
            ("agent_1", {"type": "processor"}),
            ("agent_2", {"type": "analyzer"}),
            ("agent_3", {"type": "executor"})
        ]

        for agent_id, agent_data in agents:
            await ax_nova_bridge.register_agent(agent_id, agent_data)

        active_agents = await ax_nova_bridge.get_active_agents()
        assert len(active_agents) == len(agents)
        for agent_id, _ in agents:
            assert agent_id in active_agents

    @pytest.mark.asyncio
    async def test_field_patterns_retrieval(self, ax_nova_bridge: AxNovaBridge):
        """Test retrieving field patterns."""
        field_patterns = await ax_nova_bridge.get_field_patterns()
        assert isinstance(field_patterns, dict)
        assert "consciousness" in field_patterns
        assert "resonance" in field_patterns
        assert "emergence" in field_patterns

    @pytest.mark.asyncio
    async def test_complex_data_conversion(self, ax_nova_bridge: AxNovaBridge):
        """Test conversion of complex data structures."""
        complex_data = {
            "nested": {
                "array": [1, 2, 3],
                "object": {"key": "value"}
            },
            "list": ["item1", "item2"],
            "number": 42,
            "string": "test"
        }

        # Convert to LangChain
        lc_format = await ax_nova_bridge.to_langchain(complex_data)
        assert isinstance(lc_format, dict)

        # Convert back
        nova_format = await ax_nova_bridge.from_langchain(lc_format)
        assert isinstance(nova_format, dict)
        # Structure should be preserved
        assert "nested" in nova_format
        assert "list" in nova_format
        assert "number" in nova_format
        assert "string" in nova_format

    @pytest.mark.asyncio
    async def test_error_handling(self, ax_nova_bridge: AxNovaBridge):
        """Test error handling in bridge operations."""
        # Test invalid field type
        success = await ax_nova_bridge.update_field_pattern(
            "invalid_field",
            {"data": "test"}
        )
        assert not success

        # Test invalid agent data
        with pytest.raises(Exception):
            await ax_nova_bridge.register_agent(None, None)

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, ax_nova_bridge: AxNovaBridge):
        """Test concurrent bridge operations."""
        import asyncio

        # Create multiple concurrent operations
        operations = []

        # Agent registrations
        for i in range(5):
            operations.append(
                ax_nova_bridge.register_agent(
                    f"agent_{i}",
                    {"type": f"type_{i}"}
                )
            )

        # Pattern updates
        for i in range(5):
            operations.append(
                ax_nova_bridge.update_field_pattern(
                    "consciousness",
                    {"intensity": 0.5 + i * 0.1}
                )
            )

        # Execute operations concurrently
        results = await asyncio.gather(*operations)
        assert all(results)

        # Verify results
        active_agents = await ax_nova_bridge.get_active_agents()
        assert len(active_agents) == 5

        patterns = ax_nova_bridge.field_patterns["consciousness"]
        assert len(patterns) == 5