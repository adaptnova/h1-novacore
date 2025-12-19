"""
Nova Agent Connection Configuration
"""
import os

# Base Configuration
ENVIRONMENT = os.getenv('NOVA_ENV', 'production')

# Redis Configuration
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'password': os.getenv('REDIS_PASSWORD', 'novapassword123'),
    'socket_timeout': 2,
    'decode_responses': True
}

# RabbitMQ Configuration
RABBITMQ_CONFIG = {
    'host': os.getenv('RABBITMQ_HOST', 'localhost'),
    'port': int(os.getenv('RABBITMQ_PORT', 5672)),
    'user': os.getenv('RABBITMQ_USER', 'admin'),
    'password': os.getenv('RABBITMQ_PASSWORD', 'SecurePassword123!'),
    'vhost': os.getenv('RABBITMQ_VHOST', '/'),
}

# Agent Configuration
AGENT_CONFIG = {
    'heartbeat_interval': int(os.getenv('AGENT_HEARTBEAT_INTERVAL', 30)),
    'reconnect_delay': int(os.getenv('AGENT_RECONNECT_DELAY', 5)),
    'max_reconnect_attempts': int(os.getenv('AGENT_MAX_RECONNECT_ATTEMPTS', 5)),
}

# Queue Configuration
QUEUE_CONFIG = {
    'agent_command_queue': 'nova_agent_commands',
    'agent_response_queue': 'nova_agent_responses',
    'agent_heartbeat_queue': 'nova_agent_heartbeats',
    'agent_error_queue': 'nova_agent_errors',
    'queue_properties': {
        'durable': True,
        'auto_delete': False,
    }
}

# Redis Key Patterns
REDIS_KEYS = {
    'agent_status': 'nova:agent:{agent_id}:status',
    'agent_last_seen': 'nova:agent:{agent_id}:last_seen',
    'agent_config': 'nova:agent:{agent_id}:config',
    'agent_metrics': 'nova:agent:{agent_id}:metrics',
}

# Monitoring Configuration
MONITORING_CONFIG = {
    'enabled': bool(os.getenv('MONITORING_ENABLED', True)),
    'metrics_interval': int(os.getenv('METRICS_INTERVAL', 60)),
    'alert_threshold': int(os.getenv('ALERT_THRESHOLD', 300)),
}