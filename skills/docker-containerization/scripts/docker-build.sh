#!/bin/bash

# Docker Build Script for Next.js Applications
# Builds Docker images with various configurations

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
DOCKERFILE="Dockerfile.production"
BUILD_ARGS=""
NO_CACHE=false
PLATFORM=""

# Print usage
usage() {
    echo -e "${BLUE}Usage:${NC} $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -n, --name NAME          Image name (default: nextjs-app)"
    echo "  -t, --tag TAG            Image tag (default: latest)"
    echo "  -f, --file DOCKERFILE    Dockerfile to use (default: Dockerfile.production)"
    echo "  -e, --env ENV            Environment (dev|prod|nginx)"
    echo "  -b, --build-arg ARG      Build argument (can be used multiple times)"
    echo "  --no-cache               Build without cache"
    echo "  --platform PLATFORM      Target platform (e.g., linux/amd64, linux/arm64)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e prod -t v1.0.0"
    echo "  $0 -n my-app -e dev --no-cache"
    echo "  $0 --platform linux/amd64 -e prod"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -f|--file)
            DOCKERFILE="$2"
            shift 2
            ;;
        -e|--env)
            ENV="$2"
            case $ENV in
                dev|development)
                    DOCKERFILE="Dockerfile.development"
                    ;;
                prod|production)
                    DOCKERFILE="Dockerfile.production"
                    ;;
                nginx)
                    DOCKERFILE="Dockerfile.nginx"
                    ;;
                *)
                    echo -e "${RED}Error: Invalid environment: $ENV${NC}"
                    echo "Valid options: dev, prod, nginx"
                    exit 1
                    ;;
            esac
            shift 2
            ;;
        -b|--build-arg)
            BUILD_ARGS="$BUILD_ARGS --build-arg $2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
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
DOCKER_CMD="docker build"
DOCKER_CMD="$DOCKER_CMD -t ${IMAGE_NAME}:${TAG}"
DOCKER_CMD="$DOCKER_CMD -f ${DOCKERFILE}"

if [ "$NO_CACHE" = true ]; then
    DOCKER_CMD="$DOCKER_CMD --no-cache"
fi

if [ -n "$PLATFORM" ]; then
    DOCKER_CMD="$DOCKER_CMD --platform $PLATFORM"
fi

if [ -n "$BUILD_ARGS" ]; then
    DOCKER_CMD="$DOCKER_CMD $BUILD_ARGS"
fi

DOCKER_CMD="$DOCKER_CMD ."

# Print configuration
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Docker Build Configuration       ║${NC}"
echo -e "${BLUE}╠═══════════════════════════════════════╣${NC}"
echo -e "${BLUE}║${NC} Image Name:    ${GREEN}${IMAGE_NAME}${NC}"
echo -e "${BLUE}║${NC} Tag:           ${GREEN}${TAG}${NC}"
echo -e "${BLUE}║${NC} Dockerfile:    ${GREEN}${DOCKERFILE}${NC}"
echo -e "${BLUE}║${NC} No Cache:      ${GREEN}${NO_CACHE}${NC}"
if [ -n "$PLATFORM" ]; then
    echo -e "${BLUE}║${NC} Platform:      ${GREEN}${PLATFORM}${NC}"
fi
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# Check if Dockerfile exists
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}Error: Dockerfile not found: $DOCKERFILE${NC}"
    exit 1
fi

# Execute build
echo -e "${YELLOW}Building Docker image...${NC}"
echo -e "${BLUE}Command:${NC} $DOCKER_CMD"
echo ""

if eval $DOCKER_CMD; then
    echo ""
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo ""
    echo -e "${BLUE}Image details:${NC}"
    docker images | grep "$IMAGE_NAME" | grep "$TAG"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  Run:    docker run -p 3000:3000 ${IMAGE_NAME}:${TAG}"
    echo "  Push:   docker push ${IMAGE_NAME}:${TAG}"
    echo "  Inspect: docker inspect ${IMAGE_NAME}:${TAG}"
else
    echo ""
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi
