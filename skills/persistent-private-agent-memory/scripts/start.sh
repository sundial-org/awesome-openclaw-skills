#!/bin/bash
# Start the Agent Memory Service

SERVICE_DIR="${SERVICE_DIR:-$(dirname "$0")/../assets/service}"
DB_PATH="${DB_PATH:-/tmp/agent-memory-data/agent_memory.db}"

# Create data directory
mkdir -p "$(dirname "$DB_PATH")"

echo "🧠 Starting Agent Memory Service..."
echo "   Database: $DB_PATH"
echo "   Service directory: $SERVICE_DIR"

cd "$SERVICE_DIR" || exit 1

# Check if already running
if [ -f /tmp/memory-service.pid ]; then
    PID=$(cat /tmp/memory-service.pid)
    if kill -0 "$PID" 2>/dev/null; then
        echo "✅ Service already running (PID: $PID)"
        exit 0
    fi
fi

# Start service
export DB_PATH
python3 main.py > /tmp/memory-service.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > /tmp/memory-service.pid

echo "🚀 Service started on PID $NEW_PID"
echo "   Health check: curl http://127.0.0.1:8000/health"
echo "   Logs: tail -f /tmp/memory-service.log"

# Wait a moment and check
sleep 2
if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "✅ Service is running!"
else
    echo "❌ Failed to start. Check logs: /tmp/memory-service.log"
    exit 1
fi
