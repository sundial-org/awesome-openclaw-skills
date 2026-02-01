#!/bin/bash
# Migrate Obsidian vault structure to Craft.do with full nested hierarchy
# Creates folders and documents with full markdown content
# Safe to re-run - checks for existing folders before creating

set -e

# Configuration
CRAFT_API_KEY="${CRAFT_API_KEY:-}"
CRAFT_ENDPOINT="${CRAFT_ENDPOINT:-}"
OBSIDIAN_VAULT="${1:-}"

if [ -z "$CRAFT_API_KEY" ] || [ -z "$CRAFT_ENDPOINT" ]; then
  echo "Error: Set CRAFT_API_KEY and CRAFT_ENDPOINT environment variables"
  exit 1
fi

if [ -z "$OBSIDIAN_VAULT" ]; then
  echo "Usage: $0 <obsidian_vault_path>"
  echo "Example: $0 \"/Users/you/Documents/My Vault\""
  exit 1
fi

if [ ! -d "$OBSIDIAN_VAULT" ]; then
  echo "Error: Directory not found: $OBSIDIAN_VAULT"
  exit 1
fi

echo "🚀 Starting Obsidian → Craft migration (with nested folders)"
echo "Vault: $OBSIDIAN_VAULT"
echo ""

# Helper function for API calls
craft_api() {
  local method="$1"
  local endpoint="$2"
  local data="$3"
  
  if [ -n "$data" ]; then
    curl -s -X "$method" \
      -H "Authorization: Bearer $CRAFT_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$CRAFT_ENDPOINT/$endpoint"
  else
    curl -s -X "$method" \
      -H "Authorization: Bearer $CRAFT_API_KEY" \
      "$CRAFT_ENDPOINT/$endpoint"
  fi
}

# Track created folders in temp file (path -> id mapping)
FOLDER_MAP="/tmp/craft-folders-$$.txt"
trap "rm -f $FOLDER_MAP" EXIT
touch "$FOLDER_MAP"

# Get folder ID from cache
get_folder_id() {
  local folder_path="$1"
  grep "^$folder_path:" "$FOLDER_MAP" | cut -d: -f2
}

# Save folder ID to cache
save_folder_id() {
  local folder_path="$1"
  local folder_id="$2"
  echo "$folder_path:$folder_id" >> "$FOLDER_MAP"
}

# Check if folder already exists in Craft
find_existing_folder() {
  local folder_name="$1"
  local parent_id="$2"
  
  # Get all folders from Craft
  local all_folders=$(craft_api GET "folders")
  
  # Search for folder with matching name and parent
  if [ -z "$parent_id" ]; then
    # Root level folder
    echo "$all_folders" | jq -r ".items[] | select(.name == \"$folder_name\" and (.parentFolderId == null or .parentFolderId == \"\")) | .id" | head -1
  else
    # Nested folder
    echo "$all_folders" | jq -r ".items[] | select(.name == \"$folder_name\" and .parentFolderId == \"$parent_id\") | .id" | head -1
  fi
}

# Create folder in Craft (with optional parent)
create_folder() {
  local folder_path="$1"  # Full path from vault root
  local folder_name=$(basename "$folder_path")
  
  # Check if already created in this session
  local cached_id=$(get_folder_id "$folder_path")
  if [ -n "$cached_id" ]; then
    echo "$cached_id"
    return
  fi
  
  # Get parent folder ID if this is a nested folder
  local parent_path=$(dirname "$folder_path")
  local parent_id=""
  
  if [ "$parent_path" != "." ] && [ "$parent_path" != "$OBSIDIAN_VAULT" ]; then
    parent_id=$(get_folder_id "$parent_path")
    
    # If parent doesn't exist, create it first (recursive)
    if [ -z "$parent_id" ]; then
      parent_id=$(create_folder "$parent_path")
    fi
  fi
  
  # Check if folder already exists in Craft
  local existing_id=$(find_existing_folder "$folder_name" "$parent_id")
  
  if [ -n "$existing_id" ]; then
    echo "📁 Found existing folder: $folder_path" >&2
    echo "   ✓ ID: $existing_id" >&2
    save_folder_id "$folder_path" "$existing_id"
    echo "$existing_id"
    return
  fi
  
  echo "📁 Creating folder: $folder_path" >&2
  
  # Build the JSON payload
  local name_json=$(echo -n "$folder_name" | jq -Rs .)
  local payload
  
  if [ -n "$parent_id" ]; then
    payload="{\"folders\": [{\"name\": $name_json, \"parentFolderId\": \"$parent_id\"}]}"
  else
    payload="{\"folders\": [{\"name\": $name_json}]}"
  fi
  
  local result=$(craft_api POST "folders" "$payload")
  local folder_id=$(echo "$result" | jq -r '.items[0].id // empty')
  
  if [ -n "$folder_id" ]; then
    save_folder_id "$folder_path" "$folder_id"
    echo "   ✓ ID: $folder_id" >&2
    echo "$folder_id"
  else
    echo "   ✗ Failed: $result" >&2
    echo "" >&2
  fi
}

# Create document in folder with content
create_document() {
  local title="$1"
  local folder_id="$2"
  local file_path="$3"
  
  echo "   📄 Creating: $title"
  
  # Properly escape title for JSON using jq (strip trailing newline)
  local title_json=$(echo -n "$title" | jq -Rs .)
  
  # Create the document first
  local result=$(craft_api POST "documents" "{\"documents\": [{\"title\": $title_json}], \"destination\": {\"folderId\": \"$folder_id\"}}")
  
  local doc_id=$(echo "$result" | jq -r '.items[0].id // empty')
  
  if [ -z "$doc_id" ]; then
    echo "      ✗ Failed to create: $result"
    return
  fi
  
  echo "      ✓ Created ID: $doc_id"
  
  # Read file content and escape for JSON
  local content=$(cat "$file_path" | jq -Rs .)
  
  # Add content using /blocks endpoint
  echo "      📝 Adding content..."
  local blocks_result=$(craft_api POST "blocks" "{\"blocks\": [{\"type\": \"text\", \"markdown\": $content}], \"position\": {\"pageId\": \"$doc_id\", \"position\": \"end\"}}")
  
  local block_id=$(echo "$blocks_result" | jq -r '.items[0].id // empty')
  
  if [ -n "$block_id" ]; then
    echo "      ✓ Content added"
  else
    echo "      ✗ Failed to add content: $blocks_result"
  fi
}

# Process vault recursively
echo "🔍 Scanning vault structure..."
echo ""

folder_count=0
doc_count=0

# Find all directories (excluding .obsidian)
while IFS= read -r dir; do
  # Get relative path from vault root
  rel_path="${dir#$OBSIDIAN_VAULT/}"
  
  # Skip if it's the root or hidden
  if [ "$rel_path" = "$OBSIDIAN_VAULT" ] || [[ "$rel_path" =~ ^\. ]]; then
    continue
  fi
  
  # Create folder hierarchy
  folder_id=$(create_folder "$dir")
  
  if [ -n "$folder_id" ]; then
    ((folder_count++))
    
    # Find markdown files in this folder (not recursive - only immediate children)
    find "$dir" -maxdepth 1 -name "*.md" -type f | while read -r file; do
      # Get filename without extension
      filename=$(basename "$file" .md)
      
      # Skip files starting with underscore or dot
      if [[ "$filename" =~ ^\. ]] || [[ "$filename" =~ ^_ ]]; then
        echo "   ⊘ Skipping: $filename"
        continue
      fi
      
      # Create document with content
      create_document "$filename" "$folder_id" "$file"
      ((doc_count++))
    done
  fi
  
  echo ""
done < <(find "$OBSIDIAN_VAULT" -type d ! -path "*/.obsidian*" | sort)

echo ""
echo "✅ Migration complete!"
echo ""
echo "📊 Summary:"
echo "   Folders created: $folder_count"
echo "   Documents created with full content: (check Craft)"
echo ""
echo "🎉 Full folder hierarchy migrated!"
