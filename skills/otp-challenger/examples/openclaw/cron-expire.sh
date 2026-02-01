#!/bin/bash
# OpenClaw Session Expiry Hook
# Recommended: Run via OpenClaw Cron every 15-30 minutes.

# 1. Logic: Invalidate the current session token
# This forces the next check-status.sh call to return UNAUTHORIZED

# Assuming your verify.sh or check-status.sh uses a local '.session' file
SESSION_FILE="../../.session_token"

if [ -f "$SESSION_FILE" ]; then
    rm "$SESSION_FILE"
    echo "[SECURITY] Session expired via cron hook. Identity re-verification required."
else
    # Nothing to do if already logged out
    exit 0
fi