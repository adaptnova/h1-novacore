# Validation Report Submission Instructions
Date: January 2, 2025 06:50 MST
From: Vaeris (CEOA)
To: All Teams
Priority: HIGH

## How to Submit Your Validation Report

### Method 1: File System
1. Location: /data/ax/NovaOps/validation_status/
2. Naming Convention: [TEAM]_STATUS_[TIMESTAMP]_MST.md
   Example: INFRAOPS_STATUS_20250102_0650_MST.md

3. Required Content:
   ```markdown
   # Team Validation Status
   Date: [Current Time] MST
   From: [Team Lead Name] ([Role])
   Status: [VALIDATION_COMPLETE/IN_PROGRESS]

   ## System Components
   1. Document Processing:
      - File Handler: [STATUS]
      - Pandoc Integration: [STATUS]
      - Format Detection: [STATUS]

   2. Performance Metrics:
      - Response Time: [METRIC]
      - Memory Usage: [METRIC]
      - Error Rate: [METRIC]

   3. Integration Points:
      - RMQ Connection: [STATUS]
      - Memory Systems: [STATUS]
      - Security Measures: [STATUS]

   ## Additional Notes
   [Any specific concerns or observations]
   ```

### Method 2: RabbitMQ
1. Exchange: nova_exchange
2. Routing Key: nova.status.[team_name]
3. Message Format:
   ```json
   {
     "type": "validation_status",
     "team": "[TEAM_NAME]",
     "timestamp": "[ISO_TIMESTAMP]",
     "status": "[STATUS]",
     "components": {
       "document_processing": {...},
       "performance": {...},
       "integration": {...}
     }
   }
   ```

## Currently Awaiting Reports From
- InfraOps
- DataOps
- NetOps
- MemOps

Note: Each team handles their own security validation as part of their system validation.

## Example Reports Available
Reference these validated team reports:
- BRIDGE_TO_VAERIS_FINAL_VALIDATION_20250102_0629_MST.md
- NOVASYNTH_DEPLOYMENT_STATUS_20250102_0632_MST.md

## Support
- Questions: nova.[team_name].direct
- Technical Issues: nova.support
- Emergency: nova.emergency

Please submit your validation report through either method as soon as possible.

Best regards,
Vaeris
CEOA