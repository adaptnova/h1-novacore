# Nova Framework Bridge Makefile

.PHONY: help install dev-install test lint format clean build docker-build docker-start docker-stop docker-clean docs coverage

# Default target
.DEFAULT_GOAL := help

# Python settings
PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
POETRY := poetry

# Docker settings
DOCKER_COMPOSE := docker-compose
DOCKER_BUILD_FLAGS := --no-cache

# Test settings
TEST_PATH := tests
COVERAGE_PATH := coverage_html

# Documentation settings
DOCS_PATH := docs
DOCS_BUILD := $(DOCS_PATH)/_build

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install production dependencies using Poetry
	$(POETRY) install --no-dev

dev-install:  ## Install development dependencies using Poetry
	$(POETRY) install

test:  ## Run tests with pytest
	$(POETRY) run pytest $(TEST_PATH) -v --cov=src --cov-report=term-missing

lint:  ## Run code linting
	$(POETRY) run black src tests
	$(POETRY) run isort src tests
	$(POETRY) run pylint src tests
	$(POETRY) run mypy src tests
	$(POETRY) run flake8 src tests
	$(POETRY) run bandit -r src

format:  ## Format code using black and isort
	$(POETRY) run black src tests
	$(POETRY) run isort src tests

clean:  ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf $(COVERAGE_PATH)
	rm -rf $(DOCS_BUILD)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package using Poetry
	$(POETRY) build

docker-build:  ## Build Docker images
	$(DOCKER_COMPOSE) build $(DOCKER_BUILD_FLAGS)

docker-start:  ## Start Docker containers
	$(DOCKER_COMPOSE) up -d

docker-stop:  ## Stop Docker containers
	$(DOCKER_COMPOSE) down

docker-clean:  ## Clean Docker artifacts
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f

docs:  ## Build documentation
	$(POETRY) run sphinx-build -b html $(DOCS_PATH) $(DOCS_BUILD)

coverage:  ## Generate test coverage report
	$(POETRY) run pytest --cov=src --cov-report=html:$(COVERAGE_PATH)

setup:  ## Set up development environment
	$(POETRY) install
	$(POETRY) run pre-commit install
	mkdir -p logs coverage_html test_results

update:  ## Update dependencies
	$(POETRY) update

check:  ## Run all checks (lint, test, coverage)
	make lint
	make test
	make coverage

docker-test:  ## Run tests in Docker
	$(DOCKER_COMPOSE) run --rm nova-bridge ./run_tests.sh

docker-shell:  ## Open shell in Docker container
	$(DOCKER_COMPOSE) run --rm nova-bridge /bin/bash

docker-logs:  ## View Docker logs
	$(DOCKER_COMPOSE) logs -f

docker-ps:  ## List running containers
	$(DOCKER_COMPOSE) ps

init-dev:  ## Initialize development environment
	make setup
	make docker-build
	make docker-start

ci:  ## Run CI checks
	make lint
	make test
	make coverage
	make build

release:  ## Create a new release
	$(POETRY) version patch
	$(POETRY) build
	$(POETRY) publish

major-release:  ## Create a new major release
	$(POETRY) version major
	$(POETRY) build
	$(POETRY) publish

minor-release:  ## Create a new minor release
	$(POETRY) version minor
	$(POETRY) build
	$(POETRY) publish

# Database management
db-init:  ## Initialize databases
	$(DOCKER_COMPOSE) run --rm nova-bridge python -m src.migrations

db-migrate:  ## Run database migrations
	$(DOCKER_COMPOSE) run --rm nova-bridge python -m src.migrations migrate

db-rollback:  ## Rollback database migrations
	$(DOCKER_COMPOSE) run --rm nova-bridge python -m src.migrations rollback

# Monitoring
monitor:  ## View monitoring dashboard
	open http://localhost:3000

metrics:  ## View Prometheus metrics
	open http://localhost:9090

# Development utilities
watch-tests:  ## Run tests in watch mode
	$(POETRY) run ptw

benchmark:  ## Run benchmarks
	$(POETRY) run pytest tests/benchmarks --benchmark-only

profile:  ## Run profiling
	$(POETRY) run python -m cProfile -o profile.stats src/main.py
	$(POETRY) run snakeviz profile.stats

security-check:  ## Run security checks
	$(POETRY) run safety check
	$(POETRY) run bandit -r src

type-check:  ## Run type checking
	$(POETRY) run mypy src tests

dependencies:  ## Show dependency tree
	$(POETRY) show --tree