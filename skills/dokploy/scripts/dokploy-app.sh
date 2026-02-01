#!/bin/bash
# Dokploy Application Management

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
        local projectId=""
        shift
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --project)
                    projectId="$2"
                    shift 2
                    ;;
                *)
                    ;;
            esac
        done

        if [ -z "$projectId" ]; then
            log_error "Usage: dokploy app list --project <project-id>"
            exit 1
        fi

        log_info "Fetching applications for project $projectId..."
        # Applications are nested inside project.environments in Joshua's fork
        DOKPLOY_SILENT=1
        local response=$(api_request "GET" "/project.all")

        # Parse applications from nested structure  
        echo "$response" | jq -r ".[] | select(.projectId == \"$projectId\") | .environments | .[] | .applications[] | select(. != null) | \"ID: \(.applicationId)\n  Name: \(.name)\n  Type: \(.type // \"N/A\")\n  Project: \(.projectId)\n  Status: \(.applicationStatus // \"N/A\")\n  Environment: \(.environmentId)\"" 2>/dev/null || true

        # Also include compose applications
        echo "$response" | jq -r ".[] | select(.projectId == \"$projectId\") | .environments | .[] | .compose[] | select(. != null) | \"ID: \(.composeId)\n  Name: \(.name)\n  Type: compose\n  Project: \(.projectId)\n  Status: \(.applicationStatus // \"N/A\")\n  Environment: \(.environmentId)\"" 2>/dev/null || true
        ;;
    get)
        if [ -z "$2" ]; then
            log_error "Usage: dokploy app get <application-id>"
            exit 1
        fi
        log_info "Fetching application $2..."
        local response=$(api_request "GET" "/application.byId?applicationId=$2")
        echo "$response" | jq '.' 2>/dev/null || log_error "Failed to fetch application"
        ;;
    create)
        local projectId=""
        local name=""
        local type="docker"
        local image=""
        local gitSource=""
        local env=""

        shift
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --project)
                    projectId="$2"
                    shift 2
                    ;;
                --name)
                    name="$2"
                    shift 2
                    ;;
                --type)
                    type="$2"
                    shift 2
                    ;;
                --image)
                    image="$2"
                    shift 2
                    ;;
                --env)
                    env="$2"
                    shift 2
                    ;;
                *)
                    log_error "Unknown option: $1"
                    exit 1
                    ;;
            esac
        done

        if [ -z "$projectId" ] || [ -z "$name" ]; then
            log_error "Usage: dokploy app create --project <id> --name <name> [--type <type>] [--image <image>] [--env \"KEY=VALUE\"]"
            exit 1
        fi

        # Build JSON based on type
        local data=$(jq -n \
            --arg projectId "$projectId" \
            --arg name "$name" \
            --arg type "$type" \
            --arg image "$image" \
            --arg env "$env" \
            '{
                projectId: $projectId,
                name: $name,
                type: $type,
                env: ($env | if . != "" then split(";") | map(split("=") | {(.[0]): .[1]}) else {} end)
            }')

        if [ "$type" == "docker" ] && [ -n "$image" ]; then
            data=$(echo "$data" | jq --arg image "$image" '. + {image: $image}')
        fi

        log_info "Creating application '$name'..."
        local response=$(api_request "POST" "/application.create" "$data")
        local appId=$(echo "$response" | jq -r '.applicationId')

        if [ -n "$appId" ] && [ "$appId" != "null" ]; then
            log_success "Application created with ID: $appId"
        else
            log_error "Failed to create application"
            echo "$response" | jq '.' 2>/dev/null || echo "$response"
            exit 1
        fi
        ;;
    deploy)
        if [ -z "$2" ]; then
            log_error "Usage: dokploy app deploy <application-id>"
            exit 1
        fi
        log_info "Triggering deployment for application $2..."
        local response=$(api_request "POST" "/application.deploy?applicationId=$2")
        local deploymentId=$(echo "$response" | jq -r '.deploymentId')

        if [ -n "$deploymentId" ] && [ "$deploymentId" != "null" ]; then
            log_success "Deployment started with ID: $deploymentId"
            log_info "Check status with: dokploy app deployments $2"
        else
            log_error "Failed to trigger deployment"
            echo "$response"
            exit 1
        fi
        ;;
    deployments)
        if [ -z "$2" ]; then
            log_error "Usage: dokploy app deployments <application-id>"
            exit 1
        fi
        log_info "Fetching deployments for application $2..."
        local response=$(api_request "GET" "/deployment.all?applicationId=$2")
        echo "$response" | jq -r '.[] | "ID: \(.deploymentId)\n  Status: \(.status)\n  Created: \(.createdAt)\n  Description: \(.description // "N/A")\n"' 2>/dev/null || log_error "Failed to fetch deployments"
        ;;
    logs)
        local appId=""
        local deploymentId=""

        shift
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --deployment)
                    deploymentId="$2"
                    shift 2
                    ;;
                *)
                    appId="$1"
                    shift
                    ;;
            esac
        done

        if [ -z "$appId" ] || [ -z "$deploymentId" ]; then
            log_error "Usage: dokploy app logs <app-id> --deployment <deployment-id>"
            exit 1
        fi

        log_info "Fetching logs for deployment $deploymentId..."
        local response=$(api_request "GET" "/deployment.logs?deploymentId=$deploymentId")
        echo "$response" | jq '.' 2>/dev/null || log_error "Failed to fetch logs"
        ;;
    update)
        if [ -z "$2" ]; then
            log_error "Usage: dokploy app update <application-id> [--name <name>] [--env \"KEY=VALUE\"]"
            exit 1
        fi

        local appId="$2"
        local name=""
        local env=""

        shift 2
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --name)
                    name="$2"
                    shift 2
                    ;;
                --env)
                    env="$2"
                    shift 2
                    ;;
                *)
                    ;;
            esac
        done

        local data=$(jq -n \
            --arg name "$name" \
            --arg env "$env" \
            '{}')

        if [ -n "$name" ]; then
            data=$(echo "$data" | jq --arg name "$name" '. + {name: $name}')
        fi

        if [ -n "$env" ]; then
            data=$(echo "$data" | jq --arg env "$env" '. + {env: ($env | split(";") | map(split("=") | {(.[0]): .[1]}))}')
        fi

        log_info "Updating application $appId..."
        local response=$(api_request "PATCH" "/application.update?applicationId=$appId" "$data")

        if echo "$response" | jq -e 'true' > /dev/null 2>&1; then
            log_success "Application updated"
        else
            log_error "Failed to update application"
            echo "$response"
            exit 1
        fi
        ;;
    delete)
        if [ -z "$2" ]; then
            log_error "Usage: dokploy app delete <application-id>"
            exit 1
        fi

        log_warn "Are you sure you want to delete application $2?"
        read -p "Type 'yes' to confirm: " confirm

        if [ "$confirm" != "yes" ]; then
            log_info "Cancelled"
            exit 0
        fi

        log_info "Deleting application $2..."
        local response=$(api_request "DELETE" "/application.delete?applicationId=$2")

        if echo "$response" | jq -e 'true' > /dev/null 2>&1; then
            log_success "Application deleted"
        else
            log_error "Failed to delete application"
            echo "$response"
            exit 1
        fi
        ;;
    env)
        shift
        case "$1" in
            list)
                if [ -z "$2" ]; then
                    log_error "Usage: dokploy app env list <application-id>"
                    exit 1
                fi
                log_info "Fetching environment variables for $2..."
                local response=$(api_request "GET" "/application.byId?applicationId=$2")
                echo "$response" | jq -r '.env | to_entries[] | "\(.key)=\(.value)"' 2>/dev/null || log_error "Failed to fetch env vars"
                ;;
            set)
                shift
                local appId="$1"
                local key=""
                local value=""

                shift
                while [[ $# -gt 0 ]]; do
                    case "$1" in
                        --key)
                            key="$2"
                            shift 2
                            ;;
                        --value)
                            value="$2"
                            shift 2
                            ;;
                        *)
                            ;;
                    esac
                done

                if [ -z "$appId" ] || [ -z "$key" ]; then
                    log_error "Usage: dokploy app env set <app-id> --key <key> --value <value>"
                    exit 1
                fi

                # Get current env, update, and save
                local response=$(api_request "GET" "/application.byId?applicationId=$appId")
                local currentEnv=$(echo "$response" | jq -r '.env // {}')
                local newEnv=$(echo "$currentEnv" | jq --arg key "$key" --arg value "$value" '. + {($key): $value}')

                local data=$(jq -n --argjson env "$newEnv" '{env: $env}')

                log_info "Setting environment variable $key for $appId..."
                local updateResp=$(api_request "PATCH" "/application.update?applicationId=$appId" "$data")

                if echo "$updateResp" | jq -e 'true' > /dev/null 2>&1; then
                    log_success "Environment variable set"
                else
                    log_error "Failed to set environment variable"
                    echo "$updateResp"
                    exit 1
                fi
                ;;
            delete)
                shift
                local appId="$1"
                local key=""

                shift
                while [[ $# -gt 0 ]]; do
                    case "$1" in
                        --key)
                            key="$2"
                            shift 2
                            ;;
                        *)
                            ;;
                    esac
                done

                if [ -z "$appId" ] || [ -z "$key" ]; then
                    log_error "Usage: dokploy app env delete <app-id> --key <key>"
                    exit 1
                fi

                local response=$(api_request "GET" "/application.byId?applicationId=$appId")
                local currentEnv=$(echo "$response" | jq -r '.env // {}')
                local newEnv=$(echo "$currentEnv" | jq "del(.$key)")

                local data=$(jq -n --argjson env "$newEnv" '{env: $env}')

                log_info "Deleting environment variable $key from $appId..."
                local updateResp=$(api_request "PATCH" "/application.update?applicationId=$appId" "$data")

                if echo "$updateResp" | jq -e 'true' > /dev/null 2>&1; then
                    log_success "Environment variable deleted"
                else
                    log_error "Failed to delete environment variable"
                    echo "$updateResp"
                    exit 1
                fi
                ;;
            *)
                echo "Usage: dokploy app env <command>"
                echo ""
                echo "Commands:"
                echo "  list <app-id>              List environment variables"
                echo "  set <app-id> --key <k> --value <v>  Set environment variable"
                echo "  delete <app-id> --key <k>   Delete environment variable"
                ;;
        esac
        ;;
    *)
        echo "Usage: dokploy app <command>"
        echo ""
        echo "Commands:"
        echo "  list [--project <id>]      List applications"
        echo "  get <app-id>              Get application details"
        echo "  create --project <id> ...   Create application"
        echo "  deploy <app-id>            Trigger deployment"
        echo "  deployments <app-id>       List deployments"
        echo "  logs <app-id> --depl <id>  Get deployment logs"
        echo "  update <app-id> ...         Update application"
        echo "  delete <app-id>            Delete application"
        echo "  env                        Environment variable commands"
        ;;
esac
}

# Only run main if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
