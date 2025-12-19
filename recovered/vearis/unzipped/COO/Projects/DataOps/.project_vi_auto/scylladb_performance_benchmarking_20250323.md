# ScyllaDB Performance Benchmarking Plan
**Date:** March 23, 2025
**Author:** Vertex, DataOps Team Lead
**Purpose:** Validate performance improvements after Docker to systemd migration

## Overview

This document outlines a comprehensive performance benchmarking plan for ScyllaDB following its migration from Docker container to native systemd service. The benchmarking will validate that the migration has achieved the expected performance improvements and will establish new baseline metrics for future optimization.

## Benchmarking Objectives

1. Quantify performance improvements from Docker to native deployment
2. Establish baseline metrics for the new systemd-based deployment
3. Identify potential bottlenecks or areas for further optimization
4. Validate that performance meets or exceeds project requirements
5. Document performance characteristics for capacity planning

## Key Performance Indicators (KPIs)

### Latency Metrics
- Read operation latency (p50, p95, p99)
- Write operation latency (p50, p95, p99)
- Query execution time for complex operations
- Commit log flush latency

### Throughput Metrics
- Read operations per second
- Write operations per second
- Sustained throughput under load
- Maximum throughput before degradation

### Resource Utilization
- CPU utilization (per core and overall)
- Memory usage patterns
- Disk I/O (read/write operations, throughput)
- Network throughput and packet rates

### Scalability Metrics
- Linear scaling with added resources
- Performance under concurrent connections
- Behavior under increasing data volume
- Replication performance

## Benchmarking Tools

1. **cassandra-stress**
   - Standard benchmarking tool for Cassandra/ScyllaDB
   - Provides comprehensive metrics for read/write operations
   - Supports custom workload profiles

2. **scylla-bench**
   - ScyllaDB-specific benchmarking tool
   - Optimized for ScyllaDB's architecture
   - Provides detailed latency histograms

3. **YCSB (Yahoo! Cloud Serving Benchmark)**
   - Industry-standard NoSQL database benchmark
   - Supports various workload patterns (read-heavy, write-heavy, mixed)
   - Allows for comparative analysis with other databases

4. **Custom Workload Generator**
   - Simulates actual Nova ecosystem query patterns
   - Tests real-world performance scenarios
   - Validates specific use cases (emotional data processing, vector operations)

## Benchmarking Methodology

### 1. Baseline Establishment

Before executing the migration, establish baseline performance metrics for the Docker-based deployment:

```bash
# Basic read/write performance
cassandra-stress write n=1000000 -rate threads=50 -node localhost
cassandra-stress read n=1000000 -rate threads=50 -node localhost

# Mixed workload performance
cassandra-stress mixed ratio\(write=1,read=3\) n=1000000 -rate threads=50 -node localhost

# Custom workload using YCSB
ycsb load cassandra-cql -P workloads/workloada -p hosts=localhost -p cassandra.readconsistencylevel=ONE -p cassandra.writeconsistencylevel=ONE
ycsb run cassandra-cql -P workloads/workloada -p hosts=localhost -p cassandra.readconsistencylevel=ONE -p cassandra.writeconsistencylevel=ONE
```

### 2. Post-Migration Benchmarking

After migration to systemd service, run identical benchmarks to compare performance:

```bash
# Basic read/write performance
cassandra-stress write n=1000000 -rate threads=50 -node localhost
cassandra-stress read n=1000000 -rate threads=50 -node localhost

# Mixed workload performance
cassandra-stress mixed ratio\(write=1,read=3\) n=1000000 -rate threads=50 -node localhost

# Custom workload using YCSB
ycsb load cassandra-cql -P workloads/workloada -p hosts=localhost -p cassandra.readconsistencylevel=ONE -p cassandra.writeconsistencylevel=ONE
ycsb run cassandra-cql -P workloads/workloada -p hosts=localhost -p cassandra.readconsistencylevel=ONE -p cassandra.writeconsistencylevel=ONE
```

### 3. ScyllaDB-Specific Benchmarking

Utilize ScyllaDB-specific tools to measure performance characteristics:

```bash
# ScyllaDB-specific benchmarking
scylla-bench -workload=sequential -mode=write -replication-factor=3 -partition-count=1000000 -clustering-row-count=100 -concurrency=50 -connection-count=10 -duration=10m
scylla-bench -workload=sequential -mode=read -replication-factor=3 -partition-count=1000000 -clustering-row-count=100 -concurrency=50 -connection-count=10 -duration=10m
```

### 4. Real-World Workload Simulation

Execute custom workload generators that simulate Nova ecosystem usage patterns:

```bash
# Run custom Nova emotional data workload
python /data-nova/ax/DataOps/benchmark/emotional_data_workload.py --duration=30m --concurrency=100

# Run vector operation benchmark
python /data-nova/ax/DataOps/benchmark/vector_operations_benchmark.py --vectors=10000 --dimensions=1536 --operations=1000000
```

### 5. Stress Testing

Perform stress testing to identify breaking points and system limits:

```bash
# Increasing concurrency test
for i in 10 20 50 100 200 500 1000; do
  cassandra-stress write n=1000000 -rate threads=$i -node localhost
  sleep 60  # Allow system to stabilize
done

# Maximum throughput test
cassandra-stress write duration=30m -rate threads=100 throttle=50000/s -node localhost
```

## Performance Analysis

### Comparative Metrics

Create detailed comparison tables for Docker vs. systemd deployment:

| Metric | Docker Container | Systemd Service | Improvement (%) |
|--------|-----------------|-----------------|-----------------|
| Read Latency (p99) | X ms | Y ms | Z% |
| Write Latency (p99) | X ms | Y ms | Z% |
| Read Throughput | X ops/sec | Y ops/sec | Z% |
| Write Throughput | X ops/sec | Y ops/sec | Z% |
| CPU Utilization | X% | Y% | Z% |
| Memory Usage | X GB | Y GB | Z% |
| Disk I/O | X MB/s | Y MB/s | Z% |
| Network Throughput | X Mbps | Y Mbps | Z% |

### Visualization

Generate performance visualization dashboards in Grafana:

1. Latency histograms for read/write operations
2. Throughput over time under various workloads
3. Resource utilization patterns
4. Comparative performance charts (Docker vs. systemd)

## Expected Performance Improvements

Based on previous migrations and industry benchmarks, we expect the following improvements:

1. **Latency Reduction**
   - 15-25% reduction in p99 read latency
   - 10-20% reduction in p99 write latency
   - 30-40% reduction in latency variability (jitter)

2. **Throughput Improvements**
   - 20-30% increase in maximum sustainable throughput
   - 15-25% increase in throughput under high concurrency

3. **Resource Efficiency**
   - 10-15% reduction in CPU utilization for equivalent workload
   - 15-20% reduction in memory overhead
   - 5-10% improvement in I/O efficiency

## Performance Tuning Recommendations

Based on benchmarking results, implement the following tuning recommendations:

### Memory Optimization

```yaml
# Add to scylla.yaml
memory_allocator: jemalloc
commitlog_segment_size_in_mb: 64
memtable_flush_writers: 4
memtable_heap_space_in_mb: 8192
memtable_offheap_space_in_mb: 2048
```

### CPU Optimization

```bash
# Run on target server
sudo scylla_setup --nic eth0 --setup-nic
sudo scylla_cpu_setup --smp 16
```

### Disk I/O Optimization

```yaml
# Add to scylla.yaml
compaction_throughput_mb_per_sec: 256
stream_throughput_outbound_megabits_per_sec: 1000
concurrent_reads: 32
concurrent_writes: 32
concurrent_compactors: 8
```

### Network Optimization

```bash
# Run on target server
sudo sysctl -w net.core.rmem_max=16777216
sudo sysctl -w net.core.wmem_max=16777216
sudo sysctl -w net.core.rmem_default=262144
sudo sysctl -w net.core.wmem_default=262144
sudo sysctl -w net.core.optmem_max=16777216
sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
```

## Continuous Performance Monitoring

Implement ongoing performance monitoring to track system behavior over time:

1. **Prometheus Metrics Collection**
   - Configure ScyllaDB Prometheus exporter
   - Set up custom metrics for Nova-specific operations
   - Establish alerting thresholds for performance degradation

2. **Grafana Dashboards**
   - Create dedicated ScyllaDB performance dashboard
   - Set up trend analysis panels
   - Configure anomaly detection

3. **Automated Benchmark Schedule**
   - Daily lightweight benchmarks
   - Weekly comprehensive performance tests
   - Monthly stress tests

## Conclusion

This performance benchmarking plan provides a comprehensive approach to validating the performance improvements achieved by migrating ScyllaDB from Docker container to native systemd service. By following this plan, we will establish clear metrics on the benefits of the migration and identify opportunities for further optimization.

The results of this benchmarking will be documented in a performance report that will be shared with all stakeholders and used to inform future infrastructure decisions.