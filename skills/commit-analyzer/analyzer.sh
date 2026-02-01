#!/bin/bash
# Commit Analyzer - Git activity health monitor
# Built from autonomous week learnings

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

COMMAND=${1:-help}
PARAM=${2:-7}
JSON_MODE=""
[[ "${*}" == *"--json"* ]] && JSON_MODE="true"

# Health thresholds
HEALTHY_CPH=3      # commits per hour
WARNING_CPH=1
HEALTHY_LEARNING=30  # percent
MAX_HEALTHY_GAP=3    # hours
MAX_WARNING_GAP=6

show_help() {
    cat << 'EOF'
📊 Commit Analyzer - Git Health Monitor

USAGE:
    analyzer.sh <command> [param] [--json]

COMMANDS:
    health              Quick health check (last 24h)
    report [days]       Full analysis report (default: 7)
    hourly [days]       Commits by hour of day
    categories [days]   Commits by prefix/category
    waiting [hours]     Detect idle periods (default: 48)
    help                Show this help

OPTIONS:
    --json              Output in JSON format

EXAMPLES:
    analyzer.sh health
    analyzer.sh report 3
    analyzer.sh categories 7 --json
EOF
}

get_commits() {
    local days=$1
    git log --since="$days days ago" --format="%H|%ai|%s" 2>/dev/null || echo ""
}

count_commits() {
    local days=$1
    git log --since="$days days ago" --oneline 2>/dev/null | wc -l | tr -d ' '
}

health_check() {
    local commits_24h=$(count_commits 1)
    local hours=24
    local cph=$(echo "scale=2; $commits_24h / $hours" | bc 2>/dev/null || echo "0")
    
    # Get learning commits
    local learning=$(git log --since="1 day ago" --oneline 2>/dev/null | grep -ci "learning\|meta\|insight" || echo "0")
    local learning_pct=0
    [[ $commits_24h -gt 0 ]] && learning_pct=$(echo "scale=0; $learning * 100 / $commits_24h" | bc 2>/dev/null || echo "0")
    
    # Find largest gap (simplified - check hourly buckets)
    local max_gap=0
    local last_hour=""
    while read -r line; do
        [[ -z "$line" ]] && continue
        local hour=$(echo "$line" | cut -d'|' -f2 | cut -d' ' -f2 | cut -d':' -f1)
        if [[ -n "$last_hour" ]]; then
            local diff=$((10#$hour - 10#$last_hour))
            [[ $diff -lt 0 ]] && diff=$((24 + diff))
            [[ $diff -gt $max_gap ]] && max_gap=$diff
        fi
        last_hour=$hour
    done < <(git log --since="1 day ago" --format="%H|%ai" --reverse 2>/dev/null)
    
    # Determine status
    local status="HEALTHY"
    local status_icon="✅"
    local cph_int=${cph%.*}
    [[ -z "$cph_int" ]] && cph_int=0
    
    if [[ $cph_int -lt $WARNING_CPH ]]; then
        status="CRITICAL"
        status_icon="🔴"
    elif [[ $cph_int -lt $HEALTHY_CPH ]]; then
        status="WARNING"
        status_icon="⚠️"
    fi
    
    if [[ -n "$JSON_MODE" ]]; then
        cat << EOF
{
  "commits_24h": $commits_24h,
  "commits_per_hour": $cph,
  "status": "$status",
  "learning_commits": $learning,
  "learning_percent": $learning_pct,
  "max_gap_hours": $max_gap
}
EOF
    else
        echo ""
        echo -e "${BOLD}📊 Git Health Report (last 24h)${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "Total commits: ${BOLD}$commits_24h${NC}"
        echo -e "Commits/hour: ${BOLD}$cph${NC}"
        echo -e "Status: $status_icon ${BOLD}$status${NC}"
        echo ""
        if [[ $max_gap -gt 0 ]]; then
            echo "Largest gap: ~${max_gap}h"
        fi
        echo -e "Learning commits: $learning (${learning_pct}%)"
        echo ""
        
        if [[ "$status" == "CRITICAL" ]]; then
            echo -e "${RED}⚡ Action: Check for blockers or waiting mode${NC}"
        elif [[ "$status" == "WARNING" ]]; then
            echo -e "${YELLOW}💡 Recommendation: Review task queue${NC}"
        else
            echo -e "${GREEN}👍 Autonomous operation healthy${NC}"
        fi
    fi
}

full_report() {
    local days=$PARAM
    local total=$(count_commits $days)
    local hours=$((days * 24))
    local cph=$(echo "scale=2; $total / $hours" | bc 2>/dev/null || echo "0")
    local daily_avg=$(echo "scale=1; $total / $days" | bc 2>/dev/null || echo "0")
    
    echo ""
    echo -e "${BOLD}📊 Full Git Analysis (last ${days} days)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BOLD}Overview${NC}"
    echo "  Total commits: $total"
    echo "  Daily average: $daily_avg"
    echo "  Commits/hour: $cph"
    echo ""
    
    echo -e "${BOLD}Daily Breakdown${NC}"
    for i in $(seq 0 $((days - 1))); do
        local date=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "$i days ago" +%Y-%m-%d 2>/dev/null)
        local count=$(git log --since="$date 00:00:00" --until="$date 23:59:59" --oneline 2>/dev/null | wc -l | tr -d ' ')
        local bar=""
        for j in $(seq 1 $((count / 3))); do bar+="█"; done
        [[ $count -gt 0 && ${#bar} -eq 0 ]] && bar="▏"
        echo "  $date: $count $bar"
    done
    echo ""
    
    echo -e "${BOLD}Category Distribution${NC}"
    show_categories $days "  "
    echo ""
    
    # Health assessment
    local cph_int=${cph%.*}
    [[ -z "$cph_int" ]] && cph_int=0
    
    echo -e "${BOLD}Health Assessment${NC}"
    if [[ $cph_int -ge $HEALTHY_CPH ]]; then
        echo -e "  ${GREEN}✅ Autonomous operation healthy${NC}"
    elif [[ $cph_int -ge $WARNING_CPH ]]; then
        echo -e "  ${YELLOW}⚠️ Below optimal velocity${NC}"
    else
        echo -e "  ${RED}🔴 Low activity - check for blockers${NC}"
    fi
}

show_hourly() {
    local days=$PARAM
    echo ""
    echo -e "${BOLD}📊 Commits by Hour (last ${days} days)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    for hour in $(seq 0 23); do
        local h=$(printf "%02d" $hour)
        local count=0
        while read -r line; do
            local commit_hour=$(echo "$line" | grep -o " ${h}:" | wc -l | tr -d ' ')
            count=$((count + commit_hour))
        done < <(git log --since="$days days ago" --format="%ai" 2>/dev/null)
        
        # Simplified count
        count=$(git log --since="$days days ago" --format="%ai" 2>/dev/null | grep " ${h}:" | wc -l | tr -d ' ')
        
        local bar=""
        for j in $(seq 1 $((count / 2))); do bar+="█"; done
        [[ $count -gt 0 && ${#bar} -eq 0 ]] && bar="▏"
        printf "  %s:00  %3d  %s\n" "$h" "$count" "$bar"
    done
}

show_categories() {
    local days=${1:-$PARAM}
    local prefix=${2:-""}
    
    if [[ -z "$prefix" ]]; then
        echo ""
        echo -e "${BOLD}📊 Commit Categories (last ${days} days)${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
    
    local total=$(count_commits $days)
    
    # Common prefixes
    local categories=("Queue" "Learning" "Docs" "Skills" "Fix" "Test" "Refactor" "Feat" "Chore")
    local other=$total
    
    for cat in "${categories[@]}"; do
        local count=$(git log --since="$days days ago" --oneline 2>/dev/null | grep -ci "^[a-f0-9]* ${cat}:" || echo "0")
        count=$(echo "$count" | tr -d '\n')
        if [[ $count -gt 0 ]]; then
            local pct=0
            [[ $total -gt 0 ]] && pct=$(echo "scale=0; $count * 100 / $total" | bc 2>/dev/null | tr -d '\n' || echo "0")
            printf "${prefix}%-12s %3d (%2d%%)\n" "${cat}:" "$count" "$pct"
            other=$((other - count))
        fi
    done
    
    if [[ $other -gt 0 ]]; then
        local pct=0
        [[ $total -gt 0 ]] && pct=$(echo "scale=0; $other * 100 / $total" | bc 2>/dev/null | tr -d '\n' || echo "0")
        printf "${prefix}%-12s %3d (%2d%%)\n" "Other:" "$other" "$pct"
    fi
    
    [[ -z "$prefix" ]] && echo "" && echo "Total: $total commits"
}

detect_waiting() {
    local hours=${PARAM:-48}
    echo ""
    echo -e "${BOLD}📊 Idle Period Detection (last ${hours}h)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    local idle_periods=0
    local timestamps=($(git log --since="$hours hours ago" --format="%at" --reverse 2>/dev/null))
    
    if [[ ${#timestamps[@]} -lt 2 ]]; then
        echo "Not enough commits to analyze gaps"
        return
    fi
    
    local prev=${timestamps[0]}
    for ts in "${timestamps[@]:1}"; do
        local gap=$(( (ts - prev) / 3600 ))
        if [[ $gap -ge $MAX_HEALTHY_GAP ]]; then
            local prev_time=$(date -r $prev "+%Y-%m-%d %H:%M" 2>/dev/null || date -d "@$prev" "+%Y-%m-%d %H:%M" 2>/dev/null)
            local curr_time=$(date -r $ts "+%Y-%m-%d %H:%M" 2>/dev/null || date -d "@$ts" "+%Y-%m-%d %H:%M" 2>/dev/null)
            
            if [[ $gap -ge $MAX_WARNING_GAP ]]; then
                echo -e "  ${RED}🔴 ${gap}h gap${NC}: $prev_time → $curr_time"
            else
                echo -e "  ${YELLOW}⚠️ ${gap}h gap${NC}: $prev_time → $curr_time"
            fi
            idle_periods=$((idle_periods + 1))
        fi
        prev=$ts
    done
    
    if [[ $idle_periods -eq 0 ]]; then
        echo -e "  ${GREEN}✅ No significant idle periods detected${NC}"
    else
        echo ""
        echo "Found $idle_periods idle period(s) >= ${MAX_HEALTHY_GAP}h"
    fi
}

# Main
case $COMMAND in
    health)
        health_check
        ;;
    report)
        full_report
        ;;
    hourly)
        show_hourly
        ;;
    categories)
        show_categories
        ;;
    waiting)
        detect_waiting
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
