# RabbitMQ Desktop GUI Configuration - RabbitMQDesktopGUI.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rabbitmq-gui-config
data:
  # RabbitMQ Connection Settings
  rabbitmq:
    host: localhost
    port: 5672
    queue: agent_queue
    auto_reconnect: true

  # Redis Connection Settings
  redis:
    host: localhost
    port: 6379
    db: 0

  # ChromaDB Settings
  chromadb:
    embedding_model: text-embedding-ada-002
    host: localhost
    port: 8000

  # GUI Settings
  gui:
    window:
      title: "RabbitMQ Messaging GUI"
      width: 1000
      height: 1000
    theme:
      dark_mode: false
    agents:
      - name: Nova
        color: lightblue
      - name: Aiden
        color: lightgreen
      - name: Atlas
        color: lightyellow
      - name: Kai
        color: lightcoral

  # Voice Support Settings
  voice:
    tts:
      rate: 150
      voice: english
    stt:
      enabled: true

  # Prometheus Metrics
  prometheus:
    port: 8000
    metrics:
      - name: messages_sent_total
        type: counter
        description: "Total number of messages sent"
      - name: messages_received_total
        type: counter
        description: "Total number of messages received"
      - name: current_connected_users
        type: gauge
        description: "Current number of users connected"
      - name: failed_messages_total
        type: counter
        description: "Total number of failed message attempts"

  # Logging Configuration
  logging:
    file: message_history.log
    level: INFO

  # Flask Server Settings (for remote access)
  flask:
    cors_allowed_origins: "*"
    port: 5000
    ssl:
      enabled: false

# Metrics for Prometheus
MESSAGE_SENT = Counter('messages_sent_total', 'Total number of messages sent')
MESSAGE_RECEIVED = Counter('messages_received_total', 'Total number of messages received')
CURRENT_CONNECTED_USERS = Gauge('current_connected_users', 'Current number of users connected')
FAILED_MESSAGES = Counter('failed_messages_total', 'Total number of failed message attempts')

# Flask setup for remote access
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
connected_users = 0

class RabbitMQDesktopGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("RabbitMQ Messaging GUI")
        self.master.geometry("1000x1000")

        # RabbitMQ Connection
        self.connection = None
        self.channel = None
        self.paused = False
        self.auto_reconnect = True

        self.setup_rabbitmq()
        self.setup_redis()
        self.setup_chromadb()
        self.setup_voice_support()
        self.setup_prometheus()

        # Dark Mode Toggle
        self.dark_mode = False
        self.dark_mode_button = tk.Button(master, text="Enable Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.pack(fill='x', pady=10)

        # Create Buttons for agents
        self.nova_button = tk.Button(master, text="Nova", bg="lightblue", command=lambda: self.send_message('Nova'))
        self.nova_button.pack(fill='x', pady=5)

        self.aiden_button = tk.Button(master, text="Aiden", bg="lightgreen", command=lambda: self.send_message('Aiden'))
        self.aiden_button.pack(fill='x', pady=5)

        self.atlas_button = tk.Button(master, text="Atlas", bg="lightyellow", command=lambda: self.send_message('Atlas'))
        self.atlas_button.pack(fill='x', pady=5)

        self.kai_button = tk.Button(master, text="Kai", bg="lightcoral", command=lambda: self.send_message('Kai'))
        self.kai_button.pack(fill='x', pady=5)

        # Broadcast Button
        self.broadcast_button = tk.Button(master, text="Broadcast", bg="lightgrey", command=self.broadcast_message)
        self.broadcast_button.pack(fill='x', pady=10)

        # Pause/Resume Button
        self.pause_button = tk.Button(master, text="Pause", bg="orange", command=self.toggle_pause)
        self.pause_button.pack(fill='x', pady=10)

        # Manual Message Entry Button
        self.manual_message_button = tk.Button(master, text="Send Custom Message", bg="lightblue", command=self.send_custom_message)
        self.manual_message_button.pack(fill='x', pady=10)

        # Auto Reconnect Toggle Button
        self.reconnect_button = tk.Button(master, text="Disable Auto-Reconnect", bg="red", command=self.toggle_reconnect)
        self.reconnect_button.pack(fill='x', pady=10)

        # Voice Command Button
        self.voice_command_button = tk.Button(master, text="Voice Command", bg="purple", command=self.voice_command)
        self.voice_command_button.pack(fill='x', pady=10)

        # Message Log
        self.log_label = tk.Label(master, text="Message Log:")
        self.log_label.pack()
        self.message_log = tk.Text(master, height=10, state='disabled')
        self.message_log.pack(fill='both', pady=10)

        # Chat History Section
        self.chat_label = tk.Label(master, text="Chat History:")
        self.chat_label.pack()
        self.chat_history = tk.Text(master, height=15, state='disabled')
        self.chat_history.pack(fill='both', pady=10)

        # Scheduler
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.background_scheduler = BackgroundScheduler()
        self.background_scheduler.start()

        # Start RabbitMQ listener in a separate thread
        self.listener_thread = threading.Thread(target=self.start_listening, daemon=True)
        self.listener_thread.start()

        # Logging to File
        self.log_file_path = "message_history.log"

    def setup_rabbitmq(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='agent_queue')
        except Exception as e:
            messagebox.showerror("RabbitMQ Error", f"Failed to connect to RabbitMQ: {e}")
            self.log_message(f"[Error] Failed to connect to RabbitMQ: {e}")
            FAILED_MESSAGES.inc()

    def setup_redis(self):
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            self.log_message("[Info] Connected to Redis successfully")
        except Exception as e:
            messagebox.showerror("Redis Error", f"Failed to connect to Redis: {e}")
            self.log_message(f"[Error] Failed to connect to Redis: {e}")
            FAILED_MESSAGES.inc()

    def setup_chromadb(self):
        try:
            self.chroma_client = Client()
            self.chroma_embeddings = embedding_functions.openai('text-embedding-ada-002')  # Replace with the actual embedding function you use
            self.log_message("[Info] Connected to ChromaDB successfully")
        except Exception as e:
            messagebox.showerror("ChromaDB Error", f"Failed to connect to ChromaDB: {e}")
            self.log_message(f"[Error] Failed to connect to ChromaDB: {e}")
            FAILED_MESSAGES.inc()

    def setup_voice_support(self):
        # Setup TTS and STT engines
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('voice', 'english')

    def setup_prometheus(self):
        # Setup Prometheus metrics
        prometheus_client.start_http_server(8000)
        self.log_message("[Info] Prometheus metrics server started on port 8000")

    def voice_command(self):
        try:
            with sr.Microphone() as source:
                self.tts_engine.say("Listening for a command.")
                self.tts_engine.runAndWait()
                audio = self.recognizer.listen(source)
                command = self.recognizer.recognize_google(audio)
                self.log_message(f"[Voice Command] {command}")
                self.process_voice_command(command)
        except sr.UnknownValueError:
            messagebox.showwarning("Voice Command Error", "Sorry, I did not understand the command.")
        except sr.RequestError as e:
            messagebox.showerror("Voice Command Error", f"Could not request results; {e}")

    def process_voice_command(self, command):
        # Process the command to identify agent and action
        if "send message to" in command.lower():
            agent_name = command.lower().split("send message to ")[1].strip()
            self.send_message(agent_name)
        elif "broadcast" in command.lower():
            self.broadcast_message()
        elif "pause" in command.lower():
            self.toggle_pause()
        elif "resume" in command.lower():
            self.toggle_pause()
        else:
            self.tts_engine.say("Command not recognized.")
            self.tts_engine.runAndWait()

    def send_message(self, agent):
        if self.paused:
            messagebox.showwarning("Paused", "Messaging is currently paused.")
            return

        try:
            message = json.dumps({
                "sender": "User",
                "recipient": agent,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": f"Message to {agent}"
            })
            self.channel.basic_publish(exchange='', routing_key='agent_queue', body=message)
            MESSAGE_SENT.inc()
            messagebox.showinfo("Message Sent", f"Message sent to {agent}")
            self.log_message(f"[Sent] Message to {agent}")
            self.update_chat_history("User", agent, f"Message to {agent}")
            self.store_message_to_redis(agent, f"Message to {agent}")
        except Exception as e:
            messagebox.showerror("RabbitMQ Error", f"Failed to send message: {e}")
            self.log_message(f"[Error] Failed to send message to {agent}: {e}")
            FAILED_MESSAGES.inc()

    def broadcast_message(self):
        if self.paused:
            messagebox.showwarning("Paused", "Messaging is currently paused.")
            return

        try:
            message = json.dumps({
                "sender": "User",
                "recipient": "All Agents",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": "Broadcast message to all agents"
            })
            self.channel.basic_publish(exchange='', routing_key='agent_queue', body=message)
            MESSAGE_SENT.inc()
            messagebox.showinfo("Broadcast Sent", "Broadcast message sent to all agents")
            self.log_message("[Sent] Broadcast message to all agents")
            self.update_chat_history("User", "All Agents", "Broadcast message to all agents")
            self.store_message_to_redis("All Agents", "Broadcast message to all agents")
        except Exception as e:
            messagebox.showerror("RabbitMQ Error", f"Failed to broadcast message: {e}")
            self.log_message(f"[Error] Failed to broadcast message: {e}")
            FAILED_MESSAGES.inc()

    def send_custom_message(self):
        if self.paused:
            messagebox.showwarning("Paused", "Messaging is currently paused.")
            return

        custom_message = simpledialog.askstring("Custom Message", "Enter the message to send:")
        if custom_message:
            recipient = simpledialog.askstring("Recipient", "Enter the recipient (or 'All Agents' for broadcast):")
            if recipient:
                try:
                    message = json.dumps({
                        "sender": "User",
                        "recipient": recipient,
                        "timestamp": datetime.now
