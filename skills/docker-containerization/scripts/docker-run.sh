#!/bin/bash

# Docker Run Script for Next.js Applications
# Runs Docker containers with various configurations

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="nextjs-app"
TAG="latest"
CONTAINER_NAME="nextjs-container"
HOST_PORT="3000"
CONTAINER_PORT="3000"
DETACHED=false
ENV_FILE=""
VOLUMES=""
NETWORK=""
RESTART_POLICY=""

# Print usage
usage() {
    echo -e "${BLUE}Usage:${NC} $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -n, --name NAME          Container name (default: nextjs-container)"
    echo "  -i, --image IMAGE        Image name (default: nextjs-app)"
    echo "  -t, --tag TAG            Image tag (default: latest)"
    echo "  -p, --port HOST:CONT     Port mapping (default: 3000:3000)"
    echo "  -d, --detach             Run in detached mode"
    echo "  -e, --env-file FILE      Environment file"
    echo "  -v, --volume VOL         Volume mount (can be used multiple times)"
    echo "  --network NETWORK        Docker network to use"
    echo "  --restart POLICY         Restart policy (no|on-failure|always|unless-stopped)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -i my-app -t v1.0.0 -d"
    echo "  $0 -p 8080:3000 --env-file .env.production"
    echo "  $0 -v ./data:/app/data --restart unless-stopped"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -i|--image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -p|--port)
            IFS=':' read -r HOST_PORT CONTAINER_PORT <<< "$2"
            shift 2
            ;;
        -d|--detach)
            DETACHED=true
            shift
            ;;
        -e|--env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        -v|--volume)
            VOLUMES="$VOLUMES -v $2"
            shift 2
            ;;
        --network)
            NETWORK="$2"
            shift 2
            ;;
        --restart)
            RESTART_POLICY="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Build the command
DOCKER_CMD="docker run"
DOCKER_CMD="$DOCKER_CMD --name ${CONTAINER_NAME}"
DOCKER_CMD="$DOCKER_CMD -p ${HOST_PORT}:${CONTAINER_PORT}"

if [ "$DETACHED" = true ]; then
    DOCKER_CMD="$DOCKER_CMD -d"
fi

if [ -n "$ENV_FILE" ]; then
    if [ -f "$ENV_FILE" ]; then
        DOCKER_CMD="$DOCKER_CMD --env-file $ENV_FILE"
    else
        echo -e "${YELLOW}Warning: Environment file not found: $ENV_FILE${NC}"
    fi
fi

if [ -n "$VOLUMES" ]; then
    DOCKER_CMD="$DOCKER_CMD $VOLUMES"
fi

if [ -n "$NETWORK" ]; then
    DOCKER_CMD="$DOCKER_CMD --network $NETWORK"
fi

if [ -n "$RESTART_POLICY" ]; then
    DOCKER_CMD="$DOCKER_CMD --restart $RESTART_POLICY"
fi

DOCKER_CMD="$DOCKER_CMD ${IMAGE_NAME}:${TAG}"

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}Container ${CONTAINER_NAME} already exists.${NC}"
    read -p "Do you want to remove it and create a new one? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Removing existing container...${NC}"
        docker rm -f "$CONTAINER_NAME"
    else
        echo -e "${RED}Aborted.${NC}"
        exit 1
    fi
fi

# Check if image exists
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE_NAME}:${TAG}$"; then
    echo -e "${RED}Error: Image not found: ${IMAGE_NAME}:${TAG}${NC}"
    echo -e "${YELLOW}Available images:${NC}"
    docker images | grep "$IMAGE_NAME" || echo "No images found for $IMAGE_NAME"
    exit 1
fi

# Print configuration
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Docker Run Configuration        ║${NC}"
echo -e "${BLUE}╠═══════════════════════════════════════╣${NC}"
echo -e "${BLUE}║${NC} Container:     ${GREEN}${CONTAINER_NAME}${NC}"
echo -e "${BLUE}║${NC} Image:         ${GREEN}${IMAGE_NAME}:${TAG}${NC}"
echo -e "${BLUE}║${NC} Port:          ${GREEN}${HOST_PORT}:${CONTAINER_PORT}${NC}"
echo -e "${BLUE}║${NC} Detached:      ${GREEN}${DETACHED}${NC}"
if [ -n "$ENV_FILE" ]; then
    echo -e "${BLUE}║${NC} Env File:      ${GREEN}${ENV_FILE}${NC}"
fi
if [ -n "$NETWORK" ]; then
    echo -e "${BLUE}║${NC} Network:       ${GREEN}${NETWORK}${NC}"
fi
if [ -n "$RESTART_POLICY" ]; then
    echo -e "${BLUE}║${NC} Restart:       ${GREEN}${RESTART_POLICY}${NC}"
fi
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# Execute run
echo -e "${YELLOW}Starting Docker container...${NC}"
echo -e "${BLUE}Command:${NC} $DOCKER_CMD"
echo ""

if eval $DOCKER_CMD; then
    echo ""
    echo -e "${GREEN}✓ Container started successfully!${NC}"
    echo ""

    if [ "$DETACHED" = true ]; then
        echo -e "${BLUE}Container is running in background.${NC}"
        echo ""
        echo -e "${BLUE}Container details:${NC}"
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo -e "${BLUE}Access application:${NC}"
        echo "  URL:  http://localhost:${HOST_PORT}"
        echo ""
        echo -e "${BLUE}Useful commands:${NC}"
        echo "  Logs:    docker logs -f ${CONTAINER_NAME}"
        echo "  Stop:    docker stop ${CONTAINER_NAME}"
        echo "  Restart: docker restart ${CONTAINER_NAME}"
        echo "  Remove:  docker rm -f ${CONTAINER_NAME}"
        echo "  Exec:    docker exec -it ${CONTAINER_NAME} sh"
    else
        echo -e "${BLUE}Container running in foreground. Press Ctrl+C to stop.${NC}"
    fi
else
    echo ""
    echo -e "${RED}✗ Failed to start container!${NC}"
    exit 1
fi
