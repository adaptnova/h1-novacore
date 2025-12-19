"""
Vaeris Nova Server - Main server for Vaeris Nova with LangChain integration
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
import threading
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Import Vaeris Nova core
from .core import VaerisNova
from .model_router import ModelRouter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vaeris-nova.server")

# Initialize Flask app
app = Flask(__name__, 
           static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ui'),
           template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ui'))
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global variables for agents
model_router = ModelRouter()
active_agents = {}

# Keep track of active clients
clients = {}

@app.route('/')
def index():
    """Serve the main application page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve static files."""
    return send_from_directory(app.static_folder, path)

@app.route('/api/health')
def health_check():
    """API health check endpoint."""
    return jsonify({"status": "ok", "version": "0.1.0"})

@app.route('/api/models', methods=['GET'])
def api_get_models():
    """Get all available LLM models."""
    models = get_available_models()
    return jsonify(models)

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    client_id = request.sid
    logger.info(f"Client connected: {client_id}")
    
    # Get default model from environment or fallback
    default_model = os.environ.get('DEFAULT_MODEL', 'gpt-4o')
    
    # Initialize client data
    clients[client_id] = {
        'settings': {
            'model': default_model,
            'memory_storage': 'local',
            'stream_responses': True,
            'max_iterations': int(os.environ.get('MAX_ITERATIONS', 15)),
            'temperature': 0.7
        },
        'activity': []
    }
    
    # Create a dedicated VaerisNova agent for this client
    active_agents[client_id] = {
        'main': VaerisNova(
            name="Vaeris",
            default_model=default_model,
            memory_storage='local',
            memory_key=f"client_{client_id}",
            max_iterations=clients[client_id]['settings']['max_iterations'],
            verbose=False
        ),
        'sub_agents': {}
    }
    
    # Add activity
    clients[client_id]['activity'].append({
        'timestamp': time.time(),
        'type': 'system',
        'message': 'Connected to server'
    })
    
    emit('status', {'status': 'ready', 'message': 'Agent initialized successfully'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    client_id = request.sid
    logger.info(f"Client disconnected: {client_id}")
    
    # Clean up client resources
    if client_id in clients:
        del clients[client_id]
    
    # Clean up agent resources
    if client_id in active_agents:
        # Save agent state if needed
        if hasattr(active_agents[client_id]['main'], 'save_state'):
            try:
                active_agents[client_id]['main'].save_state()
            except Exception as e:
                logger.error(f"Failed to save agent state: {e}")
        
        # Clean up sub-agents
        for agent_id in list(active_agents[client_id]['sub_agents'].keys()):
            del active_agents[client_id]['sub_agents'][agent_id]
        
        # Remove main agent
        del active_agents[client_id]

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages from clients."""
    client_id = request.sid
    if client_id not in clients or client_id not in active_agents:
        emit('error', {'message': 'Client not initialized'})
        return
    
    # Parse message data
    message = data.get('message', '')
    agent_id = data.get('agent_id', None)
    
    # Log the activity
    clients[client_id]['activity'].append({
        'timestamp': time.time(),
        'type': 'user',
        'message': message
    })
    
    # Send processing status
    emit('status', {'status': 'processing', 'message': 'Processing your request'})
    
    start_time = time.time()
    
    # Get the appropriate agent
    if agent_id and agent_id in active_agents[client_id]['sub_agents']:
        agent = active_agents[client_id]['sub_agents'][agent_id]
    else:
        agent = active_agents[client_id]['main']
        agent_id = None  # Use None for main agent
    
    # Streaming handler for response chunks
    def handle_stream(chunk: str, **kwargs):
        if clients[client_id]['settings'].get('stream_responses', True):
            emit('stream', {
                'agent_id': agent_id,
                'chunk': chunk
            })
    
    try:
        # Process with actual agent
        if clients[client_id]['settings'].get('stream_responses', True):
            # Set up streaming callback
            from langchain_core.callbacks import StreamingStdOutCallbackHandler
            from langchain_core.callbacks import CallbackManager
            
            class SocketIOCallbackHandler(StreamingStdOutCallbackHandler):
                def on_llm_new_token(self, token: str, **kwargs) -> None:
                    handle_stream(token)
            
            # Create callback manager
            callback_manager = CallbackManager([SocketIOCallbackHandler()])
            
            # Create streaming-enabled model
            current_model_name = clients[client_id]['settings']['model']
            streaming_model = model_router.get_model(
                model_name=current_model_name,
                temperature=clients[client_id]['settings']['temperature'],
                streaming=True,
                callbacks=[SocketIOCallbackHandler()]
            )
            
            # Store the original model
            original_model = agent.default_llm
            
            # Set the streaming model
            agent.default_llm = streaming_model
            
            # Get recent history to provide context
            chat_history = []  # Will be populated by memory system
            
            # Run the inference
            result = agent.invoke(message, chat_history=chat_history)
            
            # Restore original model
            agent.default_llm = original_model
        else:
            # Non-streaming mode
            # Get recent history to provide context
            chat_history = []  # Will be populated by memory system
            
            # Run the inference
            result = agent.invoke(message, chat_history=chat_history)
        
        # Extract response content
        ai_message = result.get('output', '')
        if not ai_message and 'response' in result:
            ai_message = result['response']
        
        # Extract tool usage information
        tools_used = []
        if 'intermediate_steps' in result:
            for step in result.get('intermediate_steps', []):
                if len(step) >= 2:
                    action = step[0]
                    output = step[1]
                    tools_used.append({
                        'name': getattr(action, 'tool', 'unknown'),
                        'input': getattr(action, 'tool_input', {}),
                        'output': output
                    })
                    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ai_message = f"I encountered an error while processing your request: {str(e)}"
        tools_used = []
    
    processing_time = time.time() - start_time
    
    # Send complete response
    emit('response', {
        'agent_id': agent_id,
        'message': ai_message,
        'processing_time': processing_time,
        'tools_used': tools_used
    })
    
    # Update status
    emit('status', {
        'status': 'ready',
        'message': 'Ready for next input'
    })
    
    # Log the activity
    clients[client_id]['activity'].append({
        'timestamp': time.time(),
        'type': 'ai',
        'message': f"Responded to: {message[:30]}{'...' if len(message) > 30 else ''}",
        'processing_time': processing_time
    })

@socketio.on('create_agent')
def handle_create_agent(data):
    """Create a new sub-agent."""
    client_id = request.sid
    if client_id not in clients or client_id not in active_agents:
        emit('error', {'message': 'Client not initialized'})
        return
    
    # Parse agent creation data
    name = data.get('name', 'SubAgent')
    model = data.get('model', 'gpt-4o')
    specialization = data.get('specialization', 'general')
    system_prompt = data.get('system_prompt', None)
    tool_access = data.get('tools', {})
    
    # Generate a unique ID for the sub-agent
    agent_id = f"agent_{int(time.time())}_{hash(name) % 10000}"
    
    try:
        # Create sub-agent using the main agent's create_subagent method
        main_agent = active_agents[client_id]['main']
        
        # Configure tools for the subagent
        selected_tools = []
        # Tool configuration will be implemented in the tool management section
        
        # Create a custom system prompt based on specialization if not provided
        if not system_prompt:
            if specialization == 'code':
                system_prompt = f"You are {name}, a specialized coding assistant. You are excellent at writing, reviewing, and debugging code across various programming languages."
            elif specialization == 'research':
                system_prompt = f"You are {name}, a specialized research assistant. You excel at finding, analyzing, and summarizing information on a wide range of topics."
            elif specialization == 'data':
                system_prompt = f"You are {name}, a specialized data analysis assistant. You excel at working with data, creating visualizations, and extracting insights."
            elif specialization == 'creative':
                system_prompt = f"You are {name}, a specialized creative assistant. You excel at creative writing, generating ideas, and helping with artistic projects."
            else:
                system_prompt = f"You are {name}, a specialized sub-agent of Vaeris Nova."
        
        # Create the sub-agent
        sub_agent = main_agent.create_subagent(
            name=name,
            system_prompt=system_prompt,
            model=model,
            tools=selected_tools
        )
        
        # Store the sub-agent
        active_agents[client_id]['sub_agents'][agent_id] = sub_agent
        
        # Log activity
        clients[client_id]['activity'].append({
            'timestamp': time.time(),
            'type': 'system',
            'message': f'Created sub-agent: {name} ({model}) with specialization: {specialization}'
        })
        
        # Return success with agent info
        emit('agent_created', {
            'agent_id': agent_id,
            'name': name,
            'model': model,
            'specialization': specialization
        })
        
    except Exception as e:
        logger.error(f"Failed to create sub-agent: {e}")
        emit('error', {'message': f'Failed to create sub-agent: {str(e)}'})
        return

@socketio.on('update_settings')
def handle_update_settings(data):
    """Update client settings."""
    client_id = request.sid
    if client_id not in clients or client_id not in active_agents:
        emit('error', {'message': 'Client not initialized'})
        return
    
    model_changed = False
    current_model = clients[client_id]['settings'].get('model')
    
    # Update settings
    for key, value in data.items():
        clients[client_id]['settings'][key] = value
        
        # Check if model was changed
        if key == 'model' and value != current_model:
            model_changed = True
    
    # If model changed, update the agent's model
    if model_changed and 'model' in data:
        try:
            new_model = data['model']
            main_agent = active_agents[client_id]['main']
            
            # Get the new model instance
            new_model_instance = model_router.get_model(
                model_name=new_model,
                temperature=clients[client_id]['settings'].get('temperature', 0.7),
                streaming=False
            )
            
            # Update the agent's model
            main_agent.default_model = new_model
            main_agent.default_llm = new_model_instance
            
            # Also update the agent's prompt
            if hasattr(main_agent, 'agent') and hasattr(main_agent.agent, 'llm'):
                main_agent.agent.llm = new_model_instance
            
            logger.info(f"Updated agent model to {new_model}")
        except Exception as e:
            logger.error(f"Failed to update agent model: {e}")
    
    # Log activity
    clients[client_id]['activity'].append({
        'timestamp': time.time(),
        'type': 'system',
        'message': f'Updated settings: {", ".join(f"{k}={v}" for k, v in data.items())}'
    })
    
    emit('settings_updated', {'success': True})

@socketio.on('get_activity_log')
def handle_get_activity_log():
    """Get the client's activity log."""
    client_id = request.sid
    if client_id not in clients:
        emit('error', {'message': 'Client not initialized'})
        return
    
    emit('activity_log', {
        'activities': clients[client_id]['activity'][-50:]  # Return last 50 activities
    })

@socketio.on('clear_memory')
def handle_clear_memory(data):
    """Clear agent memory."""
    client_id = request.sid
    if client_id not in clients or client_id not in active_agents:
        emit('error', {'message': 'Client not initialized'})
        return
    
    agent_id = data.get('agent_id', None)
    
    try:
        # Get the appropriate agent
        if agent_id and agent_id in active_agents[client_id]['sub_agents']:
            agent = active_agents[client_id]['sub_agents'][agent_id]
        else:
            agent = active_agents[client_id]['main']
            agent_id = None  # Use None for main agent
        
        # Clear the agent's memory
        if hasattr(agent, 'memory_manager') and hasattr(agent.memory_manager, 'clear_memory'):
            agent.memory_manager.clear_memory()
        
        # Clear conversation memory if available
        if hasattr(agent, 'memory') and hasattr(agent.memory, 'clear'):
            agent.memory.clear()
        
        logger.info(f"Cleared memory for {agent_id if agent_id else 'main agent'}")
        
        # Log the action
        clients[client_id]['activity'].append({
            'timestamp': time.time(),
            'type': 'system',
            'message': f'Cleared memory for {agent_id if agent_id else "main agent"}'
        })
        
        emit('memory_cleared', {'success': True, 'agent_id': agent_id})
    
    except Exception as e:
        logger.error(f"Failed to clear memory: {e}")
        emit('error', {'message': f'Failed to clear memory: {str(e)}'})

def get_available_models():
    """Get a list of available LLM models."""
    try:
        # Get models from the model router
        available_models = model_router.get_all_available_models()
        return available_models
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        
        # Return minimal set of models if we can't get the actual list
        return [
            {
                "name": "gpt-4o",
                "provider": "OpenAI",
                "available": True,
                "capabilities": {
                    "reasoning": 0.95,
                    "creativity": 0.90,
                    "knowledge": 0.92,
                    "instruction_following": 0.95,
                    "cost_efficiency": 0.75,
                    "long_context": 0.85
                },
                "is_default": True
            },
            {
                "name": "claude-3-opus",
                "provider": "Anthropic",
                "available": True,
                "capabilities": {
                    "reasoning": 0.95,
                    "creativity": 0.85,
                    "knowledge": 0.90,
                    "instruction_following": 0.97,
                    "cost_efficiency": 0.65,
                    "long_context": 0.93
                },
                "is_default": False
            }
        ]

def main():
    """Main entry point for running the server."""
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Initialize main model router and agents
    global model_router, active_agents
    model_router = ModelRouter()
    
    # Setup eventlet for socketio (uncomment if using eventlet)
    # import eventlet
    # eventlet.monkey_patch()
    
    logger.info(f"Starting Vaeris Nova server on port {port} (debug={debug})")
    
    # Use basic Flask development server for testing
    app.run(host='0.0.0.0', port=port, debug=debug)
    
    # For production, use socketio with eventlet
    # socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()