#!/usr/bin/env bash
set -e

# Tesla Fleet API - HTTP Proxy Setup
# This script installs Go (if needed), builds tesla-http-proxy, and generates TLS certs.

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROXY_DIR="${TESLA_PROXY_DIR:-$HOME/.clawdbot/tesla-fleet-api/proxy}"
GO_BIN="${HOME}/go/bin"

echo "==> Tesla Fleet API Proxy Setup"
echo ""

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "Go is not installed. Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Error: Homebrew is required but not installed." >&2
        echo "Visit: https://brew.sh" >&2
        exit 1
    fi
    brew install go
else
    echo "✓ Go is already installed: $(go version)"
fi

# Create proxy directory
mkdir -p "${PROXY_DIR}"
cd "${PROXY_DIR}"

# Build tesla-http-proxy if not already present
if [ ! -f "${GO_BIN}/tesla-http-proxy" ]; then
    echo ""
    echo "==> Building tesla-http-proxy..."
    
    # Clone vehicle-command repo to temp dir
    TEMP_DIR="$(mktemp -d)"
    trap "rm -rf ${TEMP_DIR}" EXIT
    
    git clone --depth 1 https://github.com/teslamotors/vehicle-command.git "${TEMP_DIR}/vehicle-command"
    cd "${TEMP_DIR}/vehicle-command"
    
    # Build
    go build -o tesla-http-proxy cmd/tesla-http-proxy/main.go
    
    # Install to ~/go/bin
    mkdir -p "${GO_BIN}"
    mv tesla-http-proxy "${GO_BIN}/"
    chmod +x "${GO_BIN}/tesla-http-proxy"
    
    echo "✓ Installed tesla-http-proxy to ${GO_BIN}/tesla-http-proxy"
else
    echo "✓ tesla-http-proxy already installed"
fi

# Generate TLS certificates if not present
cd "${PROXY_DIR}"
if [ ! -f tls-cert.pem ] || [ ! -f tls-key.pem ]; then
    echo ""
    echo "==> Generating self-signed TLS certificate for localhost..."
    openssl req -x509 -newkey rsa:4096 -keyout tls-key.pem -out tls-cert.pem -days 365 -nodes -subj "/CN=localhost" > /dev/null 2>&1
    chmod 600 tls-key.pem
    echo "✓ Generated TLS certificates in ${PROXY_DIR}"
else
    echo "✓ TLS certificates already exist"
fi

echo ""
echo "==> Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure you have a Tesla private key (ECDSA P-256)"
echo "2. Start the proxy with:"
echo "   ${SKILL_DIR}/scripts/start_proxy.sh /path/to/private-key.pem"
echo ""
