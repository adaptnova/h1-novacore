#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pika
import json
import yaml
import threading
import datetime
import prometheus_client
from prometheus_client import Counter, Gauge
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/tmp/nova_gui.log'),
        logging.StreamHandler()
    ]
)

# Load configuration
def load_config():
    try:
        with open('/data/xray/xx/nova_setup/dashboards/RabbitMQDesktopGUI.yml', 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return None

# Initialize Prometheus metrics
MESSAGES_SENT = Counter('messages_sent_total', 'Total number of messages sent')
MESSAGES_RECEIVED = Counter('messages_received_total', 'Total number of messages received')
MESSAGE_LATENCY = Gauge('message_latency_ms', 'Message latency in milliseconds')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')

class NovaGUI:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        if not self.config:
            messagebox.showerror("Error", "Failed to load configuration")
            root.destroy()
            return

        # Configure the main window
        gui_config = self.config['data']['gui']['window']
        root.title(gui_config['title'])
        root.geometry(f"{gui_config['width']}x{gui_config['height']}")
        root.minsize(gui_config['min_width'], gui_config['min_height'])

        # Setup RabbitMQ connection
        self.setup_rabbitmq()

        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create agent buttons
        self.create_agent_buttons(main_frame)

        # Create message input
        self.create_message_input(main_frame)

        # Create message display
        self.create_message_display(main_frame)

        # Start Prometheus metrics server
        prometheus_client.start_http_server(self.config['data']['prometheus']['port'])
        
        # Update active connections metric
        ACTIVE_CONNECTIONS.set(1)

    def setup_rabbitmq(self):
        try:
            rabbitmq_config = self.config['data']['rabbitmq']
            credentials = pika.PlainCredentials(
                rabbitmq_config['username'],
                rabbitmq_config['password']
            )
            parameters = pika.ConnectionParameters(
                host=rabbitmq_config['host'],
                port=rabbitmq_config['port'],
                virtual_host=rabbitmq_config['virtual_host'],
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            exchange_config = rabbitmq_config['exchange']
            self.channel.exchange_declare(
                exchange=exchange_config['name'],
                exchange_type=exchange_config['type']
            )
            
            # Declare queues
            for queue_config in rabbitmq_config['queues'].values():
                self.channel.queue_declare(
                    queue=queue_config['name'],
                    durable=queue_config['durable']
                )
            
            # Start consuming messages in a separate thread
            self.start_consuming()
            
        except Exception as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}")
            messagebox.showerror("Error", f"Failed to connect to RabbitMQ: {e}")

    def create_agent_buttons(self, parent):
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        for agent in self.config['data']['gui']['agents']:
            btn = ttk.Button(
                buttons_frame,
                text=agent['name'],
                command=lambda a=agent: self.select_agent(a['name'])
            )
            btn.pack(side=tk.LEFT, padx=5)

    def create_message_input(self, parent):
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.msg_input = ttk.Entry(input_frame)
        self.msg_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.RIGHT)

    def create_message_display(self, parent):
        self.msg_display = scrolledtext.ScrolledText(parent, height=15)
        self.msg_display.pack(fill=tk.BOTH, expand=True)
        self.msg_display.config(state=tk.DISABLED)

    def select_agent(self, agent_name):
        self.selected_agent = agent_name
        self.add_to_display(f"Selected recipient: {agent_name}")

    def send_message(self):
        if not hasattr(self, 'selected_agent'):
            messagebox.showwarning("Warning", "Please select a recipient first")
            return
            
        message = self.msg_input.get()
        if not message:
            return
            
        try:
            msg_data = {
                'sender': 'User',
                'recipient': self.selected_agent,
                'content': message,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            self.channel.basic_publish(
                exchange=self.config['data']['rabbitmq']['exchange']['name'],
                routing_key=f"{self.selected_agent.lower()}.message",
                body=json.dumps(msg_data)
            )
            
            MESSAGES_SENT.inc()
            self.add_to_display(f"Sent to {self.selected_agent}: {message}")
            self.msg_input.delete(0, tk.END)
            
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            messagebox.showerror("Error", f"Failed to send message: {e}")

    def add_to_display(self, message):
        self.msg_display.config(state=tk.NORMAL)
        self.msg_display.insert(tk.END, f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.msg_display.see(tk.END)
        self.msg_display.config(state=tk.DISABLED)

    def start_consuming(self):
        def callback(ch, method, properties, body):
            try:
                msg_data = json.loads(body)
                self.root.after(0, self.add_to_display, 
                    f"Received from {msg_data['sender']}: {msg_data['content']}")
                MESSAGES_RECEIVED.inc()
            except Exception as e:
                logging.error(f"Error processing received message: {e}")

        for queue in self.config['data']['rabbitmq']['queues'].values():
            self.channel.basic_consume(
                queue=queue['name'],
                on_message_callback=callback,
                auto_ack=True
            )

        thread = threading.Thread(target=self._consume_messages, daemon=True)
        thread.start()

    def _consume_messages(self):
        try:
            self.channel.start_consuming()
        except Exception as e:
            logging.error(f"Error in message consumption: {e}")

    def cleanup(self):
        try:
            if hasattr(self, 'connection') and self.connection.is_open:
                self.connection.close()
            ACTIVE_CONNECTIONS.dec()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NovaGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.cleanup(), root.destroy()))
    root.mainloop()