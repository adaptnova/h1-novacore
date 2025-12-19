"""
Nova Agent Connection Handler
"""
import redis
import pika
import json
import time
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from agent_config import (
    REDIS_CONFIG,
    RABBITMQ_CONFIG,
    AGENT_CONFIG,
    QUEUE_CONFIG,
    REDIS_KEYS,
    MONITORING_CONFIG,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NovaAgentHandler')

class NovaAgentConnectionHandler:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.redis_client = None
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.is_connected = False
        self.should_reconnect = True
        self.command_handlers = {}
        self.reconnect_attempt = 0
        self._setup_logging()

    def _setup_logging(self):
        self.logger = logging.getLogger(f'NovaAgent:{self.agent_id}')
        handler = logging.FileHandler(f'/x/logs/agent_{self.agent_id}.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)

    def connect(self) -> bool:
        """Establish connections to Redis and RabbitMQ"""
        try:
            # Connect to Redis
            self.redis_client = redis.Redis(**REDIS_CONFIG)
            self.redis_client.ping()  # Verify connection

            # Connect to RabbitMQ
            credentials = pika.PlainCredentials(
                RABBITMQ_CONFIG['user'],
                RABBITMQ_CONFIG['password']
            )
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_CONFIG['host'],
                port=RABBITMQ_CONFIG['port'],
                virtual_host=RABBITMQ_CONFIG['vhost'],
                credentials=credentials,
                heartbeat=600
            )
            
            self.rabbitmq_connection = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_connection.channel()

            # Declare queues
            for queue_name in QUEUE_CONFIG.values():
                if isinstance(queue_name, str):  # Skip the queue_properties dict
                    self.rabbitmq_channel.queue_declare(
                        queue=queue_name,
                        **QUEUE_CONFIG['queue_properties']
                    )

            self.is_connected = True
            self.reconnect_attempt = 0
            self._update_agent_status('connected')
            self.logger.info(f'Agent {self.agent_id} connected successfully')
            return True

        except (redis.RedisError, pika.exceptions.AMQPError) as e:
            self.logger.error(f'Connection error: {str(e)}')
            self.is_connected = False
            self._update_agent_status('connection_error')
            return False

    def disconnect(self):
        """Gracefully disconnect from services"""
        try:
            self.should_reconnect = False
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                self.rabbitmq_connection.close()
            if self.redis_client:
                self.redis_client.close()
            self.is_connected = False
            self._update_agent_status('disconnected')
            self.logger.info(f'Agent {self.agent_id} disconnected successfully')
        except Exception as e:
            self.logger.error(f'Error during disconnect: {str(e)}')

    def reconnect(self):
        """Attempt to reconnect with exponential backoff"""
        while (self.should_reconnect and 
               self.reconnect_attempt < AGENT_CONFIG['max_reconnect_attempts']):
            self.reconnect_attempt += 1
            delay = AGENT_CONFIG['reconnect_delay'] * (2 ** (self.reconnect_attempt - 1))
            self.logger.info(f'Attempting reconnection {self.reconnect_attempt}, waiting {delay}s')
            time.sleep(delay)
            
            if self.connect():
                self.logger.info('Reconnection successful')
                return True
        
        self.logger.error('Max reconnection attempts reached')
        return False

    def _update_agent_status(self, status: str):
        """Update agent status in Redis"""
        try:
            if self.redis_client:
                status_key = REDIS_KEYS['agent_status'].format(agent_id=self.agent_id)
                last_seen_key = REDIS_KEYS['agent_last_seen'].format(agent_id=self.agent_id)
                
                self.redis_client.set(status_key, status)
                self.redis_client.set(last_seen_key, datetime.now().isoformat())
        except Exception as e:
            self.logger.error(f'Error updating agent status: {str(e)}')

    def register_command_handler(self, command: str, handler: Callable):
        """Register a handler for a specific command"""
        self.command_handlers[command] = handler
        self.logger.info(f'Registered handler for command: {command}')

    def start_command_listener(self):
        """Start listening for commands on the command queue"""
        try:
            queue_name = QUEUE_CONFIG['agent_command_queue']
            self.rabbitmq_channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._handle_command,
                auto_ack=False
            )
            self.logger.info(f'Started listening on queue: {queue_name}')
            self.rabbitmq_channel.start_consuming()
        except Exception as e:
            self.logger.error(f'Error in command listener: {str(e)}')
            if self.should_reconnect:
                self.reconnect()

    def _handle_command(self, ch, method, properties, body):
        """Handle incoming commands"""
        try:
            command_data = json.loads(body)
            command = command_data.get('command')
            
            if command in self.command_handlers:
                response = self.command_handlers[command](command_data)
                self._send_response(response, properties.correlation_id)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                self.logger.warning(f'Unknown command received: {command}')
                ch.basic_nack(delivery_tag=method.delivery_tag)
        except Exception as e:
            self.logger.error(f'Error handling command: {str(e)}')
            ch.basic_nack(delivery_tag=method.delivery_tag)

    def _send_response(self, response: Dict[str, Any], correlation_id: str):
        """Send response back through RabbitMQ"""
        try:
            self.rabbitmq_channel.basic_publish(
                exchange='',
                routing_key=QUEUE_CONFIG['agent_response_queue'],
                body=json.dumps(response),
                properties=pika.BasicProperties(
                    correlation_id=correlation_id,
                    delivery_mode=2  # make message persistent
                )
            )
        except Exception as e:
            self.logger.error(f'Error sending response: {str(e)}')

    def start_heartbeat(self):
        """Start sending heartbeat messages"""
        def heartbeat_loop():
            while self.is_connected and self.should_reconnect:
                try:
                    heartbeat_data = {
                        'agent_id': self.agent_id,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'alive'
                    }
                    self.rabbitmq_channel.basic_publish(
                        exchange='',
                        routing_key=QUEUE_CONFIG['agent_heartbeat_queue'],
                        body=json.dumps(heartbeat_data),
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    self._update_agent_status('active')
                    time.sleep(AGENT_CONFIG['heartbeat_interval'])
                except Exception as e:
                    self.logger.error(f'Error in heartbeat: {str(e)}')
                    if self.should_reconnect:
                        self.reconnect()
                        
        heartbeat_thread = threading.Thread(target=heartbeat_loop)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

    def send_metrics(self, metrics: Dict[str, Any]):
        """Send agent metrics to Redis"""
        try:
            if self.redis_client:
                metrics_key = REDIS_KEYS['agent_metrics'].format(agent_id=self.agent_id)
                self.redis_client.set(metrics_key, json.dumps(metrics))
        except Exception as e:
            self.logger.error(f'Error sending metrics: {str(e)}')

# Example usage
if __name__ == "__main__":
    # Create log directory
    import os
    os.makedirs('/x/logs', exist_ok=True)
    
    # Example command handler
    def handle_echo(command_data):
        return {
            'status': 'success',
            'echo': command_data.get('message', '')
        }
    
    # Initialize and start agent
    agent = NovaAgentConnectionHandler('test_agent_1')
    if agent.connect():
        agent.register_command_handler('echo', handle_echo)
        agent.start_heartbeat()
        try:
            agent.start_command_listener()
        except KeyboardInterrupt:
            agent.disconnect()
    else:
        logger.error('Failed to connect agent')