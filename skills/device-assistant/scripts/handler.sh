#!/usr/bin/env bash
# Device Assistant Handler
# Personal device manager with error lookup and troubleshooting
# Usage: handler.sh <command> [args...] <workspace>

set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo '{"status":"error","message":"jq required"}'; exit 1; }
command -v curl >/dev/null 2>&1 || { echo '{"status":"error","message":"curl required"}'; exit 1; }

CMD="${1:-status}"
shift || true

# Get workspace (always last argument)
WORKSPACE="${!#:-$(pwd)}"
DATA_DIR="$WORKSPACE/memory/device-assistant"
CACHE_DIR="$DATA_DIR/cache"

mkdir -p "$DATA_DIR" "$CACHE_DIR"

# Files
DEVICES_FILE="$DATA_DIR/devices.json"
HISTORY_FILE="$DATA_DIR/error-history.json"
MAINTENANCE_FILE="$DATA_DIR/maintenance-log.json"

# Initialize files
[[ -f "$DEVICES_FILE" ]] || echo '{"devices":[]}' > "$DEVICES_FILE"
[[ -f "$HISTORY_FILE" ]] || echo '{"entries":[]}' > "$HISTORY_FILE"
[[ -f "$MAINTENANCE_FILE" ]] || echo '{"entries":[]}' > "$MAINTENANCE_FILE"

# ============================================
# Helper Functions
# ============================================

generate_id() {
    local name="$1"
    local base
    base=$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr ' äöü' '-aou' | tr -cd 'a-z0-9-')
    local count
    count=$(jq --arg base "$base" '[.devices[] | select(.id | startswith($base))] | length' "$DEVICES_FILE")
    if [[ "$count" -gt 0 ]]; then
        echo "${base}-$((count + 1))"
    else
        echo "$base"
    fi
}

get_device() {
    local identifier="$1"
    # Search by id, name, or nickname (case-insensitive)
    jq -c --arg id "$identifier" '[.devices[] | select(.id == $id or (.name | ascii_downcase) == ($id | ascii_downcase) or (.nickname // "" | ascii_downcase) == ($id | ascii_downcase))][0] // empty' "$DEVICES_FILE"
}

get_device_id() {
    local identifier="$1"
    local device
    device=$(get_device "$identifier")
    echo "$device" | jq -r '.id // empty'
}

# Search web for error code
search_error_code() {
    local manufacturer="$1"
    local model="$2"
    local error_code="$3"
    
    # Build search query
    local query="${manufacturer} ${model} Fehler ${error_code} Lösung"
    local encoded_query
    encoded_query=$(echo -n "$query" | jq -sRr @uri)
    
    # Check cache first
    local cache_key
    cache_key=$(echo -n "${manufacturer}-${model}-${error_code}" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    local cache_file="$CACHE_DIR/error-${cache_key}.json"
    
    if [[ -f "$cache_file" ]]; then
        local cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || echo 0)))
        if [[ $cache_age -lt 604800 ]]; then  # 1 week cache
            cat "$cache_file"
            return 0
        fi
    fi
    
    # Return structured response with search suggestion
    local result
    result=$(jq -n \
        --arg manufacturer "$manufacturer" \
        --arg model "$model" \
        --arg code "$error_code" \
        --arg query "$query" \
        '{
            manufacturer: $manufacturer,
            model: $model,
            errorCode: $code,
            searchQuery: $query,
            searchUrl: ("https://www.google.com/search?q=" + ($query | @uri))
        }')
    
    echo "$result" > "$cache_file"
    echo "$result"
}

# Get known error codes for common manufacturers
get_known_error() {
    local manufacturer="${1,,}"
    local code="${2^^}"
    
    case "$manufacturer" in
        siemens|bosch|neff|constructa)
            case "$code" in
                E15) echo '{"meaning":"Wasserschutz aktiv","description":"Wasser in der Bodenwanne erkannt.","solution":["Gerät ausschalten","Wasser aus Bodenwanne entfernen","Auf Undichtigkeit prüfen","Gerät trocknen lassen"]}' ;;
                E24) echo '{"meaning":"Abpumpproblem","description":"Wasser wird nicht richtig abgepumpt.","solution":["Sieb am Boden reinigen","Abflussschlauch prüfen","Siphon kontrollieren","Pumpe auf Fremdkörper prüfen"]}' ;;
                E25) echo '{"meaning":"Ablaufpumpe blockiert","description":"Pumpe kann nicht arbeiten.","solution":["Pumpendeckel öffnen","Fremdkörper entfernen","Flügelrad prüfen"]}' ;;
                E22) echo '{"meaning":"Filter verstopft","description":"Siebe sind verschmutzt.","solution":["Alle Siebe entnehmen","Unter Wasser reinigen","Siebe wieder einsetzen"]}' ;;
                E01|E1) echo '{"meaning":"Heizungsfehler","description":"Wasser wird nicht erhitzt.","solution":["Service kontaktieren","Heizelement defekt"]}' ;;
                E09) echo '{"meaning":"Heizfehler","description":"Problem mit der Heizung.","solution":["Service kontaktieren"]}' ;;
                *) echo '{}' ;;
            esac
            ;;
        miele)
            case "$code" in
                F11) echo '{"meaning":"Abpumpfehler","description":"Wasser läuft nicht ab.","solution":["Ablauf prüfen","Filter reinigen","Pumpe prüfen"]}' ;;
                F12|F13) echo '{"meaning":"Zulaufproblem","description":"Wasser läuft nicht zu.","solution":["Wasserhahn prüfen","Zulaufschlauch prüfen","Sieb im Zulauf reinigen"]}' ;;
                F53) echo '{"meaning":"Motorfehler","description":"Motor funktioniert nicht korrekt.","solution":["Service kontaktieren"]}' ;;
                *) echo '{}' ;;
            esac
            ;;
        samsung)
            case "$code" in
                UE|UB|E4) echo '{"meaning":"Unwucht","description":"Wäsche ungleichmäßig verteilt.","solution":["Wäsche gleichmäßiger verteilen","Nicht zu viel/wenig beladen","Gerät ausrichten"]}' ;;
                OE|OF|E3) echo '{"meaning":"Überlauf","description":"Zu viel Wasser im Gerät.","solution":["Wasserzulauf schließen","Ablauf prüfen","Service kontaktieren"]}' ;;
                LE|LE1|E9) echo '{"meaning":"Wasserleck","description":"Leck erkannt.","solution":["Gerät sofort ausschalten","Auf Undichtigkeit prüfen","Service kontaktieren"]}' ;;
                HE|HE1|HE2) echo '{"meaning":"Heizungsfehler","description":"Wasser wird nicht erhitzt.","solution":["Service kontaktieren"]}' ;;
                *) echo '{}' ;;
            esac
            ;;
        lg)
            case "$code" in
                OE) echo '{"meaning":"Abflussfehler","description":"Wasser läuft nicht ab.","solution":["Ablaufschlauch prüfen","Filter reinigen","Pumpe prüfen"]}' ;;
                IE) echo '{"meaning":"Zulaufproblem","description":"Kein Wasserzulauf.","solution":["Wasserhahn öffnen","Zulaufschlauch prüfen"]}' ;;
                UE) echo '{"meaning":"Unwucht","description":"Ungleichmäßige Beladung.","solution":["Wäsche verteilen","Gerät ausrichten"]}' ;;
                PE) echo '{"meaning":"Drucksensorfehler","description":"Wasserstandssensor defekt.","solution":["Service kontaktieren"]}' ;;
                *) echo '{}' ;;
            esac
            ;;
        aeg|electrolux)
            case "$code" in
                E10) echo '{"meaning":"Zulaufproblem","description":"Wasser läuft nicht zu.","solution":["Wasserhahn prüfen","Zulaufschlauch prüfen","Sieb reinigen"]}' ;;
                E20) echo '{"meaning":"Abpumpfehler","description":"Wasser läuft nicht ab.","solution":["Filter reinigen","Ablauf prüfen","Pumpe prüfen"]}' ;;
                E40) echo '{"meaning":"Türproblem","description":"Tür nicht richtig geschlossen.","solution":["Tür schließen","Türschloss prüfen"]}' ;;
                *) echo '{}' ;;
            esac
            ;;
        *)
            echo '{}'
            ;;
    esac
}

# ============================================
# Commands
# ============================================

case "$CMD" in
    # ----------------------------------------
    # STATUS
    # ----------------------------------------
    status)
        device_count=$(jq '.devices | length' "$DEVICES_FILE")
        
        # Check for expiring warranties (next 90 days)
        today=$(date +%s)
        ninety_days=$((today + 7776000))
        expiring=$(jq --argjson today "$today" --argjson future "$ninety_days" '[.devices[] | select(.warranty.expires != null) | select((.warranty.expires | strptime("%Y-%m-%d") | mktime) > $today and (.warranty.expires | strptime("%Y-%m-%d") | mktime) < $future)] | length' "$DEVICES_FILE" 2>/dev/null || echo "0")
        
        # Check for due maintenance
        maintenance_due=$(jq '[.devices[] | .maintenance[]? | select(.lastDone != null)] | length' "$DEVICES_FILE" 2>/dev/null || echo "0")
        
        # Categories summary
        categories=$(jq '[.devices[].category] | group_by(.) | map({category: .[0], count: length})' "$DEVICES_FILE")
        
        jq -n \
            --argjson count "$device_count" \
            --argjson expiring "$expiring" \
            --argjson maintenance "$maintenance_due" \
            --argjson categories "$categories" \
            '{
                status: "ok",
                deviceCount: $count,
                warningWarrantyExpiring: $expiring,
                maintenanceTracked: $maintenance,
                byCategory: $categories,
                commands: {
                    "/device list": "Alle Geräte anzeigen",
                    "/device add": "Neues Gerät hinzufügen",
                    "/device info <name>": "Geräte-Details",
                    "/device error <name> <code>": "Fehlercode nachschlagen",
                    "/device help <name> <problem>": "Problemlösung",
                    "/device warranty": "Garantie-Übersicht",
                    "/device maintenance": "Wartungsplan"
                }
            }'
        ;;
        
    # ----------------------------------------
    # LIST
    # ----------------------------------------
    list)
        category="${1:-}"
        
        if [[ -n "$category" && "$category" != "$WORKSPACE" ]]; then
            devices=$(jq --arg cat "$category" '[.devices[] | select(.category == $cat)]' "$DEVICES_FILE")
        else
            devices=$(jq '.devices' "$DEVICES_FILE")
        fi
        
        echo "$devices" | jq '{
            status: "ok",
            count: length,
            devices: [.[] | {
                id: .id,
                name: .name,
                nickname: .nickname,
                manufacturer: .manufacturer,
                model: .model,
                category: .category,
                location: .location
            }]
        }'
        ;;
        
    # ----------------------------------------
    # ADD
    # ----------------------------------------
    add)
        json_data="${1:-}"
        
        if [[ -z "$json_data" || "$json_data" == "$WORKSPACE" ]]; then
            # Interactive mode - return prompt
            echo '{"status":"ok","action":"prompt","message":"Gerätedaten benötigt","required":["name","manufacturer","model"],"optional":["serialNumber","purchaseDate","purchasePrice","warranty","manualUrl","location","category","nickname"]}'
            exit 0
        fi
        
        # Parse and validate JSON
        if ! echo "$json_data" | jq -e . >/dev/null 2>&1; then
            echo '{"status":"error","message":"Invalid JSON"}'
            exit 1
        fi
        
        name=$(echo "$json_data" | jq -r '.name // empty')
        [[ -z "$name" ]] && { echo '{"status":"error","message":"Name required"}'; exit 1; }
        
        # Generate ID
        device_id=$(generate_id "$name")
        
        # Build device entry
        device=$(echo "$json_data" | jq --arg id "$device_id" --arg added "$(date -Iseconds)" '
            {
                id: $id,
                name: .name,
                nickname: (.nickname // null),
                category: (.category // "other"),
                manufacturer: (.manufacturer // "Unknown"),
                model: (.model // "Unknown"),
                serialNumber: (.serialNumber // null),
                purchaseDate: (.purchaseDate // null),
                purchasePrice: (.purchasePrice // null),
                warranty: (.warranty // null),
                manualUrl: (.manualUrl // null),
                supportUrl: (.supportUrl // null),
                location: (.location // null),
                notes: (.notes // null),
                maintenance: (.maintenance // []),
                errorHistory: [],
                addedAt: $added
            }
        ')
        
        # Add to devices file
        jq --argjson device "$device" '.devices += [$device]' "$DEVICES_FILE" > "$DEVICES_FILE.tmp"
        mv "$DEVICES_FILE.tmp" "$DEVICES_FILE"
        
        echo "$device" | jq '{status: "ok", message: "Gerät hinzugefügt", device: .}'
        ;;
        
    # ----------------------------------------
    # INFO
    # ----------------------------------------
    info)
        identifier="${1:-}"
        [[ -z "$identifier" || "$identifier" == "$WORKSPACE" ]] && { echo '{"status":"error","message":"Device name/id required"}'; exit 1; }
        
        device=$(get_device "$identifier")
        [[ -z "$device" || "$device" == "null" ]] && { echo '{"status":"error","message":"Device not found: '"$identifier"'"}'; exit 1; }
        
        # Calculate warranty status
        warranty_status="unknown"
        warranty_expires=$(echo "$device" | jq -r '.warranty.expires // empty')
        if [[ -n "$warranty_expires" && "$warranty_expires" != "null" ]]; then
            expires_ts=$(date -d "$warranty_expires" +%s 2>/dev/null || echo 0)
            today_ts=$(date +%s)
            if [[ $expires_ts -gt 0 ]]; then
                if [[ $expires_ts -gt $today_ts ]]; then
                    days_left=$(( (expires_ts - today_ts) / 86400 ))
                    warranty_status="aktiv (noch $days_left Tage)"
                else
                    warranty_status="ABGELAUFEN"
                fi
            fi
        fi
        
        echo "$device" | jq --arg ws "$warranty_status" '. + {status: "ok", warrantyStatus: $ws}'
        ;;
        
    # ----------------------------------------
    # ERROR - Lookup error code
    # ----------------------------------------
    error)
        identifier="${1:-}"
        error_code="${2:-}"
        
        [[ -z "$identifier" || "$identifier" == "$WORKSPACE" ]] && { echo '{"status":"error","message":"Device name required"}'; exit 1; }
        [[ -z "$error_code" || "$error_code" == "$WORKSPACE" ]] && { echo '{"status":"error","message":"Error code required"}'; exit 1; }
        
        device=$(get_device "$identifier")
        [[ -z "$device" ]] && { echo '{"status":"error","message":"Device not found: '"$identifier"'"}'; exit 1; }
        
        manufacturer=$(echo "$device" | jq -r '.manufacturer')
        model=$(echo "$device" | jq -r '.model')
        device_name=$(echo "$device" | jq -r '.name')
        device_id=$(echo "$device" | jq -r '.id')
        
        # Try built-in error codes first
        known_error=$(get_known_error "$manufacturer" "$error_code")
        
        if [[ "$known_error" != "{}" ]]; then
            # Found in built-in database
            result=$(echo "$known_error" | jq --arg mfr "$manufacturer" --arg mdl "$model" --arg code "$error_code" --arg name "$device_name" '
                {
                    status: "ok",
                    source: "builtin",
                    device: $name,
                    manufacturer: $mfr,
                    model: $mdl,
                    errorCode: $code,
                    meaning: .meaning,
                    description: .description,
                    solution: .solution
                }
            ')
        else
            # Search online
            search_result=$(search_error_code "$manufacturer" "$model" "$error_code")
            result=$(echo "$search_result" | jq --arg name "$device_name" '
                {
                    status: "ok",
                    source: "search",
                    device: $name,
                    manufacturer: .manufacturer,
                    model: .model,
                    errorCode: .errorCode,
                    meaning: "Unbekannt",
                    description: "Fehlercode nicht in Datenbank",
                    searchUrl: .searchUrl,
                    suggestion: "Bitte online suchen oder Handbuch prüfen"
                }
            ')
        fi
        
        # Log error to history
        jq --arg device "$device_id" --arg code "$error_code" --arg ts "$(date -Iseconds)" \
            '.entries = [{timestamp: $ts, deviceId: $device, errorCode: $code}] + .entries[:99]' \
            "$HISTORY_FILE" > "$HISTORY_FILE.tmp"
        mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
        
        echo "$result"
        ;;
        
    # ----------------------------------------
    # TROUBLESHOOT - General problem help
    # ----------------------------------------
    troubleshoot)
        identifier="${1:-}"
        problem="${2:-}"
        
        [[ -z "$identifier" ]] && { echo '{"status":"error","message":"Device name required"}'; exit 1; }
        
        device=$(get_device "$identifier")
        [[ -z "$device" ]] && { echo '{"status":"error","message":"Device not found"}'; exit 1; }
        
        manufacturer=$(echo "$device" | jq -r '.manufacturer')
        model=$(echo "$device" | jq -r '.model')
        device_name=$(echo "$device" | jq -r '.name')
        manual_url=$(echo "$device" | jq -r '.manualUrl // empty')
        support_url=$(echo "$device" | jq -r '.supportUrl // empty')
        
        # Build search query for the problem
        query="${manufacturer} ${model} ${problem} Lösung"
        search_url="https://www.google.com/search?q=$(echo -n "$query" | jq -sRr @uri)"
        
        jq -n \
            --arg device "$device_name" \
            --arg mfr "$manufacturer" \
            --arg mdl "$model" \
            --arg problem "$problem" \
            --arg searchUrl "$search_url" \
            --arg manualUrl "$manual_url" \
            --arg supportUrl "$support_url" \
            '{
                status: "ok",
                device: $device,
                manufacturer: $mfr,
                model: $mdl,
                problem: $problem,
                resources: {
                    searchUrl: $searchUrl,
                    manualUrl: (if $manualUrl != "" then $manualUrl else null end),
                    supportUrl: (if $supportUrl != "" then $supportUrl else null end)
                },
                generalTips: [
                    "Gerät aus- und wieder einschalten",
                    "Bedienungsanleitung prüfen",
                    "Hersteller-Support kontaktieren"
                ]
            }'
        ;;
        
    # ----------------------------------------
    # MANUAL
    # ----------------------------------------
    manual)
        identifier="${1:-}"
        [[ -z "$identifier" ]] && { echo '{"status":"error","message":"Device name required"}'; exit 1; }
        
        device=$(get_device "$identifier")
        [[ -z "$device" ]] && { echo '{"status":"error","message":"Device not found"}'; exit 1; }
        
        manufacturer=$(echo "$device" | jq -r '.manufacturer')
        model=$(echo "$device" | jq -r '.model')
        manual_url=$(echo "$device" | jq -r '.manualUrl // empty')
        
        # If no manual URL stored, provide search link
        if [[ -z "$manual_url" ]]; then
            query="${manufacturer} ${model} Bedienungsanleitung PDF"
            search_url="https://www.google.com/search?q=$(echo -n "$query" | jq -sRr @uri)"
            manual_url="$search_url"
            stored=false
        else
            stored=true
        fi
        
        jq -n \
            --arg device "$(echo "$device" | jq -r '.name')" \
            --arg mfr "$manufacturer" \
            --arg mdl "$model" \
            --arg url "$manual_url" \
            --argjson stored "$stored" \
            '{
                status: "ok",
                device: $device,
                manufacturer: $mfr,
                model: $mdl,
                manualUrl: $url,
                isStored: $stored
            }'
        ;;
        
    # ----------------------------------------
    # WARRANTY
    # ----------------------------------------
    warranty)
        today=$(date +%s)
        
        warranties=$(jq --argjson today "$today" '
            [.devices[] | select(.warranty.expires != null) | 
                {
                    name: .name,
                    manufacturer: .manufacturer,
                    model: .model,
                    expires: .warranty.expires,
                    expiresTs: (.warranty.expires | strptime("%Y-%m-%d") | mktime),
                    daysLeft: (((.warranty.expires | strptime("%Y-%m-%d") | mktime) - $today) / 86400 | floor)
                }
            ] | sort_by(.expiresTs)
        ' "$DEVICES_FILE" 2>/dev/null || echo "[]")
        
        active=$(echo "$warranties" | jq '[.[] | select(.daysLeft > 0)]')
        expired=$(echo "$warranties" | jq '[.[] | select(.daysLeft <= 0)]')
        expiring_soon=$(echo "$warranties" | jq '[.[] | select(.daysLeft > 0 and .daysLeft <= 90)]')
        
        jq -n \
            --argjson active "$active" \
            --argjson expired "$expired" \
            --argjson soon "$expiring_soon" \
            '{
                status: "ok",
                active: ($active | length),
                expired: ($expired | length),
                expiringSoon: $soon,
                allWarranties: ($active + $expired)
            }'
        ;;
        
    # ----------------------------------------
    # MAINTENANCE
    # ----------------------------------------
    maintenance)
        # Get all devices with maintenance tasks
        devices_with_maintenance=$(jq '[.devices[] | select(.maintenance | length > 0) | {
            id: .id,
            name: .name,
            tasks: .maintenance
        }]' "$DEVICES_FILE")
        
        jq -n --argjson devices "$devices_with_maintenance" '{
            status: "ok",
            devicesWithMaintenance: ($devices | length),
            devices: $devices
        }'
        ;;
        
    # ----------------------------------------
    # UPDATE
    # ----------------------------------------
    update)
        identifier="${1:-}"
        json_data="${2:-}"
        
        [[ -z "$identifier" ]] && { echo '{"status":"error","message":"Device name required"}'; exit 1; }
        [[ -z "$json_data" || "$json_data" == "$WORKSPACE" ]] && { echo '{"status":"error","message":"Update data required"}'; exit 1; }
        
        device_id=$(get_device_id "$identifier")
        [[ -z "$device_id" ]] && { echo '{"status":"error","message":"Device not found"}'; exit 1; }
        
        # Merge updates
        jq --arg id "$device_id" --argjson updates "$json_data" '
            .devices = [.devices[] | if .id == $id then . * $updates else . end]
        ' "$DEVICES_FILE" > "$DEVICES_FILE.tmp"
        mv "$DEVICES_FILE.tmp" "$DEVICES_FILE"
        
        echo '{"status":"ok","message":"Device updated","deviceId":"'"$device_id"'"}'
        ;;
        
    # ----------------------------------------
    # REMOVE
    # ----------------------------------------
    remove)
        identifier="${1:-}"
        [[ -z "$identifier" ]] && { echo '{"status":"error","message":"Device name required"}'; exit 1; }
        
        device_id=$(get_device_id "$identifier")
        [[ -z "$device_id" ]] && { echo '{"status":"error","message":"Device not found"}'; exit 1; }
        
        jq --arg id "$device_id" '.devices = [.devices[] | select(.id != $id)]' "$DEVICES_FILE" > "$DEVICES_FILE.tmp"
        mv "$DEVICES_FILE.tmp" "$DEVICES_FILE"
        
        echo '{"status":"ok","message":"Device removed","deviceId":"'"$device_id"'"}'
        ;;
        
    # ----------------------------------------
    # SEARCH
    # ----------------------------------------
    search)
        query="${1:-}"
        [[ -z "$query" ]] && { echo '{"status":"error","message":"Search query required"}'; exit 1; }
        
        results=$(jq --arg q "$query" '
            [.devices[] | select(
                (.name | ascii_downcase | contains($q | ascii_downcase)) or
                (.manufacturer | ascii_downcase | contains($q | ascii_downcase)) or
                (.model | ascii_downcase | contains($q | ascii_downcase)) or
                ((.nickname // "") | ascii_downcase | contains($q | ascii_downcase)) or
                ((.location // "") | ascii_downcase | contains($q | ascii_downcase))
            )]
        ' "$DEVICES_FILE")
        
        echo "$results" | jq '{status: "ok", query: "'"$query"'", results: ., count: length}'
        ;;
        
    # ----------------------------------------
    # LOG - Add maintenance log
    # ----------------------------------------
    log)
        identifier="${1:-}"
        note="${2:-}"
        
        [[ -z "$identifier" ]] && { echo '{"status":"error","message":"Device name required"}'; exit 1; }
        [[ -z "$note" || "$note" == "$WORKSPACE" ]] && { echo '{"status":"error","message":"Note required"}'; exit 1; }
        
        device_id=$(get_device_id "$identifier")
        [[ -z "$device_id" ]] && { echo '{"status":"error","message":"Device not found"}'; exit 1; }
        
        # Add to maintenance log
        jq --arg device "$device_id" --arg note "$note" --arg ts "$(date -Iseconds)" \
            '.entries = [{timestamp: $ts, deviceId: $device, note: $note}] + .entries' \
            "$MAINTENANCE_FILE" > "$MAINTENANCE_FILE.tmp"
        mv "$MAINTENANCE_FILE.tmp" "$MAINTENANCE_FILE"
        
        echo '{"status":"ok","message":"Maintenance logged","deviceId":"'"$device_id"'"}'
        ;;
        
    # ----------------------------------------
    # HELP
    # ----------------------------------------
    help)
        echo '{"status":"ok","commands":["status","list","add","info","error","troubleshoot","manual","warranty","maintenance","update","remove","search","log"]}'
        ;;
        
    *)
        echo '{"status":"error","message":"Unknown command: '"$CMD"'"}'
        exit 1
        ;;
esac
