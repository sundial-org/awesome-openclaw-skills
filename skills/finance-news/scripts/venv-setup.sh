#!/usr/bin/env bash
# Finance News - venv Setup Script
# Creates or rebuilds the Python virtual environment
# Handles NixOS libstdc++ issues automatically

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${BASE_DIR}/venv"

echo "📦 Finance News - venv Setup"
echo "============================"
echo ""

# Check Python version
PYTHON_BIN="${PYTHON_BIN:-python3}"
PYTHON_VERSION=$("$PYTHON_BIN" --version 2>&1)
echo "Using: $PYTHON_VERSION"
echo "Path:  $(command -v "$PYTHON_BIN" 2>/dev/null || echo "$PYTHON_BIN")"
echo ""

# Remove existing venv if --force flag
if [[ "$1" == "--force" || "$1" == "-f" ]]; then
    if [[ -d "$VENV_DIR" ]]; then
        echo "🗑️  Removing existing venv..."
        rm -rf "$VENV_DIR"
    fi
fi

# Check if venv exists
if [[ -d "$VENV_DIR" ]]; then
    echo "⚠️  venv already exists at $VENV_DIR"
    echo "   Use --force to rebuild"
    exit 0
fi

# Create venv
echo "📁 Creating virtual environment..."
"$PYTHON_BIN" -m venv "$VENV_DIR"

# Activate venv
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "📥 Installing dependencies..."
pip install -r "$BASE_DIR/requirements.txt" --quiet

# NixOS-specific: Add LD_LIBRARY_PATH to activate script
if [[ -d "/nix/store" ]]; then
    echo "🐧 NixOS detected - configuring libstdc++ path..."

    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

    # Find libstdc++ path
    LIBSTDCXX_PATH=""
    if [[ -d "/home/linuxbrew/.linuxbrew/lib" ]]; then
        LIBSTDCXX_PATH="/home/linuxbrew/.linuxbrew/lib"
    elif [[ -d "$HOME/.linuxbrew/lib" ]]; then
        LIBSTDCXX_PATH="$HOME/.linuxbrew/lib"
    else
        # Try nix store - only set if find returns a result
        GCC_LIB_DIR=$(find /nix/store -maxdepth 2 -name "*-gcc-*-lib" -print -quit 2>/dev/null)
        if [[ -n "$GCC_LIB_DIR" && -d "$GCC_LIB_DIR/lib" ]]; then
            LIBSTDCXX_PATH="$GCC_LIB_DIR/lib"
        fi
    fi

    if [[ -n "$LIBSTDCXX_PATH" && -d "$LIBSTDCXX_PATH" ]]; then
        # Add to activate script if not already there
        if ! grep -q "FINANCE_NEWS_LD_LIBRARY_PATH" "$ACTIVATE_SCRIPT"; then
            cat >> "$ACTIVATE_SCRIPT" << EOF

# NixOS libstdc++ fix for numpy/yfinance (added by venv-setup.sh)
if [[ -z "\${FINANCE_NEWS_LD_LIBRARY_PATH:-}" ]]; then
    export FINANCE_NEWS_LD_LIBRARY_PATH=1
    if [[ -z "\${LD_LIBRARY_PATH:-}" ]]; then
        export LD_LIBRARY_PATH="$LIBSTDCXX_PATH"
    else
        export LD_LIBRARY_PATH="$LIBSTDCXX_PATH:\$LD_LIBRARY_PATH"
    fi
fi
EOF
            echo "   Added LD_LIBRARY_PATH=$LIBSTDCXX_PATH to activate script"
        fi
    else
        echo "   ⚠️  Could not find libstdc++.so.6 path"
        echo "   Install Linuxbrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    fi
fi

# Verify installation
echo ""
echo "✅ venv created successfully!"
echo ""
echo "Verifying installation..."
"$VENV_DIR/bin/python3" -c "import feedparser; print('  ✓ feedparser')"
"$VENV_DIR/bin/python3" -c "import yfinance; print('  ✓ yfinance')" 2>/dev/null || echo "  ⚠️ yfinance import failed (may need LD_LIBRARY_PATH)"

echo ""
echo "To activate manually:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "Or just use the CLI:"
echo "  ./scripts/finance-news briefing --morning"
