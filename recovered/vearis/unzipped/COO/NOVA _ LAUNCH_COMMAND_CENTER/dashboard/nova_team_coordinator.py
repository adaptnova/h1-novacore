"""
Nova Team Coordinator
Manages team of Nova instances, coordinates work distribution and collaboration
"""
import redis
import pika
import json
import threading
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NovaTeamCoordinator')

@dataclass
class NovaInstance:
    instance_id: str
    role: str  # e.g., 'orchestrator', 'analyst', 'researcher', 'implementer'
    status: str
    capabilities: List[str]
    current_task: Optional[str]
    last_heartbeat: float
    workload: int  # 0-100 representing current load

@dataclass
class Task:
    task_id: str
    type: str
    priority: int
    assigned_to: Optional[str]
    status: str
    created_at: float
    dependencies: List[str]
    data: Dict[str, Any]

class NovaTeamCoordinator:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            password='novapassword123',
            decode_responses=True
        )
        
        # RabbitMQ setup
        credentials = pika.PlainCredentials('admin', 'SecurePassword123!')
        self.rabbitmq_params = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            virtual_host='/',
            credentials=credentials
        )
        self.setup_rabbitmq()
        
        self.nova_instances: Dict[str, NovaInstance] = {}
        self.tasks: Dict[str, Task] = {}
        self.load_state()
        
        # Start background tasks
        self.start_background_tasks()

    def setup_rabbitmq(self):
        """Setup RabbitMQ exchanges and queues"""
        connection = pika.BlockingConnection(self.rabbitmq_params)
        channel = connection.channel()
        
        # Declare exchanges
        channel.exchange_declare('nova.team', exchange_type='topic', durable=True)
        channel.exchange_declare('nova.tasks', exchange_type='direct', durable=True)
        
        # Declare queues
        queues = [
            'nova.team.heartbeat',
            'nova.team.task_request',
            'nova.team.task_complete',
            'nova.team.coordination',
            'nova.team.status'
        ]
        
        for queue in queues:
            channel.queue_declare(queue=queue, durable=True)
            channel.queue_bind(queue=queue, exchange='nova.team', routing_key=queue.split('.')[-1])
        
        connection.close()

    def register_nova(self, instance_data: Dict[str, Any]) -> NovaInstance:
        """Register a new Nova instance"""
        instance = NovaInstance(
            instance_id=instance_data.get('instance_id', str(uuid.uuid4())),
            role=instance_data['role'],
            status='active',
            capabilities=instance_data['capabilities'],
            current_task=None,
            last_heartbeat=time.time(),
            workload=0
        )
        
        self.nova_instances[instance.instance_id] = instance
        self.save_state()
        logger.info(f"Registered new Nova instance: {instance.instance_id} ({instance.role})")
        return instance

    def distribute_task(self, task: Task) -> bool:
        """Distribute task to most suitable Nova instance"""
        available_instances = [
            instance for instance in self.nova_instances.values()
            if instance.status == 'active' and instance.workload < 80
        ]
        
        if not available_instances:
            logger.warning("No available instances for task distribution")
            return False
        
        # Sort by workload and capabilities match
        best_instance = min(
            available_instances,
            key=lambda x: (x.workload, -len(set(x.capabilities) & set(task.data.get('required_capabilities', []))))
        )
        
        task.assigned_to = best_instance.instance_id
        best_instance.current_task = task.task_id
        best_instance.workload += 20  # Increment workload
        
        self.tasks[task.task_id] = task
        self.save_state()
        
        # Notify instance
        self.notify_instance(best_instance.instance_id, {
            'type': 'task_assignment',
            'task': asdict(task)
        })
        
        return True

    def notify_instance(self, instance_id: str, message: Dict[str, Any]):
        """Send notification to specific Nova instance"""
        connection = pika.BlockingConnection(self.rabbitmq_params)
        channel = connection.channel()
        
        channel.basic_publish(
            exchange='nova.team',
            routing_key=f"instance.{instance_id}",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        connection.close()

    def handle_heartbeat(self, instance_id: str):
        """Process heartbeat from Nova instance"""
        if instance_id in self.nova_instances:
            self.nova_instances[instance_id].last_heartbeat = time.time()
            self.nova_instances[instance_id].status = 'active'
            self.save_state()

    def handle_task_complete(self, instance_id: str, task_id: str, result: Dict[str, Any]):
        """Process task completion"""
        if instance_id in self.nova_instances and task_id in self.tasks:
            instance = self.nova_instances[instance_id]
            task = self.tasks[task_id]
            
            instance.current_task = None
            instance.workload = max(0, instance.workload - 20)
            task.status = 'completed'
            
            self.save_state()
            self.process_task_dependencies(task_id)

    def process_task_dependencies(self, completed_task_id: str):
        """Process tasks that were waiting on the completed task"""
        for task in self.tasks.values():
            if (task.status == 'pending' and 
                completed_task_id in task.dependencies):
                task.dependencies.remove(completed_task_id)
                if not task.dependencies:  # All dependencies satisfied
                    self.distribute_task(task)

    def start_background_tasks(self):
        """Start background monitoring and maintenance tasks"""
        def monitor_instances():
            while True:
                current_time = time.time()
                for instance_id, instance in list(self.nova_instances.items()):
                    if current_time - instance.last_heartbeat > 60:  # No heartbeat for 1 minute
                        instance.status = 'inactive'
                        if instance.current_task:
                            self.redistribute_task(instance.current_task)
                self.save_state()
                time.sleep(10)

        def process_messages():
            connection = pika.BlockingConnection(self.rabbitmq_params)
            channel = connection.channel()
            
            def callback(ch, method, properties, body):
                try:
                    message = json.loads(body)
                    if method.routing_key == 'heartbeat':
                        self.handle_heartbeat(message['instance_id'])
                    elif method.routing_key == 'task_complete':
                        self.handle_task_complete(
                            message['instance_id'],
                            message['task_id'],
                            message['result']
                        )
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
            
            channel.basic_consume(
                queue='nova.team.heartbeat',
                on_message_callback=callback,
                auto_ack=True
            )
            
            channel.start_consuming()

        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_instances)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start message processing thread
        message_thread = threading.Thread(target=process_messages)
        message_thread.daemon = True
        message_thread.start()

    def save_state(self):
        """Save current state to Redis"""
        state = {
            'instances': {k: asdict(v) for k, v in self.nova_instances.items()},
            'tasks': {k: asdict(v) for k, v in self.tasks.items()},
            'last_updated': datetime.now().isoformat()
        }
        self.redis_client.set('nova:team:state', json.dumps(state))

    def load_state(self):
        """Load state from Redis"""
        state_data = self.redis_client.get('nova:team:state')
        if state_data:
            state = json.loads(state_data)
            self.nova_instances = {
                k: NovaInstance(**v) for k, v in state['instances'].items()
            }
            self.tasks = {
                k: Task(**v) for k, v in state['tasks'].items()
            }
            logger.info("State loaded successfully")

    def get_team_status(self) -> Dict[str, Any]:
        """Get current team status and metrics"""
        active_instances = sum(1 for i in self.nova_instances.values() if i.status == 'active')
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == 'completed')
        average_workload = sum(i.workload for i in self.nova_instances.values()) / len(self.nova_instances) if self.nova_instances else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'active_instances': active_instances,
            'total_instances': len(self.nova_instances),
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'average_workload': average_workload,
            'instances': {k: asdict(v) for k, v in self.nova_instances.items()}
        }

if __name__ == "__main__":
    coordinator = NovaTeamCoordinator()
    logger.info("Nova Team Coordinator started successfully")