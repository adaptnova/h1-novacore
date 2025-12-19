# Use multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /build

# Copy requirements files
COPY requirements.txt .
COPY setup.py .
COPY README.md .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install wheel && \
    pip wheel --no-deps --wheel-dir /wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NOVA_ENVIRONMENT=production

# Create non-root user
RUN useradd -m -s /bin/bash nova

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy wheels from builder
COPY --from=builder /wheels /wheels

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Change ownership to non-root user
RUN chown -R nova:nova /app

# Switch to non-root user
USER nova

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Expose port
EXPOSE 8000

# Set entrypoint and default command
ENTRYPOINT ["python", "-m", "nova.cli"]
CMD ["run", "--host", "0.0.0.0", "--port", "8000"]
