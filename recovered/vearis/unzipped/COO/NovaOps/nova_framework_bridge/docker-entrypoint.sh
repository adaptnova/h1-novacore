#!/bin/bash
set -e

# Function to wait for a service to be ready
wait_for_service() {
    local host="$1"
    local port="$2"
    local service="$3"
    local timeout="${4:-30}"

    echo "Waiting for $service to be ready..."
    for i in $(seq 1 $timeout); do
        if nc -z "$host" "$port"; then
            echo "$service is ready!"
            return 0
        fi
        echo "Waiting for $service... $i/$timeout"
        sleep 1
    done
    echo "Timeout waiting for $service"
    return 1
}

# Function to check database connections
check_databases() {
    # Check Redis
    wait_for_service "$REDIS_HOST" 6379 "Redis" || exit 1

    # Check MongoDB
    MONGODB_HOST=$(echo $MONGODB_URI | awk -F'[@/]' '{print $2}' | cut -d: -f1)
    wait_for_service "$MONGODB_HOST" 27017 "MongoDB" || exit 1

    # Check Neo4j
    NEO4J_HOST=$(echo $NEO4J_URI | awk -F'[@/]' '{print $2}' | cut -d: -f1)
    wait_for_service "$NEO4J_HOST" 7687 "Neo4j" || exit 1

    # Check Milvus
    wait_for_service "$MILVUS_HOST" "$MILVUS_PORT" "Milvus" || exit 1
}

# Function to initialize databases
init_databases() {
    echo "Initializing databases..."

    # Initialize Redis
    if [ -n "$REDIS_HOST" ]; then
        redis-cli -h "$REDIS_HOST" PING
    fi

    # Initialize MongoDB
    if [ -n "$MONGODB_URI" ]; then
        mongosh "$MONGODB_URI" --eval "db.createCollection('test')"
    fi

    # Initialize Neo4j
    if [ -n "$NEO4J_URI" ]; then
        cypher-shell -a "$NEO4J_URI" \
            -u neo4j -p novabridge \
            "CREATE CONSTRAINT IF NOT EXISTS ON (n:Node) ASSERT n.id IS UNIQUE"
    fi
}

# Function to run database migrations
run_migrations() {
    echo "Running database migrations..."
    python -m src.migrations
}

# Function to create necessary directories
create_directories() {
    echo "Creating necessary directories..."
    mkdir -p logs coverage_html test_results
}

# Function to set up development environment
setup_development() {
    echo "Setting up development environment..."

    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi

    # Set up pre-commit hooks
    if [ -f ".pre-commit-config.yaml" ]; then
        pre-commit install
    fi
}

# Main initialization logic
main() {
    echo "Starting Nova Framework Bridge initialization..."

    # Create necessary directories
    create_directories

    # Check environment
    if [ "$FASTAPI_ENV" = "development" ]; then
        setup_development
    fi

    # Wait for databases
    check_databases

    # Initialize databases
    init_databases

    # Run migrations
    run_migrations

    echo "Initialization complete!"

    # Execute the main command
    exec "$@"
}

# Run main function with all arguments
main "$@"