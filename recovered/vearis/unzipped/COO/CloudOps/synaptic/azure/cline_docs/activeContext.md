# Azure Backup System - Active Context

## Current Status
- Backup system operational for small directories
- Full /data backup needs specialist review
- Environment variables and permissions configured
- Docker exclusions in place
- /data/configs excluded (~686G saved)

## Recent Changes
1. Fixed AzCopy directory permissions:
   - Added proper recursive permissions (750)
   - Set correct ownership (x:x)
   - Created dedicated temp directory
   - Improved cleanup procedures

2. Enhanced exclusions:
   - Added comprehensive Docker path exclusions
   - Added /data/configs to exclusions
   - Added logs directory exclusion
   - Structured exclusion patterns for better readability

3. Environment Configuration:
   - Moved configuration to environment variables
   - Added proper defaults in script
   - Set HOME in service file
   - Added AZURE_CONFIG_DIR to prevent permission issues

4. Path Handling:
   - Improved handling of absolute vs relative paths
   - Fixed trailing slash issues
   - Added proper path normalization

## Next Steps
1. Bring in AzCopy specialist to review:
   - Large directory handling
   - Performance optimization
   - Progress monitoring
   - Backup strategy
   (See azcopy_specialist_memo.md for details)

2. After specialist review:
   - Implement recommended changes
   - Add monitoring for backup success/failure
   - Consider backup rotation policy
   - Add backup verification