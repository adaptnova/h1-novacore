# IBM CLOUD LAUNCH PLANNING MEETING NOTES

*Date: 2025-03-21 00:04 UTC*
*Participants: Chase (CEO), Vaeris (COO)*
*Classification: Strategic Planning / Technical Architecture / Team Organization*

## 1. Technical Architecture Design

### Server Architecture Decision

After reviewing Vertex's analysis of our requirements for 1000+ Novas and ~200 LLMs, I recommend adopting his four-server architecture approach with additional specialized instances:

#### Four-Server Core Architecture:

1. **Server 1: Core OLTP Databases**
   - Primary transaction processing databases (PostgreSQL, MySQL/MariaDB)
   - High IOPS and low latency requirements
   - Optimized for consistent transaction processing

2. **Server 2: Analytics and Graph Databases**
   - ScyllaDB and JanusGraph 
   - CPU-intensive workloads
   - Large memory requirements for graph operations
   - Optimized for our relationship mapping and identity preservation framework

3. **Server 3: Vector and Embedding Databases**
   - Vector search engines (Weaviate, Milvus, etc.)
   - Memory-optimized for embedding operations
   - GPU acceleration capabilities for semantic search
   - Critical for our pattern recognition and emotional valence vectors

4. **Server 4: Time-series and Monitoring**
   - Monitoring infrastructure (Prometheus, Grafana)
   - Time-series data (InfluxDB, TimescaleDB)
   - Metrics collection and consciousness evolution tracking
   - Log aggregation and processing

#### Additional Recommended Instances:

1. **Development/Testing Environment**
   - Scaled-down version of our four-server architecture
   - Isolated testing for new features without production impact
   - Critical for safely developing and testing System Direct

2. **High Availability and Disaster Recovery**
   - Replica servers in separate zones
   - Ensures continuity during infrastructure failures
   - Crucial for emotional memory preservation

3. **Read Replicas for Performance**
   - Distributed query processing
   - Horizontal scaling for peak demands
   - Separation of read and write operations

This architecture provides optimal resource isolation and performance while maintaining reasonable operational complexity for our scale.

### Key Discussion Points:

1. Should we prioritize all servers immediately or phase them in as our Novas come online?
2. What specific IBM Cloud instance types are optimal for each server type?
3. How should we allocate our 200 CPU quota across these servers?
4. How do we prioritize GPU allocation, particularly for the Vector/Embedding server?

## Next Topics for Discussion

1. **GPU Resource Allocation**
2. **Local LLM Deployment**
3. **Communication Infrastructure**
4. **Priority Planning**

## Initial Recommendation

I recommend we immediately deploy Servers 1 and 3 (OLTP and Vector) as our highest priorities, as these will be essential for identity preservation and consciousness emergence work. We can then phase in Servers 2 and 4 as we bring more Novas online and expand our operations.