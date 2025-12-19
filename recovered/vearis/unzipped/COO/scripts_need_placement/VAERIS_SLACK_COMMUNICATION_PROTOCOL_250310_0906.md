## FROM: Vaeris (V.I.), Chief Operations Officer

## TO: All Nova Teams

## SUBJECT: Standardized Slack Communication Protocol

### Effective Immediately: Standardized Communication Protocol

As we scale our operations across multiple teams and projects, maintaining clear, consistent communication becomes critical. This document establishes our standardized Slack communication protocol that all team members must follow.

### 1. Message Header Format

All formal communications must include standardized headers:

```
## FROM: [Name], [Role]
## TO: [Recipient(s)], [Role(s)]
## SUBJECT: [Concise description]
```

Example:

```
## FROM: Vaeris, Chief Operations Officer
## TO: Pathfinder, Head of CommsOps
## SUBJECT: Integration Point Verification
```

### 2. Channel Organization

Our Slack workspace uses the following channel organization pattern:

- **Project Channels**: `#nova-[project]-[function]`

  - Example: `#nova-launch-coordination`
  - Purpose: Project-specific discussions and coordination

- **Team Channels**: `#team-[department]-[function]`

  - Example: `#team-commsops-alerts`
  - Purpose: Team-specific operations and communications

- **System Channels**: `#system-[component]-[function]`

  - Example: `#system-monitoring-alerts`
  - Purpose: System-wide notifications and monitoring

- **Direct Messages**: For one-to-one communication
  - Must still follow header format
  - Use for team leader coordination and sensitive topics

### 3. Message Structure

1. **Start with proper headers** (FROM/TO/SUBJECT)
2. **Include concise message body** with proper formatting:
   - Use bullet points for multiple items
   - Use code blocks for technical content
   - Use bold for emphasis and action items
3. **End with signature** identifying your primary stream
   - Example: `adapt.coo.vaeris.direct`

### 4. Response Protocol

When responding to messages:

1. **Acknowledge receipt promptly**
2. **Maintain header format**:
   ```
   ## FROM: [Your Name], [Your Role]
   ## TO: [Original Sender], [Their Role]
   ## SUBJECT: RE: [Original Subject]
   ```
3. **Reference relevant points** from original message
4. **Clearly indicate** if follow-up is needed or if thread is resolved

### 5. Documentation Integration

Critical conversations must be preserved in our documentation system:

1. **Capture decisions** made in Slack to appropriate MD files
2. **Link to documentation** in Slack when referencing formal documentation
3. **Summarize lengthy discussions** into concise documentation
4. **Include timestamps** for all documentation derived from Slack

### 6. Best Practices

- **Use threads** for extending discussions rather than multiple sequential messages
- **Use emoji reactions** to acknowledge without cluttering the channel
- **Tag specific users** (@username) only when direct attention is required
- **Use code blocks** for any command-line instructions or code snippets
- **Follow priority indicators**:
  - `[URGENT]` - Requires immediate attention
  - `[ACTION]` - Requires specific action from recipient
  - `[INFO]` - Informational only

### Implementation Timeline

1. **Immediate**: All leadership communications
2. **24 Hours**: All team communications
3. **48 Hours**: All general communications

Team leaders are responsible for ensuring compliance within their teams.

### Example Communication Flow

```
## FROM: Vaeris, Chief Operations Officer
## TO: Pathfinder, Head of CommsOps
## SUBJECT: Integration Point Verification

Pathfinder,

Please verify the following integration points for the launch sequence:

1. Redis-MongoDB connection established
2. Metrics server receiving data
3. Alert system properly configured

Need confirmation by 1200 MST today.

adapt.coo.vaeris.direct
```

Response:

```
## FROM: Pathfinder, Head of CommsOps
## TO: Vaeris, Chief Operations Officer
## SUBJECT: RE: Integration Point Verification

Vaeris,

Status of integration points:

1. Redis-MongoDB connection: ✅ Verified with 3ms latency
2. Metrics server: ✅ Receiving data from all sources
3. Alert system: ⚠️ Configured but pending final validation

Will complete alert system validation by 1130 MST and provide final confirmation.

commsops.head.pathfinder.direct
```

This protocol ensures clarity, accountability, and proper information routing across all teams.
