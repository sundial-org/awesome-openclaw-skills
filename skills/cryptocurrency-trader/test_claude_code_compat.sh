#!/bin/bash
# Test if skill will work in Claude Code's .claude/skills folder

echo "=== Cryptocurrency Trader Skill - Compatibility Check ==="
echo ""

# Check SKILL.md exists and has frontmatter
echo "✓ Checking SKILL.md..."
if [ -f "SKILL.md" ]; then
    if head -3 SKILL.md | grep -q "name:"; then
        echo "  ✅ SKILL.md has proper frontmatter"
    else
        echo "  ❌ SKILL.md missing frontmatter"
        exit 1
    fi
else
    echo "  ❌ SKILL.md not found"
    exit 1
fi

# Check requirements.txt
echo "✓ Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "  ✅ requirements.txt found"
else
    echo "  ⚠️  requirements.txt missing (optional)"
fi

# Check entry points
echo "✓ Checking entry points..."
if [ -f "skill.py" ]; then
    echo "  ✅ skill.py found"
else
    echo "  ❌ skill.py not found"
    exit 1
fi

# Check if skill.py is executable
if [ -x "skill.py" ]; then
    echo "  ✅ skill.py is executable"
else
    echo "  ⚠️  skill.py not executable (will still work with 'python skill.py')"
fi

# Test help command
echo "✓ Testing skill invocation..."
if python skill.py --help > /dev/null 2>&1; then
    echo "  ✅ skill.py --help works"
else
    echo "  ❌ skill.py --help failed"
    exit 1
fi

# Check Python version
echo "✓ Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "  ℹ️  Python version: $PYTHON_VERSION"

echo ""
echo "=== Result ==="
echo "✅ This skill is compatible with Claude Code!"
echo ""
echo "To install:"
echo "  cp -r cryptocurrency-trader-skill ~/.claude/skills/cryptocurrency-trader"
echo ""
echo "Then install dependencies:"
echo "  cd ~/.claude/skills/cryptocurrency-trader"
echo "  pip install -r requirements.txt"
echo ""
echo "Claude Code will be able to invoke it with:"
echo "  cd ~/.claude/skills/cryptocurrency-trader"
echo "  python skill.py analyze BTC/USDT --balance 10000"
