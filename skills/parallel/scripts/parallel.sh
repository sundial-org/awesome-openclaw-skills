#!/bin/bash
# Parallel.ai Task API wrapper
# Usage: ./parallel.sh <command> [args]

set -e

API_KEY="${PARALLEL_API_KEY:-y2s_m4er5i6-5qCikOLUtmnkvOYRU24eDphq_jg1}"
BASE_URL="https://api.parallel.ai/v1"
MAX_WAIT="${PARALLEL_MAX_WAIT:-120}"

# Submit task and poll for result
run_task() {
  local input="$1"
  local processor="${2:-base}"
  
  # Submit
  local response=$(curl -s -X POST "$BASE_URL/tasks/runs" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"processor\": \"$processor\", \"input\": \"$input\"}")
  
  local run_id=$(echo "$response" | jq -r '.run_id // empty')
  
  if [ -z "$run_id" ]; then
    echo "$response" | jq '.'
    return 1
  fi
  
  echo "⏳ Task: $run_id" >&2
  
  # Poll for completion
  local elapsed=0
  while [ $elapsed -lt $MAX_WAIT ]; do
    sleep 3
    elapsed=$((elapsed + 3))
    
    local status_response=$(curl -s -X GET "$BASE_URL/tasks/runs/$run_id" \
      -H "x-api-key: $API_KEY")
    
    local status=$(echo "$status_response" | jq -r '.status')
    local output=$(echo "$status_response" | jq -r '.output // empty')
    
    if [ "$status" = "completed" ]; then
      if [ -n "$output" ] && [ "$output" != "null" ]; then
        echo "$output"
      else
        echo "✅ Completed (no output in response)" >&2
        echo "$status_response" | jq '.'
      fi
      return 0
    elif [ "$status" = "failed" ] || [ "$status" = "error" ]; then
      echo "❌ Failed" >&2
      echo "$status_response" | jq '.'
      return 1
    fi
    
    printf "." >&2
  done
  
  echo "" >&2
  echo "⏰ Timeout. Run ID: $run_id" >&2
  return 1
}

command="${1:-help}"
shift || true

case "$command" in
  research)
    QUERY="$*"
    [ -z "$QUERY" ] && { echo "Usage: parallel.sh research <query>" >&2; exit 1; }
    run_task "$QUERY" "base"
    ;;
    
  company)
    COMPANY="$*"
    [ -z "$COMPANY" ] && { echo "Usage: parallel.sh company <name>" >&2; exit 1; }
    run_task "Research this company comprehensively: $COMPANY. Include: description, leadership, products, recent news, funding, competitors." "base"
    ;;
    
  person)
    PERSON="$*"
    [ -z "$PERSON" ] && { echo "Usage: parallel.sh person <name>" >&2; exit 1; }
    run_task "Research this person: $PERSON. Include: background, current role, achievements, recent news." "base"
    ;;
    
  status)
    RUN_ID="$1"
    [ -z "$RUN_ID" ] && { echo "Usage: parallel.sh status <run_id>" >&2; exit 1; }
    curl -s -X GET "$BASE_URL/tasks/runs/$RUN_ID" \
      -H "x-api-key: $API_KEY" | jq '.'
    ;;
    
  help|*)
    cat << 'EOF'
Parallel.ai Task API - Deep web research

Commands:
  research <query>     General research query
  company <name>       Company research  
  person <name>        Person research
  status <run_id>      Check task status

Examples:
  parallel.sh research "What are the latest developments in AI safety?"
  parallel.sh company "Anthropic"
  parallel.sh person "Dario Amodei"

Note: Search API requires separate product activation at platform.parallel.ai
EOF
    ;;
esac
