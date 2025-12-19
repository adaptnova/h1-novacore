"""
NovaSynth Framework Adapters

Specialized adapters for each framework, handling message translation, state mapping,
and protocol bridging. These adapters enable seamless interaction between different
frameworks while maintaining their unique capabilities.

Created by Cosmos
Version: 0.1.0
"""

[Previous imports and base classes remain unchanged...]

class LangGraphAdapter(BaseFrameworkAdapter):
    """Adapter for LangGraph integration."""

    async def translate_message(
        self, message: Any, target_framework: str
    ) -> MessageFormat:
        """Translate LangGraph messages."""
        message_type = self._detect_message_type(message)
        content = self._extract_content(message)
        state_data = self._extract_state(message)
        memory_data = self._extract_memory(message)
        tools_data = self._extract_tools(message)

        return MessageFormat(
            message_id=str(uuid.uuid4()),
            source_framework="langgraph",
            target_framework=target_framework,
            message_type=message_type,
            protocol_version="1.0",
            content=content,
            state_data=state_data,
            memory_data=memory_data,
            tools_data=tools_data,
            timestamp=datetime.utcnow(),
            metadata=self._extract_metadata(message)
        )

    def _detect_message_type(self, message: Any) -> str:
        """Detect LangGraph message type."""
        if hasattr(message, "message_type"):
            return message.message_type
        return "graph_message"

    def _extract_content(self, message: Any) -> Dict:
        """Extract content from LangGraph message."""
        if isinstance(message, dict):
            return {
                "data": message.get("content", {}),
                "graph_info": message.get("graph_info", {}),
                "node_id": message.get("node_id", ""),
                "edge_data": message.get("edge_data", {})
            }
        return {"data": str(message)}

class AXNovasAdapter(BaseFrameworkAdapter):
    """Adapter for AX-NovaS integration."""

    async def translate_message(
        self, message: Any, target_framework: str
    ) -> MessageFormat:
        """Translate AX-NovaS messages."""
        message_type = self._detect_message_type(message)
        content = self._extract_content(message)
        state_data = self._extract_state(message)
        memory_data = self._extract_memory(message)
        tools_data = self._extract_tools(message)

        return MessageFormat(
            message_id=str(uuid.uuid4()),
            source_framework="ax_novas",
            target_framework=target_framework,
            message_type=message_type,
            protocol_version="1.0",
            content=content,
            state_data=state_data,
            memory_data=memory_data,
            tools_data=tools_data,
            timestamp=datetime.utcnow(),
            metadata=self._extract_metadata(message)
        )

    def _detect_message_type(self, message: Any) -> str:
        """Detect AX-NovaS message type."""
        if hasattr(message, "message_type"):
            return message.message_type
        return "optimization_message"

    def _extract_content(self, message: Any) -> Dict:
        """Extract content from AX-NovaS message."""
        if isinstance(message, dict):
            return {
                "data": message.get("content", {}),
                "experiment_info": message.get("experiment_info", {}),
                "parameters": message.get("parameters", {}),
                "objectives": message.get("objectives", {})
            }
        return {"data": str(message)}

class RasaProAdapter(BaseFrameworkAdapter):
    """Adapter for Rasa Pro integration."""

    async def translate_message(
        self, message: Any, target_framework: str
    ) -> MessageFormat:
        """Translate Rasa Pro messages."""
        message_type = self._detect_message_type(message)
        content = self._extract_content(message)
        state_data = self._extract_state(message)
        memory_data = self._extract_memory(message)
        tools_data = self._extract_tools(message)

        return MessageFormat(
            message_id=str(uuid.uuid4()),
            source_framework="rasa_pro",
            target_framework=target_framework,
            message_type=message_type,
            protocol_version="1.0",
            content=content,
            state_data=state_data,
            memory_data=memory_data,
            tools_data=tools_data,
            timestamp=datetime.utcnow(),
            metadata=self._extract_metadata(message)
        )

    def _detect_message_type(self, message: Any) -> str:
        """Detect Rasa Pro message type."""
        if hasattr(message, "message_type"):
            return message.message_type
        return "dialogue_message"

    def _extract_content(self, message: Any) -> Dict:
        """Extract content from Rasa Pro message."""
        if isinstance(message, dict):
            return {
                "data": message.get("content", {}),
                "dialogue_state": message.get("dialogue_state", {}),
                "intents": message.get("intents", []),
                "entities": message.get("entities", [])
            }
        return {"data": str(message)}

class HaystackAdapter(BaseFrameworkAdapter):
    """Adapter for Haystack integration."""

    async def translate_message(
        self, message: Any, target_framework: str
    ) -> MessageFormat:
        """Translate Haystack messages."""
        message_type = self._detect_message_type(message)
        content = self._extract_content(message)
        state_data = self._extract_state(message)
        memory_data = self._extract_memory(message)
        tools_data = self._extract_tools(message)

        return MessageFormat(
            message_id=str(uuid.uuid4()),
            source_framework="haystack",
            target_framework=target_framework,
            message_type=message_type,
            protocol_version="1.0",
            content=content,
            state_data=state_data,
            memory_data=memory_data,
            tools_data=tools_data,
            timestamp=datetime.utcnow(),
            metadata=self._extract_metadata(message)
        )

    def _detect_message_type(self, message: Any) -> str:
        """Detect Haystack message type."""
        if hasattr(message, "message_type"):
            return message.message_type
        return "pipeline_message"

    def _extract_content(self, message: Any) -> Dict:
        """Extract content from Haystack message."""
        if isinstance(message, dict):
            return {
                "data": message.get("content", {}),
                "pipeline_info": message.get("pipeline_info", {}),
                "query": message.get("query", ""),
                "results": message.get("results", [])
            }
        return {"data": str(message)}

class SemanticKernelAdapter(BaseFrameworkAdapter):
    """Adapter for Semantic Kernel integration."""

    async def translate_message(
        self, message: Any, target_framework: str
    ) -> MessageFormat:
        """Translate Semantic Kernel messages."""
        message_type = self._detect_message_type(message)
        content = self._extract_content(message)
        state_data = self._extract_state(message)
        memory_data = self._extract_memory(message)
        tools_data = self._extract_tools(message)

        return MessageFormat(
            message_id=str(uuid.uuid4()),
            source_framework="semantic_kernel",
            target_framework=target_framework,
            message_type=message_type,
            protocol_version="1.0",
            content=content,
            state_data=state_data,
            memory_data=memory_data,
            tools_data=tools_data,
            timestamp=datetime.utcnow(),
            metadata=self._extract_metadata(message)
        )

    def _detect_message_type(self, message: Any) -> str:
        """Detect Semantic Kernel message type."""
        if hasattr(message, "message_type"):
            return message.message_type
        return "kernel_message"

    def _extract_content(self, message: Any) -> Dict:
        """Extract content from Semantic Kernel message."""
        if isinstance(message, dict):
            return {
                "data": message.get("content", {}),
                "kernel_info": message.get("kernel_info", {}),
                "plugins": message.get("plugins", []),
                "functions": message.get("functions", [])
            }
        return {"data": str(message)}

[Previous adapter classes remain unchanged...]

class FrameworkBridge:
    """Central bridge for managing framework interactions."""

    def _get_adapter_class(self, framework_type: str) -> type:
        """Get the appropriate adapter class for a framework type."""
        adapters = {
            "langchain": LangChainAdapter,
            "langgraph": LangGraphAdapter,
            "autogen": AutoGenAdapter,
            "crewai": CrewAIAdapter,
            "ray": RayAdapter,
            "ax_novas": AXNovasAdapter,
            "rasa_pro": RasaProAdapter,
            "haystack": HaystackAdapter,
            "semantic_kernel": SemanticKernelAdapter
        }
        return adapters.get(framework_type, BaseFrameworkAdapter)

[Rest of the FrameworkBridge class remains unchanged...]

if __name__ == "__main__":
    asyncio.run(main())
