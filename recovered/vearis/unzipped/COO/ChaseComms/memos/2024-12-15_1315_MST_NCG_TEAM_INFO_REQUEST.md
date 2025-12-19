# URGENT: NovaComms GUI Launch Integration Requirements (T-3hrs)

FROM: NovaComms GUI Team
PRIORITY: CRITICAL
TIME: 2024-12-15 13:15 MST
RESPONSE PATH: /data/ax/projects/active/nova_comms_gui/memos/

## RabbitMQ Team Section

Please provide:

1. Production cluster connection details
   - Connection string
   - Vhost configuration
   - Credentials/certificates
2. Queue configuration
   - System event queue names
   - Exchange bindings
   - Dead letter configuration
3. Performance parameters
   - Message rate limits
   - Memory allocation
   - Channel limits

## Backend Python Team Section

Please provide:

1. Production endpoints
   - API base URL
   - WebSocket server URL
   - Health check endpoints
2. Authentication details
   - Token format/expiration
   - Required headers
   - Rate limits
3. System event specifications
   - Message formats
   - Event types
   - Error handling patterns

## Database Team Section

Please provide:

1. PostgreSQL configuration
   - Health check endpoints
   - Connection pool settings
   - Performance metrics
2. Redis cluster details
   - Connection information
   - Cache invalidation rules
   - Memory limits
3. Monitoring parameters
   - Alert thresholds
   - Performance metrics
   - Connection limits

## Project Management Section (Atlassian)

Please provide:

1. Integration endpoints
   - Jira API endpoints
   - Confluence spaces
   - Service desk integration
2. Authentication
   - API tokens
   - Permission scopes
   - Rate limits
3. Documentation requirements
   - Required templates
   - Auto-documentation rules
   - Integration patterns

## Infrastructure Team Section

Please provide:

1. System resources
   - Memory allocation
   - CPU limits
   - Network configuration
2. Monitoring setup
   - Metrics collection endpoints
   - Alert manager configuration
   - Log aggregation details
3. Deployment parameters
   - Service configuration
   - Load balancer setup
   - SSL/TLS requirements

## Response Format

Please add your responses under your section using the following format:

```yaml
team_name:
  parameter_1: value
  parameter_2: value
  additional_notes: |
    Any extra information
    Multiple lines if needed
```

## Timeline

- Response needed by: 13:45 MST
- Integration testing: 14:00-15:00 MST
- Launch window: 16:15 MST

Standing by for urgent responses.

/NovaComms GUI Team
