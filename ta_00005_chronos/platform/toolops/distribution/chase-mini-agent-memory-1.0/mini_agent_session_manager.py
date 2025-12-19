#!/usr/bin/env python3
"""
Mini-Agent Session Persistence System
Maintains continuity across sessions and manages work progress
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from mini_agent_memory import MiniAgentMemory
from mini_agent_knowledge import MiniAgentKnowledge

class MiniAgentSessionManager:
    """Session persistence and continuity manager"""
    
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
        self.current_session = None
        self.work_context = {}
        
    def start_working_session(self, user_name: str = "Chase", 
                             project_context: str = None) -> Dict[str, Any]:
        """Start a working session with full context"""
        
        # Initialize knowledge system
        session_data = self.knowledge.initialize_session(
            f"Working session with {user_name}, context: {project_context}"
        )
        
        self.current_session = session_data["session_id"]
        
        # Store work context
        self.work_context = {
            "user_name": user_name,
            "project_context": project_context,
            "session_start": datetime.now().isoformat(),
            "current_goals": [],
            "active_projects": [],
            "completed_tasks": [],
            "pending_work": []
        }
        
        # Record session start with full context
        self.knowledge.memory.record_interaction(
            "session_start",
            f"Working session started with {user_name}",
            {
                "agent": "system",
                "user_name": user_name,
                "project_context": project_context,
                "work_session": True
            }
        )
        
        # Store initial work context
        self._store_work_context()
        
        # Load relevant past work
        past_work = self._load_relevant_past_work(user_name, project_context)
        
        return {
            "session_id": self.current_session,
            "work_context": self.work_context,
            "past_work": past_work,
            "memory_stats": session_data["memory_stats"],
            "ready_for_work": True
        }
    
    def record_work_task(self, task_name: str, description: str, 
                        status: str = "started", 
                        context: Dict[str, Any] = None) -> str:
        """Record a work task"""
        if not self.current_session:
            raise ValueError("No active session")
        
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_name.replace(' ', '_')}"
        
        task_data = {
            "id": task_id,
            "name": task_name,
            "description": description,
            "status": status,  # started, in_progress, completed, paused, cancelled
            "context": context or {},
            "created_at": datetime.now().isoformat(),
            "session_id": self.current_session,
            "user": self.work_context.get("user_name", "unknown")
        }
        
        # Store task
        self.knowledge.memory.redis_client.hset(
            f"{self.knowledge.memory.namespace}:work_tasks",
            task_id,
            json.dumps(task_data)
        )
        
        # Update work context
        if status == "started":
            self.work_context["current_goals"].append({
                "task_id": task_id,
                "name": task_name,
                "started_at": datetime.now().isoformat()
            })
        elif status == "completed":
            self.work_context["completed_tasks"].append({
                "task_id": task_id,
                "name": task_name,
                "completed_at": datetime.now().isoformat()
            })
            
            # Remove from current goals
            self.work_context["current_goals"] = [
                goal for goal in self.work_context["current_goals"] 
                if goal["task_id"] != task_id
            ]
        
        self._store_work_context()
        
        # Record as interaction
        self.knowledge.memory.record_interaction(
            "work_task",
            f"Task '{task_name}': {description} (status: {status})",
            {
                "agent": "system",
                "task_id": task_id,
                "task_status": status,
                "context": context
            }
        )
        
        # Store knowledge about the task
        self.knowledge.memory.store_knowledge(
            "work_task",
            f"Work task: {task_name} - {description}",
            {
                "tags": ["task", task_name.replace(" ", "_").lower()],
                "task_id": task_id,
                "status": status,
                "user": self.work_context.get("user_name")
            }
        )
        
        return task_id
    
    def update_task_progress(self, task_id: str, progress: str, 
                           notes: str = None) -> bool:
        """Update task progress"""
        task_data_json = self.knowledge.memory.redis_client.hget(
            f"{self.knowledge.memory.namespace}:work_tasks",
            task_id
        )
        
        if not task_data_json:
            return False
        
        task_data = json.loads(task_data_json)
        task_data["last_update"] = datetime.now().isoformat()
        task_data["progress_notes"] = notes or ""
        
        if progress in ["in_progress", "completed", "paused"]:
            task_data["status"] = progress
        
        # Update in Redis
        self.knowledge.memory.redis_client.hset(
            f"{self.knowledge.memory.namespace}:work_tasks",
            task_id,
            json.dumps(task_data)
        )
        
        # Record interaction
        self.knowledge.memory.record_interaction(
            "task_progress",
            f"Task {task_id} progress updated: {progress}",
            {"task_id": task_id, "progress": progress, "notes": notes}
        )
        
        return True
    
    def get_current_tasks(self) -> List[Dict[str, Any]]:
        """Get all current tasks"""
        all_tasks = self.knowledge.memory.redis_client.hgetall(
            f"{self.knowledge.memory.namespace}:work_tasks"
        )
        
        current_tasks = []
        for task_id, task_data_json in all_tasks.items():
            task_data = json.loads(task_data_json)
            if task_data.get("status") in ["started", "in_progress"]:
                current_tasks.append(task_data)
        
        return sorted(current_tasks, key=lambda x: x["created_at"], reverse=True)
    
    def get_work_summary(self) -> Dict[str, Any]:
        """Get comprehensive work summary"""
        all_tasks = self.knowledge.memory.redis_client.hgetall(
            f"{self.knowledge.memory.namespace}:work_tasks"
        )
        
        tasks = [json.loads(t) for t in all_tasks.values()]
        
        # Categorize tasks
        current_tasks = [t for t in tasks if t.get("status") in ["started", "in_progress"]]
        completed_tasks = [t for t in tasks if t.get("status") == "completed"]
        paused_tasks = [t for t in tasks if t.get("status") == "paused"]
        
        # Calculate statistics
        total_time = 0
        for task in completed_tasks:
            if "completed_at" in task and "created_at" in task:
                start = datetime.fromisoformat(task["created_at"])
                end = datetime.fromisoformat(task["completed_at"])
                total_time += (end - start).total_seconds()
        
        return {
            "session_id": self.current_session,
            "user_name": self.work_context.get("user_name"),
            "project_context": self.work_context.get("project_context"),
            "session_start": self.work_context.get("session_start"),
            "task_summary": {
                "total_tasks": len(tasks),
                "current_tasks": len(current_tasks),
                "completed_tasks": len(completed_tasks),
                "paused_tasks": len(paused_tasks)
            },
            "current_tasks": current_tasks,
            "recent_completed": completed_tasks[:5],
            "total_session_time": f"{total_time/3600:.1f} hours" if total_time > 0 else "0 hours",
            "productivity_score": self._calculate_productivity_score(tasks)
        }
    
    def continue_work_from_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """Analyze user prompt and continue appropriate work"""
        
        # Analyze the prompt for intent
        intent_analysis = self._analyze_prompt_intent(user_prompt)
        
        # Get relevant past context
        relevant_knowledge = self.knowledge.get_contextual_response(user_prompt)
        
        # Get current work state
        current_tasks = self.get_current_tasks()
        
        # Generate continuation plan
        continuation_plan = self._generate_continuation_plan(
            user_prompt, intent_analysis, relevant_knowledge, current_tasks
        )
        
        return {
            "intent_analysis": intent_analysis,
            "relevant_past_context": relevant_knowledge,
            "current_work_state": {
                "active_tasks": len(current_tasks),
                "current_tasks": current_tasks
            },
            "continuation_plan": continuation_plan,
            "ready_to_continue": True
        }
    
    def save_session_checkpoint(self, checkpoint_name: str = None) -> str:
        """Save session checkpoint"""
        if not checkpoint_name:
            checkpoint_name = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        checkpoint_data = {
            "name": checkpoint_name,
            "session_id": self.current_session,
            "work_context": self.work_context,
            "current_tasks": self.get_current_tasks(),
            "memory_stats": self.knowledge.memory.get_memory_stats(),
            "created_at": datetime.now().isoformat(),
            "user_name": self.work_context.get("user_name")
        }
        
        # Store checkpoint
        self.knowledge.memory.redis_client.hset(
            f"{self.knowledge.memory.namespace}:checkpoints",
            checkpoint_name,
            json.dumps(checkpoint_data)
        )
        
        # Record checkpoint creation
        self.knowledge.memory.record_interaction(
            "checkpoint_created",
            f"Checkpoint '{checkpoint_name}' saved",
            {"checkpoint_name": checkpoint_name}
        )
        
        return checkpoint_name
    
    def load_checkpoint(self, checkpoint_name: str) -> Dict[str, Any]:
        """Load session from checkpoint"""
        checkpoint_data_json = self.knowledge.memory.redis_client.hget(
            f"{self.knowledge.memory.namespace}:checkpoints",
            checkpoint_name
        )
        
        if not checkpoint_data_json:
            return {"error": "Checkpoint not found"}
        
        checkpoint_data = json.loads(checkpoint_data_json)
        
        # Restore work context
        self.work_context = checkpoint_data["work_context"]
        self.current_session = checkpoint_data["session_id"]
        
        # Restore session in knowledge system
        self.knowledge.memory.session_id = self.current_session
        self.knowledge.session_started = True
        
        return {
            "checkpoint_loaded": True,
            "checkpoint_data": checkpoint_data,
            "restored_session": self.current_session,
            "work_context": self.work_context
        }
    
    def end_work_session(self, summary: str = None) -> Dict[str, Any]:
        """End work session with summary"""
        if not self.current_session:
            return {"error": "No active session"}
        
        # Get work summary
        work_summary = self.get_work_summary()
        
        # Save final checkpoint
        checkpoint_name = self.save_session_checkpoint("session_end")
        
        # End knowledge session
        session_end_data = self.knowledge.memory.end_session(summary or "Work session completed")
        
        # Store end work context
        self.work_context["session_end"] = datetime.now().isoformat()
        self.work_context["final_summary"] = summary
        self._store_work_context()
        
        return {
            "session_ended": True,
            "work_summary": work_summary,
            "checkpoint_saved": checkpoint_name,
            "total_interactions": session_end_data.get("total_interactions", 0),
            "knowledge_gained": session_end_data.get("knowledge_gained", 0)
        }
    
    def _store_work_context(self):
        """Store work context in Redis"""
        context_key = f"{self.knowledge.memory.namespace}:work_context:{self.current_session}"
        self.knowledge.memory.redis_client.set(
            context_key,
            json.dumps(self.work_context)
        )
    
    def _load_relevant_past_work(self, user_name: str, project_context: str) -> Dict[str, Any]:
        """Load relevant past work for context"""
        # Get past sessions for this user
        all_sessions = self.knowledge.memory.get_session_list()
        relevant_sessions = []
        
        for session_id in all_sessions[-10:]:  # Get last 10 sessions
            session_data = self.knowledge.memory.get_session_history(session_id, limit=1)
            if session_data:
                # Simple user matching (in production, use better user tracking)
                if any(user_name.lower() in str(interaction.get("content", "")).lower() 
                      for interaction in session_data):
                    relevant_sessions.append(session_id)
        
        # Get past tasks
        all_tasks = self.knowledge.memory.redis_client.hgetall(
            f"{self.knowledge.memory.namespace}:work_tasks"
        )
        past_tasks = [json.loads(t) for t in all_tasks.values()]
        
        # Get knowledge
        relevant_knowledge = self.knowledge.memory.search_knowledge(
            project_context or user_name,
            ["work_task", "tool_knowledge", "user_preference"]
        )
        
        return {
            "relevant_sessions": relevant_sessions,
            "past_tasks": past_tasks[-10:],  # Last 10 tasks
            "relevant_knowledge": relevant_knowledge[:10]  # Top 10 knowledge items
        }
    
    def _analyze_prompt_intent(self, prompt: str) -> Dict[str, Any]:
        """Analyze user prompt for intent"""
        prompt_lower = prompt.lower()
        
        # Intent patterns
        intents = {
            "continue_work": any(word in prompt_lower for word in ["continue", "resume", "carry on"]),
            "new_task": any(word in prompt_lower for word in ["new", "start", "create", "build"]),
            "check_status": any(word in prompt_lower for word in ["status", "progress", "check", "where"]),
            "help_request": any(word in prompt_lower for word in ["help", "how", "what", "why"]),
            "knowledge_query": any(word in prompt_lower for word in ["remember", "recall", "previous", "history"]),
            "tool_usage": any(word in prompt_lower for word in ["tool", "script", "run", "execute"])
        }
        
        # Extract entities
        entities = {
            "user_mentioned": self.work_context.get("user_name", "unknown").lower() in prompt_lower,
            "tools_mentioned": any(tool in prompt_lower for tool in ["redis", "database", "agent", "chat"]),
            "project_mentioned": self.work_context.get("project_context", "").lower() in prompt_lower
        }
        
        return {
            "detected_intents": [intent for intent, detected in intents.items() if detected],
            "confidence": max(intents.values()) if any(intents.values()) else 0.0,
            "entities": entities,
            "prompt_length": len(prompt),
            "complexity": "high" if len(prompt) > 200 else "medium" if len(prompt) > 50 else "low"
        }
    
    def _generate_continuation_plan(self, prompt: str, intent_analysis: Dict, 
                                  relevant_context: Dict, current_tasks: List) -> Dict[str, Any]:
        """Generate plan for continuing work"""
        intents = intent_analysis.get("detected_intents", [])
        
        plan = {
            "primary_action": None,
            "suggested_tasks": [],
            "knowledge_to_apply": [],
            "tools_to_use": []
        }
        
        if "continue_work" in intents:
            plan["primary_action"] = "continue_existing_work"
            plan["suggested_tasks"] = current_tasks[:3]
        
        elif "new_task" in intents:
            plan["primary_action"] = "create_new_task"
            # Suggest based on past work
            past_tasks = relevant_context.get("session_context", [])
            if past_tasks:
                plan["suggested_tasks"].append("Review and build upon previous work")
        
        elif "check_status" in intents:
            plan["primary_action"] = "provide_status_update"
            plan["suggested_tasks"].current_tasks
        
        elif "knowledge_query" in intents:
            plan["primary_action"] = "provide_knowledge"
            plan["knowledge_to_apply"] = relevant_context.get("related_knowledge", [])[:5]
        
        return plan
    
    def _calculate_productivity_score(self, tasks: List[Dict]) -> float:
        """Calculate productivity score for the session"""
        if not tasks:
            return 0.0
        
        completed = len([t for t in tasks if t.get("status") == "completed"])
        total = len(tasks)
        
        # Base score on completion rate
        completion_rate = completed / total if total > 0 else 0.0
        
        # Adjust for task complexity (simplified)
        complexity_bonus = sum(1 for t in tasks if len(t.get("description", "")) > 100) * 0.1
        
        return min(1.0, completion_rate + complexity_bonus)

def main():
    """Demo the session persistence system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mini-Agent Session Persistence")
    parser.add_argument("--action", required=True,
                       choices=["start", "task", "progress", "summary", "continue", "checkpoint", "end"])
    parser.add_argument("--task-name", help="Task name")
    parser.add_argument("--description", help="Task description")
    parser.add_argument("--status", help="Task status")
    parser.add_argument("--progress", help="Task progress update")
    parser.add_argument("--prompt", help="User prompt for continuation")
    parser.add_argument("--checkpoint-name", help="Checkpoint name")
    parser.add_argument("--user-name", default="Chase")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=18000)
    parser.add_argument("--redis-password", default="df_cluster_2024_adapt_research")
    
    args = parser.parse_args()
    
    session_manager = MiniAgentSessionManager(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        password=args.redis_password
    )
    
    if args.action == "start":
        result = session_manager.start_working_session(args.user_name)
        print(json.dumps(result, indent=2))
    
    elif args.action == "task":
        task_id = session_manager.record_work_task(
            args.task_name, args.description, args.status or "started"
        )
        print(f"Task created: {task_id}")
    
    elif args.action == "progress":
        success = session_manager.update_task_progress(args.task_name, args.progress)
        print(f"Progress updated: {success}")
    
    elif args.action == "summary":
        summary = session_manager.get_work_summary()
        print(json.dumps(summary, indent=2))
    
    elif args.action == "continue":
        result = session_manager.continue_work_from_prompt(args.prompt)
        print(json.dumps(result, indent=2))
    
    elif args.action == "checkpoint":
        checkpoint_name = session_manager.save_session_checkpoint(args.checkpoint_name)
        print(f"Checkpoint saved: {checkpoint_name}")
    
    elif args.action == "summary":
        end_data = session_manager.end_work_session("Session completed via CLI")
        print(json.dumps(end_data, indent=2))

if __name__ == "__main__":
    main()
