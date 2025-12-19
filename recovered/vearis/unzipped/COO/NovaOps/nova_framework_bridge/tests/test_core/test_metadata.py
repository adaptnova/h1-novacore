import pytest
from datetime import datetime
from typing import Dict, Any, List

from src.core.metadata import MetadataManager, FrameworkMetadata

@pytest.fixture
def metadata_manager() -> MetadataManager:
    """Create a metadata manager for testing."""
    return MetadataManager()

@pytest.fixture
def sample_framework_data() -> Dict[str, Any]:
    """Create sample framework data for testing."""
    return {
        "name": "test_framework",
        "version": "1.0.0",
        "capabilities": ["capability1", "capability2"],
        "supported_operations": ["operation1", "operation2"],
        "config": {
            "param1": "value1",
            "param2": "value2"
        }
    }

@pytest.fixture
def sample_metadata(sample_framework_data: Dict[str, Any]) -> FrameworkMetadata:
    """Create sample framework metadata for testing."""
    return FrameworkMetadata(
        name=sample_framework_data["name"],
        version=sample_framework_data["version"],
        capabilities=sample_framework_data["capabilities"],
        supported_operations=sample_framework_data["supported_operations"],
        config=sample_framework_data["config"],
        last_updated=datetime.now()
    )

class TestFrameworkMetadata:
    """Test suite for FrameworkMetadata class."""

    def test_metadata_creation(self, sample_metadata: FrameworkMetadata):
        """Test metadata creation."""
        assert sample_metadata.name == "test_framework"
        assert sample_metadata.version == "1.0.0"
        assert "capability1" in sample_metadata.capabilities
        assert "operation1" in sample_metadata.supported_operations
        assert sample_metadata.config["param1"] == "value1"
        assert isinstance(sample_metadata.last_updated, datetime)
        assert sample_metadata.status == "inactive"
        assert sample_metadata.health_check is None

    def test_metadata_to_dict(self, sample_metadata: FrameworkMetadata):
        """Test metadata conversion to dictionary."""
        metadata_dict = sample_metadata.to_dict()
        assert isinstance(metadata_dict, dict)
        assert metadata_dict["name"] == "test_framework"
        assert metadata_dict["version"] == "1.0.0"
        assert isinstance(metadata_dict["last_updated"], str)
        assert metadata_dict["status"] == "inactive"

    def test_metadata_from_dict(self, sample_metadata: FrameworkMetadata):
        """Test metadata creation from dictionary."""
        metadata_dict = sample_metadata.to_dict()
        new_metadata = FrameworkMetadata.from_dict(metadata_dict)
        assert new_metadata.name == sample_metadata.name
        assert new_metadata.version == sample_metadata.version
        assert new_metadata.capabilities == sample_metadata.capabilities
        assert isinstance(new_metadata.last_updated, datetime)

class TestMetadataManager:
    """Test suite for MetadataManager class."""

    @pytest.mark.asyncio
    async def test_register_framework(
        self,
        metadata_manager: MetadataManager,
        sample_framework_data: Dict[str, Any]
    ):
        """Test framework registration."""
        success = await metadata_manager.register_framework(
            name=sample_framework_data["name"],
            version=sample_framework_data["version"],
            capabilities=sample_framework_data["capabilities"],
            supported_operations=sample_framework_data["supported_operations"],
            config=sample_framework_data["config"]
        )
        assert success
        assert sample_framework_data["name"] in metadata_manager.framework_metadata

    @pytest.mark.asyncio
    async def test_update_framework_status(
        self,
        metadata_manager: MetadataManager,
        sample_framework_data: Dict[str, Any]
    ):
        """Test framework status update."""
        await metadata_manager.register_framework(
            name=sample_framework_data["name"],
            version=sample_framework_data["version"],
            capabilities=sample_framework_data["capabilities"],
            supported_operations=sample_framework_data["supported_operations"],
            config=sample_framework_data["config"]
        )

        health_check = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy"
        }

        success = await metadata_manager.update_framework_status(
            name=sample_framework_data["name"],
            status="active",
            health_check=health_check
        )
        assert success

        metadata = metadata_manager.framework_metadata[sample_framework_data["name"]]
        assert metadata.status == "active"
        assert metadata.health_check == health_check

    @pytest.mark.asyncio
    async def test_store_context(self, metadata_manager: MetadataManager):
        """Test operation context storage."""
        operation_id = "test_op_123"
        context = {"key": "value"}

        success = await metadata_manager.store_context(operation_id, context)
        assert success

        stored_context = await metadata_manager.get_context(operation_id)
        assert stored_context is not None
        assert stored_context["context"] == context

    @pytest.mark.asyncio
    async def test_log_operation(self, metadata_manager: MetadataManager):
        """Test operation logging."""
        operation_id = "test_op_123"
        operation_type = "test_operation"
        details = {"status": "success"}

        success = await metadata_manager.log_operation(
            operation_id,
            operation_type,
            details
        )
        assert success

        history = await metadata_manager.get_operation_history(operation_id)
        assert history is not None
        assert len(history) == 1
        assert history[0]["type"] == operation_type
        assert history[0]["details"] == details

    @pytest.mark.asyncio
    async def test_check_compatibility(
        self,
        metadata_manager: MetadataManager,
        sample_framework_data: Dict[str, Any]
    ):
        """Test framework compatibility checking."""
        # Register first framework
        await metadata_manager.register_framework(
            name=sample_framework_data["name"],
            version=sample_framework_data["version"],
            capabilities=sample_framework_data["capabilities"],
            supported_operations=sample_framework_data["supported_operations"],
            config=sample_framework_data["config"]
        )

        # Register second framework
        second_framework = {
            **sample_framework_data,
            "name": "second_framework"
        }
        await metadata_manager.register_framework(
            name=second_framework["name"],
            version=second_framework["version"],
            capabilities=second_framework["capabilities"],
            supported_operations=second_framework["supported_operations"],
            config=second_framework["config"]
        )

        # Check compatibility
        is_compatible = await metadata_manager.check_compatibility(
            sample_framework_data["name"],
            second_framework["name"],
            "operation1"
        )
        assert is_compatible

    @pytest.mark.asyncio
    async def test_cleanup_old_contexts(self, metadata_manager: MetadataManager):
        """Test cleaning up old context entries."""
        # Store some contexts
        contexts = [
            ("op1", {"data": "value1"}),
            ("op2", {"data": "value2"}),
            ("op3", {"data": "value3"})
        ]

        for op_id, context in contexts:
            await metadata_manager.store_context(op_id, context)

        # Clean up contexts
        success = await metadata_manager.cleanup_old_contexts(max_age_hours=0)
        assert success

        # Verify contexts are cleaned up
        for op_id, _ in contexts:
            context = await metadata_manager.get_context(op_id)
            assert context is None

    @pytest.mark.asyncio
    async def test_get_framework_capabilities(
        self,
        metadata_manager: MetadataManager,
        sample_framework_data: Dict[str, Any]
    ):
        """Test getting framework capabilities."""
        await metadata_manager.register_framework(
            name=sample_framework_data["name"],
            version=sample_framework_data["version"],
            capabilities=sample_framework_data["capabilities"],
            supported_operations=sample_framework_data["supported_operations"],
            config=sample_framework_data["config"]
        )

        capabilities = metadata_manager.get_framework_capabilities(
            sample_framework_data["name"]
        )
        assert capabilities == sample_framework_data["capabilities"]

    def test_get_active_frameworks(
        self,
        metadata_manager: MetadataManager,
        sample_framework_data: Dict[str, Any]
    ):
        """Test getting active frameworks."""
        # Register framework
        metadata = FrameworkMetadata(
            name=sample_framework_data["name"],
            version=sample_framework_data["version"],
            capabilities=sample_framework_data["capabilities"],
            supported_operations=sample_framework_data["supported_operations"],
            config=sample_framework_data["config"],
            last_updated=datetime.now(),
            status="active"
        )
        metadata_manager.framework_metadata[metadata.name] = metadata

        active_frameworks = metadata_manager.get_active_frameworks()
        assert metadata.name in active_frameworks

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, metadata_manager: MetadataManager):
        """Test concurrent metadata operations."""
        import asyncio

        # Create multiple operation contexts
        operations = [
            metadata_manager.store_context(f"op_{i}", {"data": f"value_{i}"})
            for i in range(5)
        ]

        # Execute operations concurrently
        results = await asyncio.gather(*operations)
        assert all(results)

        # Verify all contexts were stored
        for i in range(5):
            context = await metadata_manager.get_context(f"op_{i}")
            assert context is not None
            assert context["context"]["data"] == f"value_{i}"