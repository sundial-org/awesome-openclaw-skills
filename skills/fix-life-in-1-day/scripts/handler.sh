#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null || { echo '{"status":"error","message":"jq required"}'; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE="${HOME}/clawd"
COMMAND="${1:-start}"
shift || true

for arg in "$@"; do [[ -d "$arg" || "$arg" == */clawd ]] && WORKSPACE="$arg"; done

DATA_DIR="$WORKSPACE/memory/life-architect"
STATE_FILE="$DATA_DIR/state.json"
SESSIONS_DIR="$SKILL_DIR/references/sessions"
LOCK_FILE="$DATA_DIR/.lock"
mkdir -p "$DATA_DIR"

TITLES_EN=("" "The Anti-Vision Architect" "The Hidden Goal Decoder" "The Identity Construction Tracer" "The Lifestyle-Outcome Alignment Auditor" "The Dissonance Engine" "The Cybernetic Debugger" "The Ego Stage Navigator" "The Game Architecture Engineer" "The Conditioning Excavator" "The One-Day Reset Architect")
TITLES_RU=("" "Архитектор Анти-Видения" "Декодер Скрытых Целей" "Трассировщик Идентичности" "Аудитор Образа Жизни" "Двигатель Диссонанса" "Кибернетический Отладчик" "Навигатор Эго-Стадий" "Архитектор Жизни-Игры" "Раскопщик Обусловленности" "Архитектор Перезагрузки")

# File locking for concurrent access safety
acquire_lock() {
    exec 200>"$LOCK_FILE"
    flock -n 200 || { echo '{"status":"error","message":"Another operation in progress"}'; exit 1; }
}

release_lock() {
    flock -u 200 2>/dev/null || true
}

trap release_lock EXIT

init_state() {
    [[ -f "$STATE_FILE" ]] && return
    cat > "$STATE_FILE" << EOF
{"version":1,"lang":"${1:-en}","currentSession":1,"currentPhase":1,"startedAt":"$(date -Iseconds)","lastActivityAt":"$(date -Iseconds)","sessions":{"1":{"status":"not_started","phases":{}},"2":{"status":"not_started","phases":{}},"3":{"status":"not_started","phases":{}},"4":{"status":"not_started","phases":{}},"5":{"status":"not_started","phases":{}},"6":{"status":"not_started","phases":{}},"7":{"status":"not_started","phases":{}},"8":{"status":"not_started","phases":{}},"9":{"status":"not_started","phases":{}},"10":{"status":"not_started","phases":{}}}}
EOF
}

get() { jq -r ".$1" "$STATE_FILE"; }

upd() {
    local tmp=$(mktemp)
    jq "$1" "$STATE_FILE" > "$tmp" && mv "$tmp" "$STATE_FILE"
}

session_file() {
    local num=$(printf "%02d" "$1")
    local lang=$(jq -r '.lang' "$STATE_FILE")
    local f=$(ls "$SESSIONS_DIR/$lang/$num"-*.md 2>/dev/null | head -1)
    if [[ -n "$f" && -f "$f" ]]; then
        echo "$f"
    else
        ls "$SESSIONS_DIR/en/$num"-*.md 2>/dev/null | head -1
    fi
}

phase_count() { grep -cE "^## (Phase|Фаза) [0-9]+" "$1" 2>/dev/null || echo 0; }

# Extract phase content and clean up markdown headers for cleaner display
phase_content() {
    awk '/^## (Phase|Фаза) '"$2"'/{f=1;next}/^## (Phase|Фаза|Summary)/{if(f)exit}f' "$1" | \
    sed -E 's/^### (Introduction|Вступление)/\n/; s/^### (Questions|Вопросы)/\n**Questions:**\n/; s/^### (Question|Вопрос)$/\n/; s/^### (Transition|Переход)/\n---\n/; s/^### (Task|Задание)/\n**Task:**\n/; s/^### (Tasks|Задания)/\n**Tasks:**\n/; s/^### (Analysis|Анализ)/\n**Analysis:**\n/; s/^### (Information and Tasks|Информация и Задания)/\n/; s/^### .*/\n/'
}

title() { 
    local lang=$(jq -r '.lang' "$STATE_FILE")
    [[ "$lang" == "ru" ]] && echo "${TITLES_RU[$1]}" || echo "${TITLES_EN[$1]}"
}

# Write insight entry when session completes
write_insight() {
    local session="$1"
    local session_file="$DATA_DIR/session-$(printf "%02d" "$session").md"
    local insights_file="$DATA_DIR/insights.md"
    local lang=$(get lang)
    local t=$(title "$session")
    local ts=$(date '+%Y-%m-%d')
    
    if [[ "$lang" == "ru" ]]; then
        echo -e "\n### Сессия $session: $t\n*Завершена: $ts*\n" >> "$insights_file"
    else
        echo -e "\n### Session $session: $t\n*Completed: $ts*\n" >> "$insights_file"
    fi
    
    # Extract key responses (first 200 chars of each phase response)
    if [[ -f "$session_file" ]]; then
        local phase_num=1
        while IFS= read -r line; do
            if [[ "$line" =~ ^##\ Phase ]]; then
                phase_num="${line##*Phase }"
            elif [[ -n "$line" && ! "$line" =~ ^# && ! "$line" =~ ^--- && ! "$line" =~ ^Started ]]; then
                local snippet="${line:0:200}"
                [[ ${#line} -gt 200 ]] && snippet="${snippet}..."
                if [[ "$lang" == "ru" ]]; then
                    echo "- **Фаза $phase_num:** $snippet" >> "$insights_file"
                else
                    echo "- **Phase $phase_num:** $snippet" >> "$insights_file"
                fi
                ((phase_num++)) || true
            fi
        done < "$session_file"
    fi
    
    echo "" >> "$insights_file"
}

save_resp() {
    local f="$DATA_DIR/session-$(printf "%02d" "$1").md"
    local ts=$(date '+%Y-%m-%d %H:%M')
    [[ ! -f "$f" ]] && echo -e "# Session $1: $(title "$1")\nStarted: $ts\n" > "$f"
    echo -e "## Phase $2\n\n$3\n\n---\n" >> "$f"
    upd ".sessions.\"$1\".phases.\"$2\"={\"at\":\"$ts\"}"
    upd ".lastActivityAt=\"$(date -Iseconds)\""
}

advance() {
    local s=$(get currentSession)
    local p=$(get currentPhase)
    local f=$(session_file "$s")
    local t=$(phase_count "$f")
    local session_completed=false
    
    if [[ "$p" -lt "$t" ]]; then
        upd ".currentPhase=$((p+1))"
        upd ".sessions.\"$s\".status=\"in_progress\""
    else
        upd ".sessions.\"$s\".status=\"completed\""
        upd ".sessions.\"$s\".completedAt=\"$(date -Iseconds)\""
        session_completed=true
        write_insight "$s"
        if [[ "$s" -lt 10 ]]; then
            upd ".currentSession=$((s+1))"
            upd ".currentPhase=1"
        fi
    fi
    
    [[ "$session_completed" == "true" ]] && echo "true" || echo "false"
}

output() {
    local s=$(get currentSession)
    local p=$(get currentPhase)
    local l=$(get lang)
    local f=$(session_file "$s")
    local tp=$(phase_count "$f")
    local t=$(title "$s")
    local c=$(phase_content "$f" "$p")
    local done=$(jq '[.sessions[]|select(.status=="completed")]|length' "$STATE_FILE")
    local all_done="false"
    [[ "$done" -eq 10 ]] && all_done="true"
    
    jq -n --argjson s "$s" --argjson p "$p" --argjson tp "$tp" --arg t "$t" --arg l "$l" --arg c "$c" --argjson done "$done" --argjson allDone "$all_done" \
        '{status:"ok",session:$s,phase:$p,totalPhases:$tp,title:$t,lang:$l,content:$c,completedSessions:$done,allComplete:$allDone}'
}

output_with_completion() {
    local completed="$1"
    local s=$(get currentSession)
    local p=$(get currentPhase)
    local l=$(get lang)
    local f=$(session_file "$s")
    local tp=$(phase_count "$f")
    local t=$(title "$s")
    local c=$(phase_content "$f" "$p")
    local done=$(jq '[.sessions[]|select(.status=="completed")]|length' "$STATE_FILE")
    local all_done="false"
    [[ "$done" -eq 10 ]] && all_done="true"
    
    jq -n --argjson s "$s" --argjson p "$p" --argjson tp "$tp" --arg t "$t" --arg l "$l" --arg c "$c" --argjson done "$done" --argjson allDone "$all_done" --argjson sessionCompleted "$completed" \
        '{status:"ok",session:$s,phase:$p,totalPhases:$tp,title:$t,lang:$l,content:$c,completedSessions:$done,allComplete:$allDone,sessionJustCompleted:$sessionCompleted}'
}

do_status() {
    [[ ! -f "$STATE_FILE" ]] && echo '{"status":"not_initialized"}' && return
    local s=$(get currentSession)
    local l=$(get lang)
    local c=$(jq '[.sessions[]|select(.status=="completed")]|length' "$STATE_FILE")
    local ip=$(jq '[.sessions[]|select(.status=="in_progress")]|length' "$STATE_FILE")
    jq -n --argjson c "$c" --argjson ip "$ip" --argjson s "$s" --argjson p "$(get currentPhase)" \
        --arg n "$(title "$s")" --arg l "$l" \
        '{status:"ok",completed:$c,inProgress:$ip,total:10,percent:($c*10),currentSession:$s,currentPhase:$p,currentName:$n,lang:$l}'
}

# Session 10 cron reminder creation
create_reminders() {
    local wake_time="$1"
    local day="$2"
    local lang=$(get lang)
    
    # Parse wake time (HH:MM format)
    local hour="${wake_time%%:*}"
    local min="${wake_time##*:}"
    hour=$((10#$hour))  # Remove leading zeros
    min=$((10#$min))
    
    local reminders_file="$DATA_DIR/reminders-session10.json"
    
    # 8 interrupt times: +2h, +4h, +6h, +8h, +10h, +12h, +13h, +14h
    local offsets=(2 4 6 8 10 12 13 14)
    
    if [[ "$lang" == "ru" ]]; then
        local questions=(
            "Чего я избегаю прямо сейчас, делая то, что делаю?"
            "Если бы кто-то снимал последние 2 часа, что бы он заключил о том, чего я хочу от жизни?"
            "Я двигаюсь к жизни, которую ненавижу, или к жизни, которую хочу?"
            "Что самое важное, что я притворяюсь неважным?"
            "Что я сделал сегодня из защиты идентичности, а не из подлинного желания?"
            "Когда сегодня я чувствовал себя наиболее живым? Когда наиболее мёртвым?"
            "Что бы изменилось, если бы я перестал нуждаться в том, чтобы люди видели меня определённым образом?"
            "Где в жизни я обмениваю живость на безопасность?"
        )
    else
        local questions=(
            "What am I avoiding right now by doing what I'm doing?"
            "If someone filmed the last two hours, what would they conclude I want from my life?"
            "Am I moving toward the life I hate or the life I want?"
            "What's the most important thing I'm pretending isn't important?"
            "What did I do today out of identity protection rather than genuine desire?"
            "When did I feel most alive today? When did I feel most dead?"
            "What would change if I stopped needing people to see me a certain way?"
            "Where in my life am I trading aliveness for safety?"
        )
    fi
    
    echo "[" > "$reminders_file"
    local first=true
    
    for i in "${!offsets[@]}"; do
        local offset="${offsets[$i]}"
        local q="${questions[$i]}"
        local reminder_hour=$((hour + offset))
        local reminder_min=$min
        
        # Handle hour overflow
        if [[ $reminder_hour -ge 24 ]]; then
            reminder_hour=$((reminder_hour - 24))
        fi
        
        local time_str=$(printf "%02d:%02d" "$reminder_hour" "$reminder_min")
        
        [[ "$first" != "true" ]] && echo "," >> "$reminders_file"
        first=false
        
        cat >> "$reminders_file" << EOF
  {
    "time": "$time_str",
    "day": "$day",
    "question": "$q",
    "offset_hours": $offset
  }
EOF
    done
    
    echo "]" >> "$reminders_file"
    
    echo "$reminders_file"
}

acquire_lock

case "$COMMAND" in
    intro)
        # Check if user should see intro (fresh start)
        lang="${1:-en}"
        if [[ ! -f "$STATE_FILE" ]]; then
            is_new="true"
        else
            # Check if any progress made
            completed=$(jq '[.sessions[] | select(.status != "not_started")] | length' "$STATE_FILE")
            [[ "$completed" -eq 0 ]] && is_new="true" || is_new="false"
        fi
        jq -n --argjson isNew "$is_new" --arg lang "$lang" '{status:"ok",showIntro:$isNew,lang:$lang}' ;;
    start)
        lang="${1:-en}"
        init_state "$lang"
        [[ "$lang" == "ru" ]] && upd '.lang="ru"'
        output ;;
    status) do_status ;;
    session)
        t="${1:-1}"
        [[ "$t" -ge 1 && "$t" -le 10 ]] || { echo '{"status":"error","message":"1-10"}'; exit 1; }
        upd ".currentSession=$t" && upd ".currentPhase=1" && output ;;
    phase)
        t="${1:-1}"
        f=$(session_file "$(get currentSession)")
        max=$(phase_count "$f")
        [[ "$t" -ge 1 && "$t" -le "$max" ]] || { echo "{\"status\":\"error\",\"message\":\"1-$max\"}"; exit 1; }
        upd ".currentPhase=$t" && output ;;
    save)
        [[ -z "${1:-}" ]] && echo '{"status":"error","message":"Response required"}' && exit 1
        save_resp "$(get currentSession)" "$(get currentPhase)" "$1"
        completed=$(advance)
        output_with_completion "$completed" ;;
    skip)
        upd ".sessions.\"$(get currentSession)\".phases.\"$(get currentPhase)\"={\"skipped\":true}"
        completed=$(advance)
        output_with_completion "$completed" ;;
    reset)
        rm -f "$STATE_FILE" "$DATA_DIR"/session-*.md "$DATA_DIR/insights.md" "$DATA_DIR/final-document.md" "$DATA_DIR/reminders-session10.json" "$LOCK_FILE"
        init_state "en" && echo '{"status":"reset"}' ;;
    callback)
        case "${1:-}" in
            life:prev)
                p=$(get currentPhase)
                [[ "$p" -gt 1 ]] && upd ".currentPhase=$((p-1))"
                output ;;
            life:save) echo '{"status":"saved"}' ;;
            life:skip) release_lock; exec "$0" skip "$WORKSPACE" ;;
            life:continue) output ;;
            life:lang:en) upd '.lang="en"' && output ;;
            life:lang:ru) upd '.lang="ru"' && output ;;
            life:begin) release_lock; exec "$0" start en "$WORKSPACE" ;;
            life:begin:ru) release_lock; exec "$0" start ru "$WORKSPACE" ;;
            life:session:*) release_lock; exec "$0" session "${1##life:session:}" "$WORKSPACE" ;;
            *) echo '{"status":"error","message":"Unknown callback"}'; exit 1 ;;
        esac ;;
    lang)
        [[ "${1:-en}" =~ ^(en|ru)$ ]] || { echo '{"status":"error","message":"en or ru"}'; exit 1; }
        upd ".lang=\"$1\"" && output ;;
    reminders)
        # Create session 10 reminders: handler.sh reminders "07:00" "2026-01-27"
        wake="${1:-07:00}"
        day="${2:-$(date -d '+1 day' '+%Y-%m-%d')}"
        file=$(create_reminders "$wake" "$day")
        jq -n --arg f "$file" '{status:"ok",remindersFile:$f}' ;;
    insights)
        # Output current insights
        insights_file="$DATA_DIR/insights.md"
        if [[ -f "$insights_file" ]]; then
            content=$(cat "$insights_file")
            jq -n --arg c "$content" '{status:"ok",insights:$c}'
        else
            jq -n '{status:"ok",insights:""}'
        fi ;;
    *)
        echo '{"status":"error","message":"Unknown command"}'; exit 1 ;;
esac
