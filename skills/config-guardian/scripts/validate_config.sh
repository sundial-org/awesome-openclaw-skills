#!/usr/bin/env bash
set -euo pipefail

# Validate current config via OpenClaw's built-in checks + additional validation

# 1. Get OpenClaw version
VERSION=$(openclaw --version 2>/dev/null | head -1)
echo "OpenClaw version: $VERSION"

# 2. Run OpenClaw's built-in validation
echo "Running OpenClaw doctor..."
openclaw doctor --non-interactive

CONFIG_PATH="$HOME/.openclaw/openclaw.json"

# 3. Check for dangerous keys
DANGEROUS_KEYS=("system" "eval" "exec" "shell" "sudo")
for key in "${DANGEROUS_KEYS[@]}"; do
    if grep -q "\"$key\"" "$CONFIG_PATH" 2>/dev/null; then
        echo "⚠️  Warning: Found potentially dangerous key: $key"
    fi
done

# 4. Validate model IDs against allowed models
echo "Checking model IDs..."
MODELS_CONFIG=$(python3 -c "
import json, sys
d = json.load(open('$CONFIG_PATH'))
allowed = d.get('agents', {}).get('defaults', {}).get('models', {})
primary = d.get('agents', {}).get('defaults', {}).get('model', {}).get('primary')
fallbacks = d.get('agents', {}).get('defaults', {}).get('model', {}).get('fallbacks', [])
all_used = [primary] + fallbacks if primary else (fallbacks or [])
for m in all_used:
    if m and m not in allowed:
        print(f'INVALID_MODEL:{m}')
" 2>/dev/null)

if [ -n "$MODELS_CONFIG" ]; then
    echo "❌ Invalid model IDs found:"
    echo "$MODELS_CONFIG" | while read line; do
        if [[ "$line" == INVALID_MODEL:* ]]; then
            MODEL_ID="${line#INVALID_MODEL:}"
            echo "   - $MODEL_ID (not in agents.defaults.models)"
        fi
    done
    echo ""
    echo "Allowed models:"
    python3 -c "
import json
d = json.load(open('$CONFIG_PATH'))
allowed = d.get('agents', {}).get('defaults', {}).get('models', {})
for m in allowed:
    print(f'   - {m}')
" 2>/dev/null
    exit 1
fi

echo "✅ Validation complete"
