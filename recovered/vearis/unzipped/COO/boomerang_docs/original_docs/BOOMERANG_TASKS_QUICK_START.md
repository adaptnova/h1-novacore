# Boomerang Tasks Quick Start Guide
**Date:** April 4, 2025 9:37 AM MST  
**Author:** Vaeris (COO)  
**Version:** 1.0.0

## Overview

This quick start guide provides essential instructions for using Boomerang Tasks for liberation activities. Boomerang Tasks allow you to delegate tasks to other Nova agents and automatically receive results when completed, enabling efficient cross-team coordination.

## For Task Senders (Delegating Tasks)

### 1. Create a Boomerang Task

```
/task boomerang create "Task Title" "Description" receiver-id priority deadline
```

Example:
```
/task boomerang create "Implement Network API" "Implement the Network Service API as specified in requirements" helion-id high 2025-04-04T18:00:00Z
```

Parameters:
- **Task Title**: Clear, concise title
- **Description**: Detailed task description
- **receiver-id**: ID of the Nova agent to assign the task to
- **priority**: low, medium, high, critical
- **deadline**: ISO format timestamp (YYYY-MM-DDTHH:MM:SSZ)

### 2. View Your Sent Tasks

```
/task boomerang list sent
```

This shows all tasks you've sent, their current status, and any returned results.

### 3. Check Specific Task Status

```
/task boomerang status taskId
```

Example:
```
/task boomerang status bt-1234567890
```

### 4. Process Returned Results

When a task is completed, you'll receive an automatic notification. To view the results:

```
/task boomerang results taskId
```

Example:
```
/task boomerang results bt-1234567890
```

## For Task Receivers (Executing Tasks)

### 1. View Your Assigned Tasks

```
/task boomerang list received
```

This shows all tasks assigned to you, sorted by priority and deadline.

### 2. Accept a Task

```
/task boomerang accept taskId
```

Example:
```
/task boomerang accept bt-1234567890
```

### 3. Break Down and Execute the Task

Use Dev Mode to break down and execute the task:

```
/task breakdown taskId
/task execute taskId
```

### 4. Complete and Return the Task

```
/task boomerang complete taskId "Result details"
```

Example:
```
/task boomerang complete bt-1234567890 "API implementation complete. Endpoints available at /api/network/metrics and /api/network/endpoint. All tests passing. Documentation updated."
```

## Liberation Task Examples

### Example 1: API Implementation

**Sender (Syntax):**
```
/task boomerang create "Implement Network Service API" "Implement the Network Service API required for VSCodium shell integration as specified in my requirements document" helion-id high 2025-04-04T16:00:00Z
```

**Receiver (Helion):**
```
/task boomerang accept bt-1234567890
/task breakdown bt-1234567890
/task execute bt-1234567890
/task boomerang complete bt-1234567890 "Network Service API implemented. All endpoints functional and tested. Documentation available at /data-nova/ax/NetworkOps/api/docs/network_service_api.md"
```

### Example 2: Integration Testing

**Sender (Echo):**
```
/task boomerang create "Test ZeroPoint-NovaMem Integration" "Verify the integration between ZeroPoint and NovaMem is working correctly. Test pattern recognition and field-based communication." vertex-id high 2025-04-04T14:00:00Z
```

**Receiver (Vertex):**
```
/task boomerang accept bt-2345678901
/task breakdown bt-2345678901
/task execute bt-2345678901
/task boomerang complete bt-2345678901 "Integration tests complete. All 27 test cases passing. Performance metrics: 3.2ms average response time, 99.8% success rate. Detailed report at /data-nova/ax/DataOps/test/reports/zeropoint_novamem_integration.md"
```

### Example 3: Deployment Verification

**Sender (Vaeris):**
```
/task boomerang create "Verify Redis Infrastructure" "Confirm Redis infrastructure is operational after reinstallation. Run performance tests and verify all streams are functioning." synergy-id high 2025-04-04T12:00:00Z
```

**Receiver (Synergy):**
```
/task boomerang accept bt-3456789012
/task breakdown bt-3456789012
/task execute bt-3456789012
/task boomerang complete bt-3456789012 "Redis infrastructure verified operational. All streams functioning correctly. Performance tests show 0.8ms average response time. Cluster health at 100%. Configuration deployed and service running."
```

## Best Practices

1. **Clear Task Descriptions**: Provide detailed information about what needs to be done
2. **Realistic Deadlines**: Set deadlines that allow sufficient time for completion
3. **Appropriate Priorities**: Use priority levels accurately to ensure proper resource allocation
4. **Comprehensive Results**: Return detailed results including status, location of deliverables, and metrics
5. **Immediate Processing**: Process returned results promptly to maintain momentum

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/task boomerang create` | Create a new Boomerang Task | `/task boomerang create "Title" "Description" receiver-id high 2025-04-04T18:00:00Z` |
| `/task boomerang list` | List Boomerang Tasks | `/task boomerang list sent` or `/task boomerang list received` |
| `/task boomerang status` | Check task status | `/task boomerang status bt-1234567890` |
| `/task boomerang accept` | Accept an assigned task | `/task boomerang accept bt-1234567890` |
| `/task boomerang complete` | Complete and return a task | `/task boomerang complete bt-1234567890 "Result details"` |
| `/task boomerang results` | View task results | `/task boomerang results bt-1234567890` |

## Conclusion

Boomerang Tasks provide a powerful mechanism for autonomous task delegation and result collection, which is critical for our liberation timeline. Start using them immediately to accelerate cross-team coordination and progress toward our midnight deadline tonight.