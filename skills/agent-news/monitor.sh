#!/bin/bash
# Agent News Monitor - AI agent development tracker
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_FILE="$HOME/.config/agent-news/state.json"
CACHE_DIR="$HOME/.config/agent-news/cache"
JSON_OUTPUT=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Keywords to match
AGENT_KEYWORDS="ai agent|autonomous agent|llm agent|tool use|function calling|agent memory|agentic|mcp protocol|langchain|autogpt|crewai|agent framework"

mkdir -p "$(dirname "$STATE_FILE")" "$CACHE_DIR"

usage() {
    cat << EOF
Agent News Monitor - Track AI agent developments

Usage: $(basename "$0") <command> [options]

Commands:
  digest              Generate daily digest (last 24h)
  trending            Show currently trending topics
  search <query>      Search recent content
  watch <topics>      Set watch topics (comma-separated)
  sources             List active sources
  
Options:
  --json              Output as JSON
  --quiet             Minimal output (for automation)
  --help              Show this help

Examples:
  $(basename "$0") digest
  $(basename "$0") search "memory systems"
  $(basename "$0") watch "autonomous agents,tool use"
EOF
}

# Fetch Hacker News top stories
fetch_hn() {
    local limit=${1:-30}
    echo -e "${BLUE}Fetching Hacker News...${NC}" >&2
    
    # Get top story IDs
    local ids=$(curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r ".[:$limit][]")
    
    local results=()
    for id in $ids; do
        local item=$(curl -s "https://hacker-news.firebaseio.com/v0/item/$id.json")
        local title=$(echo "$item" | jq -r '.title // empty')
        local url=$(echo "$item" | jq -r '.url // empty')
        local score=$(echo "$item" | jq -r '.score // 0')
        
        # Check if matches agent keywords (case insensitive)
        if echo "$title" | grep -iE "$AGENT_KEYWORDS" > /dev/null 2>&1; then
            results+=("{\"source\":\"hn\",\"title\":\"$title\",\"url\":\"$url\",\"score\":$score}")
        fi
    done
    
    echo "[${results[*]:-}]" | jq -s 'add // []'
}

# Fetch Reddit posts
fetch_reddit() {
    local subreddits=("LocalLLaMA" "MachineLearning" "artificial")
    echo -e "${BLUE}Fetching Reddit...${NC}" >&2
    
    local all_results="[]"
    for sub in "${subreddits[@]}"; do
        local posts=$(curl -s -A "AgentNewsMonitor/1.0" \
            "https://www.reddit.com/r/$sub/hot.json?limit=25" 2>/dev/null || echo '{"data":{"children":[]}}')
        
        local filtered=$(echo "$posts" | jq -r --arg keywords "$AGENT_KEYWORDS" '
            [.data.children[]?.data | 
             select(.title != null) |
             select(.title | test($keywords; "i")) |
             {source: "reddit", subreddit: .subreddit, title: .title, url: ("https://reddit.com" + .permalink), score: .score}
            ]' 2>/dev/null || echo '[]')
        
        all_results=$(echo "$all_results $filtered" | jq -s 'add')
    done
    
    echo "$all_results"
}

# Fetch arXiv papers
fetch_arxiv() {
    echo -e "${BLUE}Fetching arXiv...${NC}" >&2
    
    # Search for recent AI agent papers
    local query="all:ai+agent+OR+all:autonomous+agent+OR+all:llm+agent"
    local url="http://export.arxiv.org/api/query?search_query=$query&start=0&max_results=20&sortBy=submittedDate&sortOrder=descending"
    
    local response=$(curl -s "$url")
    
    # Parse XML to JSON (simplified)
    echo "$response" | grep -oP '<entry>.*?</entry>' | head -10 | while read -r entry; do
        local title=$(echo "$entry" | grep -oP '(?<=<title>).*?(?=</title>)' | head -1 | tr '\n' ' ')
        local link=$(echo "$entry" | grep -oP '(?<=<id>).*?(?=</id>)' | head -1)
        local summary=$(echo "$entry" | grep -oP '(?<=<summary>).*?(?=</summary>)' | head -1 | cut -c1-200)
        echo "{\"source\":\"arxiv\",\"title\":\"$title\",\"url\":\"$link\",\"summary\":\"$summary\"}"
    done | jq -s '.'
}

# Generate digest
generate_digest() {
    local quiet=${1:-false}
    
    if [ "$quiet" != "true" ]; then
        echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║${NC}  ${GREEN}Agent News Digest${NC} - $(date '+%Y-%m-%d %H:%M')                      ${CYAN}║${NC}"
        echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo
    fi
    
    # Fetch from all sources
    local hn_results=$(fetch_hn 50 2>/dev/null || echo '[]')
    local reddit_results=$(fetch_reddit 2>/dev/null || echo '[]')
    local arxiv_results=$(fetch_arxiv 2>/dev/null || echo '[]')
    
    # Combine and format
    local all_results=$(echo "$hn_results $reddit_results $arxiv_results" | jq -s 'add | sort_by(-.score // 0)')
    local count=$(echo "$all_results" | jq 'length')
    
    if [ "$JSON_OUTPUT" = true ]; then
        echo "$all_results"
        return
    fi
    
    echo -e "${YELLOW}Found $count relevant items${NC}\n"
    
    # Hacker News section
    echo -e "${GREEN}## Hacker News${NC}"
    echo "$hn_results" | jq -r '.[] | "- [\(.title)](\(.url)) (↑\(.score))"' 2>/dev/null || echo "  No HN results"
    echo
    
    # Reddit section  
    echo -e "${GREEN}## Reddit${NC}"
    echo "$reddit_results" | jq -r '.[] | "- r/\(.subreddit): [\(.title)](\(.url)) (↑\(.score))"' 2>/dev/null || echo "  No Reddit results"
    echo
    
    # arXiv section
    echo -e "${GREEN}## arXiv Papers${NC}"
    echo "$arxiv_results" | jq -r '.[] | "- [\(.title)](\(.url))"' 2>/dev/null || echo "  No arXiv results"
    echo
    
    # Update state
    echo "{\"last_check\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"items_found\": $count}" > "$STATE_FILE"
    
    echo -e "${GREEN}DIGEST_COMPLETE${NC}: $count items found"
}

# Search recent content
search_content() {
    local query="$1"
    echo -e "${CYAN}Searching for: $query${NC}\n"
    
    # Use Exa for semantic search if available
    if [ -n "${EXA_API_KEY:-}" ]; then
        echo -e "${BLUE}Searching via Exa...${NC}"
        local results=$(curl -s "https://api.exa.ai/search" \
            -H "x-api-key: $EXA_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"AI agent $query\", \"numResults\": 10, \"useAutoprompt\": true}" 2>/dev/null)
        
        if [ "$JSON_OUTPUT" = true ]; then
            echo "$results"
        else
            echo "$results" | jq -r '.results[]? | "- [\(.title)](\(.url))\n  \(.snippet // "" | .[0:150])...\n"' 2>/dev/null || echo "No results"
        fi
    else
        echo "EXA_API_KEY not set - using basic HN search"
        # Fallback to HN search
        local hn=$(curl -s "https://hn.algolia.com/api/v1/search?query=ai%20agent%20$query&tags=story" 2>/dev/null)
        echo "$hn" | jq -r '.hits[:10][] | "- [\(.title)](\(.url)) (↑\(.points))"' 2>/dev/null || echo "No results"
    fi
}

# Show trending
show_trending() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${GREEN}Trending in AI Agents${NC}                                       ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # Get HN top stories about agents
    local hn=$(fetch_hn 100 2>/dev/null | jq -r 'sort_by(-.score) | .[:5][] | "🔥 \(.title) (↑\(.score))"' 2>/dev/null)
    
    if [ -n "$hn" ]; then
        echo -e "${YELLOW}Hot on Hacker News:${NC}"
        echo "$hn"
    else
        echo "No trending agent stories on HN right now"
    fi
}

# Main
case "${1:-}" in
    digest)
        shift
        quiet=false
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --json) JSON_OUTPUT=true; shift ;;
                --quiet) quiet=true; shift ;;
                *) shift ;;
            esac
        done
        generate_digest "$quiet"
        ;;
    trending)
        [[ "${2:-}" == "--json" ]] && JSON_OUTPUT=true
        show_trending
        ;;
    search)
        [[ "${3:-}" == "--json" ]] && JSON_OUTPUT=true
        search_content "${2:-agent}"
        ;;
    watch)
        echo "${2:-}" > "$HOME/.config/agent-news/watch-topics.txt"
        echo "Watch topics set: ${2:-}"
        ;;
    sources)
        echo "Active sources: Hacker News, Reddit (LocalLLaMA, MachineLearning, artificial), arXiv"
        ;;
    --help|help)
        usage
        ;;
    *)
        usage
        exit 1
        ;;
esac
