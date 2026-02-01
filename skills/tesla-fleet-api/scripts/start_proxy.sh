#!/usr/bin/env bash
set -e

# Start tesla-http-proxy in background

PROXY_DIR="${TESLA_PROXY_DIR:-$HOME/.clawdbot/tesla-fleet-api/proxy}"
GO_BIN="${HOME}/go/bin"
PROXY_BIN="${GO_BIN}/tesla-http-proxy"
PID_FILE="${PROXY_DIR}/proxy.pid"
LOG_FILE="${PROXY_DIR}/proxy.log"

if [ -z "$1" ]; then
    echo "Usage: $0 <path-to-private-key.pem>" >&2
    exit 1
fi

PRIVATE_KEY="$1"

if [ ! -f "${PRIVATE_KEY}" ]; then
    echo "Error: Private key not found: ${PRIVATE_KEY}" >&2
    exit 1
fi

if [ ! -f "${PROXY_BIN}" ]; then
    echo "Error: tesla-http-proxy not found. Run setup_proxy.sh first." >&2
    exit 1
fi

# Check if already running
if [ -f "${PID_FILE}" ]; then
    OLD_PID=$(cat "${PID_FILE}")
    if ps -p "${OLD_PID}" > /dev/null 2>&1; then
        echo "Proxy is already running (PID: ${OLD_PID})"
        exit 0
    else
        echo "Removing stale PID file..."
        rm -f "${PID_FILE}"
    fi
fi

echo "Starting tesla-http-proxy..."

# Start proxy in background
nohup "${PROXY_BIN}" \
    -key-file "${PRIVATE_KEY}" \
    -tls-key "${PROXY_DIR}/tls-key.pem" \
    -cert "${PROXY_DIR}/tls-cert.pem" \
    -host localhost \
    -port 4443 \
    >> "${LOG_FILE}" 2>&1 &

PROXY_PID=$!
echo "${PROXY_PID}" > "${PID_FILE}"

# Wait a bit and check if it's running
sleep 2
if ps -p "${PROXY_PID}" > /dev/null 2>&1; then
    echo "✓ Proxy started successfully (PID: ${PROXY_PID})"
    echo "  Listening on: https://localhost:4443"
    echo "  Logs: ${LOG_FILE}"
else
    echo "Error: Proxy failed to start. Check logs: ${LOG_FILE}" >&2
    rm -f "${PID_FILE}"
    exit 1
fi
