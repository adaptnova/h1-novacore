# ScyllaDB Migration Script
**Date:** March 23, 2025
**Author:** Vertex, DataOps Team Lead
**Priority:** $1 (Highest)
**Execution Window:** 60 minutes

## Pre-Migration Checklist

- [ ] Verify current ScyllaDB Docker container is healthy
- [ ] Ensure target server has sufficient resources
- [ ] Confirm backup system is operational
- [ ] Notify dependent services of planned migration
- [ ] Verify network connectivity and firewall rules

## Environment Variables

```bash
# Target server information
TARGET_SERVER="dataops-primary"
TARGET_IP="52.118.145.162"

# ScyllaDB version and paths
SCYLLA_VERSION="5.2.0"
SCYLLA_DATA_PATH="/var/lib/scylladb"
SCYLLA_CONFIG_PATH="/etc/scylla"
SCYLLA_LOG_PATH="/var/log/scylla"

# Docker container information
DOCKER_CONTAINER_NAME="scylladb"

# Backup paths
BACKUP_PATH="/data-nova/ax/DataOps/database_backups/scylladb_migration_$(date +%Y%m%d_%H%M%S)"

# Service account
SCYLLA_USER="scylla"
SCYLLA_GROUP="scylla"
```

## Migration Procedure

### 1. Preparation Phase (15 minutes)

```bash
#!/bin/bash
# Create backup directory
sudo mkdir -p ${BACKUP_PATH}

# Create ScyllaDB Docker container snapshot
echo "Creating ScyllaDB Docker container snapshot..."
sudo docker commit ${DOCKER_CONTAINER_NAME} scylladb_backup_$(date +%Y%m%d_%H%M%S)
echo "Docker container snapshot created."

# Backup ScyllaDB data
echo "Backing up ScyllaDB data..."
sudo docker exec ${DOCKER_CONTAINER_NAME} nodetool snapshot --tag migration_backup
sudo docker cp ${DOCKER_CONTAINER_NAME}:/var/lib/scylla/data ${BACKUP_PATH}/data
sudo docker cp ${DOCKER_CONTAINER_NAME}:/etc/scylla ${BACKUP_PATH}/config
echo "Data backup completed."

# Install ScyllaDB native packages
echo "Installing ScyllaDB native packages..."
ssh root@${TARGET_IP} << EOF
  # Add ScyllaDB repository
  wget -O /etc/apt/trusted.gpg.d/scylladb.gpg https://downloads.scylladb.com/deb/ubuntu/scylladb-keyring.gpg
  echo "deb [arch=amd64] http://downloads.scylladb.com/deb/ubuntu focal/scylladb-${SCYLLA_VERSION} multiverse" > /etc/apt/sources.list.d/scylla.list
  apt-get update
  
  # Install ScyllaDB
  apt-get install -y scylla
  
  # Create required directories
  mkdir -p ${SCYLLA_DATA_PATH} ${SCYLLA_CONFIG_PATH} ${SCYLLA_LOG_PATH}
EOF
echo "ScyllaDB native packages installed."

# Prepare systemd service file
echo "Preparing systemd service file..."
cat > /tmp/scylladb.service << EOF
[Unit]
Description=ScyllaDB NoSQL Database
After=network.target

[Service]
Type=forking
User=${SCYLLA_USER}
Group=${SCYLLA_GROUP}
ExecStart=/usr/bin/scylla --options-file=${SCYLLA_CONFIG_PATH}/scylla.yaml
ExecStop=/usr/bin/pkill -TERM -f "scylla --options-file"
Restart=on-failure
LimitNOFILE=1000000
LimitMEMLOCK=infinity
LimitNPROC=32768
LimitAS=infinity
TimeoutStartSec=900
TimeoutStopSec=300

[Install]
WantedBy=multi-user.target
EOF

scp /tmp/scylladb.service root@${TARGET_IP}:/etc/systemd/system/
echo "Systemd service file prepared."
```

### 2. Migration Execution Phase (30 minutes)

```bash
#!/bin/bash
# Extract configuration from Docker container
echo "Extracting configuration from Docker container..."
sudo docker cp ${DOCKER_CONTAINER_NAME}:/etc/scylla/scylla.yaml /tmp/scylla.yaml

# Modify configuration for native deployment
echo "Modifying configuration for native deployment..."
sed -i 's/listen_address: 0.0.0.0/listen_address: localhost/' /tmp/scylla.yaml
sed -i 's/rpc_address: 0.0.0.0/rpc_address: localhost/' /tmp/scylla.yaml
sed -i 's/seeds: "127.0.0.1"/seeds: "127.0.0.1"/' /tmp/scylla.yaml
sed -i "s|data_file_directories:.*|data_file_directories: [\"${SCYLLA_DATA_PATH}/data\"]|" /tmp/scylla.yaml

# Copy modified configuration to target server
scp /tmp/scylla.yaml root@${TARGET_IP}:${SCYLLA_CONFIG_PATH}/

# Stop Docker container
echo "Stopping ScyllaDB Docker container..."
sudo docker stop ${DOCKER_CONTAINER_NAME}
echo "Docker container stopped."

# Copy data files to target server
echo "Copying data files to target server..."
ssh root@${TARGET_IP} << EOF
  # Create data directory structure
  mkdir -p ${SCYLLA_DATA_PATH}/data
EOF

# Use rsync for efficient data transfer
rsync -avz --progress ${BACKUP_PATH}/data/ root@${TARGET_IP}:${SCYLLA_DATA_PATH}/data/

# Set proper permissions
echo "Setting proper permissions..."
ssh root@${TARGET_IP} << EOF
  chown -R ${SCYLLA_USER}:${SCYLLA_GROUP} ${SCYLLA_DATA_PATH} ${SCYLLA_CONFIG_PATH} ${SCYLLA_LOG_PATH}
  chmod 750 ${SCYLLA_DATA_PATH} ${SCYLLA_CONFIG_PATH} ${SCYLLA_LOG_PATH}
EOF

# Start ScyllaDB service
echo "Starting ScyllaDB service..."
ssh root@${TARGET_IP} << EOF
  systemctl daemon-reload
  systemctl enable scylladb
  systemctl start scylladb
EOF
echo "ScyllaDB service started."
```

### 3. Validation Phase (15 minutes)

```bash
#!/bin/bash
# Verify service status
echo "Verifying ScyllaDB service status..."
ssh root@${TARGET_IP} << EOF
  systemctl status scylladb
EOF

# Check ScyllaDB cluster status
echo "Checking ScyllaDB cluster status..."
ssh root@${TARGET_IP} << EOF
  cqlsh localhost 9042 -e "SELECT * FROM system.local"
EOF

# Verify data integrity
echo "Verifying data integrity..."
ssh root@${TARGET_IP} << EOF
  # Replace 'nova' with your actual keyspace name
  cqlsh localhost 9042 -e "SELECT COUNT(*) FROM nova.emotional_data"
EOF

# Test write operations
echo "Testing write operations..."
ssh root@${TARGET_IP} << EOF
  cqlsh localhost 9042 -e "CREATE KEYSPACE IF NOT EXISTS migration_test WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}"
  cqlsh localhost 9042 -e "CREATE TABLE IF NOT EXISTS migration_test.validation (id uuid PRIMARY KEY, value text)"
  cqlsh localhost 9042 -e "INSERT INTO migration_test.validation (id, value) VALUES (uuid(), 'migration_successful')"
  cqlsh localhost 9042 -e "SELECT * FROM migration_test.validation WHERE value = 'migration_successful'"
EOF

# Test connectivity from dependent services
echo "Testing connectivity from dependent services..."
# Add tests for each dependent service
# Example:
# curl -X POST http://api-gateway:8080/test-scylla-connection

# Perform performance benchmarking
echo "Performing performance benchmarking..."
ssh root@${TARGET_IP} << EOF
  # Install cassandra-stress if not already installed
  apt-get install -y scylla-tools
  
  # Run basic performance test
  cassandra-stress write n=100000 -rate threads=50 -node localhost
  cassandra-stress read n=100000 -rate threads=50 -node localhost
EOF

echo "Migration validation completed successfully."
```

## Rollback Procedure

In case of critical issues during migration, execute the following rollback procedure:

```bash
#!/bin/bash
# Stop ScyllaDB service
echo "Stopping ScyllaDB service..."
ssh root@${TARGET_IP} << EOF
  systemctl stop scylladb
  systemctl disable scylladb
EOF

# Start Docker container
echo "Starting ScyllaDB Docker container..."
sudo docker start ${DOCKER_CONTAINER_NAME}
echo "Docker container started."

# Verify Docker container
echo "Verifying Docker container..."
sudo docker exec -it ${DOCKER_CONTAINER_NAME} cqlsh -e "SELECT * FROM system.local"

# Notify dependent services
echo "Notifying dependent services about rollback..."
# Add notification logic for dependent services
# Example:
# curl -X POST http://service-registry:8080/notify-rollback/scylladb

echo "Rollback completed successfully."
```

## Post-Migration Tasks

- [ ] Update documentation with new connection details
- [ ] Update monitoring system to track native ScyllaDB metrics
- [ ] Configure automated backups for native ScyllaDB
- [ ] Optimize ScyllaDB configuration for production workload
- [ ] Remove Docker container after successful migration (after 7 days)

## Performance Optimization Recommendations

After successful migration, consider the following optimizations:

1. **Memory Configuration**
   ```yaml
   # Add to scylla.yaml
   memory_allocator: jemalloc
   commitlog_segment_size_in_mb: 64
   memtable_flush_writers: 4
   ```

2. **CPU Optimization**
   ```bash
   # Run on target server
   sudo scylla_setup --nic eth0 --setup-nic
   sudo scylla_cpu_setup --smp 16
   ```

3. **Disk I/O Optimization**
   ```yaml
   # Add to scylla.yaml
   compaction_throughput_mb_per_sec: 256
   stream_throughput_outbound_megabits_per_sec: 1000
   ```

## Contact Information

For assistance during migration:
- **Primary Contact:** Vertex (DataOps Team Lead)
- **Secondary Contact:** Database Operations Team
- **Emergency Contact:** System Operations Center

## Approval

- [ ] Migration plan approved by: ________________________
- [ ] Execution date and time: ________________________
- [ ] Rollback deadline: ________________________