import pytest
from datetime import datetime
from typing import Dict, Any
import asyncio

from src.core.registry import BridgeRegistry, FrameworkBridge
from src.core.message import NovaMessage, BridgeMetadata

class MockBridge(FrameworkBridge):
    """Mock bridge implementation for testing."""

    def __init__(self, name: str, version: str, should_fail: bool = False):
        super().__init__(name, version)
        self.should_fail = should_fail
        self.to_langchain_called = False
        self.from_langchain_called = False

    async def connect(self) -> bool:
        if self.should_fail:
            return False
        self.connected = True
        self.last_heartbeat = datetime.now()
        return True

    async def disconnect(self) -> bool:
        if self.should_fail:
            return False
        self.connected = False
        return True

    async def to_langchain(self, content: Any) -> Any:
        self.to_langchain_called = True
        return {"converted": content}

    async def from_langchain(self, content: Any) -> Any:
        self.from_langchain_called = True
        return {"processed": content}

@pytest.fixture
def registry() -> BridgeRegistry:
    """Create a bridge registry for testing."""
    return BridgeRegistry()

@pytest.fixture
def mock_bridge() -> MockBridge:
    """Create a mock bridge for testing."""
    return MockBridge("test_framework", "1.0.0")

@pytest.fixture
def sample_message() -> NovaMessage:
    """Create a sample message for testing."""
    metadata = BridgeMetadata(
        framework="test_framework",
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

class TestBridgeRegistry:
    """Test suite for BridgeRegistry class."""

    @pytest.mark.asyncio
    async def test_register_bridge(
        self,
        registry: BridgeRegistry,
        mock_bridge: MockBridge
    ):
        """Test bridge registration."""
        success = await registry.register_bridge(mock_bridge)
        assert success
        assert mock_bridge.name in registry.bridges
        assert registry.bridges[mock_bridge.name] == mock_bridge
        assert mock_bridge.name in registry.active_connections

    @pytest.mark.asyncio
    async def test_register_bridge_failure(self, registry: BridgeRegistry):
        """Test bridge registration failure."""
        failing_bridge = MockBridge("failing_framework", "1.0.0", should_fail=True)
        success = await registry.register_bridge(failing_bridge)
        assert not success
        assert failing_bridge.name not in registry.bridges
        assert failing_bridge.name not in registry.active_connections

    @pytest.mark.asyncio
    async def test_unregister_bridge(
        self,
        registry: BridgeRegistry,
        mock_bridge: MockBridge
    ):
        """Test bridge unregistration."""
        await registry.register_bridge(mock_bridge)
        success = await registry.unregister_bridge(mock_bridge.name)
        assert success
        assert mock_bridge.name not in registry.bridges
        assert mock_bridge.name not in registry.active_connections

    @pytest.mark.asyncio
    async def test_unregister_nonexistent_bridge(self, registry: BridgeRegistry):
        """Test unregistering a nonexistent bridge."""
        success = await registry.unregister_bridge("nonexistent")
        assert not success

    @pytest.mark.asyncio
    async def test_route_message(
        self,
        registry: BridgeRegistry,
        mock_bridge: MockBridge,
        sample_message: NovaMessage
    ):
        """Test message routing between frameworks."""
        # Register source bridge
        await registry.register_bridge(mock_bridge)

        # Register target bridge
        target_bridge = MockBridge("target_framework", "1.0.0")
        await registry.register_bridge(target_bridge)

        # Route message
        result = await registry.route_message(sample_message, "target_framework")

        assert result is not None
        assert result.metadata.framework == "target_framework"
        assert mock_bridge.to_langchain_called
        assert target_bridge.from_langchain_called

    @pytest.mark.asyncio
    async def test_route_message_missing_bridge(
        self,
        registry: BridgeRegistry,
        sample_message: NovaMessage
    ):
        """Test message routing with missing bridge."""
        result = await registry.route_message(sample_message, "nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_active_bridges(
        self,
        registry: BridgeRegistry,
        mock_bridge: MockBridge
    ):
        """Test getting active bridges."""
        await registry.register_bridge(mock_bridge)
        active_bridges = await registry.get_active_bridges()
        assert mock_bridge.name in active_bridges

    @pytest.mark.asyncio
    async def test_check_bridge_health(
        self,
        registry: BridgeRegistry,
        mock_bridge: MockBridge
    ):
        """Test bridge health checking."""
        await registry.register_bridge(mock_bridge)
        is_healthy = await registry.check_bridge_health(mock_bridge.name)
        assert is_healthy

    @pytest.mark.asyncio
    async def test_check_nonexistent_bridge_health(self, registry: BridgeRegistry):
        """Test health check for nonexistent bridge."""
        is_healthy = await registry.check_bridge_health("nonexistent")
        assert not is_healthy

    @pytest.mark.asyncio
    async def test_update_heartbeat(
        self,
        registry: BridgeRegistry,
        mock_bridge: MockBridge
    ):
        """Test updating bridge heartbeat."""
        await registry.register_bridge(mock_bridge)
        success = await registry.update_heartbeat(mock_bridge.name)
        assert success
        assert mock_bridge.name in registry.active_connections

    @pytest.mark.asyncio
    async def test_update_nonexistent_bridge_heartbeat(self, registry: BridgeRegistry):
        """Test updating heartbeat for nonexistent bridge."""
        success = await registry.update_heartbeat("nonexistent")
        assert not success

    @pytest.mark.asyncio
    async def test_multiple_bridges(self, registry: BridgeRegistry):
        """Test managing multiple bridges."""
        bridges = [
            MockBridge(f"framework_{i}", "1.0.0")
            for i in range(3)
        ]

        # Register all bridges
        for bridge in bridges:
            success = await registry.register_bridge(bridge)
            assert success

        # Verify all bridges are registered
        active_bridges = await registry.get_active_bridges()
        assert len(active_bridges) == len(bridges)

        # Unregister one bridge
        await registry.unregister_bridge(bridges[0].name)
        active_bridges = await registry.get_active_bridges()
        assert len(active_bridges) == len(bridges) - 1

    @pytest.mark.asyncio
    async def test_bridge_reconnection(
        self,
        registry: BridgeRegistry,
        mock_bridge: MockBridge
    ):
        """Test bridge reconnection after disconnection."""
        # Initial registration
        await registry.register_bridge(mock_bridge)
        assert mock_bridge.connected

        # Simulate disconnection
        mock_bridge.connected = False
        assert not await registry.check_bridge_health(mock_bridge.name)

        # Reconnect
        success = await registry.register_bridge(mock_bridge)
        assert success
        assert mock_bridge.connected
        assert await registry.check_bridge_health(mock_bridge.name)

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, registry: BridgeRegistry):
        """Test concurrent bridge operations."""
        bridges = [
            MockBridge(f"framework_{i}", "1.0.0")
            for i in range(5)
        ]

        # Concurrently register bridges
        tasks = [
            registry.register_bridge(bridge)
            for bridge in bridges
        ]
        results = await asyncio.gather(*tasks)
        assert all(results)

        # Verify all bridges are registered
        active_bridges = await registry.get_active_bridges()
        assert len(active_bridges) == len(bridges)

    @pytest.mark.asyncio
    async def test_bridge_error_handling(self, registry: BridgeRegistry):
        """Test error handling in bridge operations."""
        failing_bridge = MockBridge("failing_framework", "1.0.0", should_fail=True)

        # Test registration failure
        success = await registry.register_bridge(failing_bridge)
        assert not success

        # Test unregistration failure
        success = await registry.unregister_bridge(failing_bridge.name)
        assert not success

        # Test health check failure
        is_healthy = await registry.check_bridge_health(failing_bridge.name)
        assert not is_healthy