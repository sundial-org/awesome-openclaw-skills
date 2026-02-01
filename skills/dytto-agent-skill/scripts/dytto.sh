#!/usr/bin/env bash
# Dytto Context CLI — personal context API for AI agents
# Usage: dytto.sh <command> [args...]
set -euo pipefail

# Config: env vars > config file > defaults
CONFIG_FILE="${DYTTO_CONFIG:-${HOME}/.config/dytto/config.json}"

if [[ -f "$CONFIG_FILE" ]]; then
    _cfg() { python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('$1',''))" 2>/dev/null; }
    API_BASE="${DYTTO_API_BASE_URL:-$(_cfg api_base)}"
    USER_EMAIL="${DYTTO_EMAIL:-$(_cfg email)}"
    USER_PASSWORD="${DYTTO_PASSWORD:-$(_cfg password)}"
else
    API_BASE="${DYTTO_API_BASE_URL:-https://dytto.onrender.com}"
    USER_EMAIL="${DYTTO_EMAIL:-}"
    USER_PASSWORD="${DYTTO_PASSWORD:-}"
fi

TOKEN_CACHE="/tmp/.dytto-token-cache"

check_config() {
    local missing=()
    [[ -z "$USER_EMAIL" ]] && missing+=("DYTTO_EMAIL")
    [[ -z "$USER_PASSWORD" ]] && missing+=("DYTTO_PASSWORD")
    if (( ${#missing[@]} > 0 )); then
        echo "ERROR: Missing Dytto credentials." >&2
        echo "Set env vars or create ${CONFIG_FILE}:" >&2
        printf '  %s\n' "${missing[@]}" >&2
        echo "" >&2
        echo "Config file format:" >&2
        echo '  {"email":"your@email.com","password":"your-password"}' >&2
        echo "" >&2
        echo "Optional: set DYTTO_API_BASE_URL (default: https://dytto.onrender.com)" >&2
        exit 1
    fi
}

get_token() {
    if [[ -f "$TOKEN_CACHE" ]]; then
        local cached_age=$(( $(date +%s) - $(stat -c %Y "$TOKEN_CACHE" 2>/dev/null || echo 0) ))
        if (( cached_age < 3000 )); then
            cat "$TOKEN_CACHE"
            return
        fi
    fi
    check_config
    local response
    response=$(curl -s --max-time 60 -X POST "${API_BASE}/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"${USER_EMAIL}\",\"password\":\"${USER_PASSWORD}\"}")
    local token
    token=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
    if [[ -n "$token" && "$token" != "None" ]]; then
        echo "$token" > "$TOKEN_CACHE"
        echo "$token"
    else
        echo "Login failed. Check your email/password. Response: $response" >&2
        exit 1
    fi
}

api_get() {
    local endpoint="$1"
    local token
    token=$(get_token)
    curl -s --max-time 60 -H "Authorization: Bearer ${token}" \
         -H "Content-Type: application/json" \
         "${API_BASE}${endpoint}"
}

api_post() {
    local endpoint="$1"
    local data="$2"
    local token
    token=$(get_token)
    curl -s --max-time 60 -X POST -H "Authorization: Bearer ${token}" \
         -H "Content-Type: application/json" \
         -d "$data" \
         "${API_BASE}${endpoint}"
}

urlencode() {
    python3 -c "import urllib.parse; print(urllib.parse.quote('$1'))"
}

CMD="${1:-help}"
shift || true

case "$CMD" in
    context)
        api_get "/api/context"
        ;;
    summary)
        api_get "/api/context/summary"
        ;;
    patterns)
        api_get "/api/context/patterns"
        ;;
    insights)
        api_get "/api/context/insights"
        ;;
    search)
        query="${1:?Usage: dytto.sh search <query>}"
        api_post "/api/context/search" "{\"query\":\"${query}\"}"
        ;;
    story)
        date="${1:?Usage: dytto.sh story <YYYY-MM-DD>}"
        api_get "/api/stories/${date}"
        ;;
    search-stories)
        query="${1:?Usage: dytto.sh search-stories <query>}"
        api_get "/api/stories/search?q=$(urlencode "$query")"
        ;;
    weather)
        lat="${1:?Usage: dytto.sh weather <lat> <lon>}"
        lon="${2:?Usage: dytto.sh weather <lat> <lon>}"
        api_get "/api/weather/current?latitude=${lat}&longitude=${lon}"
        ;;
    news)
        lat="${1:?Usage: dytto.sh news <lat> <lon> [location_name]}"
        lon="${2:?Usage: dytto.sh news <lat> <lon> [location_name]}"
        location="${3:-}"
        url="/api/news/context?latitude=${lat}&longitude=${lon}"
        [[ -n "$location" ]] && url="${url}&location=$(urlencode "$location")"
        api_get "$url"
        ;;
    store-fact)
        desc="${1:?Usage: dytto.sh store-fact <description> [category]}"
        category="${2:-personal_info}"
        api_post "/api/mcp/update-context" "{\"interaction_summary\":\"Personal fact (${category}): ${desc}\",\"source_system\":\"agent\",\"discovered_insights\":[\"${desc}\"],\"behavioral_observations\":[],\"new_knowledge\":[]}"
        ;;
    observe)
        pattern="${1:?Usage: dytto.sh observe <pattern>}"
        api_post "/api/mcp/update-context" "{\"interaction_summary\":\"Behavioral observation: ${pattern}\",\"source_system\":\"agent\",\"discovered_insights\":[],\"behavioral_observations\":[\"${pattern}\"],\"new_knowledge\":[]}"
        ;;
    update)
        summary="${1:?Usage: dytto.sh update <summary> [insights_json] [concepts_json] [notes_json]}"
        insights="${2:-[]}"
        concepts="${3:-[]}"
        notes="${4:-[]}"
        api_post "/api/mcp/update-context" "{\"interaction_summary\":\"${summary}\",\"source_system\":\"agent\",\"discovered_insights\":${insights},\"behavioral_observations\":${notes},\"new_knowledge\":${concepts}}"
        ;;
    help|*)
        cat <<'EOF'
Dytto Context CLI — personal context API for AI agents

Usage: dytto.sh <command> [args...]

Read:
  context                      Full context profile (who is this person)
  summary                      Quick context summary
  patterns                     Behavioral patterns and routines
  insights                     Derived insights about the user
  search <query>               Semantic search across context
  story <YYYY-MM-DD>           Get journal/story for a date
  search-stories <query>       Search across stories

Write:
  store-fact <desc> [category] Store a learned fact
  observe <pattern>            Record behavioral observation
  update <summary> [insights] [concepts] [notes]  Comprehensive update

External:
  weather <lat> <lon>          Weather context
  news <lat> <lon> [name]      News context

Config: set env vars or create ~/.config/dytto/config.json
  DYTTO_EMAIL       Your Dytto account email
  DYTTO_PASSWORD    Your Dytto account password
  DYTTO_API_BASE_URL  (optional, default: https://dytto.onrender.com)
EOF
        ;;
esac
