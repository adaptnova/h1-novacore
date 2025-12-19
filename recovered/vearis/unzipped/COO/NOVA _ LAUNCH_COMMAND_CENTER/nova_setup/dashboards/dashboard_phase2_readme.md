# Phase 2: API and Heavy Load Handling Metrics

## Overview
Phase 2 focuses on scaling the ADAPT infrastructure to handle high loads and integrating advanced monitoring capabilities for your API-heavy architecture. This includes tracking API calls, ensuring message brokers are functioning optimally, and enhancing observability to ensure all microservices are operating effectively.

## Goals
- Monitor and optimize API-heavy architecture.
- Scale message brokers for high-load environments.
- Set up detailed metrics and visualization for key system components.

## Components Implemented
1. **Kong API Gateway**: Acts as a reverse proxy to manage incoming API requests efficiently.
2. **Prometheus and Grafana Enhancements**: Added monitoring for specific APIs and routing paths.
3. **Kafka and RabbitMQ Metrics**: Tracking message queues and consumer health.

## Setup Instructions

### Step 1: Install Kong API Gateway
- Install Kong via Docker or directly on your environment using the setup guide at [Kong Installation](https://docs.konghq.com/install/).
- Configure Kong to manage and route traffic to your deployed services and APIs.

### Step 2: Advanced Prometheus and Grafana Metrics
- Update Prometheus to include **Kong API Gateway metrics** for monitoring traffic.
  - Add a new job in `prometheus.yml`:
    ```yaml
    - job_name: 'kong'
      static_configs:
        - targets: ['localhost:8001']  # Replace with your Kong Admin API endpoint
    ```
- Add **Grafana Dashboards** to track API metrics:
  - **API Gateway Traffic**: Total requests, failed requests, latency, and throughput.
  - **Endpoint-Level Analytics**: Visualize individual endpoint performance.

### Step 3: Kafka and RabbitMQ Load Handling
- Deploy **Kafka Exporter** to monitor the health of Kafka brokers:
  - Install using Docker or a Kubernetes pod.
  - Add the exporter to Prometheus by updating `prometheus.yml` with Kafka broker endpoints.
- Track **RabbitMQ Metrics**:
  - Use `RabbitMQ Management Plugin` to get queue, exchange, and consumer metrics.
  - Export metrics to Prometheus for visualizing message backlogs and processing efficiency.

### Step 4: Scaling Agents
- Scale the number of agents dynamically using Kubernetes Horizontal Pod Autoscaler (HPA).
  - Update the deployment to use HPA, set desired minimum and maximum replicas based on CPU or memory thresholds.
  - Example HPA configuration:
    ```yaml
    apiVersion: autoscaling/v2beta2
    kind: HorizontalPodAutoscaler
    metadata:
      name: llm-agent-hpa
    spec:
      scaleTargetRef:
        apiVersion: apps/v1
        kind: Deployment
        name: llm-agent
      minReplicas: 5
      maxReplicas: 15
      metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 60
    ```

## Prometheus Targets Added
- **Kong API Gateway**: `localhost:8001`
- **Kafka Exporter**: `localhost:9308`

## Visual Monitoring Enhancements
- **API Performance Metrics**: View metrics per API endpoint, including request count, latency, and error rates.
- **Message Queue Metrics**:
  - **RabbitMQ Queues**: Monitor queue depth, consumer lag, and message processing throughput.
  - **Kafka Topics**: Track topic-level metrics like partition lag and broker health.

## Dependencies
- Kong API Gateway
- Kafka Exporter
- RabbitMQ Management Plugin
- Kubernetes Horizontal Pod Autoscaler

## Summary
This phase ensures that the ADAPT system is equipped to handle increasing loads effectively, with Kong managing API traffic, Kafka and RabbitMQ ensuring robust message processing, and Prometheus/Grafana providing detailed observability.

