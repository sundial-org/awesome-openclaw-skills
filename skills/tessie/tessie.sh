#!/bin/bash

# Tessie Skill - CLI script for Tessie API control
# Usage: ./tessie.sh [command] [args]

set -euo pipefail

# Configuration from env or fallback
TESSIE_API_URL="${TESSIE_API_URL:-https://api.tessie.com}"
TESSIE_API_KEY="${TESSIE_API_KEY:-}"

# Get API key from clawdbot config if env not set
if [[ -z "$TESSIE_API_KEY" ]]; then
    CONFIG_FILE="$HOME/.clawdbot/clawdbot.json"
    if [[ -f "$CONFIG_FILE" ]]; then
        TESSIE_API_KEY=$(jq -r '.skills.entries.tessie.apiKey // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
        TESSIE_VEHICLE_ID=$(jq -r '.skills.entries.tessie.vehicleId // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
    fi
fi

# Validate API key
if [[ -z "$TESSIE_API_KEY" ]]; then
    echo "⚠️  Tessie API key not configured"
    echo "Set TESSIE_API_KEY environment variable or configure in clawdbot.json"
    exit 1
fi

# Validate temperature input
validate_temp() {
    local temp="$1"
    local min="$2"
    local max="$3"

    if ! [[ "$temp" =~ ^[0-9]+$ ]]; then
        echo "⚠️  Temperature must be a number"
        return 1
    fi

    if (( temp < min || temp > max )); then
        echo "⚠️  Temperature must be between ${min}°F and ${max}°F"
        return 1
    fi
}

# Validate percentage input
validate_percent() {
    local value="$1"
    local name="${2:-Value}"

    if ! [[ "$value" =~ ^[0-9]+$ ]]; then
        echo "⚠️  ${name} must be a number"
        return 1
    fi

    if (( value < 0 || value > 100 )); then
        echo "⚠️  ${name} must be between 0 and 100"
        return 1
    fi
}

# Validate vehicle ID (UUID or integer)
validate_vehicle_id() {
    local id="$1"

    if [[ -z "$id" ]]; then
        echo "⚠️  Vehicle ID is empty"
        return 1
    fi

    # Basic UUID format check (version 4 UUID)
    if [[ "$id" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
        return 0
    fi

    # Or check if it's a numeric ID (Tesla format)
    if [[ "$id" =~ ^[0-9]+$ ]]; then
        return 0
    fi

    echo "⚠️  Invalid vehicle ID format"
    return 1
}

# Helper: Make API request
api_request() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"

    if [[ -n "$data" ]]; then
        curl -s --fail --max-time 30 \
            -H "Authorization: Bearer $TESSIE_API_KEY" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${TESSIE_API_URL}${endpoint}" 2>/dev/null
    else
        curl -s --fail --max-time 30 \
            -H "Authorization: Bearer $TESSIE_API_KEY" \
            "${TESSIE_API_URL}${endpoint}" 2>/dev/null
    fi
}

# Helper: Get vehicle ID and VIN if not set
get_vehicle_info() {
    if [[ -z "$TESSIE_VEHICLE_ID" ]]; then
        RESULT=$(api_request "GET" "/vehicles")
        if [[ $? -ne 0 ]] || [[ -z "$RESULT" ]]; then
            echo "⚠️  Could not get vehicle info from Tessie API"
            echo "Please provide TESSIE_VEHICLE_ID in config"
            exit 1
        fi
        TESSIE_VEHICLE_ID=$(echo "$RESULT" | jq -r '.results[0].last_state.vehicle_id // empty')
        TESSIE_VIN=$(echo "$RESULT" | jq -r '.results[0].vin // empty')

        if [[ -z "$TESSIE_VEHICLE_ID" ]]; then
            echo "⚠️  No vehicle found linked to your Tessie account"
            exit 1
        fi
    else
        # If vehicle ID is set, fetch VIN from vehicles endpoint
        RESULT=$(api_request "GET" "/vehicles")
        if [[ $? -eq 0 ]] && [[ -n "$RESULT" ]]; then
            TESSIE_VIN=$(echo "$RESULT" | jq -r '.results[0].vin // empty')
        fi
    fi
}

# Helper: Get vehicle state
get_vehicle_state() {
    get_vehicle_info
    ALL_VEHICLES=$(api_request "GET" "/vehicles")

    if [[ $? -ne 0 ]] || [[ -z "$ALL_VEHICLES" ]]; then
        echo "⚠️  Failed to fetch vehicle state"
        return 1
    fi

    STATE=$(echo "$ALL_VEHICLES" | jq -r '.results[0].last_state')

    if [[ -z "$STATE" ]] || [[ "$STATE" == "null" ]]; then
        echo "⚠️  Vehicle state not available"
        return 1
    fi

    return 0
}

# Parse command
COMMAND="${1:-help}"

case "$COMMAND" in
    status|vehicle-state|state)
        # Get vehicle status
        if ! get_vehicle_state; then
            exit 1
        fi

        echo "🚗 Vehicle Status:"
        echo "$STATE" | jq -r '
            "🔋 Battery: \(.charge_state.battery_level // "N/A")%",
            "📏 Range: \(.charge_state.battery_range // "N/A") mi",
            "🔒 Locked: \(.vehicle_state.locked // "N/A")",
            "🔌 Charging: \(.charge_state.charging_state // "N/A")",
            "🌡️  Temperature: \(.climate_state.inside_temp // "N/A")°C",
            "🚗 State: \(.state // "N/A")"
        '
        ;;

    battery|charge|soc)
        # Get battery level
        if ! get_vehicle_state; then
            exit 1
        fi

        LEVEL=$(echo "$STATE" | jq -r '.charge_state.battery_level // "N/A"')
        RANGE=$(echo "$STATE" | jq -r '.charge_state.battery_range // "N/A"')

        echo "🔋 Battery: ${LEVEL}%"
        echo "📏 Range: ${RANGE} mi"
        ;;

    location|where)
        # Get vehicle location
        if ! get_vehicle_state; then
            exit 1
        fi

        echo "$STATE" | jq -r '
            "📍 Location:",
            "  Latitude: \(.drive_state.latitude // "Unknown")",
            "  Longitude: \(.drive_state.longitude // "Unknown")",
            "  Shift State: \(.drive_state.shift_state // "Unknown")",
            "  Speed: \(.drive_state.speed // 0) mph"
        '
        ;;

    drives|drive-history|recent-drives)
        # Get recent drives
        get_vehicle_info
        LIMIT="${1:-5}"

        if ! validate_number "$LIMIT"; then
            echo "⚠️  Limit must be a number"
            exit 1
        fi

        DRIVES=$(api_request "GET" "/${TESSIE_VIN}/drives?limit=${LIMIT}")

        if [[ $? -ne 0 ]] || [[ -z "$DRIVES" ]]; then
            echo "⚠️  Failed to fetch drives"
            exit 1
        fi

        echo "🚗 Recent Drives (last ${LIMIT}):"
        echo "$DRIVES" | jq -r '
            .results[] |
            "(.ended_at | strftime("%Y-%m-%d %H:%M")): (.ending_saved_location // "Unknown") " +
            "((.odometer_distance // 0) mi, (.energy_used // 0) kWh)"
        '
        ;;


    preheat|heat|warm)
        # Preheat car
        get_vehicle_info
        echo "🔥 Starting climate..."

        PAYLOAD=$(jq -n --arg t "$TEMP" '{temperature: $t}')
        RESULT=$(api_request "POST" "/${TESSIE_VIN}/command/start_climate" "$PAYLOAD")

        if [[ $? -eq 0 ]]; then
            echo "✅ Climate started"
        else
            echo "⚠️  Failed to start climate"
            echo "Response: $RESULT"
        fi
        ;;

    precool|cool|ac)
        # Precool car (alias for preheat)
        TEMP="${2:-68}"
        if ! validate_temp "$TEMP" 60 75; then
            exit 1
        fi

        get_vehicle_id
        echo "❄️  Precooling car to ${TEMP}°F..."

        PAYLOAD=$(jq -n --arg t "$TEMP" '{temperature: $t}')
        RESULT=$(api_request "POST" "/${TESSIE_VIN}/command/start_climate" "$PAYLOAD")

        if [[ $? -eq 0 ]]; then
            echo "✅ Climate started"
        else
            echo "⚠️  Failed to start climate"
            echo "Response: $RESULT"
        fi
        ;;

    climate-off|ac-off|heat-off)
        # Turn off climate
        get_vehicle_id
        echo "🌡️  Turning off climate..."
        RESULT=$(api_request "POST" "/${TESSIE_VIN}/command/stop_climate")

        if [[ $? -eq 0 ]]; then
            echo "✅ Climate stopped"
        else
            echo "⚠️  Failed to stop climate"
            echo "Response: $RESULT"
        fi
        ;;

    drives|history|trips)
        # Show drive history
        LIMIT="${2:-10}"
        if ! validate_percent "$LIMIT" "Limit"; then
            exit 1
        fi

        get_vehicle_id
        echo "🚗 Recent Drives (last ${LIMIT}):"
        RESULT=$(api_request "GET" "/${TESSIE_VIN}/drives?limit=${LIMIT}")

        if [[ $? -ne 0 ]] || [[ -z "$RESULT" ]]; then
            echo "⚠️  Failed to fetch drives"
            exit 1
        fi

        DRIVE_COUNT=$(echo "$RESULT" | jq -r '.drives | length // 0')
        if [[ "$DRIVE_COUNT" == "0" ]]; then
            echo "No drives found in range"
        else
            echo "$RESULT" | jq -r '
                .drives[] |
                "📅 \(.date // "Unknown") - \(.distance // "N/A") mi",
                "   Duration: \(.duration // "N/A")",
                "   Efficiency: \(.efficiency // "N/A") Wh/mi"
            '
        fi
        ;;

    charge-start|start-charging|plug)
        # Start charging
        get_vehicle_id
        echo "🔌 Starting charge..."
        RESULT=$(api_request "POST" "/${TESSIE_VIN}/command/start_charging")

        if [[ $? -eq 0 ]]; then
            echo "✅ Charging started"
        else
            echo "⚠️  Failed to start charging"
            echo "Response: $RESULT"
        fi
        ;;

    charge-stop|stop-charging|unplug)
        # Stop charging
        get_vehicle_id
        echo "🛑 Stopping charge..."
        RESULT=$(api_request "POST" "/${TESSIE_VIN}/command/stop_charging")

        if [[ $? -eq 0 ]]; then
            echo "✅ Charging stopped"
        else
            echo "⚠️  Failed to stop charging"
            echo "Response: $RESULT"
        fi
        ;;

    charge-limit|set-limit)
        # Set charge limit
        LIMIT="${2:-90}"
        if ! validate_percent "$LIMIT" "Charge limit"; then
            exit 1
        fi

        get_vehicle_id
        echo "🔋 Setting charge limit to ${LIMIT}%..."

        PAYLOAD=$(jq -n --arg l "$LIMIT" '{limit: $l}')
        RESULT=$(api_request "POST" "/${TESSIE_VIN}/command/set_charge_limit" "$PAYLOAD")

        if [[ $? -eq 0 ]]; then
            echo "✅ Charge limit set to ${LIMIT}%"
        else
            echo "⚠️  Failed to set charge limit"
            echo "Response: $RESULT"
        fi
        ;;

    fsd|fsd-stats|autopilot)
        # Get FSD usage stats
        RANGE="${2:-today}"
        get_vehicle_id

        echo "🚗 FSD Stats (${RANGE}):"
        RESULT=$(api_request "GET" "/${TESSIE_VIN}/drives?range=${RANGE}")

        if [[ $? -ne 0 ]] || [[ -z "$RESULT" ]]; then
            echo "⚠️  Could not fetch FSD stats. Check if FSD is enabled on vehicle."
            echo "Response: $RESULT"
            exit 1
        fi

        echo "$RESULT" | jq -r '
            "🤖 FSD Miles: \(.miles // 0) mi",
            "📈 Engagement: \(.engagement // 0)%",
            "⏱️  Time: \(.hours // 0) hrs",
            "📅 Period: \(.period // "Unknown")"
        '
        ;;

    fsd-week|weekly-fsd)
        # Weekly FSD stats
        get_vehicle_id
        echo "📊 Weekly FSD Stats:"
        RESULT=$(api_request "GET" "/${TESSIE_VIN}/drives?range=week")

        if [[ $? -ne 0 ]] || [[ -z "$RESULT" ]]; then
            echo "⚠️  Could not fetch FSD stats"
            echo "Response: $RESULT"
            exit 1
        fi

        echo "$RESULT" | jq -r '
            "🤖 FSD Miles: \(.miles // 0) mi",
            "📈 Engagement: \(.engagement // 0)%",
            "📅 Days: \(.days // 0)"
        '
        ;;

    fsd-month|monthly-fsd)
        # Monthly FSD stats
        get_vehicle_id
        echo "📅 Monthly FSD Stats:"
        RESULT=$(api_request "GET" "/${TESSIE_VIN}/drives?range=month")

        if [[ $? -ne 0 ]] || [[ -z "$RESULT" ]]; then
            echo "⚠️  Could not fetch FSD stats"
            echo "Response: $RESULT"
            exit 1
        fi

        echo "$RESULT" | jq -r '
            "🤖 FSD Miles: \(.miles // 0) mi",
            "📈 Engagement: \(.engagement // 0)%",
            "📅 Days: \(.days // 0)"
        '
        ;;

    help|--help|-h)
        cat << EOF
Tessie Skill - Control your Tesla via Tessie API

Commands:
  status / state          Show vehicle status (battery, location, etc.)
  battery / charge         Show battery level and range
  location / where          Show vehicle location
  preheat [temp]          Preheat car to temp (default: 72°F)
  precool [temp]          Precool car to temp (default: 68°F)
  climate-off             Turn off climate control
  drives [limit]           Show recent drives (default: 10)
  charge-start             Start charging
  charge-stop             Stop charging
  charge-limit [percent]    Set charge limit (default: 90%)
  fsd [range]            Show FSD usage (today/week/month)
  fsd-week               Weekly FSD statistics
  fsd-month              Monthly FSD statistics

Examples:
  ./tessie.sh battery
  ./tessie.sh preheat 72
  ./tessie.sh drives 5
  ./tessie.sh fsd today
  ./tessie.sh fsd-week

Setup:
  1. Get API key from https://tessie.com/developers
  2. Set TESSIE_API_KEY env var or add to clawdbot.json
  3. Optionally set TESSIE_VEHICLE_ID if known
EOF
        ;;

    *)
        echo "Unknown command: $COMMAND"
        echo "Run './tessie.sh help' for usage"
        exit 1
        ;;
esac
