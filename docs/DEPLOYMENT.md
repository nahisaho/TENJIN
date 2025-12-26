# TENJIN Deployment Guide

This guide covers deployment options for the TENJIN Educational Theory GraphRAG MCP Server.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services

- **Neo4j 5.x**: Graph database for knowledge graph
- **Python 3.11+**: Runtime environment

### Optional Services

- **ChromaDB 0.5+**: Vector database for semantic search
- **Redis 7.x**: Caching layer (optional)

### Environment Variables

```bash
# Required
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# LLM Provider (choose one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Optional
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

---

## Local Development

### Quick Start

1. **Clone and setup:**
```bash
cd /path/to/TENJIN
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

2. **Start dependencies:**
```bash
docker-compose up -d neo4j
```

3. **Load data:**
```bash
python scripts/load_data.py
```

4. **Run server:**
```bash
mcp run src/tenjin/server.py
```

### Development Mode

For hot-reload during development:
```bash
mcp dev src/tenjin/server.py
```

---

## Docker Deployment

### Using Docker Compose

The included `docker-compose.yml` provides a complete stack:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f tenjin

# Stop services
docker-compose down
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  tenjin:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=tenjin_password
      - CHROMADB_HOST=chromadb
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - neo4j
      - chromadb
    restart: unless-stopped

  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/tenjin_password
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
    restart: unless-stopped

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    restart: unless-stopped

volumes:
  neo4j_data:
  chroma_data:
```

### Building Custom Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[prod]"

# Copy application
COPY src/ src/
COPY data/ data/
COPY scripts/ scripts/

# Set environment
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import tenjin; print('healthy')"

# Run server
CMD ["mcp", "run", "src/tenjin/server.py"]
```

---

## Production Deployment

### Cloud Deployment Options

#### Option 1: AWS ECS/Fargate

```json
{
  "family": "tenjin",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "tenjin",
      "image": "your-registry/tenjin:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "NEO4J_URI", "value": "bolt://neo4j.internal:7687"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {"name": "NEO4J_PASSWORD", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/tenjin",
          "awslogs-region": "ap-northeast-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Option 2: Google Cloud Run

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: tenjin
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
        - image: gcr.io/your-project/tenjin:latest
          ports:
            - containerPort: 8000
          env:
            - name: NEO4J_URI
              value: "bolt://neo4j-instance:7687"
          resources:
            limits:
              memory: "1Gi"
              cpu: "1000m"
```

#### Option 3: Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tenjin
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tenjin
  template:
    metadata:
      labels:
        app: tenjin
    spec:
      containers:
        - name: tenjin
          image: your-registry/tenjin:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: tenjin-config
            - secretRef:
                name: tenjin-secrets
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: tenjin
spec:
  selector:
    app: tenjin
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

### Neo4j Production Setup

For production, use Neo4j Aura or a managed instance:

```bash
# Neo4j Aura connection
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<aura-password>
```

Or deploy Neo4j with enterprise features:

```yaml
# neo4j-values.yaml for Helm
neo4j:
  name: neo4j-tenjin
  edition: enterprise
  resources:
    cpu: "2"
    memory: "4Gi"
  volumes:
    data:
      mode: defaultStorageClass
      size: 100Gi
```

---

## Configuration

### Environment Configuration

Create `.env` file for each environment:

```bash
# .env.development
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dev_password
LOG_LEVEL=DEBUG
ENABLE_CACHE=false

# .env.production
NEO4J_URI=bolt://neo4j-prod:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=${NEO4J_PROD_PASSWORD}
LOG_LEVEL=INFO
ENABLE_CACHE=true
REDIS_URL=redis://redis-prod:6379
```

### LLM Provider Configuration

```bash
# OpenAI (default)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Google
LLM_PROVIDER=google
GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-1.5-pro

# Ollama (local)
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

### Performance Tuning

```bash
# Connection pools
NEO4J_MAX_CONNECTIONS=50
CHROMADB_MAX_CONNECTIONS=20

# Caching
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Timeouts
REQUEST_TIMEOUT=30
LLM_TIMEOUT=60
```

---

## Monitoring

### Health Checks

The server exposes health endpoints:

```bash
# Liveness check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# Detailed status
curl http://localhost:8000/status
```

### Logging

Configure structured logging:

```python
# settings.py
LOG_FORMAT = "json"  # or "text"
LOG_LEVEL = "INFO"
LOG_FILE = "/var/log/tenjin/app.log"
```

Example log output:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Theory retrieved",
  "theory_id": "constructivism",
  "duration_ms": 45,
  "user_id": "anonymous"
}
```

### Metrics

Prometheus metrics endpoint:

```bash
curl http://localhost:8000/metrics
```

Available metrics:
- `tenjin_requests_total`: Total requests by tool
- `tenjin_request_duration_seconds`: Request duration histogram
- `tenjin_cache_hits_total`: Cache hit count
- `tenjin_neo4j_connections`: Active Neo4j connections
- `tenjin_llm_tokens_total`: LLM token usage

### Alerting

Example Prometheus alerting rules:

```yaml
groups:
  - name: tenjin
    rules:
      - alert: HighErrorRate
        expr: rate(tenjin_requests_total{status="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High error rate detected

      - alert: SlowResponses
        expr: histogram_quantile(0.95, rate(tenjin_request_duration_seconds_bucket[5m])) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: 95th percentile response time > 5s
```

---

## Troubleshooting

### Common Issues

#### Neo4j Connection Failed

```
Error: Unable to connect to Neo4j
```

**Solutions:**
1. Check Neo4j is running: `docker-compose ps neo4j`
2. Verify credentials in `.env`
3. Check network connectivity
4. Ensure bolt port (7687) is accessible

#### ChromaDB Connection Failed

```
Error: ChromaDB unavailable
```

**Solutions:**
1. Check ChromaDB status: `docker-compose ps chromadb`
2. Verify host/port configuration
3. ChromaDB is optional - system works without it

#### LLM API Error

```
Error: Rate limit exceeded
```

**Solutions:**
1. Implement exponential backoff
2. Check API key validity
3. Upgrade API tier if needed
4. Use local model (Ollama) for development

#### Memory Issues

```
Error: Out of memory
```

**Solutions:**
1. Increase container memory limits
2. Reduce cache size
3. Optimize batch sizes for data loading
4. Check for memory leaks

### Debug Mode

Enable debug mode for detailed logging:

```bash
LOG_LEVEL=DEBUG mcp run src/tenjin/server.py
```

### Data Validation

Validate loaded data:

```bash
python scripts/validate_data.py
```

### Performance Profiling

Profile slow queries:

```bash
python -m cProfile -o profile.stats scripts/benchmark.py
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

---

## Backup and Recovery

### Neo4j Backup

```bash
# Online backup (Enterprise)
neo4j-admin database dump neo4j --to-path=/backup

# Docker volume backup
docker run --rm -v neo4j_data:/data -v $(pwd):/backup \
  alpine tar cvf /backup/neo4j-backup.tar /data
```

### Data Export

```bash
# Export to JSON
python scripts/export_data.py --format json --output backup/

# Export to CSV
python scripts/export_data.py --format csv --output backup/
```

### Recovery

```bash
# Restore Neo4j
neo4j-admin database load neo4j --from-path=/backup

# Reload data
python scripts/load_data.py --force
```

---

## Security

### API Key Management

- Use environment variables or secrets manager
- Rotate keys regularly
- Never commit keys to version control

### Network Security

- Use TLS for all connections
- Implement authentication for production
- Use network policies in Kubernetes

### Data Privacy

- Educational theories are public domain
- User queries may be logged - implement retention policy
- Comply with GDPR/CCPA if applicable

---

## Support

For issues and questions:

- GitHub Issues: [TENJIN Issues](https://github.com/your-org/tenjin/issues)
- Documentation: [TENJIN Docs](https://tenjin.readthedocs.io)
