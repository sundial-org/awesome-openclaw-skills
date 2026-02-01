#!/bin/bash
# Craft.do API Helper Script
# Usage: ./craft-api.sh <command> [args]

set -e

# Configuration
CRAFT_API_KEY="${CRAFT_API_KEY:-}"
CRAFT_ENDPOINT="${CRAFT_ENDPOINT:-}"

if [ -z "$CRAFT_API_KEY" ] || [ -z "$CRAFT_ENDPOINT" ]; then
  echo "Error: Set CRAFT_API_KEY and CRAFT_ENDPOINT environment variables"
  echo "Example:"
  echo "  export CRAFT_API_KEY='pdk_xxx'"
  echo "  export CRAFT_ENDPOINT='https://connect.craft.do/links/YOUR_LINK/api/v1'"
  exit 1
fi

# Helper function for API calls
craft_api() {
  local method="$1"
  local endpoint="$2"
  local data="$3"
  
  if [ -n "$data" ]; then
    curl -s -X "$method" \
      -H "Authorization: Bearer $CRAFT_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$CRAFT_ENDPOINT/$endpoint"
  else
    curl -s -X "$method" \
      -H "Authorization: Bearer $CRAFT_API_KEY" \
      "$CRAFT_ENDPOINT/$endpoint"
  fi
}

# Commands
case "${1:-help}" in
  # List all folders
  folders)
    craft_api GET "folders" | jq '.'
    ;;
  
  # List documents in a folder
  # Usage: ./craft-api.sh docs <folder_id>
  docs)
    if [ -z "$2" ]; then
      echo "Usage: $0 docs <folder_id>"
      exit 1
    fi
    craft_api GET "documents?folderId=$2" | jq '.'
    ;;
  
  # Create a document
  # Usage: ./craft-api.sh create-doc <title> <content> [location]
  create-doc)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: $0 create-doc <title> <content> [location]"
      exit 1
    fi
    LOCATION="${4:-unsorted}"
    craft_api POST "documents" "{
      \"documents\": [{
        \"title\": \"$2\",
        \"content\": [{\"textContent\": \"$3\"}],
        \"location\": \"$LOCATION\"
      }]
    }" | jq '.'
    ;;
  
  # Read document content
  # Usage: ./craft-api.sh read <doc_id>
  read)
    if [ -z "$2" ]; then
      echo "Usage: $0 read <doc_id>"
      exit 1
    fi
    craft_api GET "blocks?id=$2" | jq '.'
    ;;
  
  # List tasks
  # Usage: ./craft-api.sh tasks [scope]
  # scope: active (default), inbox, upcoming, logbook
  tasks)
    SCOPE="${2:-active}"
    craft_api GET "tasks?scope=$SCOPE" | jq '.'
    ;;
  
  # Create a task
  # Usage: ./craft-api.sh create-task <description> [location]
  # location: inbox (default), daily_notes
  create-task)
    if [ -z "$2" ]; then
      echo "Usage: $0 create-task <description> [location]"
      exit 1
    fi
    LOCATION_TYPE="${3:-inbox}"
    craft_api POST "tasks" "{
      \"tasks\": [{
        \"markdown\": \"$2\",
        \"location\": {\"type\": \"$LOCATION_TYPE\"},
        \"status\": \"active\"
      }]
    }" | jq '.'
    ;;
  
  # Mark task as complete
  # Usage: ./craft-api.sh complete-task <task_id> <description>
  complete-task)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: $0 complete-task <task_id> <description>"
      exit 1
    fi
    craft_api PUT "tasks" "{
      \"tasksToUpdate\": [{
        \"id\": \"$2\",
        \"markdown\": \"- [x] $3\"
      }]
    }" | jq '.'
    ;;
  
  # Move document
  # Usage: ./craft-api.sh move <doc_id> <destination>
  # destination: unsorted, templates, or folder_id
  move)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: $0 move <doc_id> <destination>"
      exit 1
    fi
    craft_api PUT "documents/move" "{
      \"documentIds\": [\"$2\"],
      \"destination\": {\"location\": \"$3\"}
    }" | jq '.'
    ;;
  
  # Help
  help)
    cat <<EOF
Craft.do API Helper

Environment variables:
  CRAFT_API_KEY     Your Craft API key (required)
  CRAFT_ENDPOINT    Your Craft API endpoint (required)

Commands:
  folders                                List all folders
  docs <folder_id>                       List documents in folder
  create-doc <title> <content> [loc]     Create document
  read <doc_id>                          Read document content
  tasks [scope]                          List tasks (active/inbox/upcoming/logbook)
  create-task <desc> [location]          Create task (inbox/daily_notes)
  complete-task <id> <desc>              Mark task complete
  move <doc_id> <destination>            Move document
  help                                   Show this help

Examples:
  $0 folders
  $0 tasks active
  $0 create-task "Write documentation" inbox
  $0 create-doc "Meeting Notes" "## Agenda\\n- Item 1" unsorted
  $0 complete-task <id> "Write documentation"

EOF
    ;;
  
  *)
    echo "Unknown command: $1"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
