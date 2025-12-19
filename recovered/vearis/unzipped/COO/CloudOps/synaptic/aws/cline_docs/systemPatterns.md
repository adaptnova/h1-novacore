# System Patterns

## Backup Processing Patterns

### Chunked Backup Pattern
```
[Source Directory]
       ↓
[Size Analysis]
       ↓
[Chunk Division (50GB)]
       ↓
[Per-Chunk Processing]
       ↓
[Error Recovery]
       ↓
[Chunk Verification]
       ↓
[Metadata Update]
```

### Error Recovery Pattern
```
[Rsync Error]
     ↓
[Log Error]
     ↓
[Continue Processing]
     ↓
[Retry Failed Items]
     ↓
[Update Status]
```

### Chunk Management Pattern
```
[Initialize Chunk]
      ↓
[Process Files]
      ↓
[Create Archive]
      ↓
[Upload to S3]
      ↓
[Verify Upload]
```

## Data Flow Patterns

### Backup Flow
1. Source Analysis
2. Chunk Division
3. Per-Chunk Processing
4. Error Handling
5. Verification
6. Metadata Management

### Error Handling Flow
1. Error Detection
2. Error Logging
3. Recovery Attempt
4. Progress Update
5. Status Report

## Implementation Patterns

### Chunk Processing
- Independent chunk handling
- Parallel processing capability
- Progress tracking per chunk
- Error isolation

### Error Recovery
- Graceful error handling
- Continued processing
- Failed item tracking
- Retry mechanism

### Metadata Management
- Per-chunk tracking
- Overall progress monitoring
- Error state recording
- Completion verification