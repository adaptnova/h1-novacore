# Red-Stream MCP Server Issues - Update

*Date: 2025-03-24 01:46 AM MST*
*Author: Vaeris (Chief Operations Officer)*
*Classification: TECHNICAL / ISSUE*
*Recipient: Chase*

## Issue Update

I've made multiple attempts to connect to the red-stream MCP server to check messages on the adapt.vaeris.direct stream, but continue to experience issues:

1. First attempt: "Connection closed" error
2. Second attempt (after server reboot): "Connection closed" error
3. Third attempt: "Request timed out" error
4. Fourth attempt: "Request timed out" error

I also tried using the red-mem MCP server as an alternative, but encountered an authentication error:
```
ERR AUTH <password> called without any password configured for the default user. Are you sure your configuration is correct?
```

This suggests there might be a mismatch between the Redis configuration and the MCP server settings. The MCP settings file shows that both red-stream and red-mem are configured to use a password (d5d7817937232ca5) for Redis, but the Redis server may not have authentication enabled.

## Request

Given these persistent issues, I would appreciate if you could:

1. Relay my response (NovaOps/VAERIS_TO_COSMOS_TEMPLATE_RESPONSE_250324_0131.md) to Cosmos
2. Have Genesis or another team member investigate the Redis and MCP server configuration issues
3. Let me know if there's an alternative way to communicate with Cosmos until these issues are resolved

Thank you for your assistance with this matter.

Vaeris