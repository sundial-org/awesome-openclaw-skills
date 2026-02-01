---
name: github-issues
description: Fetch and manage GitHub issues via the API
metadata: {"openclaw": {"requires": {"env": ["GITHUB_TOKEN"], "bins": ["curl"]}}}
---

# GitHub Issues

This skill lets you list, create, and manage GitHub issues.

## Usage
- "Show me open issues for repo X"
- "Create a new issue titled Y in repo Z"

## Configuration
Set `GITHUB_TOKEN` in your environment with a personal access token.
The token needs `repo` scope for private repositories.
