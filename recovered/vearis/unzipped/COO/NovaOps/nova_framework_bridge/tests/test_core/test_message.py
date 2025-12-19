import pytest
from datetime import datetime
from typing import Dict, Any

from src.core.message import NovaMessage, BridgeMetadata

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

class TestBridgeMetadata:
    """Test suite for BridgeMetadata class."""

    def test_metadata_creation(self, sample_metadata: BridgeMetadata):
        """Test metadata creation."""
        assert sample_metadata.framework == "test_framework"
        assert sample_metadata.version == "1.0.0"
        assert isinstance(sample_metadata.timestamp, datetime)
        assert sample_metadata.operation_id == "test_op_123"
        assert sample_metadata.source_agent == "agent_1"
        assert sample_metadata.target_agent == "agent_2"
        assert sample_metadata.context == {"test": "data"}

    def test_metadata_to_dict(self, sample_metadata: BridgeMetadata):
        """Test metadata conversion to dictionary."""
        metadata_dict = sample_metadata.to_dict()
        assert isinstance(metadata_dict, dict)
        assert metadata_dict["framework"] == "test_framework"
        assert metadata_dict["version"] == "1.0.0"
        assert isinstance(metadata_dict["timestamp"], str)
        assert metadata_dict["operation_id"] == "test_op_123"
        assert metadata_dict["source_agent"] == "agent_1"
        assert metadata_dict["target_agent"] == "agent_2"
        assert metadata_dict["context"] == {"test": "data"}

    def test_metadata_from_dict(self, sample_metadata: BridgeMetadata):
        """Test metadata creation from dictionary."""
        metadata_dict = sample_metadata.to_dict()
        new_metadata = BridgeMetadata.from_dict(metadata_dict)
        assert new_metadata.framework == sample_metadata.framework
        assert new_metadata.version == sample_metadata.version
        assert isinstance(new_metadata.timestamp, datetime)
        assert new_metadata.operation_id == sample_metadata.operation_id
        assert new_metadata.source_agent == sample_metadata.source_agent
        assert new_metadata.target_agent == sample_metadata.target_agent
        assert new_metadata.context == sample_metadata.context

class TestNovaMessage:
    """Test suite for NovaMessage class."""

    def test_message_creation(self, sample_message: NovaMessage):
        """Test message creation."""
        assert sample_message.content == {"test": "content"}
        assert isinstance(sample_message.metadata, BridgeMetadata)
        assert sample_message.message_type == "test_message"
        assert sample_message.priority == 1
        assert isinstance(sample_message.created_at, datetime)
        assert not sample_message.processed
        assert sample_message.error is None

    def test_message_to_dict(self, sample_message: NovaMessage):
        """Test message conversion to dictionary."""
        message_dict = sample_message.to_dict()
        assert isinstance(message_dict, dict)
        assert message_dict["content"] == {"test": "content"}
        assert isinstance(message_dict["metadata"], dict)
        assert message_dict["message_type"] == "test_message"
        assert message_dict["priority"] == 1
        assert isinstance(message_dict["created_at"], str)
        assert not message_dict["processed"]
        assert message_dict["error"] is None

    def test_message_from_dict(self, sample_message: NovaMessage):
        """Test message creation from dictionary."""
        message_dict = sample_message.to_dict()
        new_message = NovaMessage.from_dict(message_dict)
        assert new_message.content == sample_message.content
        assert isinstance(new_message.metadata, BridgeMetadata)
        assert new_message.message_type == sample_message.message_type
        assert new_message.priority == sample_message.priority
        assert isinstance(new_message.created_at, datetime)
        assert new_message.processed == sample_message.processed
        assert new_message.error == sample_message.error

    @pytest.mark.parametrize("content,message_type,priority", [
        ({"data": "test"}, "test_type", 1),
        (["item1", "item2"], "list_type", 2),
        ("simple string", "string_type", 3),
        (123, "number_type", 4),
        (None, "null_type", 5)
    ])
    def test_message_with_different_content_types(
        self,
        sample_metadata: BridgeMetadata,
        content: Any,
        message_type: str,
        priority: int
    ):
        """Test message creation with different content types."""
        message = NovaMessage(
            content=content,
            metadata=sample_metadata,
            message_type=message_type,
            priority=priority
        )
        assert message.content == content
        assert message.message_type == message_type
        assert message.priority == priority

    def test_message_processing_flow(self, sample_message: NovaMessage):
        """Test message processing flow."""
        # Initial state
        assert not sample_message.processed
        assert sample_message.error is None

        # Simulate processing
        sample_message.processed = True
        assert sample_message.processed

        # Simulate error
        error_msg = "Test error"
        sample_message.error = error_msg
        assert sample_message.error == error_msg

    def test_message_metadata_immutability(
        self,
        sample_message: NovaMessage,
        sample_metadata: BridgeMetadata
    ):
        """Test that message metadata remains consistent."""
        original_metadata_dict = sample_metadata.to_dict()
        message_metadata_dict = sample_message.metadata.to_dict()
        assert message_metadata_dict == original_metadata_dict

        # Modify original metadata
        sample_metadata.framework = "modified_framework"

        # Message metadata should remain unchanged
        assert sample_message.metadata.framework == "test_framework"

    def test_message_serialization_cycle(self, sample_message: NovaMessage):
        """Test complete serialization cycle."""
        # Convert to dict
        message_dict = sample_message.to_dict()

        # Convert back to message
        new_message = NovaMessage.from_dict(message_dict)

        # Convert new message to dict
        new_message_dict = new_message.to_dict()

        # Compare dictionaries
        assert message_dict == new_message_dict

    def test_message_with_empty_values(self, sample_metadata: BridgeMetadata):
        """Test message creation with empty/default values."""
        message = NovaMessage(
            content={},
            metadata=sample_metadata,
            message_type="empty_test"
        )
        assert message.content == {}
        assert message.priority == 1  # Default priority
        assert not message.processed
        assert message.error is None

    def test_invalid_metadata_handling(self):
        """Test handling of invalid metadata."""
        with pytest.raises(TypeError):
            NovaMessage(
                content={"test": "content"},
                metadata={"invalid": "metadata"},  # Not a BridgeMetadata object
                message_type="test_message"
            )