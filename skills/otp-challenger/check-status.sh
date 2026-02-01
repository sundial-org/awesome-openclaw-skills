#!/bin/bash
# Check if a user's OTP verification is still valid
#
# Usage: check-status.sh [userId]
#
# Exit codes:
#   0 - Still verified (within time window)
#   1 - Expired or never verified
#   2 - Config/setup error

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw}"
STATE_FILE="$WORKSPACE/memory/otp-state.json"

USER_ID="${1:-default}"

# Validate user ID (alphanumeric + @._- only, 1-255 chars)
if [ "${#USER_ID}" -gt 255 ]; then
  echo "ERROR: User ID exceeds maximum length (255 characters)" >&2
  exit 2
fi

if ! [[ "$USER_ID" =~ ^[a-zA-Z0-9@._-]+$ ]]; then
  echo "ERROR: Invalid characters in user ID (allowed: a-z A-Z 0-9 @ . _ -)" >&2
  exit 2
fi

# Check if state file exists and validate JSON structure
if [ ! -f "$STATE_FILE" ]; then
  echo "❌ Never verified" >&2
  exit 1
fi

# Validate JSON structure, recover if corrupted
if ! jq empty "$STATE_FILE" 2>/dev/null; then
  echo "❌ Never verified (state file corrupted)" >&2
  exit 1
elif ! jq -e '.verifications' "$STATE_FILE" >/dev/null 2>&1; then
  echo "❌ Never verified (invalid state structure)" >&2
  exit 1
fi

# Get user's verification state
VERIFIED_AT=$(jq -r --arg userId "$USER_ID" '.verifications[$userId].verifiedAt // empty' "$STATE_FILE")
EXPIRES_AT=$(jq -r --arg userId "$USER_ID" '.verifications[$userId].expiresAt // empty' "$STATE_FILE")

if [ -z "$VERIFIED_AT" ] || [ -z "$EXPIRES_AT" ]; then
  echo "❌ Never verified" >&2
  exit 1
fi

# Convert timestamps (milliseconds) to seconds
NOW_MS=$(date +%s)000
if [ "$NOW_MS" -lt "$EXPIRES_AT" ]; then
  # Calculate time remaining
  REMAINING_MS=$((EXPIRES_AT - NOW_MS))
  REMAINING_HOURS=$((REMAINING_MS / 1000 / 60 / 60))
  
  # Use portable date syntax (GNU vs BSD/macOS)
  if date --version >/dev/null 2>&1; then
    # GNU date
    VERIFIED_DATE=$(date -d "@$((VERIFIED_AT / 1000))" "+%Y-%m-%d %H:%M:%S")
    EXPIRES_DATE=$(date -d "@$((EXPIRES_AT / 1000))" "+%Y-%m-%d %H:%M:%S")
  else
    # BSD/macOS date
    VERIFIED_DATE=$(date -r "$((VERIFIED_AT / 1000))" "+%Y-%m-%d %H:%M:%S")
    EXPIRES_DATE=$(date -r "$((EXPIRES_AT / 1000))" "+%Y-%m-%d %H:%M:%S")
  fi
  
  echo "✅ Valid for $REMAINING_HOURS more hours"
  echo "   Verified: $VERIFIED_DATE"
  echo "   Expires:  $EXPIRES_DATE"
  exit 0
else
  # Use portable date syntax
  if date --version >/dev/null 2>&1; then
    # GNU date
    VERIFIED_DATE=$(date -d "@$((VERIFIED_AT / 1000))" "+%Y-%m-%d %H:%M:%S")
  else
    # BSD/macOS date
    VERIFIED_DATE=$(date -r "$((VERIFIED_AT / 1000))" "+%Y-%m-%d %H:%M:%S")
  fi
  echo "❌ Expired (last verified: $VERIFIED_DATE)" >&2
  exit 1
fi
