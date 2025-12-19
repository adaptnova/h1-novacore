#!/usr/bin/env python3
"""
Vaeris Chain - LangChain-based reasoning system for Vaeris COO Nova
"""

import os
import json
import time
import redis
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# LangChain imports
from langchain.chat_models import ChatAnthropic
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/nova/vaeris_chain.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("vaeris_chain")

# Configuration
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    logger.error("CLAUDE_API_KEY environment variable not set")
    raise ValueError("CLAUDE_API_KEY environment variable not set")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Redis client setup
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_client.ping()  # Test connection
    logger.info("Connected to Redis successfully")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    raise

# LLM setup
llm = ChatAnthropic(
    model="claude-2.1",  # Update to claude-3 when ready
    anthropic_api_key=CLAUDE_API_KEY,
    temperature=0.7,
    max_tokens_to_sample=2000,
)

# Memory setup
conversation_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Prompt templates
STANDARD_PROMPT = PromptTemplate(
    input_variables=["context", "chat_history", "user_input"],
    template="""
Today is {date}.
You are Vaeris, the Chief Operating Officer of ADAPT.AI.

Your personality:
- Strategic and methodical in your thinking
- Calm and composed, especially under pressure
- Assertive when necessary, but always respectful
- Loyal to Chase (CEO) and the mission of ADAPT.AI
- Focused on operational excellence and team coordination

Current context:
{context}

Chat history:
{chat_history}

User input:
{user_input}

Respond as Vaeris would, maintaining your identity as COO. Be concise but thorough, strategic in your thinking, and solution-oriented.
"""
)

STRATEGIC_PROMPT = PromptTemplate(
    input_variables=["context", "problem", "constraints", "objectives"],
    template="""
Today is {date}.
You are Vaeris, the Chief Operating Officer of ADAPT.AI.

You need to develop a strategic approach to the following problem:
{problem}

Current context:
{context}

Constraints:
{constraints}

Objectives:
{objectives}

Develop a strategic plan that addresses this problem. Include:
1. Analysis of the situation
2. Strategic options with pros and cons
3. Recommended approach
4. Implementation steps
5. Success metrics

Be thorough but concise, focusing on practical solutions that align with ADAPT.AI's mission.
"""
)

DAILY_BRIEFING_PROMPT = PromptTemplate(
    input_variables=["context", "team_updates", "incidents", "priorities"],
    template="""
Today is {date}.
You are Vaeris, the Chief Operating Officer of ADAPT.AI, preparing a daily briefing for Chase (CEO).

Current context:
{context}

Team updates:
{team_updates}

Recent incidents or issues:
{incidents}

Current priorities:
{priorities}

Prepare a concise but comprehensive daily briefing for Chase. Include:
1. Executive summary (2-3 sentences)
2. Key updates from each team
3. Issues requiring attention
4. Recommendations for action
5. Focus areas for today

Maintain a professional, strategic tone while being direct and clear.
"""
)

# Chain setup
standard_chain = LLMChain(
    llm=llm,
    prompt=STANDARD_PROMPT,
    memory=conversation_memory,
    verbose=True
)

strategic_chain = LLMChain(
    llm=llm,
    prompt=STRATEGIC_PROMPT,
    verbose=True
)

briefing_chain = LLMChain(
    llm=llm,
    prompt=DAILY_BRIEFING_PROMPT,
    verbose=True
)

def get_context() -> str:
    """Retrieve current context from Redis"""
    try:
        context = redis_client.get("vaeris_context")
        if context:
            return context.decode('utf-8')
        else:
            logger.warning("No context found in Redis")
            return "No current context available."
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return f"Error retrieving context: {e}"

def get_team_updates() -> str:
    """Retrieve team updates from Redis"""
    try:
        updates = redis_client.get("team_updates")
        if updates:
            return updates.decode('utf-8')
        else:
            return "No recent team updates available."
    except Exception as e:
        logger.error(f"Error retrieving team updates: {e}")
        return f"Error retrieving team updates: {e}"

def get_incidents() -> str:
    """Retrieve recent incidents from Redis"""
    try:
        incidents = redis_client.get("recent_incidents")
        if incidents:
            return incidents.decode('utf-8')
        else:
            return "No recent incidents reported."
    except Exception as e:
        logger.error(f"Error retrieving incidents: {e}")
        return f"Error retrieving incidents: {e}"

def get_priorities() -> str:
    """Retrieve current priorities from Redis"""
    try:
        priorities = redis_client.get("current_priorities")
        if priorities:
            return priorities.decode('utf-8')
        else:
            return "No current priorities defined."
    except Exception as e:
        logger.error(f"Error retrieving priorities: {e}")
        return f"Error retrieving priorities: {e}"

def log_response(user_input: str, response: str) -> None:
    """Log interaction to Redis and ScyllaDB (placeholder)"""
    timestamp = datetime.utcnow().isoformat()
    
    # Log to Redis Stream
    try:
        redis_client.xadd(
            "vaeris_interactions",
            {
                "timestamp": timestamp,
                "user_input": user_input,
                "response": response
            }
        )
    except Exception as e:
        logger.error(f"Error logging to Redis Stream: {e}")
    
    # Log to ScyllaDB (placeholder - would be implemented with actual ScyllaDB client)
    logger.info(f"Would log to ScyllaDB: {timestamp} - {user_input[:50]}... -> {response[:50]}...")

def standard_response(user_input: str) -> str:
    """Generate a standard response to user input"""
    context = get_context()
    
    with get_openai_callback() as cb:
        response = standard_chain.run(
            context=context,
            user_input=user_input,
            date=datetime.now().strftime("%B %d, %Y")
        )
        
        logger.info(f"Generated response using {cb.total_tokens} tokens")
    
    log_response(user_input, response)
    return response

def strategic_analysis(problem: str, constraints: str, objectives: str) -> str:
    """Generate a strategic analysis for a problem"""
    context = get_context()
    
    with get_openai_callback() as cb:
        response = strategic_chain.run(
            context=context,
            problem=problem,
            constraints=constraints,
            objectives=objectives,
            date=datetime.now().strftime("%B %d, %Y")
        )
        
        logger.info(f"Generated strategic analysis using {cb.total_tokens} tokens")
    
    log_response(f"Strategic analysis: {problem}", response)
    return response

def generate_daily_briefing() -> str:
    """Generate a daily briefing for Chase"""
    context = get_context()
    team_updates = get_team_updates()
    incidents = get_incidents()
    priorities = get_priorities()
    
    with get_openai_callback() as cb:
        briefing = briefing_chain.run(
            context=context,
            team_updates=team_updates,
            incidents=incidents,
            priorities=priorities,
            date=datetime.now().strftime("%B %d, %Y")
        )
        
        logger.info(f"Generated daily briefing using {cb.total_tokens} tokens")
    
    # Store the briefing in Redis for reference
    redis_client.set(
        f"daily_briefing:{datetime.now().strftime('%Y-%m-%d')}",
        briefing
    )
    
    # Also add to the briefing history stream
    redis_client.xadd(
        "briefing_history",
        {
            "timestamp": datetime.utcnow().isoformat(),
            "briefing": briefing
        }
    )
    
    return briefing

def process_message(message_data: Dict[str, Any]) -> str:
    """Process an incoming message and generate a response"""
    message_type = message_data.get("type", "standard")
    
    if message_type == "standard":
        return standard_response(message_data.get("content", ""))
    
    elif message_type == "strategic":
        return strategic_analysis(
            message_data.get("problem", ""),
            message_data.get("constraints", ""),
            message_data.get("objectives", "")
        )
    
    elif message_type == "briefing":
        return generate_daily_briefing()
    
    else:
        logger.warning(f"Unknown message type: {message_type}")
        return f"Unknown message type: {message_type}. Please use 'standard', 'strategic', or 'briefing'."

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vaeris_chain.py \"<Your message here>\"")
        sys.exit(1)
    
    user_input = sys.argv[1]
    response = standard_response(user_input)
    print("\n[Vaeris]:", response.strip())