#!/bin/bash
# Portainer CLI - Control Docker containers via Portainer API
# Author: Andy Steinberger (with help from his Clawdbot Owen the Frog 🐸)

set -e

# Load config from environment or .env
PORTAINER_URL="${PORTAINER_URL:-}"
PORTAINER_API_KEY="${PORTAINER_API_KEY:-}"

# Try to load from clawdbot .env if not set
if [[ -z "$PORTAINER_URL" || -z "$PORTAINER_API_KEY" ]]; then
    ENV_FILE="$HOME/.clawdbot/.env"
    if [[ -f "$ENV_FILE" ]]; then
        export $(grep -E "^PORTAINER_" "$ENV_FILE" | xargs)
    fi
fi

if [[ -z "$PORTAINER_URL" || -z "$PORTAINER_API_KEY" ]]; then
    echo "Error: PORTAINER_URL and PORTAINER_API_KEY must be set"
    echo "Add to ~/.clawdbot/.env or export as environment variables"
    exit 1
fi

API="$PORTAINER_URL/api"
AUTH_HEADER="X-API-Key: $PORTAINER_API_KEY"

# Helper function for API calls
api_get() {
    curl -s -H "$AUTH_HEADER" "$API$1"
}

api_post() {
    curl -s -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" "$API$1" -d "$2"
}

api_put() {
    curl -s -X PUT -H "$AUTH_HEADER" -H "Content-Type: application/json" "$API$1" -d "$2"
}

# Commands
case "$1" in
    status)
        api_get "/status" | jq -r '"Portainer v\(.Version)"'
        ;;
    
    endpoints|envs)
        api_get "/endpoints" | jq -r '.[] | "\(.Id): \(.Name) (\(.Type == 1 | if . then "local" else "remote" end)) - \(if .Status == 1 then "✓ online" else "✗ offline" end)"'
        ;;
    
    containers)
        ENDPOINT="${2:-4}"
        api_get "/endpoints/$ENDPOINT/docker/containers/json?all=true" | jq -r '.[] | "\(.Names[0] | ltrimstr("/"))\t\(.State)\t\(.Status)"' | column -t -s $'\t'
        ;;
    
    stacks)
        api_get "/stacks" | jq -r '.[] | "\(.Id): \(.Name) - \(if .Status == 1 then "✓ active" else "✗ inactive" end)"'
        ;;
    
    stack-info)
        STACK_ID="$2"
        if [[ -z "$STACK_ID" ]]; then
            echo "Usage: portainer.sh stack-info <stack-id>"
            exit 1
        fi
        api_get "/stacks/$STACK_ID" | jq '{Id, Name, Status, EndpointId, GitConfig: .GitConfig.URL, UpdateDate: (.UpdateDate | todate)}'
        ;;
    
    redeploy)
        STACK_ID="$2"
        if [[ -z "$STACK_ID" ]]; then
            echo "Usage: portainer.sh redeploy <stack-id> [endpoint-id]"
            exit 1
        fi
        
        # Get stack info for env vars and endpoint
        STACK_INFO=$(api_get "/stacks/$STACK_ID")
        ENDPOINT_ID=$(echo "$STACK_INFO" | jq -r '.EndpointId')
        ENV_VARS=$(echo "$STACK_INFO" | jq -c '.Env')
        GIT_CRED_ID=$(echo "$STACK_INFO" | jq -r '.GitConfig.Authentication.GitCredentialID // 0')
        
        PAYLOAD=$(jq -n \
            --argjson env "$ENV_VARS" \
            --argjson gitCredId "$GIT_CRED_ID" \
            '{env: $env, prune: false, pullImage: true, repositoryAuthentication: true, repositoryGitCredentialID: $gitCredId}')
        
        RESULT=$(api_put "/stacks/$STACK_ID/git/redeploy?endpointId=$ENDPOINT_ID" "$PAYLOAD")
        
        if echo "$RESULT" | jq -e '.Id' > /dev/null 2>&1; then
            STACK_NAME=$(echo "$RESULT" | jq -r '.Name')
            echo "✓ Stack '$STACK_NAME' redeployed successfully"
        else
            echo "✗ Redeploy failed:"
            echo "$RESULT" | jq -r '.message // .details // .'
            exit 1
        fi
        ;;
    
    start)
        ENDPOINT="${3:-4}"
        CONTAINER="$2"
        if [[ -z "$CONTAINER" ]]; then
            echo "Usage: portainer.sh start <container-name> [endpoint-id]"
            exit 1
        fi
        # Get container ID
        CONTAINER_ID=$(api_get "/endpoints/$ENDPOINT/docker/containers/json?all=true" | jq -r ".[] | select(.Names[0] == \"/$CONTAINER\") | .Id")
        if [[ -z "$CONTAINER_ID" ]]; then
            echo "✗ Container '$CONTAINER' not found"
            exit 1
        fi
        api_post "/endpoints/$ENDPOINT/docker/containers/$CONTAINER_ID/start" "{}" > /dev/null
        echo "✓ Container '$CONTAINER' started"
        ;;
    
    stop)
        ENDPOINT="${3:-4}"
        CONTAINER="$2"
        if [[ -z "$CONTAINER" ]]; then
            echo "Usage: portainer.sh stop <container-name> [endpoint-id]"
            exit 1
        fi
        CONTAINER_ID=$(api_get "/endpoints/$ENDPOINT/docker/containers/json?all=true" | jq -r ".[] | select(.Names[0] == \"/$CONTAINER\") | .Id")
        if [[ -z "$CONTAINER_ID" ]]; then
            echo "✗ Container '$CONTAINER' not found"
            exit 1
        fi
        api_post "/endpoints/$ENDPOINT/docker/containers/$CONTAINER_ID/stop" "{}" > /dev/null
        echo "✓ Container '$CONTAINER' stopped"
        ;;
    
    restart)
        ENDPOINT="${3:-4}"
        CONTAINER="$2"
        if [[ -z "$CONTAINER" ]]; then
            echo "Usage: portainer.sh restart <container-name> [endpoint-id]"
            exit 1
        fi
        CONTAINER_ID=$(api_get "/endpoints/$ENDPOINT/docker/containers/json?all=true" | jq -r ".[] | select(.Names[0] == \"/$CONTAINER\") | .Id")
        if [[ -z "$CONTAINER_ID" ]]; then
            echo "✗ Container '$CONTAINER' not found"
            exit 1
        fi
        api_post "/endpoints/$ENDPOINT/docker/containers/$CONTAINER_ID/restart" "{}" > /dev/null
        echo "✓ Container '$CONTAINER' restarted"
        ;;
    
    logs)
        ENDPOINT="${3:-4}"
        CONTAINER="$2"
        TAIL="${4:-100}"
        if [[ -z "$CONTAINER" ]]; then
            echo "Usage: portainer.sh logs <container-name> [endpoint-id] [tail-lines]"
            exit 1
        fi
        CONTAINER_ID=$(api_get "/endpoints/$ENDPOINT/docker/containers/json?all=true" | jq -r ".[] | select(.Names[0] == \"/$CONTAINER\") | .Id")
        if [[ -z "$CONTAINER_ID" ]]; then
            echo "✗ Container '$CONTAINER' not found"
            exit 1
        fi
        curl -s -H "$AUTH_HEADER" "$API/endpoints/$ENDPOINT/docker/containers/$CONTAINER_ID/logs?stdout=true&stderr=true&tail=$TAIL" | strings
        ;;
    
    *)
        echo "Portainer CLI - Control Docker via Portainer API"
        echo ""
        echo "Usage: portainer.sh <command> [args]"
        echo ""
        echo "Commands:"
        echo "  status                    Show Portainer version"
        echo "  endpoints                 List all environments"
        echo "  containers [endpoint]     List containers (default endpoint: 4)"
        echo "  stacks                    List all stacks"
        echo "  stack-info <id>           Show stack details"
        echo "  redeploy <stack-id>       Pull and redeploy a stack"
        echo "  start <container>         Start a container"
        echo "  stop <container>          Stop a container"
        echo "  restart <container>       Restart a container"
        echo "  logs <container> [ep] [n] Show container logs (last n lines)"
        echo ""
        echo "Environment:"
        echo "  PORTAINER_URL             Portainer server URL"
        echo "  PORTAINER_API_KEY         API access token"
        ;;
esac
