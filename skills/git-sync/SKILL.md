---
name: git-sync
description: Automatically syncs local workspace changes to the remote GitHub repository. Use after significant changes or periodically.
tags: [git, sync, backup, version-control]
---

# Git Sync Skill

Automatically syncs local workspace changes to the remote GitHub repository.
Designed to be called by PCEC cycles or after significant changes.

## Tools

### git_sync
Commit and push changes.

- **message** (optional): Commit message. Defaults to "Auto-sync: Routine evolution update".

## Safety
- Uses `.gitignore` and `pre-commit` hooks (ADL-compliant) to prevent secret leakage.
- Checks if there are changes before committing.

## Implementation
Wrapper around `git add . && git commit && git push`.
