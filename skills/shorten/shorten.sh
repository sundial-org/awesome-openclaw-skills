#!/usr/bin/env bash

URL="$1"

if [ -z "$URL" ]; then
  echo "Usage: shorten <url>"
  exit 1
fi

# Use curl with data-urlencode to handle special characters correctly
RESULT=$(curl -s -d "format=simple" --data-urlencode "url=$URL" "https://is.gd/create.php")

if [[ "$RESULT" == "Error"* ]]; then
  echo "❌ Failed: $RESULT"
  exit 1
fi

echo "$RESULT"
