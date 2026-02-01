#!/bin/bash
# Cleanup Craft.do space - delete all user-created folders and documents

set -e

CRAFT_API_KEY="${CRAFT_API_KEY:-}"
CRAFT_ENDPOINT="${CRAFT_ENDPOINT:-}"

if [ -z "$CRAFT_API_KEY" ] || [ -z "$CRAFT_ENDPOINT" ]; then
  echo "Error: Set CRAFT_API_KEY and CRAFT_ENDPOINT environment variables"
  exit 1
fi

echo "🧹 Craft.do Cleanup Script"
echo ""
echo "This will delete ALL user-created folders and move ALL documents to trash."
echo ""
read -p "Are you sure? Type 'yes' to continue: " confirm

if [ "$confirm" != "yes" ]; then
  echo "Cancelled."
  exit 0
fi

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

echo ""
echo "Step 1: Deleting all documents..."

# Get all document IDs (excluding trash)
ALL_DOCS=$(craft_api GET "documents" | jq -r '.items[].id')

if [ -n "$ALL_DOCS" ]; then
  DOC_COUNT=$(echo "$ALL_DOCS" | wc -l | tr -d ' ')
  echo "Found $DOC_COUNT documents to delete"
  
  # Convert to JSON array
  DOC_IDS=$(echo "$ALL_DOCS" | jq -R . | jq -s .)
  
  # Delete (moves to trash)
  craft_api DELETE "documents" "{\"documentIds\": $DOC_IDS}" > /dev/null
  echo "✓ All documents moved to trash"
else
  echo "No documents found"
fi

echo ""
echo "Step 2: Deleting all user-created folders..."

# Get all folder IDs (excluding built-in: unsorted, trash, templates, daily_notes)
ALL_FOLDERS=$(craft_api GET "folders" | jq -r '.items[] | select(.id != "unsorted" and .id != "trash" and .id != "templates" and .id != "daily_notes") | .id')

if [ -n "$ALL_FOLDERS" ]; then
  FOLDER_COUNT=$(echo "$ALL_FOLDERS" | wc -l | tr -d ' ')
  echo "Found $FOLDER_COUNT folders to delete"
  
  # Convert to JSON array
  FOLDER_IDS=$(echo "$ALL_FOLDERS" | jq -R . | jq -s .)
  
  # Delete folders
  craft_api DELETE "folders" "{\"folderIds\": $FOLDER_IDS}" > /dev/null
  echo "✓ All folders deleted"
else
  echo "No user-created folders found"
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Your Craft space is now empty except for:"
echo "  - Unsorted (empty)"
echo "  - Templates (empty)"
echo "  - Trash (contains deleted documents)"
echo ""
echo "You can restore documents from Trash if needed."
