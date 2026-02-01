#!/bin/bash
# Deploy project to GitHub Pages

set -e

PROJECT_NAME=$1
GITHUB_USERNAME=$2

if [ -z "$PROJECT_NAME" ] || [ -z "$GITHUB_USERNAME" ]; then
    echo "Usage: bash deploy_github_pages.sh <project-name> <github-username>"
    exit 1
fi

echo "🚀 Deploying $PROJECT_NAME to GitHub Pages"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

cd "$PROJECT_NAME"

# Initialize git if not already
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Create GitHub repository
echo "📦 Creating GitHub repository..."
if gh repo create "$PROJECT_NAME" --public --source=. --remote=origin --push 2>/dev/null; then
    echo "✅ Repository created and pushed"
else
    echo "⚠️  Repository might already exist, adding remote..."
    git remote add origin "https://github.com/$GITHUB_USERNAME/$PROJECT_NAME.git" 2>/dev/null || true
    git push -u origin main
fi

# Enable GitHub Pages
echo "🌐 Configuring GitHub Pages..."
gh api -X POST "/repos/$GITHUB_USERNAME/$PROJECT_NAME/pages" \
    -f source[branch]=gh-pages \
    -f source[path]=/ 2>/dev/null || echo "⚠️  Pages already configured or needs manual setup"

# Trigger workflow
echo "🔄 Triggering deployment workflow..."
git push origin main

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📍 Your site will be available at:"
echo "   https://$GITHUB_USERNAME.github.io/$PROJECT_NAME/"
echo ""
echo "⏳ First deployment may take 1-2 minutes"
echo "🔗 Check status: gh workflow view"
