#!/bin/bash

# Docker Cleanup Script
# Removes unused Docker resources to free up disk space

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
DRY_RUN=false
FORCE=false
ALL=false
CONTAINERS=false
IMAGES=false
VOLUMES=false
NETWORKS=false

# Print usage
usage() {
    echo -e "${BLUE}Usage:${NC} $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all                    Clean all unused resources"
    echo "  --containers             Remove stopped containers"
    echo "  --images                 Remove dangling images"
    echo "  --volumes                Remove unused volumes"
    echo "  --networks               Remove unused networks"
    echo "  --dry-run                Show what would be removed without actually removing"
    echo "  -f, --force              Force removal without confirmation"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all                 # Clean everything"
    echo "  $0 --containers --images  # Clean containers and images"
    echo "  $0 --all --dry-run       # Preview cleanup without removing"
}

# Parse arguments
if [ $# -eq 0 ]; then
    usage
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            ALL=true
            shift
            ;;
        --containers)
            CONTAINERS=true
            shift
            ;;
        --images)
            IMAGES=true
            shift
            ;;
        --volumes)
            VOLUMES=true
            shift
            ;;
        --networks)
            NETWORKS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
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

# If --all is specified, enable all cleanup options
if [ "$ALL" = true ]; then
    CONTAINERS=true
    IMAGES=true
    VOLUMES=true
    NETWORKS=true
fi

# Show current disk usage
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Current Docker Disk Usage        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
docker system df
echo ""

# Confirmation prompt (unless --force or --dry-run)
if [ "$FORCE" = false ] && [ "$DRY_RUN" = false ]; then
    echo -e "${YELLOW}This will remove unused Docker resources.${NC}"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Aborted.${NC}"
        exit 0
    fi
fi

# Cleanup functions
cleanup_containers() {
    echo -e "${BLUE}Cleaning up stopped containers...${NC}"

    if [ "$DRY_RUN" = true ]; then
        STOPPED=$(docker ps -aq -f status=exited)
        if [ -n "$STOPPED" ]; then
            echo -e "${YELLOW}Would remove:${NC}"
            docker ps -a -f status=exited --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
        else
            echo -e "${GREEN}No stopped containers to remove.${NC}"
        fi
    else
        REMOVED=$(docker container prune -f 2>&1 | grep "Total reclaimed space" || echo "")
        if [ -n "$REMOVED" ]; then
            echo -e "${GREEN}✓ $REMOVED${NC}"
        else
            echo -e "${GREEN}✓ No stopped containers to remove.${NC}"
        fi
    fi
    echo ""
}

cleanup_images() {
    echo -e "${BLUE}Cleaning up dangling images...${NC}"

    if [ "$DRY_RUN" = true ]; then
        DANGLING=$(docker images -f "dangling=true" -q)
        if [ -n "$DANGLING" ]; then
            echo -e "${YELLOW}Would remove:${NC}"
            docker images -f "dangling=true" --format "table {{.ID}}\t{{.Repository}}\t{{.Tag}}\t{{.Size}}"
        else
            echo -e "${GREEN}No dangling images to remove.${NC}"
        fi
    else
        REMOVED=$(docker image prune -f 2>&1 | grep "Total reclaimed space" || echo "")
        if [ -n "$REMOVED" ]; then
            echo -e "${GREEN}✓ $REMOVED${NC}"
        else
            echo -e "${GREEN}✓ No dangling images to remove.${NC}"
        fi
    fi
    echo ""
}

cleanup_volumes() {
    echo -e "${BLUE}Cleaning up unused volumes...${NC}"

    if [ "$DRY_RUN" = true ]; then
        UNUSED=$(docker volume ls -qf dangling=true)
        if [ -n "$UNUSED" ]; then
            echo -e "${YELLOW}Would remove:${NC}"
            docker volume ls -f dangling=true --format "table {{.Name}}\t{{.Driver}}\t{{.Mountpoint}}"
        else
            echo -e "${GREEN}No unused volumes to remove.${NC}"
        fi
    else
        REMOVED=$(docker volume prune -f 2>&1 | grep "Total reclaimed space" || echo "")
        if [ -n "$REMOVED" ]; then
            echo -e "${GREEN}✓ $REMOVED${NC}"
        else
            echo -e "${GREEN}✓ No unused volumes to remove.${NC}"
        fi
    fi
    echo ""
}

cleanup_networks() {
    echo -e "${BLUE}Cleaning up unused networks...${NC}"

    if [ "$DRY_RUN" = true ]; then
        UNUSED=$(docker network ls -qf "dangling=true")
        if [ -n "$UNUSED" ]; then
            echo -e "${YELLOW}Would remove:${NC}"
            docker network ls -f "dangling=true" --format "table {{.ID}}\t{{.Name}}\t{{.Driver}}"
        else
            echo -e "${GREEN}No unused networks to remove.${NC}"
        fi
    else
        REMOVED=$(docker network prune -f 2>&1 | grep "Total reclaimed space" || echo "")
        if [ -n "$REMOVED" ]; then
            echo -e "${GREEN}✓ $REMOVED${NC}"
        else
            echo -e "${GREEN}✓ No unused networks to remove.${NC}"
        fi
    fi
    echo ""
}

# Execute cleanup operations
if [ "$CONTAINERS" = true ]; then
    cleanup_containers
fi

if [ "$IMAGES" = true ]; then
    cleanup_images
fi

if [ "$VOLUMES" = true ]; then
    cleanup_volumes
fi

if [ "$NETWORKS" = true ]; then
    cleanup_networks
fi

# Show final disk usage
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Final Docker Disk Usage         ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
docker system df
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}Dry run complete. No resources were removed.${NC}"
    echo -e "${BLUE}Run without --dry-run to actually remove resources.${NC}"
else
    echo -e "${GREEN}✓ Cleanup complete!${NC}"
fi
