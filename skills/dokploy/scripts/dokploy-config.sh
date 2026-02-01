#!/bin/bash
# Dokploy Config Management

CONFIG_FILE="$HOME/.dokployrc"

# Helper functions
log_info() { echo -e "\033[0;34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1" >&2; }

case "$1" in
    set)
        shift
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --url)
                    DOKPLOY_API_URL="$2"
                    shift 2
                    ;;
                --key)
                    DOKPLOY_API_KEY="$2"
                    shift 2
                    ;;
                *)
                    log_error "Unknown option: $1"
                    exit 1
                    ;;
            esac
        done

        # Save to config file
        mkdir -p "$(dirname "$CONFIG_FILE")"
        cat > "$CONFIG_FILE" << EOF
export DOKPLOY_API_URL="${DOKPLOY_API_URL}"
export DOKPLOY_API_KEY="${DOKPLOY_API_KEY}"
EOF
        log_success "Config saved to $CONFIG_FILE"
        log_info "Run: source $CONFIG_FILE to load"
        ;;
    show)
        echo "Dokploy Configuration:"
        echo "  API URL: ${DOKPLOY_API_URL:-not set}"
        echo "  API Key: ${DOKPLOY_API_KEY:+***set***} ${DOKPLOY_API_KEY:-not set}"

        if [ -f "$CONFIG_FILE" ]; then
            echo ""
            echo "Config file: $CONFIG_FILE"
            echo "To load: source $CONFIG_FILE"
        fi
        ;;
    *)
        echo "Usage: dokploy-config <command>"
        echo ""
        echo "Commands:"
        echo "  set --url <url> --key <key>  Set configuration"
        echo "  show                            Show current configuration"
        ;;
esac
