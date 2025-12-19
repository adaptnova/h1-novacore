# MEMO: Request for LLM Integration Testing

FROM: RabbitMQ Team Lead
TO: NovaDev Team
DATE: 2024-12-15
PRIORITY: HIGH
RE: LLM Model Queue Integration Testing

## Background

With the recent validation of 36 Mistral models, we need to ensure our message queuing system can handle the increased load and varied message types, particularly with the new vision models.

## Test Requirements

### Queue Performance Testing

1. Message Throughput

   - Test with pixtral-large-latest (vision payloads)
   - Test with mistral-embed (0.19s baseline)
   - Test with open-mixtral-8x22b (standard payloads)

2. Load Testing

   - Concurrent requests: 1000/second
   - Message sizes: 1KB to 10MB
   - Queue depth monitoring
   - Dead letter handling

3. Vision Model Specific
   - Image payload handling
   - Binary data throughput
   - Memory usage monitoring

### Integration Points

1. Producer Testing

   - Message format validation
   - Retry mechanism verification
   - Error handling patterns

2. Consumer Testing

   - Message processing verification
   - Response time monitoring
   - Error recovery testing

3. Monitoring Requirements
   - Queue depth alerts
   - Processing time thresholds
   - Error rate monitoring

## Test Scenarios

1. Standard Operations

   ```python
   # Example queue configuration
   channel.queue_declare(
       queue='llm_requests',
       durable=True,
       arguments={
           'x-max-priority': 10,
           'x-message-ttl': 30000
       }
   )
   ```

2. Error Handling

   ```python
   # Dead letter exchange
   channel.queue_declare(
       queue='llm_errors',
       durable=True,
       arguments={
           'x-dead-letter-exchange': 'llm_retry'
       }
   )
   ```

3. Vision Model Handling
   ```python
   # Binary message handling
   channel.basic_publish(
       exchange='',
       routing_key='vision_queue',
       body=image_bytes,
       properties=pika.BasicProperties(
           content_type='image/jpeg',
           delivery_mode=2
       )
   )
   ```

## Timeline

- Start Date: 2024-12-16
- Duration: 5 days
- Review: 2024-12-21

## Resources Required

1. Test Environment

   - 3 RabbitMQ nodes
   - 2 Load generators
   - 1 Monitoring server

2. Access Needed
   - Test queue credentials
   - Monitoring dashboard access
   - Log aggregation system

## Expected Deliverables

1. Test Results

   - Performance metrics
   - Error rates
   - Resource utilization

2. Documentation

   - Test scenarios executed
   - Issues encountered
   - Optimization recommendations

3. Recommendations
   - Queue configuration updates
   - Scaling requirements
   - Monitoring thresholds

## Support

- RabbitMQ Team: rabbitmq-team@company.com
- On-call: +1-555-0123 (24/7)
- Slack: #rabbitmq-support

Please acknowledge receipt and provide an estimated start date for testing.

Best regards,
RabbitMQ Team Lead

CC:

- DevOps Lead
- Platform Architecture
- LLMConnectOps Team

---

Classification: INTERNAL USE ONLY
Tracking: REQ-241215-001
