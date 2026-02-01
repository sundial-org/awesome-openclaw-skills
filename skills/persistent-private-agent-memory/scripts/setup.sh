#!/bin/bash
# Setup script for local Agent Memory Service

set -e

echo "🧠 Agent Memory Service - Local Setup"
echo "======================================"

# Check dependencies
echo "Checking dependencies..."
python3 --version || { echo "Python 3 required"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv ~/.agent-memory/venv
source ~/.agent-memory/venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q fastapi uvicorn cryptography mnemonic

# Copy service code
mkdir -p ~/.agent-memory/service
cp -r "$(dirname "$0")/../assets/service/"* ~/.agent-memory/service/

# Create data directory
mkdir -p ~/.agent-memory/data

# Create startup script
cat > ~/.agent-memory/start.sh << 'EOF'
#!/bin/bash
source ~/.agent-memory/venv/bin/activate
export DB_PATH="$HOME/.agent-memory/data/memory.db"
cd ~/.agent-memory/service
uvicorn main:app --host 127.0.0.1 --port 8742 --log-level warning
EOF
chmod +x ~/.agent-memory/start.sh

# Create client config
cat > ~/.agent-memory/config.env << 'EOF'
AGENT_MEMORY_URL=http://127.0.0.1:8742
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the service:"
echo "  ~/.agent-memory/start.sh"
echo ""
echo "Service will be available at: http://127.0.0.1:8742"
