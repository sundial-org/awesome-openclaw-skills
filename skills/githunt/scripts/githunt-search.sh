#!/bin/bash
# GitHunt Streaming Search - Find GitHub developers
# Usage: githunt-search.sh <location> [role] [skills]
#
# Roles: frontend, backend, fullstack, mobile, devops, data, security, blockchain, ai, gaming

API_URL="${GITHUNT_API_URL:-https://api.githunt.ai/v1}"

location="${1:-}"
role="${2:-}"
skills="${3:-}"

if [ -z "$location" ]; then
  echo "🔍 GitHunt - Find GitHub Developers"
  echo ""
  echo "Usage: githunt-search.sh <location> [role] [skills]"
  echo ""
  echo "Roles: frontend, backend, fullstack, mobile, devops, data, security, blockchain, ai, gaming"
  echo ""
  echo "Examples:"
  echo "  githunt-search.sh berlin frontend"
  echo "  githunt-search.sh 'san francisco' backend"
  echo "  githunt-search.sh london ai 'pytorch,transformers'"
  echo ""
  echo "Free preview shows top matches."
  echo "Full report: https://githunt.ai (\$19)"
  exit 1
fi

# Build JSON payload properly
payload="{\"location\": \"$location\", \"maxUsers\": 100"

if [ -n "$role" ]; then
  payload="$payload, \"role\": \"$role\""
fi

if [ -n "$skills" ]; then
  skills_json=$(echo "$skills" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')
  payload="$payload, \"skills\": $skills_json"
fi

payload="$payload}"

echo "🔍 Searching for developers in '$location'..."
[ -n "$role" ] && echo "   Role: $role"
[ -n "$skills" ] && echo "   Skills: $skills"
echo ""

# Make streaming request and parse SSE
curl -s -N -X POST "$API_URL/rank/users/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "User-Agent: OpenClaw/1.0 (githunt-skill)" \
  -d "$payload" 2>/dev/null | while IFS= read -r line; do
  
  # Skip empty lines and "data: " prefix
  if [[ "$line" == data:* ]]; then
    json="${line#data: }"
    
    type=$(echo "$json" | jq -r '.type // empty' 2>/dev/null)
    
    case "$type" in
      "user")
        echo "$json" | jq -r '
          .data | 
          "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
          "👤 \(.name // .login) (@\(.login))",
          "   📍 \(.location // "Unknown") | 🏢 \(.company // "—")",
          "   💼 Hireable: \(if .isHireable then "Yes ✓" else "No" end) | 👥 \(.followers // 0) followers",
          "",
          "   ⭐ SCORE: \(.score // 0)/100",
          "      Profile: \(.profile_score // 0) | Tech: \(.tech_stack_score // 0) | Activity: \(.activity_score // 0)",
          "      Matched: \(.matching_keywords // "—")",
          "",
          "   📊 COMMIT STATS:",
          "      Commits: \(.total_commits // 0) | PRs: \(.total_prs // 0) | Issues: \(.total_issues // 0)",
          "      Frequency: \(.commit_frequency_label // "Unknown") (\(.commits_per_month // 0)/month)",
          "      Message Quality: \(.commit_message_quality_label // "Unknown") (\(.semantic_commit_percentage // 0)% semantic)",
          "",
          "   📦 TOP REPOS:",
          ((.topRepositories // [])[:3] | to_entries | .[] |
            "      \(.value.name) ⭐\(.value.stars // 0) 🍴\(.value.forks // 0) [\(.value.language // "—")]"
          ),
          "",
          "   🔗 https://github.com/\(.login)",
          "   📧 \(.email // "—") | 🐦 \(if .twitter_username and .twitter_username != "" then "@" + .twitter_username else "—" end)",
          ""
        ' 2>/dev/null
        ;;
      "complete")
        total=$(echo "$json" | jq -r '.data.totalCount // 0' 2>/dev/null)
        preview=$(echo "$json" | jq -r '.data.previewLimit // 10' 2>/dev/null)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📊 Found ~$total total matches (showing top $preview)"
        echo ""
        echo "💰 Want ALL candidates with full contact info?"
        echo "   Get the full report for \$19: https://githunt.ai"
        echo ""
        ;;
      "error")
        msg=$(echo "$json" | jq -r '.data.message // "Unknown error"' 2>/dev/null)
        echo "❌ Error: $msg"
        ;;
    esac
  fi
done
