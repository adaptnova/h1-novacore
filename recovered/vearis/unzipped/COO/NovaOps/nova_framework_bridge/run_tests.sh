#!/bin/bash

# Nova Framework Bridge Test Runner Script

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Make run_tests.py executable
chmod +x run_tests.py

# Default test configuration
SOURCE_DIR="src"
TEST_PATHS="tests"
COVERAGE_DIR="coverage_html"
TEST_RESULTS_DIR="test_results"
LOGS_DIR="logs"

# Create necessary directories
mkdir -p "$COVERAGE_DIR" "$TEST_RESULTS_DIR" "$LOGS_DIR"

# Parse command line arguments
POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --all)
            TEST_TYPE="all"
            shift
            ;;
        --failfast)
            FAILFAST="--failfast"
            shift
            ;;
        --coverage-only)
            COVERAGE_ONLY=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --unit           Run unit tests only"
            echo "  --integration    Run integration tests only"
            echo "  --all           Run all tests (default)"
            echo "  --failfast      Stop on first failure"
            echo "  --coverage-only Generate coverage report without running tests"
            exit 0
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

# Restore positional arguments
set -- "${POSITIONAL_ARGS[@]}"

# Generate coverage report only if requested
if [ "$COVERAGE_ONLY" = true ]; then
    echo "Generating coverage report..."
    coverage combine
    coverage html -d "$COVERAGE_DIR"
    echo "Coverage report generated in $COVERAGE_DIR"
    exit 0
fi

# Set test markers based on test type
case $TEST_TYPE in
    "unit")
        MARKERS="unit"
        echo "Running unit tests..."
        ;;
    "integration")
        MARKERS="integration"
        echo "Running integration tests..."
        ;;
    *)
        MARKERS=""
        echo "Running all tests..."
        ;;
esac

# Build test command
TEST_CMD="./run_tests.py"
if [ ! -z "$MARKERS" ]; then
    TEST_CMD="$TEST_CMD --markers $MARKERS"
fi
if [ ! -z "$FAILFAST" ]; then
    TEST_CMD="$TEST_CMD --failfast"
fi

# Run tests
echo "Running tests with command: $TEST_CMD"
$TEST_CMD

# Check test result
TEST_RESULT=$?

# Generate coverage badge
COVERAGE=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
echo "Coverage: $COVERAGE%"

# Create coverage badge using shields.io
BADGE_URL="https://img.shields.io/badge/coverage-$COVERAGE%25-${COVERAGE_COLOR}.svg"
curl -s "$BADGE_URL" > coverage_badge.svg

# Display test summary
echo
echo "Test Summary"
echo "============"
echo "Test Type: ${TEST_TYPE:-all}"
echo "Coverage: $COVERAGE%"
echo "Results Directory: $TEST_RESULTS_DIR"
echo "Coverage Report: $COVERAGE_DIR/index.html"
echo

# Exit with test result
exit $TEST_RESULT