"""
Test suite for the main Nova Framework Bridge system.
"""

import pytest
import asyncio
from typing import Dict, Any
import yaml
from pathlib import Path

from src.main import NovaBridgeSystem
from src.core.registry import BridgeRegistry
from src.core.metadata import MetadataManager

@pytest.fixture
def bridge_system() -> NovaBridgeSystem:
    """Create a Nova Bridge system instance for testing."""
    return NovaBridgeSystem()

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Create mock configuration for testing."""
    return {
        "core": {
            "message_timeout": 30,
            "retry_attempts": 3,
            "batch_size": 100,
            "max_concurrent_operations": 50,
            "health_check_interval": 60
        },
        "frameworks": {
            "ax_nova": {
                "version": "1.0.0",
                "capabilities": [
                    "agent_communication",
                    "memory_management",
                    "knowledge_integration"
                ],
                "field_monitoring": {
                    "enabled": True,
                    "check_interval": 10
                }
            },
            "langgraph": {
                "version": "1.0.0",
                "capabilities": [
                    "graph_operations",
                    "chain_execution",
                    "agent_coordination"
                ],
                "graph_operations": {
                    "max_depth": 10,
                    "cache_enabled": True
                }
            },
            "autogen": {
                "version": "1.0.0",
                "capabilities": [
                    "autonomous_agents",
                    "agent_collaboration",
                    "task_planning"
                ],
                "agent_configuration": {
                    "max_agents": 100,
                    "collaboration_threshold": 0.8
                }
            }
        }
    }

class TestNovaBridgeSystem:
    """Test suite for NovaBridgeSystem class."""

    @pytest.mark.asyncio
    async def test_system_initialization(self, bridge_system: NovaBridgeSystem):
        """Test system initialization."""
        assert isinstance(bridge_system.registry, BridgeRegistry)
        assert isinstance(bridge_system.metadata_manager, MetadataManager)
        assert not bridge_system.running
        assert isinstance(bridge_system.bridges, dict)

    @pytest.mark.asyncio
    async def test_load_config(
        self,
        bridge_system: NovaBridgeSystem,
        mock_config: Dict[str, Any],
        tmp_path: Path
    ):
        """Test configuration loading."""
        # Create temporary config files
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Write bridge config
        bridge_config_path = config_dir / "bridge_config.yaml"
        with open(bridge_config_path, "w") as f:
            yaml.dump(mock_config, f)

        # Write logging config
        logging_config_path = config_dir / "logging_config.yaml"
        with open(logging_config_path, "w") as f:
            yaml.dump({
                "version": 1,
                "disable_existing_loggers": False,
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "INFO"
                    }
                }
            }, f)

        # Load configuration
        await bridge_system.load_config()
        assert bridge_system.config is not None
        assert "core" in bridge_system.config
        assert "frameworks" in bridge_system.config

    @pytest.mark.asyncio
    async def test_initialize_bridges(
        self,
        bridge_system: NovaBridgeSystem,
        mock_config: Dict[str, Any]
    ):
        """Test bridge initialization."""
        bridge_system.config = mock_config
        await bridge_system.initialize_bridges()

        assert "ax_nova" in bridge_system.bridges
        assert "langgraph" in bridge_system.bridges
        assert "autogen" in bridge_system.bridges

        for bridge in bridge_system.bridges.values():
            assert bridge.connected

    @pytest.mark.asyncio
    async def test_register_capabilities(
        self,
        bridge_system: NovaBridgeSystem,
        mock_config: Dict[str, Any]
    ):
        """Test capability registration."""
        bridge_system.config = mock_config
        await bridge_system.initialize_bridges()
        await bridge_system.register_capabilities()

        for name, bridge in bridge_system.bridges.items():
            metadata = await bridge_system.metadata_manager.get_framework_capabilities(name)
            assert metadata is not None
            assert len(metadata) > 0

    @pytest.mark.asyncio
    async def test_health_monitoring(
        self,
        bridge_system: NovaBridgeSystem,
        mock_config: Dict[str, Any]
    ):
        """Test health monitoring."""
        bridge_system.config = mock_config
        await bridge_system.initialize_bridges()
        bridge_system.running = True

        # Start monitoring
        monitor_task = asyncio.create_task(bridge_system.start_health_monitoring())

        # Let it run for a bit
        await asyncio.sleep(0.1)

        # Check bridge health status
        for name, bridge in bridge_system.bridges.items():
            is_healthy = await bridge_system.registry.check_bridge_health(name)
            assert is_healthy

        # Stop monitoring
        bridge_system.running = False
        await monitor_task

    @pytest.mark.asyncio
    async def test_system_start_stop(
        self,
        bridge_system: NovaBridgeSystem,
        mock_config: Dict[str, Any]
    ):
        """Test system start and stop."""
        bridge_system.config = mock_config

        # Start system
        await bridge_system.start()
        assert bridge_system.running
        assert all(bridge.connected for bridge in bridge_system.bridges.values())

        # Stop system
        await bridge_system.stop()
        assert not bridge_system.running
        assert all(not bridge.connected for bridge in bridge_system.bridges.values())

    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        bridge_system: NovaBridgeSystem,
        mock_config: Dict[str, Any]
    ):
        """Test system error handling."""
        # Test with invalid config
        invalid_config = {"invalid": "config"}
        bridge_system.config = invalid_config

        with pytest.raises(Exception):
            await bridge_system.initialize_bridges()

        # Test with valid config but failing bridge
        bridge_system.config = mock_config
        await bridge_system.initialize_bridges()

        # Simulate bridge failure
        for bridge in bridge_system.bridges.values():
            bridge.connected = False

        # Health check should detect failures
        for name in bridge_system.bridges:
            is_healthy = await bridge_system.registry.check_bridge_health(name)
            assert not is_healthy

    @pytest.mark.asyncio
    async def test_concurrent_operations(
        self,
        bridge_system: NovaBridgeSystem,
        mock_config: Dict[str, Any]
    ):
        """Test concurrent system operations."""
        bridge_system.config = mock_config
        await bridge_system.start()

        # Create multiple concurrent operations
        async def check_health(name: str):
            return await bridge_system.registry.check_bridge_health(name)

        operations = [
            check_health(name)
            for name in bridge_system.bridges
        ]

        # Execute operations concurrently
        results = await asyncio.gather(*operations)
        assert all(results)

        await bridge_system.stop()

    @pytest.mark.asyncio
    async def test_system_recovery(
        self,
        bridge_system: NovaBridgeSystem,
        mock_config: Dict[str, Any]
    ):
        """Test system recovery from failures."""
        bridge_system.config = mock_config
        await bridge_system.start()

        # Simulate bridge failures
        for bridge in bridge_system.bridges.values():
            bridge.connected = False

        # Wait for health check to detect failures
        await asyncio.sleep(0.1)

        # Bridges should reconnect
        for bridge in bridge_system.bridges.values():
            await bridge.connect()

        # Verify recovery
        for name in bridge_system.bridges:
            is_healthy = await bridge_system.registry.check_bridge_health(name)
            assert is_healthy

        await bridge_system.stop()