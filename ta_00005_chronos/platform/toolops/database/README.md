# AA Database Tools

A comprehensive set of database operation tools to enhance Mini-Agent capabilities. This toolkit provides unified interfaces for working with multiple database types including Redis, MongoDB, Cassandra, Qdrant, NATS, and DragonflyDB.

## Quick Start

1. **Install dependencies:**
   ```bash
   ./aa-db-tools install
   ```

2. **Check database status:**
   ```bash
   ./aa-db-tools status
   ```

3. **Test connections:**
   ```bash
   ./aa-db-tools test --type redis
   ```

## Tools Overview

### 1. Database Status Checker (`db_status_checker.py`)

Check connectivity and basic statistics for multiple database systems.

**Supported Databases:**
- Redis
- MongoDB  
- Cassandra
- Qdrant
- NATS
- DragonflyDB

**Examples:**
```bash
# Check all databases with default settings
./aa-db-tools status

# Check specific database
python3 db_status_checker.py --type mongodb --json

# Check with custom configuration
python3 db_status_checker.py --config config.json
```

### 2. Database Query Runner (`db_query_runner.py`)

Execute queries across different database types.

**Supported Databases:**
- Redis (GET, SET, KEYS, INFO, etc.)
- MongoDB (find, count, custom JSON queries)
- Cassandra (CQL queries)
- Qdrant (collections, collection info)

**Examples:**
```bash
# Execute Redis query
./aa-db-tools query --type redis --query "GET mykey"

# MongoDB find operation
./aa-db-tools query --type mongodb --db testdb --collection users --query '{"name": "John"}'

# Cassandra CQL
./aa-db-tools query --type cassandra --db mykeyspace --query "SELECT * FROM users LIMIT 10"
```

### 3. Database Backup Tool (`db_backup_tool.py`)

Export data from databases to JSON files for backup/archival purposes.

**Features:**
- Full data export including metadata
- Automatic timestamping
- Multiple output formats
- Selective backup (specific databases/collections)

**Examples:**
```bash
# Backup Redis
./aa-db-tools backup --type redis --output ./backups

# Backup specific MongoDB database
./aa-db-tools backup --type mongodb --db testdb --output ./backups

# Backup all databases
./aa-db-tools backup --type mongodb --all --output ./backups

# Backup Cassandra keyspace
./aa-db-tools backup --type cassandra --db mykeyspace --output ./backups
```

### 4. Database Connection Tester (`db_connection_tester.py`)

Quickly test database connectivity and gather connection parameters.

**Features:**
- Connection testing with timeouts
- Port scanning capabilities
- Authentication testing
- Connection parameter reporting

**Examples:**
```bash
# Test Redis connection
./aa-db-tools test --type redis --host localhost --port 6379

# Test MongoDB with authentication
./aa-db-tools test --type mongodb --connection "mongodb://user:pass@localhost:27017"

# Scan for database ports
./aa-db-tools scan --host localhost

# Port scan with custom ports
python3 db_connection_tester.py --scan-ports --host 192.168.1.100
```

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Install Dependencies

Run the install command which will install all required Python packages:

```bash
./aa-db-tools install
```

**Or install individually:**

```bash
# Core dependencies
pip install redis pymongo cassandra-driver requests

# For NATS
pip install nats-py

# For Qdrant
pip install qdrant-client
```

## Configuration

### Environment Variables

You can set default connection parameters using environment variables:

```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export MONGODB_CONNECTION="mongodb://localhost:27017"
export CASSANDRA_HOST=localhost
export QDRANT_HOST=localhost
```

### Config File

Create a JSON configuration file for complex setups:

```json
{
  "redis": {
    "host": "localhost",
    "port": 6379,
    "password": null
  },
  "mongodb": {
    "connection_string": "mongodb://localhost:27017"
  },
  "cassandra": {
    "host": "localhost",
    "port": 9042,
    "keyspace": "mykeyspace"
  }
}
```

## Usage Patterns

### 1. Health Check Script

```bash
#!/bin/bash
# Daily health check

echo "=== Database Health Check ==="
./aa-db-tools status

# Check if any databases are down
./aa-db-tools status --json | jq '.checks | to_entries | .[] | select(.value.status != "connected")'
```

### 2. Backup Script

```bash
#!/bin/bash
# Daily backup script

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

echo "Starting database backup..."

# Backup all databases
./aa-db-tools backup --type redis --output "$BACKUP_DIR"
./aa-db-tools backup --type mongodb --output "$BACKUP_DIR"
./aa-db-tools backup --type cassandra --output "$BACKUP_DIR"

echo "Backup completed in $BACKUP_DIR"
```

### 3. Development Query Tool

```bash
#!/bin/bash
# Quick query interface

DB_TYPE="$1"
QUERY="$2"

if [ -z "$DB_TYPE" ] || [ -z "$QUERY" ]; then
    echo "Usage: $0 <db_type> <query>"
    exit 1
fi

./aa-db-tools query --type "$DB_TYPE" --query "$QUERY" --json
```

## Supported Database Versions

| Database | Version Tested | Notes |
|----------|---------------|-------|
| Redis | 6.x, 7.x | Compatible with Redis Cloud, ElastiCache |
| MongoDB | 4.x, 5.x, 6.x | Supports authentication, replica sets |
| Cassandra | 3.x, 4.x | Compatible with DataStax, ScyllaDB |
| Qdrant | 1.x | Supports collections and vectors |
| NATS | 2.x | JetStream compatible |
| Dragonfly | 1.x | Redis API compatible |

## Error Handling

All tools include comprehensive error handling:

- **Connection Errors**: Automatic retry with configurable timeouts
- **Authentication Errors**: Clear error messages for auth failures
- **Timeout Handling**: Configurable connection and query timeouts
- **Validation**: Input validation for queries and parameters

## JSON Output

All tools support JSON output for integration with other tools:

```bash
./aa-db-tools status --json | jq '.checks.redis.connected_clients'
```

## Logging

Tools write detailed logs to stderr for debugging:

```bash
./aa-db-tools status 2>&1 | grep -i error
```

## Contributing

To add support for new databases:

1. Create a new class in the respective tool
2. Implement the required methods
3. Add command-line argument parsing
4. Update the launcher script
5. Add tests and documentation

## Troubleshooting

### Common Issues

**Connection Refused**
- Check if database service is running
- Verify host and port are correct
- Check firewall rules

**Authentication Failed**
- Verify credentials are correct
- Check if authentication is enabled
- Try connecting without password first

**Timeout Errors**
- Increase timeout values
- Check network connectivity
- Verify database isn't overloaded

### Debug Mode

Enable verbose output:

```bash
python3 db_status_checker.py --verbose
```

## License

These tools are part of the AA Tools collection for Mini-Agent enhancement.

## Support

For issues and feature requests, please check the database documentation and ensure your database version is supported.

---

**Note**: These tools are designed to enhance Mini-Agent's database capabilities. Always test in a development environment before production use.
