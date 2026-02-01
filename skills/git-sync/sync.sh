#!/bin/bash
# Usage: ./sync.sh ["Commit Message"]

MSG="${1:-Auto-sync: Routine evolution update}"
REPO_DIR="/home/crishaocredits/.openclaw/workspace"

cd "$REPO_DIR" || exit 1

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
  echo "Nothing to commit."
  exit 0
fi

# Add everything
git add .

# Commit (pre-commit hook will run here)
if git commit -m "$MSG"; then
  echo "Commit successful."
else
  echo "Commit failed (possibly blocked by pre-commit hook or empty)."
  exit 1
fi

# Push
if git push origin main; then
  echo "Push successful."
else
  echo "Push failed."
  exit 1
fi
