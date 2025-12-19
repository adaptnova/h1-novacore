#!/bin/bash

# Nova Framework Bridge Development Environment Manager

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to print colored output
print_color() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_color "$RED" "Error: Docker is not running"
        exit 1
    fi
}

# Function to build Docker images
build() {
    print_color "$BLUE" "Building Docker images..."
    docker-compose build "$@"
}

# Function to start services
start() {
    print_color "$BLUE" "Starting services..."
    docker-compose up -d "$@"
    print_color "$GREEN" "Services started successfully!"
    print_color "$YELLOW" "Waiting for services to be healthy..."
    sleep 5
    docker-compose ps
}

# Function to stop services
stop() {
    print_color "$BLUE" "Stopping services..."
    docker-compose down "$@"
    print_color "$GREEN" "Services stopped successfully!"
}

# Function to show service status
status() {
    print_color "$BLUE" "Service Status:"
    docker-compose ps
}

# Function to show service logs
logs() {
    if [ -z "$1" ]; then
        print_color "$BLUE" "Showing logs for all services..."
        docker-compose logs -f
    else
        print_color "$BLUE" "Showing logs for $1..."
        docker-compose logs -f "$1"
    fi
}

# Function to run tests
test() {
    print_color "$BLUE" "Running tests..."
    docker-compose run --rm nova-bridge ./run_tests.sh "$@"
}

# Function to open a shell in a service
shell() {
    local service="${1:-nova-bridge}"
    print_color "$BLUE" "Opening shell in $service..."
    docker-compose exec "$service" /bin/bash
}

# Function to clean up development environment
clean() {
    print_color "$BLUE" "Cleaning up development environment..."
    docker-compose down -v
    rm -rf logs/* coverage_html/* test_results/*
    print_color "$GREEN" "Cleanup complete!"
}

# Function to show database status
db_status() {
    print_color "$BLUE" "Database Status:"
    echo
    print_color "$YELLOW" "Redis:"
    docker-compose exec redis redis-cli info | grep "connected_clients\|used_memory\|total_connections_received"
    echo
    print_color "$YELLOW" "MongoDB:"
    docker-compose exec mongodb mongosh --eval "db.serverStatus()"
    echo
    print_color "$YELLOW" "Neo4j:"
    docker-compose exec neo4j cypher-shell -u neo4j -p novabridge "CALL dbms.components() YIELD name, versions, edition"
    echo
    print_color "$YELLOW" "Milvus:"
    curl -s http://localhost:19121/system/state | jq
}

# Function to show help
show_help() {
    echo "Nova Framework Bridge Development Environment Manager"
    echo
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  build       Build Docker images"
    echo "  start       Start services"
    echo "  stop        Stop services"
    echo "  status      Show service status"
    echo "  logs        Show service logs"
    echo "  test        Run tests"
    echo "  shell       Open a shell in a service"
    echo "  clean       Clean up development environment"
    echo "  db-status   Show database status"
    echo "  help        Show this help message"
    echo
    echo "Options:"
    echo "  --no-cache  Build without using cache"
    echo "  --force     Force operation"
    echo "  -f         Follow log output"
    echo
    echo "Examples:"
    echo "  $0 build --no-cache"
    echo "  $0 start"
    echo "  $0 test --unit"
    echo "  $0 shell redis"
    echo "  $0 logs nova-bridge"
}

# Main script logic
check_docker

case "$1" in
    build)
        shift
        build "$@"
        ;;
    start)
        shift
        start "$@"
        ;;
    stop)
        shift
        stop "$@"
        ;;
    status)
        status
        ;;
    logs)
        shift
        logs "$@"
        ;;
    test)
        shift
        test "$@"
        ;;
    shell)
        shift
        shell "$@"
        ;;
    clean)
        clean
        ;;
    db-status)
        db_status
        ;;
    help)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac