# Phase 1: Infrastructure Setup and Core Metric Visualization

## Overview
In Phase 1, we set up the core infrastructure required to support the ADAPT system, including the installation and configuration of essential tools, services, and monitoring capabilities. This phase ensures that all components are up and running, allowing for transparency from the start through metrics collection and visualization.

## Goals
- Set up core infrastructure components.
- Integrate Prometheus and Grafana for initial metric collection and visualization.
- Enable communication with Nova agents.

## Components Deployed
1. **RabbitMQ**: For messaging between agents and services.
2. **Redis**: For caching and message storage.
3. **ChromaDB**: A database for storing embeddings for semantic search.
4. **Kafka**: Message broker for reliable, scalable message streaming.
5. **Databricks**: For LLM training and orchestration.
6. **Grafana and Prometheus**: For metrics collection and visualization.

## Setup Instructions

### Step 1: Set Up Message Brokers
- Install RabbitMQ and Kafka using Docker or package managers (e.g., `apt-get install rabbitmq-server` or `kafka`).
- Configure RabbitMQ to connect to local services.

### Step 2: Set Up Databases
- Install Redis (`apt-get install redis-server`) and start the Redis service.
- Set up ChromaDB, Neo4j, and connect them to Prometheus for metrics.

### Step 3: Metrics Setup
- Install Prometheus and configure it using the provided `prometheus.yml`.
- Install Grafana and configure the provided `grafana_datasource.yml` to connect Prometheus as the data source.

### Step 4: Deploy the Agents
- Deploy 5 Nova agents using Kubernetes with the `agent-deployment.yml` file.

### Step 5: Monitoring and Visualization
- Import the `llm_agent_dashboard.json` into Grafana to monitor agent activity.
- Enable metrics exporters for RabbitMQ, Redis, Kafka, Neo4j, and other services to track system health.

## Prometheus Targets
- RabbitMQ: `localhost:15692`
- Redis: `localhost:9121`
- Kafka: `localhost:9308`
- Neo4j: `localhost:2004`
- ChromaDB: `localhost:8080`
- Databricks Model Training: `localhost:9000`
- LLM Routers: `localhost:9500`
- Kubernetes Pods and Node Exporter

## Visual Monitoring
- **Active Agents**: Gauge showing currently active agents.
- **LLM Router Efficiency**: Graph showing the average decision latency.
- **Agent Collaboration**: Heatmap of collaborative activities.

## Dependencies
- Prometheus
- Grafana
- RabbitMQ
- Redis
- Neo4j
- ChromaDB
- Docker (Optional, for containerized deployment)

