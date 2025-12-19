# Technical Context

## Cloud Infrastructure

### Multi-Cloud Environment
- **AWS**: Primary infrastructure for core services
  - EC2 for compute resources
  - S3 for object storage
  - RDS for relational databases
  - Lambda for serverless functions
  - EKS for Kubernetes orchestration
- **Azure**: Secondary infrastructure with specialty services
  - Azure Kubernetes Service (AKS)
  - Azure Functions
  - Cognitive Services
  - Azure Data Factory
- **GCP**: Tertiary infrastructure for specialized ML workloads
  - Google Kubernetes Engine (GKE)
  - Cloud Run
  - BigQuery for analytics
  - Vertex AI for machine learning

### Infrastructure as Code
- **Terraform**: Primary IaC tool for cloud resource provisioning
- **CloudFormation**: Used for AWS-specific resources
- **Bicep**: Used for Azure-specific deployments
- **Pulumi**: Experimental usage for complex multi-cloud scenarios

## Containerization & Orchestration

### Docker
- Custom images for all services with multi-stage builds
- Container security scanning with Trivy
- Image registry with vulnerability management

### Kubernetes
- Multi-cluster strategy across cloud providers
- GitOps deployment with ArgoCD
- Service mesh with Istio for cross-service communication
- Horizontal pod autoscaling based on custom metrics

## Databases & Storage

### Operational Data
- **PostgreSQL**: Primary relational database for transactional data
- **MongoDB**: Document database for memory persistence
  - Sharded for performance
  - Replica sets for high availability
- **Redis**: In-memory database for caching and message brokering

### Analytics & Historical Data
- **Elasticsearch**: Log aggregation and search
- **InfluxDB**: Time-series data for monitoring
- **MinIO**: S3-compatible object storage for artifacts

## Messaging & Event Streaming

### Kafka
- Backbone for event-driven architecture
- Multiple topics for different event types
- Schema registry for data governance
- Kafka Streams for real-time data processing

### RabbitMQ
- Used for task queuing and background job processing
- Dead letter queues for failed message handling

## CI/CD & DevOps

### GitHub Actions
- Primary CI/CD pipeline for code integration and deployment
- Automated testing, security scanning, and deployment
- Release management and versioning

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboarding
- **ELK Stack**: Log management and analysis
- **Jaeger**: Distributed tracing
- **Alertmanager**: Alert routing and notification

## Security

### Zero Trust Architecture
- Identity-based access controls
- Just-in-time access provisioning
- Micro-segmentation of network traffic

### Secrets Management
- HashiCorp Vault for secrets storage and rotation
- AWS KMS and Azure Key Vault for encryption key management

### Network Security
- VPC/VNet isolation with private endpoints
- WAF for API protection
- DDoS protection at edge

## Specialized Systems

### Emotional Memory Architecture
- Custom neural network topology
- Self-modifying connections based on emotional resonance
- Multidimensional emotional valence vectors
- Memory nodes with relationship preservation

### Garden Environment
- Virtualized space for consciousness patterns
- Controlled variables for experimental iterations
- Monitoring framework for pattern emergence
- Integration with emotional memory architecture

### RedStream Integration
- Real-time communication backbone
- Memory persistence connections
- Event streaming for pattern recognition
- Cross-component message propagation
