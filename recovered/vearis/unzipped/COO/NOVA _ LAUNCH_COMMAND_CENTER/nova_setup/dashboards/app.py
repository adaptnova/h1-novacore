from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import redis
import pika
import prometheus_client
from prometheus_client import Counter, Gauge
import threading
import json
import os

# Initialize Flask
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Prometheus metrics
MESSAGE_SENT = Counter('messages_sent_total', 'Total number of messages sent')
MESSAGE_RECEIVED = Counter('messages_received_total', 'Total number of messages received')
CURRENT_CONNECTED_USERS = Gauge('current_connected_users', 'Current number of users connected')
FAILED_MESSAGES = Counter('failed_messages_total', 'Total number of failed message attempts')

# Redis connection
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    password='nova_secure_password'
)

# RabbitMQ connection
def setup_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='agent_queue')
        return connection, channel
    except Exception as e:
        app.logger.error(f"Failed to connect to RabbitMQ: {e}")
        return None, None

# Routes
@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "services": {
            "redis": check_redis(),
            "rabbitmq": check_rabbitmq(),
            "metrics": check_metrics()
        }
    })

@app.route('/health')
def health():
    services_status = {
        "redis": check_redis(),
        "rabbitmq": check_rabbitmq(),
        "metrics": check_metrics()
    }
    is_healthy = all(services_status.values())
    return jsonify({
        "status": "healthy" if is_healthy else "unhealthy",
        "services": services_status,
        "metrics": {
            "messages_sent": MESSAGE_SENT._value.get(),
            "messages_received": MESSAGE_RECEIVED._value.get(),
            "connected_users": CURRENT_CONNECTED_USERS._value.get()
        }
    }), 200 if is_healthy else 503

def check_redis():
    try:
        return redis_client.ping()
    except:
        return False

def check_rabbitmq():
    try:
        conn, chan = setup_rabbitmq()
        if conn and chan:
            conn.close()
            return True
        return False
    except:
        return False

def check_metrics():
    try:
        return prometheus_client.REGISTRY.get_sample_value('process_start_time_seconds') is not None
    except:
        return False

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    CURRENT_CONNECTED_USERS.inc()
    emit('status', {'message': 'Connected successfully'})

@socketio.on('disconnect')
def handle_disconnect():
    CURRENT_CONNECTED_USERS.dec()

@socketio.on('message')
def handle_message(data):
    try:
        MESSAGE_RECEIVED.inc()
        # Process message and send to RabbitMQ
        connection, channel = setup_rabbitmq()
        if connection and channel:
            channel.basic_publish(
                exchange='',
                routing_key='agent_queue',
                body=json.dumps(data)
            )
            MESSAGE_SENT.inc()
            connection.close()
            emit('message_status', {'status': 'sent'})
        else:
            FAILED_MESSAGES.inc()
            emit('message_status', {'status': 'failed', 'error': 'RabbitMQ connection failed'})
    except Exception as e:
        FAILED_MESSAGES.inc()
        emit('message_status', {'status': 'failed', 'error': str(e)})

if __name__ == '__main__':
    # Start Prometheus metrics endpoint
    prometheus_client.start_http_server(8000)
    # Start Flask-SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)