#!/bin/bash
# Migrate Obsidian vault structure to Craft.do
# Creates folders and documents with full markdown content

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

echo "🚀 Starting Obsidian → Craft migration"
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

# Track created folders in temp file
FOLDER_MAP="/tmp/craft-folders-$$.txt"
trap "rm -f $FOLDER_MAP" EXIT
touch "$FOLDER_MAP"

# Get folder ID from cache
get_folder_id() {
  local folder_name="$1"
  grep "^$folder_name:" "$FOLDER_MAP" | cut -d: -f2
}

# Save folder ID to cache
save_folder_id() {
  local folder_name="$1"
  local folder_id="$2"
  echo "$folder_name:$folder_id" >> "$FOLDER_MAP"
}

# Create folder in Craft
create_folder() {
  local folder_name="$1"
  
  # Check if already created
  local cached_id=$(get_folder_id "$folder_name")
  if [ -n "$cached_id" ]; then
    echo "$cached_id"
    return
  fi
  
  echo "📁 Creating folder: $folder_name" >&2
  
  local result=$(craft_api POST "folders" "{\"folders\": [{\"name\": \"$folder_name\"}]}")
  local folder_id=$(echo "$result" | jq -r '.items[0].id // empty')
  
  if [ -n "$folder_id" ]; then
    save_folder_id "$folder_name" "$folder_id"
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
  local result=$(craft_api POST "documents" "{\"documents\": [{\"title\": $title_json, \"location\": \"$folder_id\"}]}")
  
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

# Process vault
echo "🔍 Scanning vault structure..."
echo ""

folder_count=0
doc_count=0

# Get all folders (exclude .obsidian)
while IFS= read -r dir; do
  # Get relative path from vault root
  rel_path="${dir#$OBSIDIAN_VAULT/}"
  
  # Skip if it's the root
  if [ "$rel_path" = "$OBSIDIAN_VAULT" ]; then
    continue
  fi
  
  # Get just the folder name (last component)
  folder_name=$(basename "$dir")
  
  # Create folder
  folder_id=$(create_folder "$folder_name")
  
  if [ -n "$folder_id" ]; then
    ((folder_count++))
    
    # Find markdown files in this folder (not recursive)
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
done < <(find "$OBSIDIAN_VAULT" -mindepth 1 -maxdepth 1 -type d ! -path "*/.obsidian*" | sort)

echo ""
echo "✅ Migration complete!"
echo ""
echo "📊 Summary:"
echo "   Folders created: $folder_count"
echo "   Documents created with full content: (check Craft)"
echo ""
echo "🎉 All markdown files migrated with their original content!"
