import pytest
from datetime import datetime
from typing import Dict, Any

from src.bridges.langgraph_bridge import LangGraphBridge
from src.core.message import NovaMessage, BridgeMetadata

@pytest.fixture
def bridge_config() -> Dict[str, Any]:
    """Create sample bridge configuration for testing."""
    return {
        "graph_operations": {
            "max_depth": 10,
            "cache_enabled": True,
            "cache_ttl": 300
        },
        "chain_execution": {
            "max_steps": 50,
            "timeout": 300,
            "parallel_chains": 10
        }
    }

@pytest.fixture
def langgraph_bridge(bridge_config: Dict[str, Any]) -> LangGraphBridge:
    """Create a LangGraph bridge instance for testing."""
    return LangGraphBridge(bridge_config)

@pytest.fixture
def sample_message() -> NovaMessage:
    """Create a sample message for testing."""
    metadata = BridgeMetadata(
        framework="langgraph",
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

class TestLangGraphBridge:
    """Test suite for LangGraphBridge class."""

    @pytest.mark.asyncio
    async def test_bridge_initialization(
        self,
        langgraph_bridge: LangGraphBridge,
        bridge_config: Dict[str, Any]
    ):
        """Test bridge initialization."""
        assert langgraph_bridge.name == "langgraph"
        assert langgraph_bridge.version == "1.0.0"
        assert langgraph_bridge.config == bridge_config
        assert not langgraph_bridge.connected
        assert langgraph_bridge.last_heartbeat is None
        assert len(langgraph_bridge.capabilities) > 0
        assert len(langgraph_bridge.supported_operations) > 0

    @pytest.mark.asyncio
    async def test_bridge_connection(self, langgraph_bridge: LangGraphBridge):
        """Test bridge connection."""
        success = await langgraph_bridge.connect()
        assert success
        assert langgraph_bridge.connected
        assert langgraph_bridge.last_heartbeat is not None
        assert len(langgraph_bridge.graph_patterns) > 0

    @pytest.mark.asyncio
    async def test_bridge_disconnection(self, langgraph_bridge: LangGraphBridge):
        """Test bridge disconnection."""
        await langgraph_bridge.connect()
        success = await langgraph_bridge.disconnect()
        assert success
        assert not langgraph_bridge.connected

    @pytest.mark.asyncio
    async def test_langchain_conversion(
        self,
        langgraph_bridge: LangGraphBridge,
        sample_message: NovaMessage
    ):
        """Test conversion to and from LangChain format."""
        # Test graph pattern conversion
        graph_pattern = {
            "graph_pattern": {
                "nodes": ["A", "B", "C"],
                "edges": [("A", "B"), ("B", "C")]
            }
        }

        # Convert to LangChain
        lc_format = await langgraph_bridge.to_langchain(graph_pattern)
        assert isinstance(lc_format, dict)
        assert "graph_pattern" in lc_format

        # Convert back
        nova_format = await langgraph_bridge.from_langchain(lc_format)
        assert isinstance(nova_format, dict)
        assert "graph_pattern" in nova_format

    @pytest.mark.asyncio
    async def test_chain_registration(self, langgraph_bridge: LangGraphBridge):
        """Test chain registration."""
        chain_id = "test_chain_1"
        chain_config = {
            "type": "sequential",
            "steps": ["step1", "step2", "step3"]
        }

        success = await langgraph_bridge.register_chain(chain_id, chain_config)
        assert success
        assert chain_id in langgraph_bridge.active_chains
        assert langgraph_bridge.active_chains[chain_id]["config"] == chain_config

    @pytest.mark.asyncio
    async def test_framework_connection_registration(
        self,
        langgraph_bridge: LangGraphBridge
    ):
        """Test framework connection registration."""
        framework_name = "test_framework"
        connection_config = {
            "type": "direct",
            "protocol": "http",
            "endpoint": "http://localhost:8000"
        }

        success = await langgraph_bridge.register_framework_connection(
            framework_name,
            connection_config
        )
        assert success
        assert framework_name in langgraph_bridge.framework_connections
        assert langgraph_bridge.framework_connections[framework_name]["config"] == connection_config

    @pytest.mark.asyncio
    async def test_graph_pattern_update(self, langgraph_bridge: LangGraphBridge):
        """Test graph pattern updates."""
        pattern_type = "execution"
        pattern_data = {
            "nodes": ["A", "B", "C"],
            "edges": [("A", "B"), ("B", "C")],
            "properties": {"weight": 1.0}
        }

        success = await langgraph_bridge.update_graph_pattern(
            pattern_type,
            pattern_data
        )
        assert success
        assert len(langgraph_bridge.graph_patterns[pattern_type]) > 0
        latest_pattern = langgraph_bridge.graph_patterns[pattern_type][-1]
        assert "nodes" in latest_pattern
        assert "edges" in latest_pattern

    @pytest.mark.asyncio
    async def test_active_chains_retrieval(self, langgraph_bridge: LangGraphBridge):
        """Test retrieving active chains."""
        # Register some chains
        chains = [
            ("chain_1", {"type": "sequential"}),
            ("chain_2", {"type": "parallel"}),
            ("chain_3", {"type": "conditional"})
        ]

        for chain_id, chain_config in chains:
            await langgraph_bridge.register_chain(chain_id, chain_config)

        active_chains = await langgraph_bridge.get_active_chains()
        assert len(active_chains) == len(chains)
        for chain_id, _ in chains:
            assert chain_id in active_chains

    @pytest.mark.asyncio
    async def test_framework_connections_retrieval(
        self,
        langgraph_bridge: LangGraphBridge
    ):
        """Test retrieving framework connections."""
        # Register some connections
        connections = [
            ("framework_1", {"type": "direct"}),
            ("framework_2", {"type": "proxy"}),
            ("framework_3", {"type": "gateway"})
        ]

        for framework_name, connection_config in connections:
            await langgraph_bridge.register_framework_connection(
                framework_name,
                connection_config
            )

        framework_connections = await langgraph_bridge.get_framework_connections()
        assert len(framework_connections) == len(connections)
        for framework_name, _ in connections:
            assert framework_name in framework_connections

    @pytest.mark.asyncio
    async def test_graph_patterns_retrieval(self, langgraph_bridge: LangGraphBridge):
        """Test retrieving graph patterns."""
        graph_patterns = await langgraph_bridge.get_graph_patterns()
        assert isinstance(graph_patterns, dict)
        assert "execution" in graph_patterns
        assert "coordination" in graph_patterns
        assert "synthesis" in graph_patterns

    @pytest.mark.asyncio
    async def test_complex_chain_execution(self, langgraph_bridge: LangGraphBridge):
        """Test handling of complex chain configurations."""
        chain_id = "complex_chain"
        chain_config = {
            "type": "composite",
            "components": [
                {
                    "id": "comp1",
                    "type": "sequential",
                    "steps": ["step1", "step2"]
                },
                {
                    "id": "comp2",
                    "type": "parallel",
                    "steps": ["step3", "step4"]
                }
            ],
            "connections": [
                {"from": "comp1", "to": "comp2"}
            ]
        }

        success = await langgraph_bridge.register_chain(chain_id, chain_config)
        assert success
        assert chain_id in langgraph_bridge.active_chains
        stored_config = langgraph_bridge.active_chains[chain_id]["config"]
        assert len(stored_config["components"]) == 2

    @pytest.mark.asyncio
    async def test_error_handling(self, langgraph_bridge: LangGraphBridge):
        """Test error handling in bridge operations."""
        # Test invalid pattern type
        success = await langgraph_bridge.update_graph_pattern(
            "invalid_pattern",
            {"data": "test"}
        )
        assert not success

        # Test invalid chain registration
        with pytest.raises(Exception):
            await langgraph_bridge.register_chain(None, None)

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, langgraph_bridge: LangGraphBridge):
        """Test concurrent bridge operations."""
        import asyncio

        # Create multiple concurrent operations
        operations = []

        # Chain registrations
        for i in range(5):
            operations.append(
                langgraph_bridge.register_chain(
                    f"chain_{i}",
                    {"type": f"type_{i}"}
                )
            )

        # Pattern updates
        for i in range(5):
            operations.append(
                langgraph_bridge.update_graph_pattern(
                    "execution",
                    {"nodes": [f"node_{i}"]}
                )
            )

        # Execute operations concurrently
        results = await asyncio.gather(*operations)
        assert all(results)

        # Verify results
        active_chains = await langgraph_bridge.get_active_chains()
        assert len(active_chains) == 5

        patterns = langgraph_bridge.graph_patterns["execution"]
        assert len(patterns) == 5