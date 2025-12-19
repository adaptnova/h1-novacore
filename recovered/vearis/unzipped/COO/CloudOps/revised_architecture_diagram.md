# Revised Architecture Diagram

## Overall Architecture

```mermaid
graph TD
    subgraph "IBM Cloud us-south Region"
        subgraph "us-south-2 Zone (Dallas 2)"
            subgraph "dataops-vpc"
                subgraph "dataops-subnet (10.240.64.0/24)"
                    DB1[nova-db-primary<br>MongoDB/PostgreSQL<br>bx2-8x32]
                    DB2[nova-db-graph<br>Neo4j/ArangoDB<br>bx2-8x32]
                    DB3[nova-db-timeseries<br>Redis/DragonflyDB<br>bx2-8x32]
                    GPU[ethos<br>GPU Server<br>gx3-48x240x2l40s]
                    LOG[nova-logs<br>Logging Server<br>bx2-4x16]
                end
                SG1[nova-db-sg<br>Security Group]
                SG2[ethos-sg<br>Security Group]
                SG3[nova-logs-sg<br>Security Group]
            end
            
            subgraph "us-south-default-vpc"
                subgraph "Default Subnet"
                    ADAPT[adapt<br>mx3d-96x960<br>Renamed from adapt3]
                end
                SG4[adapt-sg<br>Security Group]
            end
        end
        
        subgraph "Object Storage"
            OBJ[IBM Cloud Object Storage<br>Log Archives]
        end
    end
    
    SG1 --> DB1
    SG1 --> DB2
    SG1 --> DB3
    SG2 --> GPU
    SG3 --> LOG
    SG4 --> ADAPT
    
    DB1 -.-> |Log Forwarding| LOG
    DB2 -.-> |Log Forwarding| LOG
    DB3 -.-> |Log Forwarding| LOG
    GPU -.-> |Log Forwarding| LOG
    ADAPT -.-> |Log Forwarding| LOG
    
    LOG -.-> |Log Archiving| OBJ
```

## Storage Architecture (Optimized Sizing)

```mermaid
graph TD
    subgraph "nova-db-primary Storage"
        PRI_BOOT[Boot Volume<br>50GB NVMe SSD<br>3000 IOPS]
        PRI_DATA[Data Volume<br>50GB NVMe SSD<br>3000 IOPS<br>XFS Formatted]
        PRI_LOG[Log Volume<br>10GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
    end
    
    subgraph "nova-db-graph Storage"
        GRA_BOOT[Boot Volume<br>50GB NVMe SSD<br>3000 IOPS]
        GRA_DATA[Data Volume<br>40GB NVMe SSD<br>3000 IOPS<br>XFS Formatted]
        GRA_LOG[Log Volume<br>10GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
    end
    
    subgraph "nova-db-timeseries Storage"
        TIM_BOOT[Boot Volume<br>50GB NVMe SSD<br>2000 IOPS]
        TIM_DATA[Data Volume<br>30GB NVMe SSD<br>2000 IOPS<br>XFS Formatted]
        TIM_LOG[Log Volume<br>10GB NVMe SSD<br>1000 IOPS<br>XFS Formatted]
    end
    
    subgraph "ethos Storage"
        ETH_BOOT[Boot Volume<br>50GB NVMe SSD<br>5000 IOPS]
        ETH_DATA[Data Volume<br>100GB NVMe SSD<br>10000 IOPS<br>XFS Formatted]
        ETH_LOG[Log Volume<br>20GB NVMe SSD<br>2000 IOPS<br>XFS Formatted]
    end
    
    subgraph "nova-logs Storage"
        LOG_BOOT[Boot Volume<br>50GB NVMe SSD<br>2000 IOPS]
        LOG_DATA[Log Volume<br>100GB NVMe SSD<br>5000 IOPS<br>XFS Formatted]
    end
    
    subgraph "adapt Storage (Existing)"
        ADAPT_BOOT[Boot Volume<br>100GB]
        ADAPT_DATA[Data Volume<br>1.5TB<br>/data-nova]
    end
    
    subgraph "Snapshot System"
        SNAP[Hourly Snapshots<br>2-day Retention<br>Last Snapshot: 7-day Retention]
    end
    
    SNAP --> PRI_BOOT
    SNAP --> PRI_DATA
    SNAP --> PRI_LOG
    SNAP --> GRA_BOOT
    SNAP --> GRA_DATA
    SNAP --> GRA_LOG
    SNAP --> TIM_BOOT
    SNAP --> TIM_DATA
    SNAP --> TIM_LOG
    SNAP --> ETH_BOOT
    SNAP --> ETH_DATA
    SNAP --> ETH_LOG
    SNAP --> LOG_BOOT
    SNAP --> LOG_DATA
    SNAP --> ADAPT_BOOT
    SNAP --> ADAPT_DATA
```

## Disk Scaling Strategy

```mermaid
graph TD
    START[Start with Minimal Sizes] --> MONITOR[Monitor Usage]
    MONITOR --> THRESHOLD{Reached 70%<br>Threshold?}
    THRESHOLD -->|No| MONITOR
    THRESHOLD -->|Yes| PLAN[Plan Expansion]
    PLAN --> SCHEDULE[Schedule Maintenance Window]
    SCHEDULE --> EXPAND[Expand LVM Volume]
    EXPAND --> RESIZE[Resize Filesystem]
    RESIZE --> VERIFY[Verify Performance]
    VERIFY --> MONITOR
    
    subgraph "Expansion Process"
        PLAN
        SCHEDULE
        EXPAND
        RESIZE
        VERIFY
    end
```

## Tiered Logging Architecture

```mermaid
graph TD
    subgraph "Tier 1: Local Log Storage"
        PRI_LOCAL[nova-db-primary<br>Local Logs<br>7-day Retention]
        GRA_LOCAL[nova-db-graph<br>Local Logs<br>7-day Retention]
        TIM_LOCAL[nova-db-timeseries<br>Local Logs<br>7-day Retention]
        ETH_LOCAL[ethos<br>Local Logs<br>7-day Retention]
        ADAPT_LOCAL[adapt<br>Local Logs<br>7-day Retention]
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
    ADAPT_LOCAL -.-> |Filebeat| ELK
    
    ELK -.-> |Weekly Archive| OBJ_STORE
    
    subgraph "Log Analysis"
        DASH[Dashboards<br>Visualizations<br>Alerts]
        SEARCH[Search & Analysis<br>Query Interface]
    end
    
    ELK --> DASH
    ELK --> SEARCH
    PROM --> DASH
```

## Implementation Timeline

```mermaid
gantt
    title Implementation Timeline
    dateFormat  YYYY-MM-DD
    section Infrastructure Preparation
    Create Security Groups           :2025-03-22, 1d
    Create NVMe Volumes              :2025-03-22, 1d
    section Server Deployment
    Deploy DataOps Servers           :2025-03-22, 1d
    Deploy Ethos GPU Server          :2025-03-22, 1d
    Deploy Logging Server            :2025-03-22, 1d
    Rename adapt3 to adapt           :2025-03-22, 1d
    section Server Configuration
    Configure Storage (XFS)          :2025-03-23, 1d
    Configure Database Software      :2025-03-23, 1d
    Configure GPU Software           :2025-03-23, 1d
    Configure Logging Infrastructure :2025-03-23, 1d
    section Monitoring & Backup
    Configure Snapshots              :2025-03-23, 1d
    Set Up Monitoring                :2025-03-24, 1d
    Configure Alerts                 :2025-03-24, 1d
    Complete Documentation           :2025-03-24, 1d
```

## Future Expansion Path

```mermaid
graph TD
    CURRENT[Current Simplified<br>Architecture] --> EXPAND[Disk Expansion<br>As Needed]
    EXPAND --> NOVA[Add Nova Server<br>Q2 2025]
    NOVA --> TAPESTRY[Integrate with<br>Project Tapestry]
    TAPESTRY --> MULTI[Multi-Region<br>Expansion]
    
    subgraph "Disk Expansion Strategy"
        MONITOR[Monitor Usage] --> THRESHOLD{70% Threshold<br>Reached?}
        THRESHOLD -->|Yes| RESIZE[Resize Volume]
        THRESHOLD -->|No| MONITOR
        RESIZE --> MONITOR
    end
```

These diagrams provide a visual representation of the revised architecture, including the simplified network approach, optimized storage sizing, disk scaling strategy, and implementation timeline. The diagrams use Mermaid syntax and can be rendered in any Markdown viewer that supports Mermaid.