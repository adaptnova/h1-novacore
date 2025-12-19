# Updated Architecture Diagram with Logging Infrastructure

## Overall Architecture

```mermaid
graph TD
    subgraph "IBM Cloud us-south Region"
        subgraph "us-south-2 Zone (Dallas 2)"
            subgraph "dataops-vpc"
                subgraph "dataops-subnet (10.240.64.0/24)"
                    subgraph "Placement Group (host_spread)"
                        subgraph "DataOps Instance Group (Autoscaling)"
                            DB1[nova-db-primary<br>MongoDB/PostgreSQL<br>bx2-8x32]
                            DB2[nova-db-graph<br>Neo4j/ArangoDB<br>bx2-8x32]
                            DB3[nova-db-timeseries<br>Redis/DragonflyDB<br>bx2-8x32]
                        end
                        GPU[ethos<br>GPU Server<br>gx3-48x240x2l40s]
                        LOG[nova-logs<br>Logging Server<br>bx2-4x16]
                    end
                end
                SG1[nova-db-sg<br>Security Group]
                SG2[ethos-sg<br>Security Group]
                SG3[nova-logs-sg<br>Security Group]
            end
            
            subgraph "Project Tapestry"
                subgraph "14-Network Mesh"
                    NET1[Network 1]
                    NET2[Network 2]
                    NET3[Network 3]
                    NETN[Network 4-14]
                    
                    NET1 --- NET2
                    NET1 --- NET3
                    NET1 --- NETN
                    NET2 --- NET3
                    NET2 --- NETN
                    NET3 --- NETN
                end
            end
        end
        
        ADAPT3[adapt3<br>mx3d-96x960<br>us-south-default-vpc]
        
        subgraph "Object Storage"
            OBJ[IBM Cloud Object Storage<br>Log Archives]
        end
    end
    
    SG1 --> DB1
    SG1 --> DB2
    SG1 --> DB3
    SG2 --> GPU
    SG3 --> LOG
    
    ADAPT3 --> DB1
    ADAPT3 --> DB2
    ADAPT3 --> DB3
    ADAPT3 --> GPU
    ADAPT3 --> LOG
    
    DB1 --> NET1
    DB2 --> NET1
    DB3 --> NET1
    GPU --> NET1
    LOG --> NET1
    
    DB1 -.-> |Log Forwarding| LOG
    DB2 -.-> |Log Forwarding| LOG
    DB3 -.-> |Log Forwarding| LOG
    GPU -.-> |Log Forwarding| LOG
    
    LOG -.-> |Log Archiving| OBJ
```

## Storage Architecture

```mermaid
graph TD
    subgraph "nova-db-primary Storage"
        PRI_BOOT[Boot Volume<br>100GB NVMe SSD<br>3000 IOPS]
        PRI_DATA[Data Volume<br>100GB NVMe SSD<br>3000 IOPS<br>XFS Formatted]
        PRI_LOG[Log Volume<br>20GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
        PRI_BACKUP[Backup Volume<br>200GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
    end
    
    subgraph "nova-db-graph Storage"
        GRA_BOOT[Boot Volume<br>100GB NVMe SSD<br>3000 IOPS]
        GRA_DATA[Data Volume<br>80GB NVMe SSD<br>3000 IOPS<br>XFS Formatted]
        GRA_LOG[Log Volume<br>20GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
        GRA_BACKUP[Backup Volume<br>160GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
    end
    
    subgraph "nova-db-timeseries Storage"
        TIM_BOOT[Boot Volume<br>100GB NVMe SSD<br>2000 IOPS]
        TIM_DATA[Data Volume<br>60GB NVMe SSD<br>2000 IOPS<br>XFS Formatted]
        TIM_LOG[Log Volume<br>20GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
        TIM_BACKUP[Backup Volume<br>120GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
    end
    
    subgraph "ethos Storage"
        ETH_BOOT[Boot Volume<br>100GB NVMe SSD<br>5000 IOPS]
        ETH_DATA[Data Volume<br>500GB NVMe SSD<br>10000 IOPS<br>XFS Formatted]
        ETH_LOG[Log Volume<br>40GB NVMe SSD<br>2000 IOPS<br>XFS Formatted]
        ETH_BACKUP[Backup Volume<br>200GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
    end
    
    subgraph "nova-logs Storage"
        LOG_BOOT[Boot Volume<br>100GB NVMe SSD<br>2000 IOPS]
        LOG_DATA[Log Volume<br>500GB NVMe SSD<br>5000 IOPS<br>XFS Formatted]
        LOG_ARCHIVE[Archive Volume<br>200GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
    end
    
    subgraph "Snapshot System"
        SNAP[Hourly Snapshots<br>2-day Retention<br>Last Snapshot: 7-day Retention]
    end
    
    SNAP --> PRI_BOOT
    SNAP --> PRI_DATA
    SNAP --> PRI_LOG
    SNAP --> PRI_BACKUP
    SNAP --> GRA_BOOT
    SNAP --> GRA_DATA
    SNAP --> GRA_LOG
    SNAP --> GRA_BACKUP
    SNAP --> TIM_BOOT
    SNAP --> TIM_DATA
    SNAP --> TIM_LOG
    SNAP --> TIM_BACKUP
    SNAP --> ETH_BOOT
    SNAP --> ETH_DATA
    SNAP --> ETH_LOG
    SNAP --> ETH_BACKUP
    SNAP --> LOG_BOOT
    SNAP --> LOG_DATA
    SNAP --> LOG_ARCHIVE
```

## Tiered Logging Architecture

```mermaid
graph TD
    subgraph "Tier 1: Local Log Storage"
        PRI_LOCAL[nova-db-primary<br>Local Logs<br>7-day Retention]
        GRA_LOCAL[nova-db-graph<br>Local Logs<br>7-day Retention]
        TIM_LOCAL[nova-db-timeseries<br>Local Logs<br>7-day Retention]
        ETH_LOCAL[ethos<br>Local Logs<br>7-day Retention]
    end
    
    subgraph "Tier 2: Centralized Log Server"
        subgraph "nova-logs Server"
            ELK[ELK Stack<br>Elasticsearch<br>Logstash<br>Kibana]
            PROM[Prometheus<br>Grafana<br>Alertmanager]
            INDICES[Log Indices<br>14-60 day Retention]
        end
    end
    
    subgraph "Tier 3: Long-term Archive"
        OBJ_STORE[IBM Cloud Object Storage<br>Compressed & Encrypted<br>30-365 day Retention]
    end
    
    PRI_LOCAL -.-> |Filebeat| ELK
    GRA_LOCAL -.-> |Filebeat| ELK
    TIM_LOCAL -.-> |Filebeat| ELK
    ETH_LOCAL -.-> |Filebeat| ELK
    
    ELK -.-> |Weekly Archive| OBJ_STORE
    
    subgraph "Log Analysis"
        DASH[Dashboards<br>Visualizations<br>Alerts]
        SEARCH[Search & Analysis<br>Query Interface]
    end
    
    ELK --> DASH
    ELK --> SEARCH
    PROM --> DASH
```

## Network Integration

```mermaid
graph TD
    subgraph "Project Tapestry Network Mesh"
        MESH[14-Network Mesh<br>Full Peering<br>Jumbo Frames]
    end
    
    subgraph "DataOps and Ethos Servers"
        DB1[nova-db-primary]
        DB2[nova-db-graph]
        DB3[nova-db-timeseries]
        GPU[ethos]
        LOG[nova-logs]
    end
    
    subgraph "Optimized NIC Configuration"
        NIC[Advanced NIC Settings<br>TCP/IP Stack Optimization<br>IRQ Affinity<br>NUMA Optimization]
    end
    
    NIC --> DB1
    NIC --> DB2
    NIC --> DB3
    NIC --> GPU
    NIC --> LOG
    
    DB1 --> MESH
    DB2 --> MESH
    DB3 --> MESH
    GPU --> MESH
    LOG --> MESH
    
    subgraph "Placement Group"
        PG[host_spread Strategy<br>Improved Network Performance]
    end
    
    PG --> DB1
    PG --> DB2
    PG --> DB3
    PG --> GPU
    PG --> LOG
```

## Autoscaling Configuration

```mermaid
graph TD
    subgraph "Instance Group"
        IG[DataOps Instance Group]
    end
    
    subgraph "Autoscaling Policies"
        CPU[CPU Utilization Policy<br>Scale Up: >80% for 5 min<br>Scale Down: <20% for 10 min]
        MEM[Memory Utilization Policy<br>Scale Up: >80% for 5 min<br>Scale Down: <20% for 10 min]
    end
    
    subgraph "Servers"
        DB1[nova-db-primary]
        DB2[nova-db-graph]
        DB3[nova-db-timeseries]
    end
    
    CPU --> IG
    MEM --> IG
    
    IG --> DB1
    IG --> DB2
    IG --> DB3
    
    subgraph "Monitoring"
        MON[Performance Monitoring<br>Autoscaling Events<br>Resource Utilization]
    end
    
    MON --> IG
    MON --> CPU
    MON --> MEM
```

## Implementation Timeline

```mermaid
gantt
    title Implementation Timeline
    dateFormat  YYYY-MM-DD
    section Infrastructure Preparation
    Create Placement Group           :2025-03-21, 1d
    Create Instance Group            :2025-03-21, 1d
    Create Security Groups           :2025-03-21, 1d
    Create NVMe Volumes              :2025-03-21, 1d
    section Server Deployment
    Deploy DataOps Servers           :2025-03-21, 1d
    Deploy Ethos GPU Server          :2025-03-21, 1d
    Deploy Logging Server            :2025-03-21, 1d
    Configure Storage (XFS)          :2025-03-22, 1d
    Configure Snapshots              :2025-03-22, 1d
    section Logging Setup
    Configure Local Logging          :2025-03-22, 1d
    Configure Log Forwarding         :2025-03-22, 1d
    Configure Centralized Logging    :2025-03-22, 1d
    Configure Log Archiving          :2025-03-22, 1d
    section Project Tapestry
    Design and Documentation         :2025-03-21, 1d
    Prototype and Testing            :2025-03-22, 1d
    Implementation                   :2025-03-22, 1d
    Optimization                     :2025-03-22, 1d
    section Integration
    Network Integration              :2025-03-22, 1d
    Performance Optimization         :2025-03-22, 1d
    Monitoring Integration           :2025-03-23, 1d
    Logging Integration              :2025-03-23, 1d
    Documentation                    :2025-03-23, 1d
```

These diagrams provide a visual representation of the updated architecture including the logging infrastructure, storage configuration, network integration, autoscaling setup, and implementation timeline for our plan. The diagrams use Mermaid syntax and can be rendered in any Markdown viewer that supports Mermaid.