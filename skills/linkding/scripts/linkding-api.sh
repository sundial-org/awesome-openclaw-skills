#!/bin/bash
# Linkding API helper script
# Usage: linkding-api.sh <command> [args...]

set -euo pipefail

CONFIG_FILE="${LINKDING_CONFIG:-$HOME/.clawdbot/credentials/linkding/config.json}"

# Load config
if [[ -f "$CONFIG_FILE" ]]; then
    LINKDING_URL=$(jq -r '.url // empty' "$CONFIG_FILE")
    LINKDING_API_KEY=$(jq -r '.apiKey // empty' "$CONFIG_FILE")
fi

LINKDING_URL="${LINKDING_URL:-}"
LINKDING_API_KEY="${LINKDING_API_KEY:-}"

if [[ -z "$LINKDING_URL" || -z "$LINKDING_API_KEY" ]]; then
    echo "Error: LINKDING_URL and LINKDING_API_KEY must be set (via env or $CONFIG_FILE)" >&2
    exit 1
fi

# Remove trailing slash
LINKDING_URL="${LINKDING_URL%/}"

api_call() {
    local method="$1"
    local endpoint="$2"
    shift 2
    
    curl -sS -X "$method" \
        -H "Authorization: Token $LINKDING_API_KEY" \
        -H "Content-Type: application/json" \
        "$@" \
        "${LINKDING_URL}${endpoint}"
}

usage() {
    cat <<EOF
Linkding API CLI

Usage: $(basename "$0") <command> [options]

Commands:
  bookmarks [--query Q] [--limit N] [--offset N] [--archived] [--modified-since DATE] [--added-since DATE]
  get <id>                      Get bookmark by ID
  check <url>                   Check if URL is bookmarked
  create <url> [--title T] [--description D] [--notes N] [--tags t1,t2] [--archived] [--unread] [--shared]
  update <id> [--url U] [--title T] [--description D] [--notes N] [--tags t1,t2] [--unread] [--shared]
  archive <id>                  Archive a bookmark
  unarchive <id>                Unarchive a bookmark
  delete <id>                   Delete a bookmark
  
  tags [--limit N] [--offset N]
  tag-get <id>                  Get tag by ID
  tag-create <name>             Create a new tag
  
  bundles [--limit N] [--offset N]
  bundle-get <id>               Get bundle by ID
  bundle-create <name> [--search S] [--any-tags T] [--all-tags T] [--excluded-tags T] [--order N]
  bundle-update <id> [--name N] [--search S] [--any-tags T] [--all-tags T] [--excluded-tags T] [--order N]
  bundle-delete <id>            Delete a bundle
  
  profile                       Get user profile/preferences

Examples:
  $(basename "$0") bookmarks --query "python" --limit 10
  $(basename "$0") create "https://example.com" --title "Example" --tags "ref,docs"
  $(basename "$0") check "https://example.com"
EOF
}

cmd_bookmarks() {
    local query="" limit="" offset="" archived="" modified_since="" added_since="" bundle=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --query|-q) query="$2"; shift 2 ;;
            --limit|-l) limit="$2"; shift 2 ;;
            --offset|-o) offset="$2"; shift 2 ;;
            --archived|-a) archived="1"; shift ;;
            --modified-since) modified_since="$2"; shift 2 ;;
            --added-since) added_since="$2"; shift 2 ;;
            --bundle) bundle="$2"; shift 2 ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    done
    
    local endpoint="/api/bookmarks/"
    [[ -n "$archived" ]] && endpoint="/api/bookmarks/archived/"
    
    local params=()
    [[ -n "$query" ]] && params+=("q=$(jq -rn --arg v "$query" '$v | @uri')")
    [[ -n "$limit" ]] && params+=("limit=$limit")
    [[ -n "$offset" ]] && params+=("offset=$offset")
    [[ -n "$modified_since" ]] && params+=("modified_since=$(jq -rn --arg v "$modified_since" '$v | @uri')")
    [[ -n "$added_since" ]] && params+=("added_since=$(jq -rn --arg v "$added_since" '$v | @uri')")
    [[ -n "$bundle" ]] && params+=("bundle=$bundle")
    
    if [[ ${#params[@]} -gt 0 ]]; then
        endpoint="${endpoint}?$(IFS='&'; echo "${params[*]}")"
    fi
    
    api_call GET "$endpoint"
}

cmd_get() {
    local id="$1"
    api_call GET "/api/bookmarks/${id}/"
}

cmd_check() {
    local url="$1"
    local encoded=$(jq -rn --arg v "$url" '$v | @uri')
    api_call GET "/api/bookmarks/check/?url=${encoded}"
}

cmd_create() {
    local url="$1"; shift
    local title="" description="" notes="" tags="" archived="false" unread="false" shared="false"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --title|-t) title="$2"; shift 2 ;;
            --description|-d) description="$2"; shift 2 ;;
            --notes|-n) notes="$2"; shift 2 ;;
            --tags) tags="$2"; shift 2 ;;
            --archived|-a) archived="true"; shift ;;
            --unread|-u) unread="true"; shift ;;
            --shared|-s) shared="true"; shift ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    done
    
    # Build tag array
    local tag_array="[]"
    if [[ -n "$tags" ]]; then
        tag_array=$(echo "$tags" | tr ',' '\n' | jq -R . | jq -s .)
    fi
    
    local payload=$(jq -n \
        --arg url "$url" \
        --arg title "$title" \
        --arg description "$description" \
        --arg notes "$notes" \
        --argjson tag_names "$tag_array" \
        --argjson is_archived "$archived" \
        --argjson unread "$unread" \
        --argjson shared "$shared" \
        '{
            url: $url,
            title: (if $title == "" then null else $title end),
            description: (if $description == "" then null else $description end),
            notes: (if $notes == "" then null else $notes end),
            tag_names: $tag_names,
            is_archived: $is_archived,
            unread: $unread,
            shared: $shared
        } | with_entries(select(.value != null))')
    
    api_call POST "/api/bookmarks/" -d "$payload"
}

cmd_update() {
    local id="$1"; shift
    local url="" title="" description="" notes="" tags="" unread="" shared=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --url) url="$2"; shift 2 ;;
            --title|-t) title="$2"; shift 2 ;;
            --description|-d) description="$2"; shift 2 ;;
            --notes|-n) notes="$2"; shift 2 ;;
            --tags) tags="$2"; shift 2 ;;
            --unread) unread="$2"; shift 2 ;;
            --shared) shared="$2"; shift 2 ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    done
    
    local payload="{}"
    [[ -n "$url" ]] && payload=$(echo "$payload" | jq --arg v "$url" '. + {url: $v}')
    [[ -n "$title" ]] && payload=$(echo "$payload" | jq --arg v "$title" '. + {title: $v}')
    [[ -n "$description" ]] && payload=$(echo "$payload" | jq --arg v "$description" '. + {description: $v}')
    [[ -n "$notes" ]] && payload=$(echo "$payload" | jq --arg v "$notes" '. + {notes: $v}')
    [[ -n "$unread" ]] && payload=$(echo "$payload" | jq --argjson v "$unread" '. + {unread: $v}')
    [[ -n "$shared" ]] && payload=$(echo "$payload" | jq --argjson v "$shared" '. + {shared: $v}')
    
    if [[ -n "$tags" ]]; then
        local tag_array=$(echo "$tags" | tr ',' '\n' | jq -R . | jq -s .)
        payload=$(echo "$payload" | jq --argjson v "$tag_array" '. + {tag_names: $v}')
    fi
    
    api_call PATCH "/api/bookmarks/${id}/" -d "$payload"
}

cmd_archive() {
    api_call POST "/api/bookmarks/${1}/archive/"
}

cmd_unarchive() {
    api_call POST "/api/bookmarks/${1}/unarchive/"
}

cmd_delete() {
    api_call DELETE "/api/bookmarks/${1}/"
}

cmd_tags() {
    local limit="" offset=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --limit|-l) limit="$2"; shift 2 ;;
            --offset|-o) offset="$2"; shift 2 ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    done
    
    local endpoint="/api/tags/"
    local params=()
    [[ -n "$limit" ]] && params+=("limit=$limit")
    [[ -n "$offset" ]] && params+=("offset=$offset")
    
    if [[ ${#params[@]} -gt 0 ]]; then
        endpoint="${endpoint}?$(IFS='&'; echo "${params[*]}")"
    fi
    
    api_call GET "$endpoint"
}

cmd_tag_get() {
    api_call GET "/api/tags/${1}/"
}

cmd_tag_create() {
    local name="$1"
    api_call POST "/api/tags/" -d "$(jq -n --arg name "$name" '{name: $name}')"
}

cmd_bundles() {
    local limit="" offset=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --limit|-l) limit="$2"; shift 2 ;;
            --offset|-o) offset="$2"; shift 2 ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    done
    
    local endpoint="/api/bundles/"
    local params=()
    [[ -n "$limit" ]] && params+=("limit=$limit")
    [[ -n "$offset" ]] && params+=("offset=$offset")
    
    if [[ ${#params[@]} -gt 0 ]]; then
        endpoint="${endpoint}?$(IFS='&'; echo "${params[*]}")"
    fi
    
    api_call GET "$endpoint"
}

cmd_bundle_get() {
    api_call GET "/api/bundles/${1}/"
}

cmd_bundle_create() {
    local name="$1"; shift
    local search="" any_tags="" all_tags="" excluded_tags="" order=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --search|-s) search="$2"; shift 2 ;;
            --any-tags) any_tags="$2"; shift 2 ;;
            --all-tags) all_tags="$2"; shift 2 ;;
            --excluded-tags) excluded_tags="$2"; shift 2 ;;
            --order) order="$2"; shift 2 ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    done
    
    local payload=$(jq -n \
        --arg name "$name" \
        --arg search "$search" \
        --arg any_tags "$any_tags" \
        --arg all_tags "$all_tags" \
        --arg excluded_tags "$excluded_tags" \
        --arg order "$order" \
        '{
            name: $name,
            search: $search,
            any_tags: $any_tags,
            all_tags: $all_tags,
            excluded_tags: $excluded_tags
        } + (if $order != "" then {order: ($order | tonumber)} else {} end)')
    
    api_call POST "/api/bundles/" -d "$payload"
}

cmd_bundle_update() {
    local id="$1"; shift
    local name="" search="" any_tags="" all_tags="" excluded_tags="" order=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --name|-n) name="$2"; shift 2 ;;
            --search|-s) search="$2"; shift 2 ;;
            --any-tags) any_tags="$2"; shift 2 ;;
            --all-tags) all_tags="$2"; shift 2 ;;
            --excluded-tags) excluded_tags="$2"; shift 2 ;;
            --order) order="$2"; shift 2 ;;
            *) echo "Unknown option: $1" >&2; exit 1 ;;
        esac
    done
    
    local payload="{}"
    [[ -n "$name" ]] && payload=$(echo "$payload" | jq --arg v "$name" '. + {name: $v}')
    [[ -n "$search" ]] && payload=$(echo "$payload" | jq --arg v "$search" '. + {search: $v}')
    [[ -n "$any_tags" ]] && payload=$(echo "$payload" | jq --arg v "$any_tags" '. + {any_tags: $v}')
    [[ -n "$all_tags" ]] && payload=$(echo "$payload" | jq --arg v "$all_tags" '. + {all_tags: $v}')
    [[ -n "$excluded_tags" ]] && payload=$(echo "$payload" | jq --arg v "$excluded_tags" '. + {excluded_tags: $v}')
    [[ -n "$order" ]] && payload=$(echo "$payload" | jq --argjson v "$order" '. + {order: $v}')
    
    api_call PATCH "/api/bundles/${id}/" -d "$payload"
}

cmd_bundle_delete() {
    api_call DELETE "/api/bundles/${1}/"
}

cmd_profile() {
    api_call GET "/api/user/profile/"
}

# Main dispatch
case "${1:-}" in
    bookmarks) shift; cmd_bookmarks "$@" ;;
    get) shift; cmd_get "$@" ;;
    check) shift; cmd_check "$@" ;;
    create) shift; cmd_create "$@" ;;
    update) shift; cmd_update "$@" ;;
    archive) shift; cmd_archive "$@" ;;
    unarchive) shift; cmd_unarchive "$@" ;;
    delete) shift; cmd_delete "$@" ;;
    tags) shift; cmd_tags "$@" ;;
    tag-get) shift; cmd_tag_get "$@" ;;
    tag-create) shift; cmd_tag_create "$@" ;;
    bundles) shift; cmd_bundles "$@" ;;
    bundle-get) shift; cmd_bundle_get "$@" ;;
    bundle-create) shift; cmd_bundle_create "$@" ;;
    bundle-update) shift; cmd_bundle_update "$@" ;;
    bundle-delete) shift; cmd_bundle_delete "$@" ;;
    profile) shift; cmd_profile "$@" ;;
    -h|--help|help|"") usage ;;
    *) echo "Unknown command: $1" >&2; usage; exit 1 ;;
esac
