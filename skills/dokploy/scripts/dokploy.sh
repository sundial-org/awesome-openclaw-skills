#!/bin/bash
# Dokploy CLI - Main entry point

set -e

# Configuration
DOKPLOY_API_URL="${DOKPLOY_API_URL:-http://localhost:3000}"
DOKPLOY_API_KEY="${DOKPLOY_API_KEY:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

# API request helper
api_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local url="${DOKPLOY_API_URL}/api${endpoint}"

    # Silent mode - don't log when DOKPLOY_SILENT is set
    if [ -z "$DOKPLOY_SILENT" ]; then
        log_info "API: ${method} ${url}"
    fi

    if [ -z "$DOKPLOY_API_KEY" ]; then
        log_error "DOKPLOY_API_KEY not set. Run: export DOKPLOY_API_KEY='your-key'"
        exit 1
    fi

    if [ -n "$data" ]; then
        curl -s -X "${method}" "${url}" \
            -H "accept: application/json" \
            -H "x-api-key: ${DOKPLOY_API_KEY}" \
            -H "Content-Type: application/json" \
            -d "${data}"
    else
        curl -s -X "${method}" "${url}" \
            -H "accept: application/json" \
            -H "x-api-key: ${DOKPLOY_API_KEY}"
    fi
}

# Parse JSON helper (requires jq)
json_get() {
    echo "$1" | jq -r "$2"
}

# Check connection
check_connection() {
    local response=$(api_request "GET" "/project.all" 2>/dev/null)
    local type=$(echo "$response" | jq -r 'type' 2>/dev/null || echo "error")

    if [[ "$type" == "array" ]]; then
        return 0
    else
        return 1
    fi
}

# Main function - only execute when running directly (not when sourced)
main() {
    # Command routing
    case "$1" in
        config)
            shift
            bash "${0%/*}/dokploy-config.sh" "$@"
            ;;
        status)
            if check_connection; then
                log_success "Connected to Dokploy at ${DOKPLOY_API_URL}"
                echo
                echo "Projects:"
                api_request "GET" "/project.all" | jq -r '.[] | "- \(.name) (\(.projectId))"' 2>/dev/null || log_warn "No projects found"
            else
                log_error "Failed to connect to Dokploy at ${DOKPLOY_API_URL}"
                log_error "Check DOKPLOY_API_URL and DOKPLOY_API_KEY"
                exit 1
            fi
            ;;
        project)
            shift
            bash "${0%/*}/dokploy-project.sh" "$@"
            ;;
        app|application)
            shift
            bash "${0%/*}/dokploy-app.sh" "$@"
            ;;
        domain)
            shift
            bash "${0%/*}/dokploy-domain.sh" "$@"
            ;;
        *)
            echo "Dokploy CLI - Manage Dokploy deployments"
            echo ""
            echo "Usage: dokploy <command> [options]"
            echo ""
            echo "Commands:"
            echo "  status       Check API connection"
            echo "  config       Manage configuration"
            echo "  project      Manage projects"
            echo "  app          Manage applications"
            echo "  domain       Manage domains"
            echo ""
            echo "Environment Variables:"
            echo "  DOKPLOY_API_URL  Dokploy instance URL (default: http://localhost:3000)"
            echo "  DOKPLOY_API_KEY   API authentication key"
            echo ""
            echo "Examples:"
            echo "  dokploy status"
            echo "  dokploy project list"
            echo "  dokploy app list --project <project-id>"
            echo "  dokploy domain list --app <app-id>"
            ;;
    esac
}

# Only run main if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
