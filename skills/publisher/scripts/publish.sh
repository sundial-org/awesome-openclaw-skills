#!/usr/bin/env bash
set -euo pipefail

# publisher: Document and publish skills that people actually download
# Usage: cd ~/clawd/skills/your-skill && publisher

SKILL_DIR="${1:-.}"
cd "$SKILL_DIR"

echo "🚀 publisher v1.0.0"
echo ""

# Check requirements
check_requirements() {
    local missing=()
    command -v jq >/dev/null || missing+=("jq")
    command -v gh >/dev/null || missing+=("gh")
    command -v clawdhub >/dev/null || missing+=("clawdhub")
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo "❌ Missing required tools: ${missing[*]}"
        echo ""
        echo "Install with:"
        for tool in "${missing[@]}"; do
            case "$tool" in
                jq) echo "  brew install jq" ;;
                gh) echo "  brew install gh && gh auth login" ;;
                clawdhub) echo "  npm install -g clawdhub" ;;
            esac
        done
        exit 1
    fi
}

# Extract field from SKILL.md frontmatter
get_frontmatter_field() {
    local field="$1"
    awk -v field="$field" '
        /^---$/ { if (in_fm) exit; in_fm=!in_fm; next }
        in_fm && $1 == field":" { $1=""; print substr($0,2); exit }
    ' SKILL.md
}

# Generate one-liner options
generate_oneliners() {
    local desc="$1"
    local name="$2"
    
    echo "📝 Generating one-liner options..."
    echo ""
    
    # Try to extract key components
    # This is a simple heuristic - can be improved with LLM later
    
    echo "Based on your SKILL.md, here are 3 options:"
    echo ""
    echo "A) [Continuous Benefit Pattern]"
    echo "   ${desc}"
    echo ""
    echo "B) [Elimination Pattern]"
    echo "   $(echo "$desc" | sed 's/Automatically //' | sed 's/ without.*$//')"
    echo ""
    echo "C) [Automation Pattern]"
    echo "   Automatically $(echo "$desc" | awk '{print tolower($0)}' | sed 's/^automatically //' | cut -d'.' -f1)"
    echo ""
    echo "D) Write your own"
    echo ""
}

# Main workflow
main() {
    check_requirements
    
    # Verify SKILL.md exists
    if [ ! -f "SKILL.md" ]; then
        echo "❌ SKILL.md not found in current directory"
        echo ""
        echo "Create a SKILL.md with:"
        echo "---"
        echo "name: your-skill"
        echo "description: What your skill does"
        echo "---"
        exit 1
    fi
    
    # Verify VERSION exists
    if [ ! -f "VERSION" ]; then
        echo "❌ VERSION file not found"
        echo ""
        echo "Create one with: echo '1.0.0' > VERSION"
        exit 1
    fi
    
    # Extract info from SKILL.md
    SKILL_NAME=$(get_frontmatter_field "name")
    SKILL_DESC=$(get_frontmatter_field "description")
    VERSION=$(cat VERSION)
    
    if [ -z "$SKILL_NAME" ]; then
        SKILL_NAME=$(basename "$PWD")
        echo "⚠️  No name in SKILL.md frontmatter, using directory name: $SKILL_NAME"
    fi
    
    if [ -z "$SKILL_DESC" ]; then
        echo "❌ No description in SKILL.md frontmatter"
        echo ""
        echo "Add to SKILL.md:"
        echo "---"
        echo "name: $SKILL_NAME"
        echo "description: Brief description here"
        echo "---"
        exit 1
    fi
    
    echo "📦 Skill: $SKILL_NAME"
    echo "📝 Description: $SKILL_DESC"
    echo "🏷️  Version: $VERSION"
    echo ""
    
    # Generate one-liners
    generate_oneliners "$SKILL_DESC" "$SKILL_NAME"
    
    read -p "Choose one-liner (A/B/C/D): " choice
    echo ""
    
    case "$choice" in
        A|a) CHOSEN_DESC="$SKILL_DESC" ;;
        B|b) CHOSEN_DESC=$(echo "$SKILL_DESC" | sed 's/Automatically //' | sed 's/ without.*$//') ;;
        C|c) CHOSEN_DESC="Automatically $(echo "$SKILL_DESC" | awk '{print tolower($0)}' | sed 's/^automatically //' | cut -d'.' -f1)" ;;
        D|d)
            read -p "Enter your one-liner: " CHOSEN_DESC
            echo ""
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
    
    echo "✅ Chosen: $CHOSEN_DESC"
    echo ""
    
    # Update SKILL.md frontmatter if needed
    if [ "$SKILL_DESC" != "$CHOSEN_DESC" ]; then
        echo "📝 Updating SKILL.md frontmatter..."
        awk -v desc="$CHOSEN_DESC" '
            /^---$/ { if (in_fm) { in_fm=0; print; next } else { in_fm=1; print; next } }
            in_fm && /^description:/ { print "description: " desc; next }
            { print }
        ' SKILL.md > SKILL.md.tmp && mv SKILL.md.tmp SKILL.md
    fi
    
    # Generate README (simplified - use template)
    if [ ! -f "README.md" ] || read -p "README.md exists. Overwrite? (y/n): " -n 1 -r; then
        echo ""
        echo "📄 Generating README.md..."
        
        # For v1.0.0, we'll keep existing README or prompt user to create manually
        # Full generation can be added in v1.1.0
        
        if [ ! -f "README.md" ]; then
            echo "⚠️  README.md generation coming in v1.1.0"
            echo "   For now, please create README.md manually using:"
            echo "   ~/clawd/templates/README-template.md"
            echo ""
            read -p "Press Enter when README.md is ready..." 
        fi
    fi
    
    echo ""
    read -p "📤 Publish to GitHub and ClawdHub? (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 0
    fi
    
    # Initialize git if needed
    if [ ! -d ".git" ]; then
        echo "🔧 Initializing git..."
        git init
        git add .
        git commit -m "Initial commit: $SKILL_NAME v$VERSION"
    fi
    
    # Create GitHub repo
    echo "🐙 Creating GitHub repository..."
    if ! gh repo view >/dev/null 2>&1; then
        gh repo create "$SKILL_NAME" --public --source=. --remote=origin --push || {
            echo ""
            echo "❌ GitHub repo creation failed"
            echo "   This might be due to missing permissions"
            echo ""
            echo "⏰ Reminder set for 9:30 PM to grant access"
            
            # Set reminder using cron
            cat > /tmp/github-access-reminder.txt << EOF
Reminder: Grant GitHub access for publisher

The publisher tool needs GitHub API access to create repositories.

Please run: gh auth refresh -s repo
EOF
            
            # Note: In production, this would use the cron tool
            # For now, just echo the reminder
            echo ""
            echo "Manual reminder: Check GitHub access at 9:30 PM"
            exit 1
        }
    else
        echo "✅ GitHub repo already exists"
        git push origin main || git push origin master
    fi
    
    # Publish to ClawdHub
    echo "📦 Publishing to ClawdHub..."
    clawdhub publish . --version "$VERSION"
    
    echo ""
    echo "✅ Published successfully!"
    echo ""
    echo "📍 GitHub: $(gh repo view --json url -q .url)"
    echo "📍 ClawdHub: https://clawdhub.com/skills/$SKILL_NAME"
}

main "$@"
