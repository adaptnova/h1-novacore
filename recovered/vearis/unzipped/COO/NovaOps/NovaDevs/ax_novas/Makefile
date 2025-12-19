# NOVA Development Makefile

.PHONY: help install dev-install test lint format clean build docs publish

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  docs         - Build documentation"
	@echo "  publish      - Publish package to PyPI"

# Installation targets
install:
	pip install -e .

dev-install:
	pip install -e ".[dev,test,lint,security,docs]"

# Testing targets
test:
	pytest tests/ --cov=nova --cov-report=term-missing --cov-report=html

test-fast:
	pytest tests/ -m "not slow" --cov=nova

test-integration:
	pytest tests/ -m "integration" --cov=nova

# Linting and formatting targets
lint: lint-black lint-isort lint-mypy lint-pylint lint-bandit

lint-black:
	black --check nova/ tests/

lint-isort:
	isort --check-only nova/ tests/

lint-mypy:
	mypy nova/

lint-pylint:
	pylint nova/

lint-bandit:
	bandit -r nova/

format:
	black nova/ tests/
	isort nova/ tests/

# Cleaning targets
clean: clean-build clean-pyc clean-test clean-docs

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/

clean-docs:
	rm -rf docs/_build/

# Build targets
build: clean
	python -m build

# Documentation targets
docs:
	$(MAKE) -C docs html

# Publishing targets
publish: build
	twine check dist/*
	twine upload dist/*

# Development environment setup
setup-dev: dev-install
	pre-commit install
	git config core.hooksPath .github/hooks

# Docker targets
docker-build:
	docker build -t teamadapt/nova:latest .

docker-run:
	docker run -it --rm teamadapt/nova:latest

# Database targets
db-migrate:
	alembic upgrade head

db-rollback:
	alembic downgrade -1

# Dependency management
deps-update:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in

deps-sync:
	pip-sync requirements.txt requirements-dev.txt

# Security checks
security-check:
	safety check
	bandit -r nova/
	pip-audit

# Type checking
type-check:
	mypy nova/ --strict

# Code quality checks
quality-check: lint type-check security-check test

# Continuous Integration
ci: quality-check build

# Git hooks
hooks:
	cp -r .github/hooks/* .git/hooks/
	chmod +x .git/hooks/*

# Environment setup
setup-env:
	cp .env.example .env

# Version management
bump-version:
	bump2version patch  # or minor/major

# Monitoring
monitor:
	python -m nova.cli monitor

# Development server
dev-server:
	python -m nova.cli run --debug

# Generate documentation
gen-docs:
	sphinx-apidoc -o docs/source nova/
	$(MAKE) -C docs html
