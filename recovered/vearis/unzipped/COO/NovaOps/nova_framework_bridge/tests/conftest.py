"""
Shared test fixtures for the Nova Framework Bridge test suite.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from src.core.message import NovaMessage, BridgeMetadata
from src.core.registry import BridgeRegistry, FrameworkBridge
from src.core.metadata import MetadataManager, FrameworkMetadata
from src.bridges.ax_nova_bridge import AxNovaBridge
from src.bridges.langgraph_bridge import LangGraphBridge
from src.bridges.autogen_bridge import AutoGenBridge

# Core Fixtures

@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def base_config() -> Dict[str, Any]:
    """Create base configuration for testing."""
    return {
        "core": {
            "message_timeout": 30,
            "retry_attempts": 3,
            "batch_size": 100
        },
        "security": {
            "enabled": True,
            "token_expiry": 3600
        },
        "monitoring": {
            "enabled": True,
            "interval": 60
        }
    }

# Message System Fixtures

@pytest.fixture
def sample_metadata() -> BridgeMetadata:
    """Create sample metadata for testing."""
    return BridgeMetadata(
        framework="test_framework",
        version="1.0.0",
        timestamp=datetime.now(),
        operation_id="test_op_123",
        source_agent="agent_1",
        target_agent="agent_2",
        context={"test": "data"}
    )

@pytest.fixture
def sample_message(sample_metadata: BridgeMetadata) -> NovaMessage:
    """Create sample message for testing."""
    return NovaMessage(
        content={"test": "content"},
        metadata=sample_metadata,
        message_type="test_message",
        priority=1
    )

# Bridge System Fixtures

@pytest.fixture
def mock_bridge() -> FrameworkBridge:
    """Create a mock bridge for testing."""
    class MockBridge(FrameworkBridge):
        async def to_langchain(self, content: Any) -> Any:
            return {"converted": content}

        async def from_langchain(self, content: Any) -> Any:
            return {"processed": content}

    return MockBridge("mock_framework", "1.0.0")

@pytest.fixture
def bridge_registry() -> BridgeRegistry:
    """Create a bridge registry for testing."""
    return BridgeRegistry()

# Framework Bridge Fixtures

@pytest.fixture
def ax_nova_config() -> Dict[str, Any]:
    """Create AxNova bridge configuration."""
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
def langgraph_config() -> Dict[str, Any]:
    """Create LangGraph bridge configuration."""
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
def autogen_config() -> Dict[str, Any]:
    """Create AutoGen bridge configuration."""
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
def ax_nova_bridge(ax_nova_config: Dict[str, Any]) -> AxNovaBridge:
    """Create an AxNova bridge instance."""
    return AxNovaBridge(ax_nova_config)

@pytest.fixture
def langgraph_bridge(langgraph_config: Dict[str, Any]) -> LangGraphBridge:
    """Create a LangGraph bridge instance."""
    return LangGraphBridge(langgraph_config)

@pytest.fixture
def autogen_bridge(autogen_config: Dict[str, Any]) -> AutoGenBridge:
    """Create an AutoGen bridge instance."""
    return AutoGenBridge(autogen_config)

# Metadata System Fixtures

@pytest.fixture
def metadata_manager() -> MetadataManager:
    """Create a metadata manager for testing."""
    return MetadataManager()

@pytest.fixture
def framework_metadata() -> FrameworkMetadata:
    """Create framework metadata for testing."""
    return FrameworkMetadata(
        name="test_framework",
        version="1.0.0",
        capabilities=["capability1", "capability2"],
        supported_operations=["operation1", "operation2"],
        config={"param1": "value1"},
        last_updated=datetime.now()
    )

# Utility Fixtures

@pytest.fixture
def async_context():
    """Create an async context for testing."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
def error_handler():
    """Create an error handler for testing."""
    errors = []
    def handler(error: Exception):
        errors.append(error)
    return handler, errors

# Clean Up Fixtures

@pytest.fixture(autouse=True)
async def cleanup_after_test(
    bridge_registry: BridgeRegistry,
    metadata_manager: MetadataManager
):
    """Clean up after each test."""
    yield
    # Clean up bridges
    for bridge in list(bridge_registry.bridges.keys()):
        await bridge_registry.unregister_bridge(bridge)

    # Clean up metadata
    metadata_manager.framework_metadata.clear()
    metadata_manager.context_store.clear()
    metadata_manager.operation_history.clear()