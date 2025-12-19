# Mini-Agent Memory System - Docker Setup

# Start with Redis (basic memory)
docker run -d --name mini-agent-redis -p 6379:6379 redis

# Start with full stack (PostgreSQL + Redis)
docker-compose up -d

# Or use individual containers:
# PostgreSQL
docker run -d --name mini-agent-postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=mini_agent_memory \
  postgres

# ClickHouse (for analytics)
docker run -d --name mini-agent-clickhouse \
  -p 8123:8123 \
  -p 9000:9000 \
  clickhouse/clickhouse-server

echo "Memory system databases ready!"
echo "Run setup.sh to initialize the memory system"
