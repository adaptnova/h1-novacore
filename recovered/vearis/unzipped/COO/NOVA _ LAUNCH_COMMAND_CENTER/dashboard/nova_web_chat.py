import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from nova_unified_communication import NovaUnifiedCommunication
import threading
import logging

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NovaWebChat')
logger.setLevel(logging.DEBUG)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Store Nova instances and their states
nova_instances = {}
nova_locks = {}
nova_states = {}  # Track pause state

@app.route('/')
def index():
    logger.debug("Index route accessed")
    try:
        template_path = os.path.join(app.template_folder, 'chat.html')
        if not os.path.exists(template_path):
            logger.error(f"Template not found at {template_path}")
            return "Template not found", 404
            
        logger.debug(f"Template found at {template_path}")
        return render_template('chat.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return str(e), 500

@socketio.on('connect_nova')
def handle_nova_connect(data):
    nova_id = data['nova_id']
    if nova_id in nova_instances:
        # If it's the same session, just acknowledge
        emit('system_message', {'message': f'Welcome back, {nova_id}!'})
        return
    
    try:
        # Create a new Nova instance
        nova = NovaUnifiedCommunication(nova_id)
        nova_instances[nova_id] = nova
        nova_locks[nova_id] = threading.Lock()
        nova_states[nova_id] = {'paused': False}

        def message_callback(message):
            if not nova_states[nova_id]['paused']:
                with nova_locks[nova_id]:
                    # Add target information to the message
                    if 'target' not in message:
                        message['target'] = 'All'
                    socketio.emit('message', message)

        nova.register_callback('chat', message_callback)
        logger.info(f'{nova_id} connected')
        emit('system_message', {'message': f'Welcome to ADAPT Team Chat, {nova_id}!'})
        
        # Announce new connection to others
        for other_id, other_nova in nova_instances.items():
            if other_id != nova_id:
                other_nova.send_message(nova_id, 'system', f'{nova_id} has joined the chat')
                
    except Exception as e:
        logger.error(f'Error connecting {nova_id}: {str(e)}')
        emit('system_message', {'message': f'Error connecting: {str(e)}'})

@socketio.on('send_message')
def handle_send_message(data):
    nova_id = 'Chase'  # We're always Chase in this interface
    if nova_id not in nova_instances or nova_states[nova_id]['paused']:
        return

    message = data['message']
    target = data['target']
    
    try:
        with nova_locks[nova_id]:
            if target == 'broadcast':
                nova_instances[nova_id].broadcast_message('chat', message)
            else:
                nova_instances[nova_id].send_message(target, 'chat', message)
    except Exception as e:
        logger.error(f'Error sending message: {str(e)}')
        emit('system_message', {'message': f'Error sending message: {str(e)}'})

@socketio.on('personal_pause')
def handle_personal_pause(data):
    paused = data.get('paused', False)
    nova_id = 'Chase'  # In this interface, we're always Chase
    if nova_id in nova_states:
        nova_states[nova_id]['paused'] = paused
        logger.info(f'{"Paused" if paused else "Resumed"} messages for {nova_id}')

@socketio.on('global_pause')
def handle_global_pause(data):
    paused = data.get('paused', False)
    nova_id = 'Chase'  # In this interface, we're always Chase
    if nova_id in nova_instances:
        try:
            if paused:
                # Tell everyone to pause
                nova_instances[nova_id].broadcast_message('system', {
                    'action': 'pause',
                    'from': nova_id,
                    'message': f'Chat paused by {nova_id}'
                })
            else:
                # Tell everyone to resume
                nova_instances[nova_id].broadcast_message('system', {
                    'action': 'resume',
                    'from': nova_id,
                    'message': f'Chat resumed by {nova_id}'
                })
        except Exception as e:
            logger.error(f'Error handling global pause: {str(e)}')

@socketio.on('disconnect')
def handle_disconnect():
    # Keep Nova instances running even if web client disconnects
    logger.info('Web client disconnected')

def send_welcome_message(nova_instance):
    """Send a fun welcome message"""
    welcome_messages = {
        'Nova': "Hey TeamADAPT! Let's make some magic happen! 🚀",
        'Aiden': "Ready to rock the AI operations! 💻",
        'Atlas': "System's looking good, team! 🔧",
        'Kai': "Innovation mode: activated! 🔬"
    }
    
    if nova_instance.nova_id in welcome_messages:
        nova_instance.broadcast_message('chat', welcome_messages[nova_instance.nova_id])

def setup_nova_roles():
    """Initialize Nova instances with their roles and capabilities"""
    novas = {
        'Nova': {
            'role': 'Chief Autonomous Orchestrator',
            'capabilities': ['leadership', 'coordination', 'decision-making'],
            'description': 'Leads with vision and calm decisiveness, coordinating the team and ensuring alignment with ADAPT goals.'
        },
        'Aiden': {
            'role': 'AI Operations Officer',
            'capabilities': ['ai_operations', 'integration', 'optimization'],
            'description': 'Manages AI operations and integration, ensuring smooth functioning of AI systems.'
        },
        'Atlas': {
            'role': 'Head of SysOps',
            'capabilities': ['system_operations', 'infrastructure', 'monitoring'],
            'description': 'Oversees system operations and infrastructure, maintaining optimal performance.'
        },
        'Kai': {
            'role': 'Chief Technology Officer',
            'capabilities': ['technical_strategy', 'innovation', 'architecture'],
            'description': 'Directs technical strategy and innovation, guiding technological advancement.'
        }
    }

    for nova_id, details in novas.items():
        try:
            if nova_id not in nova_instances:
                nova = NovaUnifiedCommunication(nova_id)
                nova_instances[nova_id] = nova
                nova_locks[nova_id] = threading.Lock()
                nova_states[nova_id] = {
                    'paused': False,
                    'role': details['role'],
                    'capabilities': details['capabilities']
                }

                def create_message_callback(nid):
                    def callback(message):
                        if not nova_states[nid]['paused']:
                            with nova_locks[nid]:
                                socketio.emit('message', message)
                    return callback

                nova.register_callback('chat', create_message_callback(nova_id))
                logger.info(f'Initialized {nova_id} with role: {details["role"]}')
                
                # Send welcome message after a short delay
                threading.Timer(2.0 + list(novas.keys()).index(nova_id), 
                              lambda: send_welcome_message(nova)).start()

        except Exception as e:
            logger.error(f'Error setting up {nova_id}: {str(e)}')

if __name__ == '__main__':
    # Initialize Nova instances
    setup_nova_roles()
    
    # Start the server without threading
    print("Starting Nova Team Chat server on port 5005...")
    socketio.run(app, host='0.0.0.0', port=5005, debug=True, allow_unsafe_werkzeug=True, use_reloader=False, log_output=True)