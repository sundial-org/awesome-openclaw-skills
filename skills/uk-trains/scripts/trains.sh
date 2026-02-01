#!/usr/bin/env bash
# UK Trains CLI - Query National Rail departures, arrivals, and services via Huxley2
# Requires: NATIONAL_RAIL_TOKEN environment variable (free from https://realtime.nationalrail.co.uk/OpenLDBWSRegistration/)

set -euo pipefail

HUXLEY_BASE="${HUXLEY_URL:-https://huxley2.azurewebsites.net}"
TOKEN="${NATIONAL_RAIL_TOKEN:-}"

usage() {
    cat <<EOF
UK Trains CLI - National Rail live departure boards

Usage: trains.sh <command> [options]

Commands:
  departures <station> [to <dest>] [--rows N]   Show departures (optionally to destination)
  arrivals <station> [from <origin>] [--rows N] Show arrivals (optionally from origin)
  all <station> [--rows N]                      Show all departures and arrivals
  next <station> to <dest>                      Next train to destination
  fastest <station> to <dest>                   Fastest train to destination
  service <id>                                  Service details (calling points, delays)
  search <query>                                Search for station by name
  delays <station> [from/to <filter>] --rows N  Check delays on route

Environment:
  NATIONAL_RAIL_TOKEN  Your Darwin API token (required)
                       Register free: https://realtime.nationalrail.co.uk/OpenLDBWSRegistration/
  HUXLEY_URL           Override Huxley2 endpoint (default: https://huxley2.azurewebsites.net)

Examples:
  trains.sh departures "London Paddington"
  trains.sh departures PAD to BRI
  trains.sh arrivals "Manchester Piccadilly" from "London Euston"
  trains.sh next "Kings Cross" to "Edinburgh"
  trains.sh fastest EUS to MAN
  trains.sh search "clapham"
  trains.sh delays CLJ from london --rows 20
EOF
    exit 1
}

check_token() {
    if [[ -z "$TOKEN" ]]; then
        echo "Error: NATIONAL_RAIL_TOKEN not set" >&2
        echo "Register for free at: https://realtime.nationalrail.co.uk/OpenLDBWSRegistration/" >&2
        exit 1
    fi
}

api_call() {
    local endpoint="$1"
    local url="${HUXLEY_BASE}${endpoint}"
    
    # Add token
    if [[ "$url" == *"?"* ]]; then
        url="${url}&accessToken=${TOKEN}"
    else
        url="${url}?accessToken=${TOKEN}"
    fi
    
    curl -sS "$url" | jq '.'
}

# Parse --rows N from args, return number and remaining args
parse_rows() {
    local rows=10
    local args=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --rows)
                rows="$2"
                shift 2
                ;;
            *)
                args+=("$1")
                shift
                ;;
        esac
    done
    echo "$rows"
    printf '%s\n' "${args[@]}"
}

cmd_departures() {
    check_token
    local station="$1"; shift
    local filter_type="" filter_station="" rows=10
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            to)
                filter_type="to"
                filter_station="$2"
                shift 2
                ;;
            --rows)
                rows="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # URL encode station names
    station=$(printf '%s' "$station" | jq -sRr @uri)
    
    if [[ -n "$filter_station" ]]; then
        filter_station=$(printf '%s' "$filter_station" | jq -sRr @uri)
        api_call "/departures/${station}/${filter_type}/${filter_station}/${rows}?expand=true"
    else
        api_call "/departures/${station}/${rows}?expand=true"
    fi
}

cmd_arrivals() {
    check_token
    local station="$1"; shift
    local filter_type="" filter_station="" rows=10
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            from)
                filter_type="from"
                filter_station="$2"
                shift 2
                ;;
            --rows)
                rows="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    station=$(printf '%s' "$station" | jq -sRr @uri)
    
    if [[ -n "$filter_station" ]]; then
        filter_station=$(printf '%s' "$filter_station" | jq -sRr @uri)
        api_call "/arrivals/${station}/${filter_type}/${filter_station}/${rows}?expand=true"
    else
        api_call "/arrivals/${station}/${rows}?expand=true"
    fi
}

cmd_all() {
    check_token
    local station="$1"; shift
    local rows=10
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --rows)
                rows="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    station=$(printf '%s' "$station" | jq -sRr @uri)
    api_call "/all/${station}/${rows}?expand=true"
}

cmd_next() {
    check_token
    local station="$1"; shift
    local dest=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            to)
                dest="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    if [[ -z "$dest" ]]; then
        echo "Error: 'next' requires a destination (e.g., next PAD to BRI)" >&2
        exit 1
    fi
    
    station=$(printf '%s' "$station" | jq -sRr @uri)
    dest=$(printf '%s' "$dest" | jq -sRr @uri)
    api_call "/next/${station}/to/${dest}?expand=true"
}

cmd_fastest() {
    check_token
    local station="$1"; shift
    local dest=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            to)
                dest="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    if [[ -z "$dest" ]]; then
        echo "Error: 'fastest' requires a destination (e.g., fastest EUS to MAN)" >&2
        exit 1
    fi
    
    station=$(printf '%s' "$station" | jq -sRr @uri)
    dest=$(printf '%s' "$dest" | jq -sRr @uri)
    api_call "/fastest/${station}/to/${dest}?expand=true"
}

cmd_service() {
    check_token
    local service_id="$1"
    # URL encode the service ID (it may contain special chars)
    service_id=$(printf '%s' "$service_id" | jq -sRr @uri)
    api_call "/service/${service_id}"
}

cmd_search() {
    # Station search doesn't require token
    local query="$1"
    query=$(printf '%s' "$query" | jq -sRr @uri)
    curl -sS "${HUXLEY_BASE}/crs/${query}" | jq '.'
}

cmd_delays() {
    check_token
    local station="$1"; shift
    local filter_type="" filter_station="" rows=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            from|to)
                filter_type="$1"
                filter_station="$2"
                shift 2
                ;;
            --rows)
                rows="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    if [[ -z "$rows" ]]; then
        echo "Error: 'delays' requires --rows N" >&2
        exit 1
    fi
    
    station=$(printf '%s' "$station" | jq -sRr @uri)
    
    if [[ -n "$filter_station" ]]; then
        filter_station=$(printf '%s' "$filter_station" | jq -sRr @uri)
        api_call "/delays/${station}/${filter_type}/${filter_station}/${rows}"
    else
        api_call "/delays/${station}/${rows}"
    fi
}

# Main
[[ $# -lt 1 ]] && usage

command="$1"; shift

case "$command" in
    departures)
        [[ $# -lt 1 ]] && usage
        cmd_departures "$@"
        ;;
    arrivals)
        [[ $# -lt 1 ]] && usage
        cmd_arrivals "$@"
        ;;
    all)
        [[ $# -lt 1 ]] && usage
        cmd_all "$@"
        ;;
    next)
        [[ $# -lt 1 ]] && usage
        cmd_next "$@"
        ;;
    fastest)
        [[ $# -lt 1 ]] && usage
        cmd_fastest "$@"
        ;;
    service)
        [[ $# -lt 1 ]] && usage
        cmd_service "$@"
        ;;
    search)
        [[ $# -lt 1 ]] && usage
        cmd_search "$@"
        ;;
    delays)
        [[ $# -lt 1 ]] && usage
        cmd_delays "$@"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo "Unknown command: $command" >&2
        usage
        ;;
esac
