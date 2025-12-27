#!/bin/bash
# Script to initialize TENJIN databases with educational theory data
# This script is used during Docker image build to pre-load data

set -e

echo "=== TENJIN Data Initialization ==="
echo "Waiting for Neo4j to be ready..."

# Wait for Neo4j to be ready
MAX_RETRIES=30
RETRY_COUNT=0
while ! wget --no-verbose --tries=1 --spider http://localhost:7474 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Error: Neo4j did not become ready in time"
        exit 1
    fi
    echo "Waiting for Neo4j... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo "Neo4j is ready!"

# Load educational theory data
echo "Loading educational theory data..."
cd /app
python -m scripts.load_data --clear --verbose

echo "=== Data initialization complete! ==="
