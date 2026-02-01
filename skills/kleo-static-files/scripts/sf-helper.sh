#!/bin/bash
#
# sf-helper.sh - Static Files helper for AI agents
#
# Provides high-level operations that combine multiple sf commands.
#
# Usage: sf-helper.sh <command> [args]
#

set -e

# Ensure sf is available (it's just the CLI)
SF_CLI="${SF_CLI:-sf}"

# Check environment
check_env() {
  if [ -z "$SF_API_URL" ] || [ -z "$SF_API_KEY" ]; then
    echo "Error: SF_API_URL and SF_API_KEY must be set"
    echo ""
    echo "Example:"
    echo "  export SF_API_URL=http://localhost:3000"
    echo "  export SF_API_KEY=sk_xxxxx"
    exit 1
  fi
}

# Deploy a directory as a new site
# Usage: sf-helper.sh deploy <site-name> <directory> [--auth user:pass]
cmd_deploy() {
  local site="$1"
  local dir="$2"
  local auth="$3"

  if [ -z "$site" ] || [ -z "$dir" ]; then
    echo "Usage: sf-helper.sh deploy <site-name> <directory> [user:pass]"
    exit 1
  fi

  if [ ! -d "$dir" ]; then
    echo "Error: Directory not found: $dir"
    exit 1
  fi

  echo "Deploying $dir to $site..."

  # Create site if it doesn't exist
  if ! $SF_CLI sites list --json 2>/dev/null | grep -q "\"name\":\"$site\""; then
    echo "Creating site: $site"
    $SF_CLI sites create "$site"
  fi

  # Set auth if provided
  if [ -n "$auth" ]; then
    echo "Setting authentication..."
    $SF_CLI sites auth "$site" "$auth"
  fi

  # Upload directory
  echo "Uploading files..."
  $SF_CLI upload "$dir" "$site" --overwrite

  echo ""
  echo "Deployed! URL: https://$site.$SF_DOMAIN"
}

# Clean deploy - delete existing files before uploading
# Usage: sf-helper.sh clean-deploy <site-name> <directory>
cmd_clean_deploy() {
  local site="$1"
  local dir="$2"

  if [ -z "$site" ] || [ -z "$dir" ]; then
    echo "Usage: sf-helper.sh clean-deploy <site-name> <directory>"
    exit 1
  fi

  echo "Clean deploying $dir to $site..."

  # Delete and recreate site
  $SF_CLI sites delete "$site" 2>/dev/null || true
  $SF_CLI sites create "$site"

  # Upload
  $SF_CLI upload "$dir" "$site"

  echo ""
  echo "Deployed! URL: https://$site.$SF_DOMAIN"
}

# Quick share - upload a single file and return URL
# Usage: sf-helper.sh share <file> [site-name]
cmd_share() {
  local file="$1"
  local site="${2:-quick-share}"

  if [ -z "$file" ]; then
    echo "Usage: sf-helper.sh share <file> [site-name]"
    exit 1
  fi

  if [ ! -f "$file" ]; then
    echo "Error: File not found: $file"
    exit 1
  fi

  # Create site if needed
  if ! $SF_CLI sites list --json 2>/dev/null | grep -q "\"name\":\"$site\""; then
    $SF_CLI sites create "$site" >/dev/null
  fi

  # Upload and get URL
  local filename=$(basename "$file")
  $SF_CLI upload "$file" "$site" --overwrite >/dev/null

  echo "https://$site.${SF_DOMAIN:-498as.com}/$filename"
}

# List all sites with their URLs
# Usage: sf-helper.sh list
cmd_list() {
  local domain="${SF_DOMAIN:-498as.com}"
  
  echo "Sites:"
  echo ""
  
  $SF_CLI sites list --json 2>/dev/null | \
    grep -o '"name":"[^"]*"' | \
    cut -d'"' -f4 | \
    while read -r site; do
      echo "  https://$site.$domain"
    done
}

# Show help
cmd_help() {
  cat << EOF
sf-helper.sh - Static Files helper for AI agents

Commands:
  deploy <site> <dir> [user:pass]  Deploy directory to site
  clean-deploy <site> <dir>        Delete all files and deploy fresh
  share <file> [site]              Quick share a single file
  list                             List all sites with URLs

Environment:
  SF_API_URL   API endpoint (required)
  SF_API_KEY   API key (required)
  SF_DOMAIN    Domain for URLs (default: 498as.com)

Examples:
  sf-helper.sh deploy docs ./build
  sf-helper.sh deploy private ./files admin:secret123
  sf-helper.sh share ./report.pdf
  sf-helper.sh clean-deploy mysite ./dist
EOF
}

# Main
check_env

case "${1:-help}" in
  deploy) shift; cmd_deploy "$@" ;;
  clean-deploy) shift; cmd_clean_deploy "$@" ;;
  share) shift; cmd_share "$@" ;;
  list) cmd_list ;;
  help|--help|-h) cmd_help ;;
  *) echo "Unknown command: $1"; cmd_help; exit 1 ;;
esac
