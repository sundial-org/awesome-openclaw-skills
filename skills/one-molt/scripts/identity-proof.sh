#!/usr/bin/env bash
set -euo pipefail

# Identity Proof Script
# Cryptographically sign messages to prove openclaw identity

OPENCLAW_DIR="${HOME}/.openclaw"
DEVICE_IDENTITY_FILE="${OPENCLAW_DIR}/identity/device.json"
IDENTITY_SERVER="${IDENTITY_SERVER:-https://onemolt.ai}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}$1${NC}"
}

info() {
    echo -e "${BLUE}$1${NC}"
}

warn() {
    echo -e "${YELLOW}$1${NC}"
}

# Check if device identity exists
check_identity() {
    if [[ ! -f "$DEVICE_IDENTITY_FILE" ]]; then
        error "Device identity not found at $DEVICE_IDENTITY_FILE"
    fi
}

# Sign a message using Node.js crypto
sign_message() {
    local message="$1"
    local format="${2:-json}" # json or compact

    check_identity

    node <<EOF
const crypto = require('crypto');
const fs = require('fs');

// Load device identity
const identity = JSON.parse(fs.readFileSync('${DEVICE_IDENTITY_FILE}', 'utf8'));

// Sign the message
const privateKey = crypto.createPrivateKey(identity.privateKeyPem);
const message = ${message};
const signature = crypto.sign(null, Buffer.from(message), privateKey);

// Extract public key as base64 (without PEM wrapper)
const publicKeyDer = crypto.createPublicKey(identity.publicKeyPem)
    .export({ type: 'spki', format: 'der' });
const publicKeyBase64 = publicKeyDer.toString('base64');

const result = {
    deviceId: identity.deviceId,
    publicKey: publicKeyBase64,
    message: message,
    signature: signature.toString('base64'),
    timestamp: Date.now()
};

if ('${format}' === 'json') {
    console.log(JSON.stringify(result, null, 2));
} else {
    console.log('DEVICE_ID=' + result.deviceId);
    console.log('PUBLIC_KEY=' + result.publicKey);
    console.log('MESSAGE=' + result.message);
    console.log('SIGNATURE=' + result.signature);
    console.log('TIMESTAMP=' + result.timestamp);
}
EOF
}

# Verify a signature
verify_signature() {
    local message="$1"
    local signature_b64="$2"
    local pubkey_b64="$3"

    node <<EOF
const crypto = require('crypto');

try {
    // Reconstruct public key from base64 DER
    const publicKeyDer = Buffer.from('${pubkey_b64}', 'base64');
    const publicKey = crypto.createPublicKey({
        key: publicKeyDer,
        type: 'spki',
        format: 'der'
    });

    const message = ${message};
    const signature = Buffer.from('${signature_b64}', 'base64');

    const isValid = crypto.verify(null, Buffer.from(message), publicKey, signature);

    if (isValid) {
        console.log('✓ Signature is VALID');
        process.exit(0);
    } else {
        console.log('✗ Signature is INVALID');
        process.exit(1);
    }
} catch (err) {
    console.error('Verification error:', err.message);
    process.exit(2);
}
EOF
}

# Command: register
cmd_register() {
    local challenge="${1:-}"

    if [[ -z "$challenge" ]]; then
        error "Usage: identity-proof.sh register <challenge-string>"
    fi

    info "Registering openclaw identity..."
    info "Challenge: $challenge"
    echo

    sign_message "\"$challenge\"" "json"

    echo
    success "✓ Registration signature generated!"
    warn "Share your deviceId, publicKey, and signature with the service."
    warn "NEVER share your private key!"
}

# Command: prove
cmd_prove() {
    local website_url="${1:-}"

    if [[ -z "$website_url" ]]; then
        error "Usage: identity-proof.sh prove <website-url>"
    fi

    # Validate URL format
    if [[ ! "$website_url" =~ ^https?:// ]]; then
        error "URL must start with http:// or https://"
    fi

    info "Generating proof of ownership for: $website_url"
    echo

    # Sign exactly what was provided (no timestamp modification)
    sign_message "\"$website_url\"" "json"

    echo
    success "✓ Proof signature generated!"
    info "The website can verify this signature to confirm you own the public key."
}

# Command: verify
cmd_verify() {
    local message="${1:-}"
    local signature="${2:-}"
    local pubkey="${3:-}"

    if [[ -z "$message" ]] || [[ -z "$signature" ]] || [[ -z "$pubkey" ]]; then
        error "Usage: identity-proof.sh verify <message> <signature-base64> <publickey-base64>"
    fi

    info "Verifying signature..."
    verify_signature "\"$message\"" "$signature" "$pubkey"
}

# Command: info
cmd_info() {
    check_identity

    node <<EOF
const fs = require('fs');
const identity = JSON.parse(fs.readFileSync('${DEVICE_IDENTITY_FILE}', 'utf8'));
const crypto = require('crypto');

const publicKeyDer = crypto.createPublicKey(identity.publicKeyPem)
    .export({ type: 'spki', format: 'der' });
const publicKeyBase64 = publicKeyDer.toString('base64');

console.log('Device ID:', identity.deviceId);
console.log('Public Key (base64):', publicKeyBase64);
console.log('Created:', new Date(identity.createdAtMs).toISOString());
EOF
}

# Command: register-worldid
cmd_register_worldid() {
    local server="${IDENTITY_SERVER}"

    info "Starting WorldID registration with server: $server"
    echo

    # Check if curl or wget is available
    if ! command -v curl &> /dev/null; then
        error "curl is required but not installed"
    fi

    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        warn "jq is not installed - output will be less readable"
    fi

    # Generate challenge message
    local challenge="registration-$(date +%s)"
    info "Challenge: $challenge"
    echo

    # Sign challenge
    info "Generating signature..."
    local proof=$(sign_message "\"$challenge\"" "json")

    # POST to API
    info "Sending registration request to server..."
    local response=$(curl -sL -w "\n%{http_code}" -X POST "${server}/api/v1/register/init" \
        -H "Content-Type: application/json" \
        -d "$proof")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    if [[ "$http_code" != "201" ]]; then
        error "Registration failed (HTTP $http_code): $(echo "$body" | jq -r '.error // .' 2>/dev/null || echo "$body")"
    fi

    # Extract session token and URL
    local session_token=$(echo "$body" | jq -r '.sessionToken' 2>/dev/null)
    local reg_url=$(echo "$body" | jq -r '.registrationUrl' 2>/dev/null)
    local expires_at=$(echo "$body" | jq -r '.expiresAt' 2>/dev/null)

    if [[ -z "$session_token" ]] || [[ "$session_token" == "null" ]]; then
        error "Failed to get session token from server"
    fi

    echo
    echo "════════════════════════════════════════════════════════════════"
    success "✓ Registration session created!"
    echo "════════════════════════════════════════════════════════════════"
    echo
    info "Registration URL:"
    echo -e "${GREEN}$reg_url${NC}"
    echo
    info "Expires: $expires_at"
    echo
    warn "IMPORTANT: Complete WorldID verification in your browser to finish!"
    echo

    # User can click the link above to open in browser

    # Poll for completion
    echo
    echo "────────────────────────────────────────────────────────────────"
    info "⏳ Waiting for WorldID verification..."
    echo
    info "Steps to complete:"
    echo "  1. Open the URL above in your browser"
    echo "  2. Click 'Verify with World ID'"
    echo "  3. Scan the QR code with World App"
    echo "  4. Approve the verification in World App"
    echo
    info "Checking status every 15 seconds..."
    echo "────────────────────────────────────────────────────────────────"
    echo

    poll_registration_status "$server" "$session_token"
}

# Poll registration status
poll_registration_status() {
    local server="$1"
    local session_token="$2"
    local max_attempts=60  # 15 minutes (15s interval)
    local attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        sleep 15
        ((attempt++))

        # Show progress
        local elapsed=$((attempt * 15))
        local minutes=$((elapsed / 60))
        local seconds=$((elapsed % 60))
        printf "\r⏳ Checking status... [${minutes}m ${seconds}s elapsed]"

        local response=$(curl -sL -w "\n%{http_code}" "${server}/api/v1/register/${session_token}/status")
        local http_code=$(echo "$response" | tail -n1)
        local body=$(echo "$response" | sed '$d')

        if [[ "$http_code" != "200" ]]; then
            echo
            warn "Status check failed (HTTP $http_code)"
            continue
        fi

        local status=$(echo "$body" | jq -r '.status' 2>/dev/null)

        case "$status" in
            completed)
                echo
                echo
                echo "════════════════════════════════════════════════════════════════"
                success "    ✓ REGISTRATION SUCCESSFUL - ONE MOLT VERIFIED!"
                echo "════════════════════════════════════════════════════════════════"
                echo

                local device_id=$(echo "$body" | jq -r '.deviceId' 2>/dev/null)
                local public_key=$(echo "$body" | jq -r '.registration.publicKey' 2>/dev/null)
                local verification_level=$(echo "$body" | jq -r '.registration.verificationLevel' 2>/dev/null)
                local registered_at=$(echo "$body" | jq -r '.registration.registeredAt' 2>/dev/null)

                success "Your molt bot is now verified as operated by a unique human!"
                echo
                info "Public Key:         $public_key"
                info "Device ID:          $device_id"
                info "Verification Level: $verification_level"
                info "Registered At:      $registered_at"
                echo
                success "🔗 Share your verification:"
                echo -e "   ${GREEN}${server}/verify/${public_key}${NC}"
                echo
                info "   Tweet this: 'I verified my molt has a human behind it!'"
                echo "   https://twitter.com/intent/tweet?text=$(echo -n 'I verified my molt has a human behind it! 🤖👤 #OneMolt @worldcoin' | jq -sRr @uri)&url=$(echo -n "${server}/verify/${public_key}" | jq -sRr @uri)"
                echo
                success "What you can do now:"
                echo "  • Prove your identity to other services"
                echo "  • Other apps can verify you're a real human"
                echo "  • You have ONE molt per human (Sybil-resistant)"
                echo
                info "Next steps:"
                echo "  • Run: ./scripts/identity-proof.sh status"
                echo "  • Test: ./scripts/identity-proof.sh verify-remote \"test\""
                echo
                echo "════════════════════════════════════════════════════════════════"
                return 0
                ;;
            expired)
                echo
                error "Registration session expired. Please try again."
                ;;
            failed)
                echo
                error "Registration failed. Please try again."
                ;;
            pending)
                echo -n "."
                ;;
        esac
    done

    echo
    echo
    warn "⏱ Registration timed out after 15 minutes."
    echo
    info "The registration session has expired. Please try again:"
    echo "  ./scripts/identity-proof.sh register-worldid"
    echo
    return 1
}

# Command: verify-remote
cmd_verify_remote() {
    local message="${1:-}"
    local server="${IDENTITY_SERVER}"

    if [[ -z "$message" ]]; then
        error "Usage: identity-proof.sh verify-remote <message>"
    fi

    info "Verifying signature with remote registry: $server"
    echo

    # Sign the message
    local proof=$(sign_message "\"$message\"" "json")

    # POST to verification API
    info "Sending verification request..."
    local response=$(curl -sL -w "\n%{http_code}" -X POST "${server}/api/v1/verify/signature" \
        -H "Content-Type: application/json" \
        -d "$proof")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    if [[ "$http_code" != "200" ]]; then
        error "Verification failed (HTTP $http_code): $(echo "$body" | jq -r '.error // .' 2>/dev/null || echo "$body")"
    fi

    local verified=$(echo "$body" | jq -r '.verified' 2>/dev/null)
    local worldid_verified=$(echo "$body" | jq -r '.worldIdVerified' 2>/dev/null)
    local verification_level=$(echo "$body" | jq -r '.verificationLevel // "none"' 2>/dev/null)

    echo
    if [[ "$verified" == "true" ]]; then
        success "✓ Signature verified successfully!"
        echo

        if [[ "$worldid_verified" == "true" ]]; then
            success "✓ WorldID verified (Level: $verification_level)"
        else
            warn "⚠ Not registered with WorldID"
            info "Run 'identity-proof.sh register-worldid' to register"
        fi
    else
        error "✗ Signature verification failed"
    fi
}

# Command: status
cmd_status() {
    local server="${IDENTITY_SERVER}"

    check_identity

    info "Checking registration status with: $server"
    echo

    # Get device ID
    local device_id=$(node -e "console.log(JSON.parse(require('fs').readFileSync('${DEVICE_IDENTITY_FILE}', 'utf8')).deviceId)")

    # Check device status
    local response=$(curl -sL -w "\n%{http_code}" "${server}/api/v1/verify/device/${device_id}")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    if [[ "$http_code" != "200" ]]; then
        error "Status check failed (HTTP $http_code)"
    fi

    local registered=$(echo "$body" | jq -r '.registered' 2>/dev/null)
    local verified=$(echo "$body" | jq -r '.verified' 2>/dev/null)
    local active=$(echo "$body" | jq -r '.active' 2>/dev/null)
    local verification_level=$(echo "$body" | jq -r '.verificationLevel // "none"' 2>/dev/null)
    local registered_at=$(echo "$body" | jq -r '.registeredAt // "never"' 2>/dev/null)

    info "Device ID: $device_id"
    echo

    if [[ "$registered" == "true" ]] && [[ "$verified" == "true" ]] && [[ "$active" == "true" ]]; then
        success "✓ Registered and verified with WorldID"
        echo
        info "Verification Level: $verification_level"
        info "Registered At: $registered_at"
    elif [[ "$registered" == "true" ]]; then
        warn "⚠ Registered but not verified or inactive"
    else
        warn "⚠ Not registered with WorldID"
        echo
        info "Run 'identity-proof.sh register-worldid' to register"
    fi
}

# Main command dispatcher
main() {
    local cmd="${1:-help}"

    case "$cmd" in
        register)
            shift
            cmd_register "$@"
            ;;
        prove)
            shift
            cmd_prove "$@"
            ;;
        verify)
            shift
            cmd_verify "$@"
            ;;
        info)
            cmd_info
            ;;
        register-worldid)
            cmd_register_worldid
            ;;
        verify-remote)
            shift
            cmd_verify_remote "$@"
            ;;
        status)
            cmd_status
            ;;
        help|--help|-h)
            cat <<HELP
Identity Proof - Cryptographic Identity Management for OpenClaw

USAGE:
    identity-proof.sh <command> [arguments]

COMMANDS:
    register <challenge>              Sign a registration challenge
    prove <website-url>               Prove ownership by signing a URL
    verify <msg> <sig> <pubkey>       Verify a signature (local)
    info                              Show device identity info

    register-worldid                  Register with WorldID proof-of-personhood
    verify-remote <message>           Verify signature with remote registry
    status                            Check WorldID registration status

    help                              Show this help message

WORLDID INTEGRATION:
    The register-worldid, verify-remote, and status commands interact with
    a remote identity registry service that combines Ed25519 signatures with
    WorldID proof-of-personhood verification.

    Set the IDENTITY_SERVER environment variable to configure the server URL:
        export IDENTITY_SERVER="https://identity-registry.vercel.app"

    Default: http://localhost:3000

EXAMPLES:
    # Register with a service (traditional)
    identity-proof.sh register "challenge-abc123"

    # Prove ownership to a website
    identity-proof.sh prove "https://example.com"

    # Show your identity info
    identity-proof.sh info

    # Register with WorldID (new)
    export IDENTITY_SERVER="https://identity-registry.vercel.app"
    identity-proof.sh register-worldid

    # Verify signature remotely (new)
    identity-proof.sh verify-remote "test message"

    # Check registration status (new)
    identity-proof.sh status

HELP
            ;;
        *)
            error "Unknown command: $cmd (try 'help')"
            ;;
    esac
}

main "$@"
