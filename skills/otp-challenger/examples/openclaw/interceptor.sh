#!/bin/bash
# Identity Interceptor for OpenClaw
# Usage: Register this in .openclaw/settings.json as a PostGenerate hook.

RESPONSE_TEXT="$1"

# 1. Define 'Sensitive' patterns (AWS, NewRelic, GitHub, SSH/PEM)
# Patterns cover Access Keys, Secret Keys, and Private Key headers
AWS_REGEX="(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPJ|ASIA)[A-Z0-9]{16}"
NR_REGEX="NRRA-[a-f0-9]{42}"
GH_REGEX="(ghp|gho|ghs|ghr|ghu)_[A-Za-z0-9_]{36,255}"
SSH_REGEX="-----BEGIN (RSA|OPENSSH|PEM) PRIVATE KEY-----"

if [[ $RESPONSE_TEXT =~ $AWS_REGEX || $RESPONSE_TEXT =~ $NR_REGEX || $RESPONSE_TEXT =~ $GH_REGEX || $RESPONSE_TEXT =~ $SSH_REGEX ]]; then
    
    # 2. Check current identity status via otp-challenger
    ../../check-status.sh > /dev/null
    
    if [ $? -ne 0 ]; then
        # 3. Block the output and send a challenge instead
        echo "[SECURITY BLOCK]: The AI attempted to output sensitive data. Please provide your OTP code using 'verify_identity' to unlock this response."
        exit 1
    fi
fi

# 4. If safe or verified, release the response
echo "$RESPONSE_TEXT"