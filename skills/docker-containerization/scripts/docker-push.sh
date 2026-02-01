#!/bin/bash

# Docker Push Script for Next.js Applications
# Pushes Docker images to registries (Docker Hub, ECR, GCR, etc.)

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
REGISTRY=""
REPOSITORY=""
ADDITIONAL_TAGS=""

# Print usage
usage() {
    echo -e "${BLUE}Usage:${NC} $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -n, --name NAME          Image name (default: nextjs-app)"
    echo "  -t, --tag TAG            Image tag (default: latest)"
    echo "  -r, --registry REG       Registry URL (e.g., docker.io, gcr.io, 123456789012.dkr.ecr.us-east-1.amazonaws.com)"
    echo "  --repo REPO              Repository name (e.g., mycompany/myapp)"
    echo "  --also-tag TAG           Additional tags to create and push (can be used multiple times)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -n my-app -t v1.0.0 --repo username/my-app"
    echo "  $0 -r gcr.io/my-project --repo my-app -t latest --also-tag stable"
    echo "  $0 -r 123456789012.dkr.ecr.us-east-1.amazonaws.com --repo my-app"
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
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        --repo)
            REPOSITORY="$2"
            shift 2
            ;;
        --also-tag)
            ADDITIONAL_TAGS="$ADDITIONAL_TAGS $2"
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

# Check if image exists locally
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE_NAME}:${TAG}$"; then
    echo -e "${RED}Error: Image not found: ${IMAGE_NAME}:${TAG}${NC}"
    echo -e "${YELLOW}Available images:${NC}"
    docker images | grep "$IMAGE_NAME" || echo "No images found for $IMAGE_NAME"
    exit 1
fi

# Build the target image name
if [ -n "$REGISTRY" ] && [ -n "$REPOSITORY" ]; then
    TARGET_IMAGE="${REGISTRY}/${REPOSITORY}:${TAG}"
elif [ -n "$REPOSITORY" ]; then
    TARGET_IMAGE="${REPOSITORY}:${TAG}"
else
    TARGET_IMAGE="${IMAGE_NAME}:${TAG}"
fi

# Print configuration
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Docker Push Configuration       ║${NC}"
echo -e "${BLUE}╠═══════════════════════════════════════╣${NC}"
echo -e "${BLUE}║${NC} Source Image:  ${GREEN}${IMAGE_NAME}:${TAG}${NC}"
echo -e "${BLUE}║${NC} Target Image:  ${GREEN}${TARGET_IMAGE}${NC}"
if [ -n "$ADDITIONAL_TAGS" ]; then
    echo -e "${BLUE}║${NC} Also pushing:  ${GREEN}${ADDITIONAL_TAGS}${NC}"
fi
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# Tag the image if source and target are different
if [ "${IMAGE_NAME}:${TAG}" != "$TARGET_IMAGE" ]; then
    echo -e "${YELLOW}Tagging image...${NC}"
    if docker tag "${IMAGE_NAME}:${TAG}" "$TARGET_IMAGE"; then
        echo -e "${GREEN}✓ Tagged successfully${NC}"
    else
        echo -e "${RED}✗ Failed to tag image${NC}"
        exit 1
    fi
    echo ""
fi

# Push the main image
echo -e "${YELLOW}Pushing image: ${TARGET_IMAGE}${NC}"
if docker push "$TARGET_IMAGE"; then
    echo -e "${GREEN}✓ Pushed successfully: ${TARGET_IMAGE}${NC}"
else
    echo -e "${RED}✗ Failed to push image${NC}"
    exit 1
fi
echo ""

# Push additional tags
for EXTRA_TAG in $ADDITIONAL_TAGS; do
    if [ -n "$REGISTRY" ] && [ -n "$REPOSITORY" ]; then
        EXTRA_IMAGE="${REGISTRY}/${REPOSITORY}:${EXTRA_TAG}"
    elif [ -n "$REPOSITORY" ]; then
        EXTRA_IMAGE="${REPOSITORY}:${EXTRA_TAG}"
    else
        EXTRA_IMAGE="${IMAGE_NAME}:${EXTRA_TAG}"
    fi

    echo -e "${YELLOW}Tagging and pushing: ${EXTRA_IMAGE}${NC}"

    if docker tag "${IMAGE_NAME}:${TAG}" "$EXTRA_IMAGE"; then
        if docker push "$EXTRA_IMAGE"; then
            echo -e "${GREEN}✓ Pushed successfully: ${EXTRA_IMAGE}${NC}"
        else
            echo -e "${RED}✗ Failed to push: ${EXTRA_IMAGE}${NC}"
        fi
    else
        echo -e "${RED}✗ Failed to tag: ${EXTRA_IMAGE}${NC}"
    fi
    echo ""
done

echo -e "${GREEN}✓ All images pushed successfully!${NC}"
echo ""
echo -e "${BLUE}Pushed images:${NC}"
echo "  - ${TARGET_IMAGE}"
for EXTRA_TAG in $ADDITIONAL_TAGS; do
    if [ -n "$REGISTRY" ] && [ -n "$REPOSITORY" ]; then
        echo "  - ${REGISTRY}/${REPOSITORY}:${EXTRA_TAG}"
    elif [ -n "$REPOSITORY" ]; then
        echo "  - ${REPOSITORY}:${EXTRA_TAG}"
    else
        echo "  - ${IMAGE_NAME}:${EXTRA_TAG}"
    fi
done
