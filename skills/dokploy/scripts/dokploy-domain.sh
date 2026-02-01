#!/bin/bash
# Dokploy Domain Management

# Source helper functions
source "$(dirname "$0")/dokploy.sh"

# Colors (redirect log_info to stderr)
log_info() { echo -e "\033[0;34m[INFO]\033[0m $1" >&2; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1" >&2; }
log_warn() { echo -e "\033[1;33m[WARN]\033[0m $1" >&2; }

main() {
case "$1" in
    list)
        local appId=""

        shift
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --application|--app)
                    appId="$2"
                    shift 2
                    ;;
                *)
                    ;;
            esac
        done

        if [ -z "$appId" ]; then
            log_error "Usage: dokploy domain list --app <app-id> or --project <project-id>"
            exit 1
        fi

        if [ -z "$appId" ]; then
            log_error "Usage: dokploy domain list --app <app-id>"
            exit 1
        fi

        log_info "Fetching domains for application $appId..."
        # Domains are nested inside applications/compose in Joshua's fork
        local response=$(api_request "GET" "/project.all")

        # Parse domains from nested structure - filter by project first, then find app, then domains
        echo "$response" | jq -r ".[] | .environments[] | .applications[] | select(.applicationId == \"$appId\") | .domains[]? | select(. != null) | \"ID: \(.domainId)\n  Domain: \(.host)\n  App: \(.applicationId)\n  Path: \(.path)\n  Port: \(.port)\n  HTTPS: \(.https)\"" 2>/dev/null || true

        # Also check compose apps
        echo "$response" | jq -r ".[] | .environments[] | .compose[] | select(.composeId == \"$appId\") | .domains[]? | select(. != null) | \"ID: \(.domainId)\n  Domain: \(.host)\n  App: \(.composeId)\n  Path: \(.path)\n  Port: \(.port)\n  HTTPS: \(.https)\"" 2>/dev/null || true
        ;;
    get)
        if [ -z "$2" ]; then
            log_error "Usage: dokploy domain get <domain-id>"
            exit 1
        fi
        log_info "Fetching domain $2..."
        local response=$(api_request "GET" "/domain.byId?domainId=$2")
        echo "$response" | jq '.' 2>/dev/null || log_error "Failed to fetch domain"
        ;;
    create)
        local appId=""
        local domain=""
        local path="/"
        local port=80
        local https="true"

        shift
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --application|--app)
                    appId="$2"
                    shift 2
                    ;;
                --domain)
                    domain="$2"
                    shift 2
                    ;;
                --path)
                    path="$2"
                    shift 2
                    ;;
                --port)
                    port="$2"
                    shift 2
                    ;;
                --no-https)
                    https="false"
                    shift
                    ;;
                *)
                    log_error "Unknown option: $1"
                    exit 1
                    ;;
            esac
        done

        if [ -z "$appId" ] || [ -z "$domain" ]; then
            log_error "Usage: dokploy domain create --app <id> --domain <name> [--path <path>] [--port <port>] [--no-https]"
            exit 1
        fi

        local data=$(jq -n \
            --arg appId "$appId" \
            --arg domain "$domain" \
            --arg path "$path" \
            --argjson port "$port" \
            --argjson https "$https" \
            '{
                applicationId: $appId,
                domain: $domain,
                path: $path,
                port: $port,
                https: $https
            }')

        log_info "Creating domain '$domain' for application $appId..."
        local response=$(api_request "POST" "/domain.create" "$data")
        local domainId=$(echo "$response" | jq -r '.domainId')

        if [ -n "$domainId" ] && [ "$domainId" != "null" ]; then
            log_success "Domain created with ID: $domainId"
        else
            log_error "Failed to create domain"
            echo "$response" | jq '.' 2>/dev/null || echo "$response"
            exit 1
        fi
        ;;
    update)
        if [ -z "$2" ]; then
            log_error "Usage: dokploy domain update <domain-id> --domain <name> [--path <path>] [--port <port>]"
            exit 1
        fi

        local domainId="$2"
        local domain=""
        local path=""
        local port=""
        local https=""

        shift 2
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --domain)
                    domain="$2"
                    shift 2
                    ;;
                --path)
                    path="$2"
                    shift 2
                    ;;
                --port)
                    port="$2"
                    shift 2
                    ;;
                --https)
                    https="$2"
                    shift 2
                    ;;
                --no-https)
                    https="false"
                    shift
                    ;;
                *)
                    ;;
            esac
        done

        # Build minimal update data
        local data=$(jq -n '{}')

        if [ -n "$domain" ]; then
            data=$(echo "$data" | jq --arg domain "$domain" '. + {domain: $domain}')
        fi
        if [ -n "$path" ]; then
            data=$(echo "$data" | jq --arg path "$path" '. + {path: $path}')
        fi
        if [ -n "$port" ]; then
            data=$(echo "$data" | jq --argjson port "$port" '. + {port: $port}')
        fi
        if [ -n "$https" ]; then
            data=$(echo "$data" | jq --argjson https "$https" '. + {https: $https}')
        fi

        log_info "Updating domain $domainId..."
        local response=$(api_request "PATCH" "/domain.update?domainId=$domainId" "$data")

        if echo "$response" | jq -e 'true' > /dev/null 2>&1; then
            log_success "Domain updated"
        else
            log_error "Failed to update domain"
            echo "$response"
            exit 1
        fi
        ;;
    delete)
        if [ -z "$2" ]; then
            log_error "Usage: dokploy domain delete <domain-id>"
            exit 1
        fi

        log_warn "Are you sure you want to delete domain $2?"
        read -p "Type 'yes' to confirm: " confirm

        if [ "$confirm" != "yes" ]; then
            log_info "Cancelled"
            exit 0
        fi

        log_info "Deleting domain $2..."
        local response=$(api_request "DELETE" "/domain.delete?domainId=$2")

        if echo "$response" | jq -e 'true' > /dev/null 2>&1; then
            log_success "Domain deleted"
        else
            log_error "Failed to delete domain"
            echo "$response"
            exit 1
        fi
        ;;
    *)
        echo "Usage: dokploy domain <command>"
        echo ""
        echo "Commands:"
        echo "  list [--app <id>]          List domains"
        echo "  get <domain-id>             Get domain details"
        echo "  create --app <id> ...       Create domain"
        echo "  update <id> --domain <name>  Update domain"
        echo "  delete <domain-id>           Delete domain"
        echo ""
        echo "Create options:"
        echo "  --application <id>   Application ID (required)"
        echo "  --domain <name>      Domain name (required)"
        echo "  --path <path>       Path (default: /)"
        echo "  --port <port>       Port (default: 80)"
        echo "  --no-https          Disable HTTPS"
        ;;
esac
}

# Only run main if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
