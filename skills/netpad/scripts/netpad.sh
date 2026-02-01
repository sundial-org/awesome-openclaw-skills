#!/bin/bash
# NetPad API CLI Wrapper
# Requires: NETPAD_API_KEY

set -euo pipefail

BASE_URL="${NETPAD_BASE_URL:-https://www.netpad.io/api/v1}"

# Check credentials
if [[ -z "${NETPAD_API_KEY:-}" ]]; then
    echo "Error: NETPAD_API_KEY must be set" >&2
    echo "  export NETPAD_API_KEY=np_live_xxx" >&2
    exit 1
fi

# API request helper
api() {
    local method="$1"
    endpoint="$2"
    data="${3:-}"
    
    local args=(
        --silent
        --header "Authorization: Bearer ${NETPAD_API_KEY}"
        --header "Content-Type: application/json"
        -X "$method"
    )
    
    if [[ -n "$data" ]]; then
        args+=(--data "$data")
    fi
    
    curl "${args[@]}" "${BASE_URL}${endpoint}"
}

# Commands
case "${1:-help}" in
    projects)
        case "${2:-list}" in
            list)
                api GET "/projects" | jq '.data[] | {projectId, name, slug}'
                ;;
            *)
                echo "Usage: $0 projects list"
                ;;
        esac
        ;;
        
    forms)
        case "${2:-list}" in
            list)
                status="${3:-}"
                endpoint="/forms"
                [[ -n "$status" ]] && endpoint="${endpoint}?status=${status}"
                api GET "$endpoint" | jq '.data[] | {id, name, slug, status, responseCount}'
                ;;
            get)
                api GET "/forms/${3:?Form ID required}" | jq '.'
                ;;
            create)
                name="${3:?Name required}"
                project_id="${4:?Project ID required}"
                description="${5:-}"
                api POST "/forms" "{\"name\":\"$name\",\"projectId\":\"$project_id\",\"description\":\"$description\"}" | jq '.'
                ;;
            publish)
                api PATCH "/forms/${3:?Form ID required}" '{"status":"published"}' | jq '.data | {id, name, status}'
                ;;
            unpublish)
                api PATCH "/forms/${3:?Form ID required}" '{"status":"draft"}' | jq '.data | {id, name, status}'
                ;;
            delete)
                api DELETE "/forms/${3:?Form ID required}"
                echo "Form deleted"
                ;;
            add-field)
                form_id="${3:?Form ID required}"
                fpath="${4:?Field path required}"
                label="${5:?Field label required}"
                ftype="${6:-text}"
                freq="${7:-false}"
                # Get current form, add field, update
                current=$(api GET "/forms/${form_id}")
                fields=$(echo "$current" | jq ".data.fields + [{\"path\":\"$path\",\"label\":\"$label\",\"type\":\"$type\",\"required\":$required}]")
                api PATCH "/forms/${form_id}" "{\"fields\":$fields}" | jq '.data.fields[-1]'
                ;;
            *)
                echo "Usage: $0 forms [list|get|create|publish|unpublish|delete|add-field] [args]"
                echo ""
                echo "Commands:"
                echo "  list [status]              List forms (optional: draft|published)"
                echo "  get <form-id>              Get form details"
                echo "  create <name> <project-id> Create new form"
                echo "  publish <form-id>          Publish form"
                echo "  unpublish <form-id>        Unpublish form (set to draft)"
                echo "  delete <form-id>           Delete form"
                echo "  add-field <form-id> <path> <label> [type] [required]"
                ;;
        esac
        ;;
        
    submissions)
        case "${2:-list}" in
            list)
                form_id="${3:?Form ID required}"
                limit="${4:-20}"
                api GET "/forms/${form_id}/submissions?pageSize=${limit}" | jq '.data[] | {id, data, submittedAt: .metadata.submittedAt}'
                ;;
            get)
                api GET "/forms/${3:?Form ID required}/submissions/${4:?Submission ID required}" | jq '.'
                ;;
            create)
                form_id="${3:?Form ID required}"
                data="${4:?JSON data required}"
                api POST "/forms/${form_id}/submissions" "{\"data\":$data}" | jq '.'
                ;;
            delete)
                api DELETE "/forms/${3:?Form ID required}/submissions/${4:?Submission ID required}"
                echo "Submission deleted"
                ;;
            export)
                form_id="${3:?Form ID required}"
                api GET "/forms/${form_id}/submissions?pageSize=1000" | jq -r '.data[].data | @json'
                ;;
            count)
                form_id="${3:?Form ID required}"
                api GET "/forms/${form_id}/submissions" | jq '.pagination.total'
                ;;
            *)
                echo "Usage: $0 submissions [list|get|create|delete|export|count] [args]"
                echo ""
                echo "Commands:"
                echo "  list <form-id> [limit]     List submissions (default: 20)"
                echo "  get <form-id> <sub-id>     Get submission details"
                echo "  create <form-id> <json>    Submit data (JSON object)"
                echo "  delete <form-id> <sub-id>  Delete submission"
                echo "  export <form-id>           Export all submissions as JSON lines"
                echo "  count <form-id>            Get submission count"
                ;;
        esac
        ;;
        
    health)
        api GET "/health" | jq '.'
        ;;
        
    help|*)
        echo "NetPad CLI Wrapper"
        echo ""
        echo "Usage: $0 <command> [subcommand] [args]"
        echo ""
        echo "Commands:"
        echo "  projects    Manage projects"
        echo "  forms       Manage forms"
        echo "  submissions Manage form submissions"
        echo "  health      Check API health"
        echo ""
        echo "Environment:"
        echo "  NETPAD_API_KEY     API key (required)"
        echo "  NETPAD_BASE_URL    Base URL (default: https://www.netpad.io/api/v1)"
        echo ""
        echo "Examples:"
        echo "  $0 projects list"
        echo "  $0 forms list published"
        echo "  $0 forms create 'Contact Form' proj_xxx"
        echo "  $0 forms publish frm_xxx"
        echo "  $0 submissions list frm_xxx"
        echo "  $0 submissions create frm_xxx '{\"name\":\"John\",\"email\":\"john@example.com\"}'"
        echo "  $0 submissions export frm_xxx > data.jsonl"
        ;;
esac
