#!/bin/bash
set -e

# Sonarr API wrapper
# Credentials: ~/.clawdbot/credentials/sonarr/config.json

CONFIG_FILE="$HOME/.clawdbot/credentials/sonarr/config.json"

if [ -f "$CONFIG_FILE" ]; then
  SONARR_URL=$(jq -r '.url' "$CONFIG_FILE")
  SONARR_API_KEY=$(jq -r '.apiKey' "$CONFIG_FILE")
  DEFAULT_QUALITY_PROFILE=$(jq -r '.defaultQualityProfile // empty' "$CONFIG_FILE")
fi

if [ -z "$SONARR_URL" ] || [ -z "$SONARR_API_KEY" ]; then
  echo "Error: Sonarr not configured. Create $CONFIG_FILE with {\"url\": \"...\", \"apiKey\": \"...\"}"
  exit 1
fi

API="$SONARR_URL/api/v3"
AUTH="X-Api-Key: $SONARR_API_KEY"

cmd="$1"
shift || true

case "$cmd" in
  search)
    query="$1"
    curl -s -H "$AUTH" "$API/series/lookup?term=$(echo "$query" | jq -sRr @uri)" | jq -r '
      to_entries | .[:10] | .[] | 
      "\(.key + 1). \(.value.title) (\(.value.year)) - https://thetvdb.com/dereferrer/series/\(.value.tvdbId)"
    '
    ;;
    
  search-json)
    query="$1"
    curl -s -H "$AUTH" "$API/series/lookup?term=$(echo "$query" | jq -sRr @uri)"
    ;;
    
  exists)
    tvdbId="$1"
    result=$(curl -s -H "$AUTH" "$API/series?tvdbId=$tvdbId")
    if [ "$result" = "[]" ]; then
      echo "not_found"
    else
      echo "exists"
      echo "$result" | jq -r '.[0] | "ID: \(.id), Title: \(.title), Seasons: \(.statistics.seasonCount)"'
    fi
    ;;
    
  config)
    echo "=== Root Folders ==="
    curl -s -H "$AUTH" "$API/rootfolder" | jq -r '.[] | "\(.id): \(.path)"'
    echo ""
    echo "=== Quality Profiles ==="
    curl -s -H "$AUTH" "$API/qualityprofile" | jq -r '.[] | "\(.id): \(.name)"'
    ;;
    
  add)
    tvdbId="$1"
    qualityProfileId="$2"
    searchFlag="true"
    
    # Check for --no-search flag
    for arg in "$@"; do
      if [ "$arg" = "--no-search" ]; then
        searchFlag="false"
      fi
    done
    
    # Get series details from lookup
    series=$(curl -s -H "$AUTH" "$API/series/lookup?term=tvdb:$tvdbId" | jq '.[0]')
    
    if [ "$series" = "null" ] || [ -z "$series" ]; then
      echo "❌ Show not found with TVDB ID: $tvdbId"
      exit 1
    fi
    
    # Get default root folder
    rootFolder=$(curl -s -H "$AUTH" "$API/rootfolder" | jq -r '.[0].path')
    
    # Use provided quality profile ID, config default, or first available
    if [ -z "$qualityProfileId" ] || [ "$qualityProfileId" = "--no-search" ]; then
      if [ -n "$DEFAULT_QUALITY_PROFILE" ]; then
        qualityProfile="$DEFAULT_QUALITY_PROFILE"
      else
        qualityProfile=$(curl -s -H "$AUTH" "$API/qualityprofile" | jq -r '.[0].id')
      fi
    else
      qualityProfile="$qualityProfileId"
    fi
    
    # Build add request
    addRequest=$(echo "$series" | jq --arg rf "$rootFolder" --argjson qp "$qualityProfile" --argjson search "$searchFlag" '
      . + {
        rootFolderPath: $rf,
        qualityProfileId: $qp,
        monitored: true,
        seasonFolder: true,
        addOptions: {
          monitor: "all",
          searchForMissingEpisodes: $search,
          searchForCutoffUnmetEpisodes: false
        }
      }
    ')
    
    result=$(curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" -d "$addRequest" "$API/series")
    
    if echo "$result" | jq -e '.id' > /dev/null 2>&1; then
      title=$(echo "$result" | jq -r '.title')
      year=$(echo "$result" | jq -r '.year')
      seasons=$(echo "$result" | jq -r '.statistics.seasonCount // "?"')
      echo "✅ Added: $title ($year) - $seasons seasons"
      if [ "$searchFlag" = "true" ]; then
        echo "🔍 Search started"
      fi
    else
      echo "❌ Failed to add show"
      echo "$result" | jq -r '.message // .'
    fi
    ;;
    
  remove)
    tvdbId="$1"
    deleteFiles="false"
    if [ "$2" = "--delete-files" ]; then
      deleteFiles="true"
    fi
    
    # Get series ID from library
    series=$(curl -s -H "$AUTH" "$API/series?tvdbId=$tvdbId")
    
    if [ "$series" = "[]" ]; then
      echo "❌ Show not found in library"
      exit 1
    fi
    
    seriesId=$(echo "$series" | jq -r '.[0].id')
    title=$(echo "$series" | jq -r '.[0].title')
    year=$(echo "$series" | jq -r '.[0].year')
    
    curl -s -X DELETE -H "$AUTH" "$API/series/$seriesId?deleteFiles=$deleteFiles" > /dev/null
    
    if [ "$deleteFiles" = "true" ]; then
      echo "🗑️ Removed: $title ($year) + deleted files"
    else
      echo "🗑️ Removed: $title ($year) (files kept)"
    fi
    ;;
    
  *)
    echo "Usage: sonarr.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  search <query>              Search for TV shows"
    echo "  search-json <query>         Search (JSON output)"
    echo "  exists <tvdbId>             Check if show is in library"
    echo "  config                      Show root folders & quality profiles"
    echo "  add <tvdbId> [profileId] [--no-search]  Add a show (searches by default)"
    echo "  remove <tvdbId> [--delete-files]  Remove a show from library"
    ;;
esac
