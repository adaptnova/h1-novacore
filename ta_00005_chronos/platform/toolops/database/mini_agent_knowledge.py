#!/usr/bin/env python3
"""
Mini-Agent Knowledge Integration Layer
Ties memory system into core agent capabilities for intelligent responses
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from mini_agent_memory import MiniAgentMemory

class MiniAgentKnowledge:
    """Knowledge integration layer for Mini-Agent"""
    
    def __init__(self, redis_host="localhost", redis_port=18000, password=None):
        self.memory = MiniAgentMemory(
            redis_host=redis_host,
            redis_port=redis_port,
            password=password
        )
        self.session_started = False
        
    def initialize_session(self, user_context: str = None) -> Dict[str, Any]:
        """Initialize a new session and load relevant knowledge"""
        session_id = self.memory.start_session()
        
        # Record session start
        self.memory.record_interaction(
            "session_start",
            f"Session started with context: {user_context}" if user_context else "Session started",
            {"agent": "system", "user_context": user_context}
        )
        
        self.session_started = True
        
        # Load recent knowledge for context
        recent_knowledge = self.memory.get_recent_knowledge(limit=10)
        user_preferences = self._get_all_preferences()
        
        # Store session context knowledge
        self.memory.store_knowledge(
            "session_context",
            f"Session started with user context: {user_context}" if user_context else "Session started",
            {
                "tags": ["session", "context"],
                "session_id": session_id,
                "preferences": user_preferences
            }
        )
        
        return {
            "session_id": session_id,
            "recent_knowledge": recent_knowledge,
            "user_preferences": user_preferences,
            "memory_stats": self.memory.get_memory_stats()
        }
    
    def process_user_input(self, user_input: str, agent_response: str = None) -> str:
        """Process user input and extract knowledge"""
        if not self.session_started:
            self.initialize_session()
        
        # Record user interaction
        self.memory.record_interaction(
            "user_query",
            user_input,
            {"agent": "user", "response_provided": bool(agent_response)}
        )
        
        # Extract potential knowledge from user input
        knowledge_items = self._extract_knowledge(user_input)
        for item in knowledge_items:
            self.memory.store_knowledge(item["type"], item["content"], {
                "tags": item["tags"],
                "source": "user_input",
                "extraction_confidence": item["confidence"]
            })
        
        # Store agent response if provided
        if agent_response:
            self.memory.record_interaction(
                "agent_response",
                agent_response,
                {"agent": "mini_agent"}
            )
            
            # Extract knowledge from agent response
            knowledge_items = self._extract_knowledge(agent_response)
            for item in knowledge_items:
                self.memory.store_knowledge(item["type"], item["content"], {
                    "tags": item["tags"],
                    "source": "agent_response",
                    "extraction_confidence": item["confidence"]
                })
        
        return self._generate_response_insights(user_input, agent_response)
    
    def record_tool_execution(self, tool_name: str, arguments: Dict[str, Any], 
                            result: Any, success: bool = True) -> str:
        """Record tool execution for knowledge building"""
        if not self.session_started:
            self.initialize_session()
        
        execution_data = {
            "tool": tool_name,
            "arguments": arguments,
            "result": str(result)[:500],  # Truncate long results
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        # Record interaction
        self.memory.record_interaction(
            "tool_execution",
            f"Executed {tool_name} with arguments: {arguments}",
            {"tool": tool_name, "success": success, "arguments": arguments}
        )
        
        # Store as knowledge if successful
        if success:
            knowledge_content = f"Successfully executed {tool_name} with {len(arguments)} arguments"
            self.memory.store_knowledge("tool_knowledge", knowledge_content, {
                "tags": ["tool", tool_name, "execution"],
                "tool_name": tool_name,
                "arguments": arguments,
                "result_sample": str(result)[:100]
            })
        
        return str(uuid.uuid4()) if success else None
    
    def learn_user_preference(self, preference_key: str, value: Any, 
                             context: str = None) -> bool:
        """Learn user preference"""
        if not self.session_started:
            self.initialize_session()
        
        # Store preference in memory
        self.memory.store_user_preference(preference_key, value, context)
        
        # Record as knowledge
        self.memory.store_knowledge("user_preference", 
            f"User prefers {preference_key}: {value}",
            {
                "tags": ["preference", preference_key],
                "preference_key": preference_key,
                "preference_value": value,
                "context": context
            }
        )
        
        return True
    
    def get_contextual_response(self, current_input: str) -> Dict[str, Any]:
        """Generate contextual response based on past knowledge"""
        # Search for related knowledge
        related_knowledge = self.memory.search_knowledge(current_input)
        
        # Get user preferences
        preferences = self._get_all_preferences()
        
        # Get session history
        session_history = self.memory.get_session_history(limit=5)
        
        # Generate insights
        insights = self._generate_contextual_insights(
            current_input, related_knowledge, preferences, session_history
        )
        
        return {
            "related_knowledge": related_knowledge,
            "user_preferences": preferences,
            "session_context": session_history,
            "contextual_insights": insights,
            "suggested_actions": self._suggest_actions(current_input, related_knowledge)
        }
    
    def get_intelligent_suggestions(self, input_context: str) -> List[str]:
        """Get intelligent suggestions based on knowledge"""
        # Search for patterns in past interactions
        past_interactions = self.memory.get_session_history(limit=20)
        
        # Get relevant knowledge
        knowledge = self.memory.search_knowledge(input_context)
        
        # Generate suggestions based on:
        # 1. Similar past inputs
        # 2. Related tools used
        # 3. Knowledge areas
        # 4. User preferences
        
        suggestions = []
        
        # Suggest tools based on past successful usage
        tool_suggestions = self._suggest_tools_from_history(past_interactions)
        suggestions.extend(tool_suggestions)
        
        # Suggest knowledge areas
        if knowledge:
            suggestions.append(f"You have knowledge about: {', '.join([k['type'] for k in knowledge[:3]])}")
        
        # Suggest relevant actions
        action_suggestions = self._suggest_actions(input_context, knowledge)
        suggestions.extend(action_suggestions)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def build_session_summary(self) -> str:
        """Build summary of the current session"""
        if not self.session_started:
            return "No active session"
        
        # Get session data
        session_data = self.memory.get_session_history(limit=100)
        
        # Analyze interactions
        interaction_types = {}
        tools_used = set()
        knowledge_gained = 0
        
        for interaction in session_data:
            itype = interaction.get("type", "unknown")
            interaction_types[itype] = interaction_types.get(itype, 0) + 1
            
            if itype == "tool_execution":
                tools_used.add(interaction.get("metadata", {}).get("tool", "unknown"))
            elif itype == "knowledge_gain":
                knowledge_gained += 1
        
        # Generate summary
        summary = f"Session Summary:\n"
        summary += f"- Total interactions: {len(session_data)}\n"
        summary += f"- Interaction types: {', '.join([f'{k}({v})' for k, v in interaction_types.items()])}\n"
        summary += f"- Tools used: {', '.join(tools_used) if tools_used else 'None'}\n"
        summary += f"- Knowledge gained: {knowledge_gained} items\n"
        summary += f"- Session timestamp: {datetime.now().isoformat()}\n"
        
        return summary
    
    def _extract_knowledge(self, text: str) -> List[Dict[str, Any]]:
        """Extract knowledge items from text (simplified)"""
        knowledge_items = []
        
        # Simple pattern matching for knowledge extraction
        # In production, use NLP models for better extraction
        
        # Tool patterns
        if "created" in text.lower() and ("tool" in text.lower() or "script" in text.lower()):
            knowledge_items.append({
                "type": "tool_creation",
                "content": f"Tool/script creation: {text[:100]}...",
                "tags": ["tool", "creation"],
                "confidence": 0.8
            })
        
        # Database patterns
        if any(db in text.lower() for db in ["redis", "mongodb", "postgresql", "database"]):
            knowledge_items.append({
                "type": "database_knowledge",
                "content": f"Database interaction: {text[:100]}...",
                "tags": ["database"],
                "confidence": 0.7
            })
        
        # Configuration patterns
        if any(word in text.lower() for word in ["config", "setting", "preference"]):
            knowledge_items.append({
                "type": "configuration",
                "content": f"Configuration learned: {text[:100]}...",
                "tags": ["configuration"],
                "confidence": 0.6
            })
        
        # User preference patterns
        if any(word in text.lower() for word in ["always", "prefer", "want", "need"]):
            knowledge_items.append({
                "type": "user_preference",
                "content": f"User preference: {text[:100]}...",
                "tags": ["preference"],
                "confidence": 0.5
            })
        
        return knowledge_items
    
    def _generate_response_insights(self, user_input: str, agent_response: str) -> str:
        """Generate insights about the interaction"""
        insights = []
        
        # Check if this is a new topic
        if user_input and len(user_input) > 50:
            insights.append("Complex user input detected - knowledge stored")
        
        # Check for tool usage
        if agent_response and "tool" in agent_response.lower():
            insights.append("Tool execution occurred - execution pattern learned")
        
        # Check for knowledge gain
        knowledge_items = self._extract_knowledge(user_input + " " + (agent_response or ""))
        if knowledge_items:
            insights.append(f"Extracted {len(knowledge_items)} knowledge items")
        
        return "; ".join(insights) if insights else "Standard interaction recorded"
    
    def _get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""
        return self.memory.redis_client.hgetall(f"{self.memory.namespace}:user_preferences")
    
    def _generate_contextual_insights(self, current_input: str, knowledge: List[Dict], 
                                    preferences: Dict[str, Any], history: List[Dict]) -> List[str]:
        """Generate contextual insights"""
        insights = []
        
        if knowledge:
            insights.append(f"Found {len(knowledge)} related knowledge items")
        
        if preferences:
            insights.append(f"User has {len(preferences)} stored preferences")
        
        if history:
            insights.append(f"Session has {len(history)} past interactions")
        
        return insights
    
    def _suggest_actions(self, current_input: str, knowledge: List[Dict]) -> List[str]:
        """Suggest relevant actions based on context"""
        suggestions = []
        
        # Database-related suggestions
        if any(word in current_input.lower() for word in ["database", "query", "connection"]):
            suggestions.append("Use database tools for queries")
            suggestions.append("Check database status")
        
        # Tool creation suggestions
        if any(word in current_input.lower() for word in ["create", "build", "make"]):
            suggestions.append("Create new tool or script")
            suggestions.append("Use existing templates")
        
        # Communication suggestions
        if any(word in current_input.lower() for word in ["agent", "communicate", "message"]):
            suggestions.append("Use agent communication platform")
            suggestions.append("Set up HITL interface")
        
        return suggestions
    
    def _suggest_tools_from_history(self, history: List[Dict]) -> List[str]:
        """Suggest tools based on past usage"""
        tools_used = {}
        
        for interaction in history:
            if interaction.get("type") == "tool_execution":
                tool = interaction.get("metadata", {}).get("tool")
                if tool:
                    tools_used[tool] = tools_used.get(tool, 0) + 1
        
        # Suggest most used tools
        if tools_used:
            top_tools = sorted(tools_used.items(), key=lambda x: x[1], reverse=True)[:3]
            return [f"Previously used {tool} successfully" for tool, count in top_tools]
        
        return []

def main():
    """Demo the knowledge integration system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mini-Agent Knowledge Integration")
    parser.add_argument("--action", required=True,
                       choices=["init", "process", "suggest", "summary", "stats"])
    parser.add_argument("--input", help="User input")
    parser.add_argument("--response", help="Agent response")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=18000)
    parser.add_argument("--redis-password", default="df_cluster_2024_adapt_research")
    
    args = parser.parse_args()
    
    knowledge = MiniAgentKnowledge(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        password=args.redis_password
    )
    
    if args.action == "init":
        result = knowledge.initialize_session(args.input)
        print(json.dumps(result, indent=2))
    
    elif args.action == "process":
        insights = knowledge.process_user_input(args.input, args.response)
        print(f"Insights: {insights}")
    
    elif args.action == "suggest":
        suggestions = knowledge.get_intelligent_suggestions(args.input)
        print(json.dumps(suggestions, indent=2))
    
    elif args.action == "summary":
        summary = knowledge.build_session_summary()
        print(summary)
    
    elif args.action == "stats":
        stats = knowledge.memory.get_memory_stats()
        print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
