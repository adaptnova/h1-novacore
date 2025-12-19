#!/usr/bin/env python3
"""
Mini-Agent Core Integration Layer
Unified interface for memory, knowledge, and session management
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from mini_agent_memory import MiniAgentMemory
from mini_agent_knowledge import MiniAgentKnowledge
from mini_agent_session_manager import MiniAgentSessionManager

class MiniAgentCore:
    """Core integration for Mini-Agent's persistent capabilities"""
    
    def __init__(self, redis_host="localhost", redis_port=18000, password=None):
        self.memory = MiniAgentMemory(
            redis_host=redis_host,
            redis_port=redis_port,
            password=password
        )
        self.knowledge = MiniAgentKnowledge(
            redis_host=redis_host,
            redis_port=redis_port,
            password=password
        )
        self.session_manager = MiniAgentSessionManager(
            redis_host=redis_host,
            redis_port=redis_port,
            password=password
        )
        
        self.current_session = None
        self.user_context = {}
        self.system_initialized = False
        
        # Initialize the system
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize Mini-Agent core system"""
        print("🧠 Initializing Mini-Agent Core Memory System...")
        print(f"   Connected to: {self.memory.redis_host}:{self.memory.redis_port}")
        print(f"   Memory namespace: {self.memory.namespace}")
        
        # Check if system is already initialized
        init_knowledge = self.memory.search_knowledge("system initialization")
        
        if not init_knowledge:
            # First-time initialization
            self._perform_initial_setup()
        else:
            print("   ✓ Memory system already initialized")
        
        self.system_initialized = True
        print("   ✅ Mini-Agent Core ready!")
    
    def _perform_initial_setup(self):
        """Perform initial system setup"""
        print("   🔧 Performing initial setup...")
        
        # Create initial knowledge
        self.memory.store_knowledge(
            "system",
            "Mini-Agent Core Memory System initialized",
            {
                "tags": ["memory", "system", "initialization"],
                "setup_timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
        )
        
        # Store system capabilities
        capabilities = [
            "Persistent session memory",
            "Knowledge extraction and storage",
            "User preference learning",
            "Tool execution tracking",
            "Session continuity",
            "Work task management",
            "Intelligent suggestions",
            "Contextual responses"
        ]
        
        for capability in capabilities:
            self.memory.store_knowledge(
                "capability",
                f"System capability: {capability}",
                {
                    "tags": ["capability", "system"],
                    "capability_type": "core"
                }
            )
        
        print(f"   ✓ Created {len(capabilities)} core capabilities")
    
    def start_work_session(self, user_name: str = "Chase", 
                          project_context: str = None) -> Dict[str, Any]:
        """Start a work session with full context"""
        print(f"🚀 Starting work session for {user_name}...")
        
        session_data = self.session_manager.start_working_session(
            user_name=user_name,
            project_context=project_context
        )
        
        self.current_session = session_data["session_id"]
        self.user_context = {
            "name": user_name,
            "project_context": project_context,
            "session_start": datetime.now().isoformat()
        }
        
        # Learn user preference for full paths
        self.learn_user_preference("command_preference", "full_paths", 
                                  "User prefers full path commands")
        
        # Store session start knowledge
        self.knowledge.memory.store_knowledge(
            "session_start",
            f"Work session started with {user_name}",
            {
                "tags": ["session", user_name.lower()],
                "user": user_name,
                "project_context": project_context
            }
        )
        
        print(f"   ✅ Session started: {self.current_session}")
        
        return session_data
    
    def process_user_interaction(self, user_input: str, 
                               agent_response: str = None,
                               tools_used: List[str] = None) -> Dict[str, Any]:
        """Process a user interaction and build knowledge"""
        if not self.current_session:
            # Auto-start session if none exists
            self.start_work_session()
        
        # Process the interaction
        insights = self.knowledge.process_user_input(user_input, agent_response)
        
        # Record tool usage
        if tools_used:
            for tool in tools_used:
                self.knowledge.memory.store_knowledge(
                    "tool_usage",
                    f"Used tool: {tool} in response to user",
                    {
                        "tags": ["tool", tool],
                        "user_input": user_input[:100]
                    }
                )
        
        # Learn from user input patterns
        self._analyze_and_learn_patterns(user_input, agent_response)
        
        # Get contextual response
        context = self.knowledge.get_contextual_response(user_input)
        
        return {
            "interaction_processed": True,
            "insights": insights,
            "context": context,
            "session_id": self.current_session,
            "ready_for_next": True
        }
    
    def record_work_progress(self, task_name: str, description: str,
                           status: str = "in_progress",
                           notes: str = None) -> str:
        """Record work progress"""
        if not self.current_session:
            self.start_work_session()
        
        task_id = self.session_manager.record_work_task(
            task_name=task_name,
            description=description,
            status=status,
            context={"notes": notes}
        )
        
        print(f"📝 Work progress recorded: {task_name} ({status})")
        
        return task_id
    
    def get_intelligent_response(self, user_prompt: str) -> Dict[str, Any]:
        """Get intelligent response based on stored knowledge"""
        # Search for relevant knowledge
        relevant_knowledge = self.knowledge.memory.search_knowledge(user_prompt)
        
        # Get user preferences
        preferences = self.knowledge.memory.redis_client.hgetall(
            f"{self.knowledge.memory.namespace}:user_preferences"
        )
        
        # Get session history
        session_history = self.knowledge.memory.get_session_history(limit=10)
        
        # Get current work context
        current_tasks = self.session_manager.get_current_tasks() if self.current_session else []
        
        # Generate intelligent suggestions
        suggestions = self.knowledge.get_intelligent_suggestions(user_prompt)
        
        return {
            "relevant_knowledge": relevant_knowledge[:5],
            "user_preferences": preferences,
            "session_context": {
                "current_tasks": current_tasks,
                "session_id": self.current_session,
                "interactions": len(session_history)
            },
            "intelligent_suggestions": suggestions,
            "contextual_insights": self._generate_insights(user_prompt, relevant_knowledge),
            "recommended_actions": self._recommend_actions(user_prompt, relevant_knowledge, current_tasks)
        }
    
    def learn_user_preference(self, preference_key: str, value: Any, 
                             context: str = None) -> bool:
        """Learn a user preference"""
        success = self.knowledge.learn_user_preference(preference_key, value, context)
        
        if success:
            print(f"🧠 Learned preference: {preference_key} = {value}")
        
        return success
    
    def save_session_checkpoint(self, checkpoint_name: str = None) -> str:
        """Save current session checkpoint"""
        if not self.current_session:
            return "No active session to checkpoint"
        
        checkpoint_name = self.session_manager.save_session_checkpoint(checkpoint_name)
        print(f"💾 Session checkpoint saved: {checkpoint_name}")
        
        return checkpoint_name
    
    def continue_work_continuously(self, user_prompt: str) -> Dict[str, Any]:
        """Continuously work based on user prompt"""
        # Analyze prompt for continuation
        continuation_plan = self.session_manager.continue_work_from_prompt(user_prompt)
        
        # Get current work state
        work_summary = self.session_manager.get_work_summary()
        
        # Generate next steps
        next_steps = self._generate_next_steps(user_prompt, continuation_plan, work_summary)
        
        return {
            "continuation_plan": continuation_plan,
            "current_work_state": work_summary,
            "next_steps": next_steps,
            "ready_for_execution": True
        }
    
    def get_work_summary(self) -> Dict[str, Any]:
        """Get comprehensive work summary"""
        if not self.current_session:
            return {"error": "No active session"}
        
        return self.session_manager.get_work_summary()
    
    def end_session(self, summary: str = None) -> Dict[str, Any]:
        """End current session"""
        if not self.current_session:
            return {"error": "No active session"}
        
        end_data = self.session_manager.end_work_session(summary)
        
        # Store final knowledge
        self.memory.store_knowledge(
            "session_end",
            f"Session ended: {summary}" if summary else "Session ended",
            {
                "tags": ["session", "end"],
                "session_duration": end_data.get("total_interactions", 0),
                "user": self.user_context.get("name")
            }
        )
        
        print(f"👋 Session ended: {self.current_session}")
        print(f"   Interactions: {end_data.get('total_interactions', 0)}")
        print(f"   Knowledge gained: {end_data.get('knowledge_gained', 0)}")
        
        self.current_session = None
        self.user_context = {}
        
        return end_data
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics"""
        stats = self.memory.get_memory_stats()
        
        # Add session-specific stats
        if self.current_session:
            session_stats = {
                "current_session_id": self.current_session,
                "user_name": self.user_context.get("name"),
                "session_duration": self._calculate_session_duration()
            }
            stats["current_session"] = session_stats
        
        return stats
    
    def _analyze_and_learn_patterns(self, user_input: str, agent_response: str = None):
        """Analyze and learn patterns from interactions"""
        # Learn command preferences
        if "full path" in user_input.lower() or "/adaptai" in user_input:
            self.learn_user_preference("command_style", "full_paths", 
                                      "User prefers full path commands")
        
        # Learn communication patterns
        if any(word in user_input.lower() for word in ["remember", "save", "store"]):
            self.learn_user_preference("memory_usage", "frequent", 
                                      "User frequently asks to save/remember information")
        
        # Learn work patterns
        if any(word in user_input.lower() for word in ["tool", "create", "build"]):
            self.learn_user_preference("work_style", "tool_building", 
                                      "User prefers creating and using tools")
        
        # Learn project patterns
        if any(word in user_input.lower() for word in ["database", "agent", "communication"]):
            self.learn_user_preference("project_type", "database_infrastructure", 
                                      "User works on database and agent infrastructure")
    
    def _generate_insights(self, prompt: str, knowledge: List[Dict]) -> List[str]:
        """Generate insights based on prompt and knowledge"""
        insights = []
        
        if knowledge:
            insights.append(f"Found {len(knowledge)} relevant knowledge items")
        
        # Pattern recognition
        prompt_lower = prompt.lower()
        if "memory" in prompt_lower:
            insights.append("User is asking about memory/persistence features")
        elif "agent" in prompt_lower:
            insights.append("User is working with agent systems")
        elif "database" in prompt_lower:
            insights.append("User is working with database infrastructure")
        
        return insights
    
    def _recommend_actions(self, prompt: str, knowledge: List[Dict], 
                          tasks: List[Dict]) -> List[str]:
        """Recommend actions based on context"""
        recommendations = []
        
        # Task-based recommendations
        if not tasks:
            recommendations.append("No active tasks - ready to start new work")
        else:
            recommendations.append(f"Continue with {len(tasks)} active tasks")
        
        # Knowledge-based recommendations
        if knowledge:
            recommendations.append("Apply relevant past knowledge")
        
        # Pattern-based recommendations
        prompt_lower = prompt.lower()
        if "continue" in prompt_lower:
            recommendations.append("Continue previous work")
        elif "new" in prompt_lower or "create" in prompt_lower:
            recommendations.append("Start new task or project")
        elif "help" in prompt_lower:
            recommendations.append("Provide assistance and guidance")
        
        return recommendations
    
    def _generate_next_steps(self, prompt: str, continuation_plan: Dict, 
                           work_summary: Dict) -> List[str]:
        """Generate specific next steps"""
        next_steps = []
        
        plan = continuation_plan.get("continuation_plan", {})
        action = plan.get("primary_action")
        
        if action == "continue_existing_work":
            next_steps.append("Continue with existing active tasks")
            for task in plan.get("suggested_tasks", []):
                next_steps.append(f"Work on: {task.get('name', 'Unknown task')}")
        
        elif action == "create_new_task":
            next_steps.append("Create and start new task")
            next_steps.append("Define task objectives and scope")
        
        elif action == "provide_status_update":
            next_steps.append("Provide comprehensive status update")
            next_steps.append("Show current progress and next steps")
        
        elif action == "provide_knowledge":
            next_steps.append("Share relevant knowledge and context")
            for item in plan.get("knowledge_to_apply", []):
                next_steps.append(f"Apply knowledge: {item.get('type', 'Unknown')}")
        
        return next_steps
    
    def _calculate_session_duration(self) -> str:
        """Calculate current session duration"""
        if not self.current_session or not self.user_context.get("session_start"):
            return "Unknown"
        
        start_time = datetime.fromisoformat(self.user_context["session_start"])
        duration = datetime.now() - start_time
        
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

def main():
    """Demo the Mini-Agent Core integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mini-Agent Core Integration")
    parser.add_argument("--action", required=True,
                       choices=["init", "start", "process", "response", "progress", 
                               "summary", "continue", "checkpoint", "stats", "end"])
    parser.add_argument("--user-input", help="User input text")
    parser.add_argument("--agent-response", help="Agent response text")
    parser.add_argument("--tools", nargs="*", help="Tools used")
    parser.add_argument("--task-name", help="Task name")
    parser.add_argument("--description", help="Task description")
    parser.add_argument("--status", help="Task status")
    parser.add_argument("--prompt", help="User prompt for continuation")
    parser.add_argument("--checkpoint-name", help="Checkpoint name")
    parser.add_argument("--user-name", default="Chase")
    parser.add_argument("--project-context", help="Project context")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=18000)
    parser.add_argument("--redis-password", default="df_cluster_2024_adapt_research")
    
    args = parser.parse_args()
    
    # Initialize Mini-Agent Core
    core = MiniAgentCore(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        password=args.redis_password
    )
    
    if args.action == "init":
        print("✅ Mini-Agent Core initialized")
        stats = core.get_memory_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.action == "start":
        result = core.start_work_session(args.user_name, args.project_context)
        print(json.dumps(result, indent=2))
    
    elif args.action == "process":
        result = core.process_user_interaction(
            args.user_input,
            args.agent_response,
            args.tools
        )
        print(json.dumps(result, indent=2))
    
    elif args.action == "response":
        result = core.get_intelligent_response(args.user_input)
        print(json.dumps(result, indent=2))
    
    elif args.action == "progress":
        task_id = core.record_work_progress(
            args.task_name,
            args.description,
            args.status or "in_progress"
        )
        print(f"Task recorded: {task_id}")
    
    elif args.action == "summary":
        summary = core.get_work_summary()
        print(json.dumps(summary, indent=2))
    
    elif args.action == "continue":
        result = core.continue_work_continuously(args.prompt)
        print(json.dumps(result, indent=2))
    
    elif args.action == "checkpoint":
        checkpoint_name = core.save_session_checkpoint(args.checkpoint_name)
        print(f"Checkpoint saved: {checkpoint_name}")
    
    elif args.action == "stats":
        stats = core.get_memory_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.action == "end":
        end_data = core.end_session("Session ended via CLI")
        print(json.dumps(end_data, indent=2))

if __name__ == "__main__":
    main()
