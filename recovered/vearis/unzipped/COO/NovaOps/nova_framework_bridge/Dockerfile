# Multi-stage build for Nova Framework Bridge

# Stage 1: Base Python image
FROM python:3.8-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Stage 2: Builder image
FROM python-base as builder
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        git

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy project files
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
COPY src/ src/
COPY tests/ tests/
COPY config/ config/

# Install dependencies
RUN poetry install --no-dev

# Stage 3: Development image
FROM python-base as development
ENV FASTAPI_ENV=development

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        git \
        redis-tools \
        postgresql-client \
        mongodb-clients \
    && rm -rf /var/lib/apt/lists/*

# Copy project files from builder
COPY --from=builder $POETRY_HOME $POETRY_HOME
COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

# Set working directory
WORKDIR $PYSETUP_PATH

# Install development dependencies
RUN poetry install

# Copy development configurations
COPY .pre-commit-config.yaml pytest.ini bandit.yaml ./
COPY run_tests.py run_tests.sh ./

# Make test scripts executable
RUN chmod +x run_tests.py run_tests.sh

# Stage 4: Testing image
FROM development as testing
ENV FASTAPI_ENV=testing

# Copy test configurations
COPY tests/ tests/
COPY pytest.ini .coveragerc ./

# Create directories for test artifacts
RUN mkdir -p \
    coverage_html \
    test_results \
    logs

# Stage 5: Production image
FROM python-base as production
ENV FASTAPI_ENV=production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        redis-tools \
        postgresql-client \
        mongodb-clients \
    && rm -rf /var/lib/apt/lists/*

# Copy project files from builder
COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

# Set working directory
WORKDIR $PYSETUP_PATH

# Copy production configurations
COPY config/ config/

# Create necessary directories
RUN mkdir -p logs

# Set up entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command
CMD ["python", "-m", "src.main"]

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1