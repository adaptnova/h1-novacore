"""
NovaSynth Framework Adapters Unit Tests

Tests individual framework adapters and their message translation, state handling,
and protocol bridging capabilities.

Created by Cosmos
Version: 0.1.0
"""

import pytest
from datetime import datetime
from typing import Dict

from src.adapters.framework_adapters import (
    BaseFrameworkAdapter,
    LangChainAdapter,
    AutoGenAdapter,
    CrewAIAdapter,
    MessageFormat,
    FrameworkState
)

@pytest.fixture
def langchain_adapter():
    """Initialize LangChain adapter for testing."""
    return LangChainAdapter("langchain_test")

@pytest.fixture
def autogen_adapter():
    """Initialize AutoGen adapter for testing."""
    return AutoGenAdapter("autogen_test")

@pytest.fixture
def crewai_adapter():
    """Initialize CrewAI adapter for testing."""
    return CrewAIAdapter("crewai_test")

@pytest.fixture
def test_message():
    """Create test message for translation testing."""
    return {
        "content": "Test message content",
        "type": "test_type",
        "metadata": {
            "source": "test",
            "timestamp": datetime.utcnow().isoformat()
        },
        "state": {
            "key": "value"
        },
        "memory": {
            "history": ["previous message"]
        },
        "tools": {
            "tool1": {"enabled": True}
        }
    }

@pytest.mark.asyncio
async def test_langchain_message_translation(langchain_adapter, test_message):
    """Test LangChain message translation."""
    translated = await langchain_adapter.translate_message(
        test_message,
        "target_framework"
    )

    assert isinstance(translated, MessageFormat)
    assert translated.source_framework == "langchain"
    assert translated.target_framework == "target_framework"
    assert translated.message_type == "chain_message"
    assert "content" in translated.content
    assert translated.state_data is not None
    assert translated.memory_data is not None
    assert translated.tools_data is not None

@pytest.mark.asyncio
async def test_autogen_message_translation(autogen_adapter, test_message):
    """Test AutoGen message translation."""
    translated = await autogen_adapter.translate_message(
        test_message,
        "target_framework"
    )

    assert isinstance(translated, MessageFormat)
    assert translated.source_framework == "autogen"
    assert translated.target_framework == "target_framework"
    assert translated.message_type == "agent_message"
    assert "content" in translated.content
    assert "agent_info" in translated.content

@pytest.mark.asyncio
async def test_crewai_message_translation(crewai_adapter, test_message):
    """Test CrewAI message translation."""
    translated = await crewai_adapter.translate_message(
        test_message,
        "target_framework"
    )

    assert isinstance(translated, MessageFormat)
    assert translated.source_framework == "crewai"
    assert translated.target_framework == "target_framework"
    assert translated.message_type == "crew_message"
    assert "content" in translated.content
    assert "crew_info" in translated.content

@pytest.mark.asyncio
async def test_langchain_state_handling(langchain_adapter):
    """Test LangChain state handling."""
    test_state = {
        "chain_state": {
            "current_step": "test_step",
            "variables": {"key": "value"}
        },
        "memory": {
            "chat_history": ["message1", "message2"]
        },
        "tools": {
            "tool1": {"type": "basic"}
        }
    }

    state = await langchain_adapter._extract_state(test_state)
    memory = await langchain_adapter._extract_memory(test_state)
    tools = await langchain_adapter._extract_tools(test_state)

    assert "current_step" in state
    assert "chat_history" in memory
    assert "tool1" in tools

@pytest.mark.asyncio
async def test_autogen_state_handling(autogen_adapter):
    """Test AutoGen state handling."""
    test_state = {
        "agent_state": {
            "status": "active",
            "context": {"key": "value"}
        },
        "memory": {
            "conversation": ["message1", "message2"]
        },
        "tools": {
            "tool1": {"enabled": True}
        }
    }

    state = await autogen_adapter._extract_state(test_state)
    memory = await autogen_adapter._extract_memory(test_state)
    tools = await autogen_adapter._extract_tools(test_state)

    assert "status" in state
    assert "conversation" in memory
    assert "tool1" in tools

@pytest.mark.asyncio
async def test_crewai_state_handling(crewai_adapter):
    """Test CrewAI state handling."""
    test_state = {
        "crew_state": {
            "task": "test_task",
            "role": "test_role"
        },
        "memory": {
            "shared_knowledge": ["fact1", "fact2"]
        },
        "tools": {
            "tool1": {"type": "specialized"}
        }
    }

    state = await crewai_adapter._extract_state(test_state)
    memory = await crewai_adapter._extract_memory(test_state)
    tools = await crewai_adapter._extract_tools(test_state)

    assert "task" in state
    assert "shared_knowledge" in memory
    assert "tool1" in tools

@pytest.mark.asyncio
async def test_message_type_detection():
    """Test message type detection across adapters."""
    adapters = {
        "langchain": LangChainAdapter("langchain_test"),
        "autogen": AutoGenAdapter("autogen_test"),
        "crewai": CrewAIAdapter("crewai_test")
    }

    test_messages = {
        "langchain": {"type": "chain_message"},
        "autogen": {"message_type": "agent_message"},
        "crewai": {"message_type": "crew_message"}
    }

    for framework, adapter in adapters.items():
        message_type = adapter._detect_message_type(test_messages[framework])
        assert message_type is not None
        assert isinstance(message_type, str)

@pytest.mark.asyncio
async def test_content_extraction():
    """Test content extraction across adapters."""
    adapters = {
        "langchain": LangChainAdapter("langchain_test"),
        "autogen": AutoGenAdapter("autogen_test"),
        "crewai": CrewAIAdapter("crewai_test")
    }

    test_message = {
        "content": "Test content",
        "metadata": {"key": "value"}
    }

    for adapter in adapters.values():
        content = adapter._extract_content(test_message)
        assert isinstance(content, dict)
        assert "data" in content

@pytest.mark.asyncio
async def test_metadata_handling():
    """Test metadata handling across adapters."""
    adapters = {
        "langchain": LangChainAdapter("langchain_test"),
        "autogen": AutoGenAdapter("autogen_test"),
        "crewai": CrewAIAdapter("crewai_test")
    }

    for adapter in adapters.values():
        metadata = adapter._extract_metadata({})
        assert isinstance(metadata, dict)
        assert "framework" in metadata
        assert "timestamp" in metadata
        assert "version" in metadata

if __name__ == "__main__":
    pytest.main(["-v", "test_framework_adapters.py"])