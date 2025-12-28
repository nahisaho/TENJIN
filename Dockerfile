# ===========================================
# TENJIN - Educational Theory GraphRAG System
# ===========================================
# Multi-stage Dockerfile with data pre-loading support
#
# Targets:
#   - base: Application with dependencies
#   - runtime: Production image (default)
#   - data-loader: Image for loading data into databases
#
# Build examples:
#   docker build -t tenjin:latest .
#   docker build --target data-loader -t tenjin:data-loader .

# ===========================================
# Base Stage: Dependencies
# ===========================================
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install uv

# Copy dependency files and source code
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install dependencies
RUN uv pip install --system -e ".[dev]" && \
    find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Copy remaining files
COPY data/ ./data/
COPY scripts/ ./scripts/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# ===========================================
# Runtime Stage: Production Server
# ===========================================
FROM base AS runtime

# Default environment for databases
ENV NEO4J_URI=bolt://localhost:7687
ENV NEO4J_USERNAME=neo4j
ENV NEO4J_PASSWORD=password
ENV CHROMADB_HOST=localhost
ENV CHROMADB_PORT=8000
ENV EMBEDDING_PROVIDER=ollama
ENV EMBEDDING_MODEL=nomic-embed-text

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose MCP stdio
ENTRYPOINT ["python", "-m", "tenjin.interface.mcp_server"]

# ===========================================
# Data Loader Stage: Load Educational Theories
# ===========================================
FROM base AS data-loader

# Script to wait for databases and load data
COPY scripts/init_data.sh /app/init_data.sh
RUN chmod +x /app/init_data.sh

# Default: load data with verbose output
ENTRYPOINT ["python", "-m", "scripts.load_data", "--clear", "--verbose"]
