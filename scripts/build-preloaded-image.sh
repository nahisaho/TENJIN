#!/bin/bash
# ===========================================
# Build Pre-loaded TENJIN Docker Images
# ===========================================
# This script creates Docker images with educational theory data
# already loaded into Neo4j and ChromaDB.
#
# Usage: ./scripts/build-preloaded-image.sh [--push]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="${IMAGE_NAME:-tenjin}"
IMAGE_TAG="${IMAGE_TAG:-latest-preloaded}"
COMPOSE_FILE="docker-compose.preload.yml"
PUSH_IMAGE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN} Building Pre-loaded TENJIN Docker Images ${NC}"
echo -e "${GREEN}============================================${NC}"

# Step 1: Build the base image
echo -e "${YELLOW}Step 1: Building base image...${NC}"
docker build -t ${IMAGE_NAME}:base .

# Step 2: Start the databases
echo -e "${YELLOW}Step 2: Starting databases...${NC}"
docker-compose -f ${COMPOSE_FILE} up -d neo4j chromadb

# Step 3: Wait for databases to be healthy
echo -e "${YELLOW}Step 3: Waiting for databases to be healthy...${NC}"
echo "Waiting for Neo4j..."
until docker-compose -f ${COMPOSE_FILE} exec -T neo4j wget --no-verbose --tries=1 --spider http://localhost:7474 2>/dev/null; do
    echo "  Neo4j not ready yet, waiting..."
    sleep 5
done
echo -e "${GREEN}  Neo4j is healthy!${NC}"

echo "Waiting for ChromaDB..."
until docker-compose -f ${COMPOSE_FILE} exec -T chromadb curl -f http://localhost:8000/api/v1/heartbeat 2>/dev/null; do
    echo "  ChromaDB not ready yet, waiting..."
    sleep 5
done
echo -e "${GREEN}  ChromaDB is healthy!${NC}"

# Step 4: Load educational theory data
echo -e "${YELLOW}Step 4: Loading educational theory data...${NC}"
docker-compose -f ${COMPOSE_FILE} run --rm data-loader

# Step 5: Verify data was loaded
echo -e "${YELLOW}Step 5: Verifying loaded data...${NC}"
NEO4J_COUNT=$(docker-compose -f ${COMPOSE_FILE} exec -T neo4j cypher-shell -u neo4j -p password "MATCH (n) RETURN count(n) as count" 2>/dev/null | tail -1)
echo -e "${GREEN}  Neo4j node count: ${NEO4J_COUNT}${NC}"

# Step 6: Create volume backup images (optional)
echo -e "${YELLOW}Step 6: Creating volume snapshots...${NC}"

# Export Neo4j data
docker run --rm \
    -v tenjin_neo4j_preload:/source:ro \
    -v $(pwd)/build:/backup \
    alpine tar czf /backup/neo4j-data.tar.gz -C /source .

# Export ChromaDB data
docker run --rm \
    -v tenjin_chromadb_preload:/source:ro \
    -v $(pwd)/build:/backup \
    alpine tar czf /backup/chromadb-data.tar.gz -C /source .

echo -e "${GREEN}  Volume backups created in ./build/${NC}"

# Step 7: Build the final image with data
echo -e "${YELLOW}Step 7: Building final pre-loaded image...${NC}"

# Create a Dockerfile for the pre-loaded image
cat > Dockerfile.preloaded << 'EOF'
# Pre-loaded TENJIN Image
FROM tenjin:base

# Copy pre-loaded database backups
COPY build/neo4j-data.tar.gz /data/backups/
COPY build/chromadb-data.tar.gz /data/backups/

# Add initialization script
COPY scripts/restore-data.sh /docker-entrypoint.d/

# Default command
CMD ["python", "-m", "tenjin.interface.mcp_server"]
EOF

# Build the pre-loaded image
docker build -f Dockerfile.preloaded -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN} Build Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "  Image: ${IMAGE_NAME}:${IMAGE_TAG}"

# Step 8: Cleanup
echo -e "${YELLOW}Cleaning up containers...${NC}"
docker-compose -f ${COMPOSE_FILE} down

# Optional: Push to registry
if [ "$PUSH_IMAGE" = true ]; then
    echo -e "${YELLOW}Pushing image to registry...${NC}"
    docker push ${IMAGE_NAME}:${IMAGE_TAG}
fi

echo -e "${GREEN}Done!${NC}"
