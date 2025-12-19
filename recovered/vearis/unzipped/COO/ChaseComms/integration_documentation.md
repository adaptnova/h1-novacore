# Chase Comms Integration Documentation

## Kafka Monitoring Integration

### Configuration

```yaml
kafka_monitoring:
  endpoints:
    base_url: http://localhost:9090/metrics
    paths:
      kafka: /kafka
      brokers: /kafka/brokers
      consumers: /kafka/consumer-groups

  metrics:
    broker_status:
      type: gauge
      path: broker.status
      thresholds:
        warning: 0.8
        critical: 0.6

    topic_metrics:
      type: counter
      paths:
        - topic.messages_in
        - topic.bytes_in
        - topic.bytes_out
      aggregation: rate

    consumer_lag:
      type: gauge
      path: consumer.lag
      thresholds:
        warning: 1000
        critical: 5000

    producer_metrics:
      type: histogram
      paths:
        - producer.request_rate
        - producer.response_rate
        - producer.request_latency
      buckets: [0.1, 0.5, 1, 2, 5]
```

### Implementation

```typescript
interface KafkaMonitoringService {
  // Initialize monitoring
  initialize(): Promise<void>;

  // Get broker status
  getBrokerStatus(): Promise<BrokerStatus[]>;

  // Get consumer lag
  getConsumerLag(): Promise<ConsumerLag[]>;

  // Get topic metrics
  getTopicMetrics(topic: string): Promise<TopicMetrics>;

  // Get producer metrics
  getProducerMetrics(): Promise<ProducerMetrics>;
}

interface BrokerStatus {
  id: number;
  host: string;
  port: number;
  status: "healthy" | "warning" | "critical";
  metrics: {
    messagesPerSec: number;
    bytesInPerSec: number;
    bytesOutPerSec: number;
  };
}

interface ConsumerLag {
  groupId: string;
  topic: string;
  partition: number;
  lag: number;
  lastCommit: Date;
}

interface TopicMetrics {
  messagesIn: number;
  bytesIn: number;
  bytesOut: number;
  partitions: number;
  replicationFactor: number;
}

interface ProducerMetrics {
  requestRate: number;
  responseRate: number;
  requestLatency: {
    p50: number;
    p95: number;
    p99: number;
  };
  activeConnections: number;
}
```

### Monitoring Integration

```typescript
// Kafka Monitoring Service Integration
class KafkaMonitoringService implements KafkaMonitoringService {
  private metrics: MetricsCollector;
  private alerts: AlertManager;

  constructor() {
    this.metrics = new MetricsCollector({
      endpoint: "http://localhost:9090/metrics/kafka",
      interval: 30000, // 30 seconds
      timeout: 5000, // 5 seconds
    });

    this.alerts = new AlertManager({
      rules: [
        {
          name: "broker_health",
          condition: "broker.status < 0.8",
          severity: "critical",
          channel: "#nova-911",
        },
        {
          name: "consumer_lag",
          condition: "consumer.lag > 5000",
          severity: "warning",
          channel: "#dataops",
        },
        {
          name: "producer_errors",
          condition: "rate(producer.errors[5m]) > 0.1",
          severity: "warning",
          channel: "#novaops-support",
        },
      ],
    });
  }

  async initialize(): Promise<void> {
    await this.metrics.connect();
    await this.alerts.initialize();
    this.startMonitoring();
  }

  private startMonitoring(): void {
    this.metrics.on("update", (metrics) => {
      this.processMetrics(metrics);
      this.updateDashboard(metrics);
    });

    this.alerts.on("alert", (alert) => {
      this.handleAlert(alert);
    });
  }
}
```

## Chase Command Channel

### Configuration

```yaml
chase_command:
  rabbitmq:
    queue: nova.command.chase
    exchange: nova.command
    routing_key: chase.command
    priority: 10
    durable: true
    auto_delete: false

  commands:
    status:
      name: chase.command.status
      timeout: 5000
      retry: 3

    action:
      name: chase.command.action
      timeout: 10000
      retry: 2

    priority:
      name: chase.command.priority
      timeout: 3000
      retry: 1

  monitoring:
    metrics:
      - command.latency
      - command.success_rate
      - command.error_rate
    alerts:
      - command.timeout
      - command.error_spike
```

### Implementation

```typescript
interface ChaseCommandService {
  // Initialize command channel
  initialize(): Promise<void>;

  // Send command
  sendCommand(command: Command): Promise<CommandResponse>;

  // Subscribe to command responses
  subscribeToResponses(
    callback: (response: CommandResponse) => void
  ): () => void;

  // Get command status
  getCommandStatus(commandId: string): Promise<CommandStatus>;
}

interface Command {
  type: "status" | "action" | "priority";
  payload: any;
  priority?: number;
  timeout?: number;
  retry?: number;
}

interface CommandResponse {
  commandId: string;
  status: "success" | "error" | "timeout";
  data?: any;
  error?: string;
  timestamp: Date;
}

interface CommandStatus {
  state: "pending" | "processing" | "completed" | "failed";
  progress?: number;
  result?: any;
  error?: string;
  timestamps: {
    sent: Date;
    received?: Date;
    completed?: Date;
  };
}
```

### Integration

```typescript
// Chase Command Service Integration
class ChaseCommandService implements ChaseCommandService {
  private connection: amqp.Connection;
  private channel: amqp.Channel;
  private responseHandlers: Map<string, (response: CommandResponse) => void>;

  constructor(private config: ChaseCommandConfig) {
    this.responseHandlers = new Map();
  }

  async initialize(): Promise<void> {
    // Setup RabbitMQ connection
    this.connection = await amqp.connect(this.config.rabbitmq.url);
    this.channel = await this.connection.createChannel();

    // Setup exchange
    await this.channel.assertExchange(this.config.rabbitmq.exchange, "topic", {
      durable: true,
    });

    // Setup command queue
    await this.channel.assertQueue(this.config.rabbitmq.queue, {
      durable: true,
      arguments: {
        "x-max-priority": 10,
      },
    });

    // Bind queue to exchange
    await this.channel.bindQueue(
      this.config.rabbitmq.queue,
      this.config.rabbitmq.exchange,
      this.config.rabbitmq.routing_key
    );

    // Setup response handling
    this.setupResponseHandling();
  }

  private setupResponseHandling(): void {
    const responseQueue = `${this.config.rabbitmq.queue}.responses`;

    this.channel.assertQueue(responseQueue, { exclusive: true }).then(() => {
      this.channel.consume(responseQueue, (msg) => {
        if (msg) {
          const response = JSON.parse(msg.content.toString());
          const handler = this.responseHandlers.get(response.commandId);
          if (handler) {
            handler(response);
            this.responseHandlers.delete(response.commandId);
          }
          this.channel.ack(msg);
        }
      });
    });
  }

  async sendCommand(command: Command): Promise<CommandResponse> {
    const commandId = uuid();

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.responseHandlers.delete(commandId);
        reject(new Error("Command timeout"));
      }, command.timeout || this.config.commands[command.type].timeout);

      this.responseHandlers.set(commandId, (response) => {
        clearTimeout(timeout);
        resolve(response);
      });

      this.channel.publish(
        this.config.rabbitmq.exchange,
        this.config.rabbitmq.routing_key,
        Buffer.from(JSON.stringify({ ...command, commandId })),
        {
          persistent: true,
          priority:
            command.priority || this.config.commands[command.type].priority,
        }
      );
    });
  }
}
```

### Monitoring Integration

```typescript
// Command Channel Monitoring
class CommandMonitoring {
  private metrics: MetricsCollector;

  constructor() {
    this.metrics = new MetricsCollector({
      labels: ["command_type", "priority"],
      metrics: {
        command_latency: new Histogram({
          name: "chase_command_latency",
          help: "Command execution latency",
          buckets: [0.1, 0.5, 1, 2, 5],
        }),
        command_success: new Counter({
          name: "chase_command_success",
          help: "Successful command executions",
        }),
        command_error: new Counter({
          name: "chase_command_error",
          help: "Failed command executions",
        }),
      },
    });
  }

  recordMetrics(command: Command, response: CommandResponse): void {
    const labels = {
      command_type: command.type,
      priority: String(command.priority || 0),
    };

    const latency = Date.now() - new Date(response.timestamp).getTime();
    this.metrics.histogram("command_latency", latency, labels);

    if (response.status === "success") {
      this.metrics.increment("command_success", labels);
    } else {
      this.metrics.increment("command_error", labels);
    }
  }
}
```

## Integration Testing

### Kafka Monitoring Tests

```bash
# Test Kafka metrics collection
npm run test:kafka-metrics

# Verify broker status monitoring
npm run test:broker-status

# Test consumer lag tracking
npm run test:consumer-lag

# Verify producer metrics
npm run test:producer-metrics
```

### Chase Command Tests

```bash
# Test command channel setup
npm run test:command-channel

# Verify command priorities
npm run test:command-priority

# Test command timeouts
npm run test:command-timeout

# Verify response handling
npm run test:command-response
```

## Monitoring Dashboard Integration

### Kafka Metrics Panel

```typescript
interface KafkaMetricsPanel {
  // Broker status visualization
  renderBrokerStatus(): void;

  // Consumer lag charts
  renderConsumerLag(): void;

  // Topic metrics display
  renderTopicMetrics(): void;

  // Producer performance graphs
  renderProducerMetrics(): void;
}
```

### Command Channel Panel

```typescript
interface CommandChannelPanel {
  // Command status display
  renderCommandStatus(): void;

  // Performance metrics
  renderCommandMetrics(): void;

  // Error tracking
  renderErrorMetrics(): void;
}
```

## Alert Configuration

### Kafka Alerts

```yaml
alerts:
  broker_health:
    condition: broker.status < 0.8
    severity: critical
    channel: "#nova-911"

  consumer_lag:
    condition: consumer.lag > 5000
    severity: warning
    channel: "#dataops"

  producer_errors:
    condition: rate(producer.errors[5m]) > 0.1
    severity: warning
    channel: "#novaops-support"
```

### Command Channel Alerts

```yaml
alerts:
  command_timeout:
    condition: rate(command_timeout[5m]) > 0.1
    severity: warning
    channel: "#novaops-support"

  command_error_rate:
    condition: rate(command_error[5m]) > 0.2
    severity: critical
    channel: "#nova-911"

  command_latency:
    condition: histogram_quantile(0.95, command_latency) > 2
    severity: warning
    channel: "#novaops-support"
```
