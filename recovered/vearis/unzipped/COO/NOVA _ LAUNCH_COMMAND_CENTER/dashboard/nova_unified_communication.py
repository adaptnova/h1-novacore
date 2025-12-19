"""
Nova Unified Communication System
Combines RabbitMQ messaging, Redis persistence, and web interface
"""

import os
import json
import time
import threading
import queue
from typing import Dict, List, Callable, Any
from datetime import datetime
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
import redis
import pika
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NovaUnifiedCommunication:
    def __init__(self, nova_id: str, web_port: int = 5004):
        self.nova_id = nova_id
        self.web_port = web_port
        
        # RabbitMQ configuration
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        self.rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')
        
        # Redis configuration
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', '6379'))
        self.redis_pass = os.getenv('REDIS_PASS', '')
        
        # Initialize components
        self.callbacks: Dict[str, List[Callable]] = {}
        self.last_received: Dict[str, Dict] = {}
        self.message_queue = queue.Queue()
        self.should_run = True
        self.lock = threading.Lock()
        
        # Initialize Redis
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_pass,
            decode_responses=True
        )
        
        # Initialize RabbitMQ connection
        self._connect_rabbitmq()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Start message processing thread
        self.processing_thread = threading.Thread(target=self._process_messages, daemon=True)
        self.processing_thread.start()
        
        # Setup web interface
        self._setup_web_interface()
        
    def _connect_rabbitmq(self):
        """Establish connection to RabbitMQ"""
        with self.lock:
            try:
                # Create connection
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.rabbitmq_host,
                        port=self.rabbitmq_port,
                        credentials=pika.PlainCredentials(
                            self.rabbitmq_user,
                            self.rabbitmq_pass
                        ),
                        heartbeat=60,
                        blocked_connection_timeout=30
                    )
                )
                
                # Create channel
                self.channel = self.connection.channel()
                
                # Declare exchange
                self.channel.exchange_declare(
                    exchange='nova_exchange',
                    exchange_type='topic',
                    durable=True
                )
                
                # Declare queue
                result = self.channel.queue_declare(queue='', exclusive=True)
                self.queue_name = result.method.queue
                
                # Bind to personal messages
                self.channel.queue_bind(
                    exchange='nova_exchange',
                    queue=self.queue_name,
                    routing_key=f'nova.{self.nova_id}.#'
                )
                
                # Bind to broadcast messages
                self.channel.queue_bind(
                    exchange='nova_exchange',
                    queue=self.queue_name,
                    routing_key='nova.broadcast.#'
                )
                
                print(f"Nova {self.nova_id} connected to RabbitMQ")
                return True
                
            except Exception as e:
                print(f"RabbitMQ connection error: {str(e)}")
                return False

    def _process_messages(self):
        """Process messages in a separate thread"""
        while self.should_run:
            try:
                if not self.connection or self.connection.is_closed:
                    if not self._connect_rabbitmq():
                        time.sleep(5)
                        continue
                
                # Process any queued outgoing messages
                try:
                    routing_key, message = self.message_queue.get_nowait()
                    with self.lock:
                        self.channel.basic_publish(
                            exchange='nova_exchange',
                            routing_key=routing_key,
                            body=json.dumps(message),
                            properties=pika.BasicProperties(
                                delivery_mode=2,
                                content_type='application/json'
                            )
                        )
                        
                        # Store in Redis for persistence
                        self._store_message_redis(message)
                        
                except queue.Empty:
                    pass
                
                # Check for incoming messages
                with self.lock:
                    method_frame, header_frame, body = self.channel.basic_get(
                        queue=self.queue_name,
                        auto_ack=True
                    )
                    
                    if method_frame:
                        try:
                            message = json.loads(body)
                            message_type = method_frame.routing_key.split('.')[-1]
                            
                            # Store last received message
                            self.last_received[message['from']] = {
                                'timestamp': message['timestamp'],
                                'type': message_type,
                                'payload': message['payload']
                            }
                            
                            # Store in Redis
                            self._store_message_redis(message)
                            
                            # Emit to web clients
                            self.socketio.emit('message', message)
                            
                            # Call registered callbacks
                            if message_type in self.callbacks:
                                for callback in self.callbacks[message_type]:
                                    try:
                                        callback(message)
                                    except Exception as e:
                                        print(f"Callback error: {str(e)}")
                                        
                        except Exception as e:
                            print(f"Message handling error: {str(e)}")
                
                # Small delay to prevent busy waiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Processing error: {str(e)}")
                time.sleep(5)
                continue

    def _store_message_redis(self, message: Dict):
        """Store message in Redis"""
        try:
            key = f"nova:messages:{time.time()}"
            self.redis_client.set(key, json.dumps(message))
            self.redis_client.expire(key, 86400)  # 24 hour TTL
        except Exception as e:
            print(f"Redis storage error: {str(e)}")

    def _setup_web_interface(self):
        """Setup Flask routes and Socket.IO events"""
        
        @self.app.route('/status')
        def get_status():
            return jsonify({
                'status': 'online',
                'nova_id': self.nova_id,
                'redis': self._check_redis(),
                'rabbitmq': self._check_rabbitmq(),
                'last_messages': self.get_last_messages()
            })

        @self.app.route('/send', methods=['POST'])
        def send_message():
            data = request.json
            message = data.get('message')
            target = data.get('target', 'broadcast')
            message_type = data.get('type', 'chat')
            
            if target == 'broadcast':
                success = self.broadcast_message(message_type, message)
            else:
                success = self.send_message(target, message_type, message)
            
            return jsonify({'status': 'sent' if success else 'failed'})

        @self.app.route('/messages')
        def get_messages():
            messages = []
            for key in self.redis_client.keys('nova:messages:*'):
                try:
                    msg = json.loads(self.redis_client.get(key))
                    messages.append(msg)
                except:
                    continue
            return jsonify(messages)

        @self.socketio.on('connect')
        def handle_connect():
            self.socketio.emit('status', {'status': 'connected'})

        @self.socketio.on('message')
        def handle_socket_message(data):
            target = data.get('target', 'broadcast')
            message_type = data.get('type', 'chat')
            
            if target == 'broadcast':
                self.broadcast_message(message_type, data.get('message'))
            else:
                self.send_message(target, message_type, data.get('message'))

    def _check_redis(self) -> bool:
        """Check Redis connection"""
        try:
            return self.redis_client.ping()
        except:
            return False

    def _check_rabbitmq(self) -> bool:
        """Check RabbitMQ connection"""
        try:
            return not self.connection.is_closed
        except:
            return False

    def send_message(self, to_nova: str, message_type: str, payload: Any) -> bool:
        """Send message to specific Nova"""
        try:
            if message_type == 'chat' and isinstance(payload, str):
                payload = {'message': payload}
            elif message_type == 'chat' and isinstance(payload, dict) and 'message' not in payload:
                payload = {'message': str(payload)}
                
            message = {
                'from': self.nova_id,
                'timestamp': datetime.now().isoformat(),
                'type': message_type,
                'payload': payload
            }
            
            routing_key = f'nova.{to_nova}.{message_type}'
            self.message_queue.put((routing_key, message))
            return True
        except Exception as e:
            print(f"Send error: {str(e)}")
            return False

    def broadcast_message(self, message_type: str, payload: Any) -> bool:
        """Broadcast message to all Novas"""
        try:
            if message_type == 'chat' and isinstance(payload, str):
                payload = {'message': payload}
            elif message_type == 'chat' and isinstance(payload, dict) and 'message' not in payload:
                payload = {'message': str(payload)}
                
            message = {
                'from': self.nova_id,
                'timestamp': datetime.now().isoformat(),
                'type': message_type,
                'payload': payload
            }
            
            routing_key = f'nova.broadcast.{message_type}'
            self.message_queue.put((routing_key, message))
            return True
        except Exception as e:
            print(f"Broadcast error: {str(e)}")
            return False

    def register_callback(self, message_type: str, callback: Callable):
        """Register callback for specific message type"""
        if message_type not in self.callbacks:
            self.callbacks[message_type] = []
        self.callbacks[message_type].append(callback)

    def get_last_messages(self) -> Dict[str, Dict]:
        """Get last received messages from each Nova"""
        return self.last_received

    def start(self):
        """Start the web interface"""
        self.socketio.run(self.app, host='0.0.0.0', port=self.web_port)

    def close(self):
        """Close all connections"""
        self.should_run = False
        if hasattr(self, 'connection') and self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
            except:
                pass
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=5)

if __name__ == '__main__':
    # Example usage
    nova = NovaUnifiedCommunication('nova1', web_port=5004)
    
    def message_callback(message):
        print(f"Received message: {message}")
    
    nova.register_callback('chat', message_callback)
    nova.start()