---
name: jira-ai
version: 1.0.0
description: CLI tool for interacting with Atlassian Jira and Confluence
homepage: https://github.com/festoinc/jira-ai
metadata: {"moltbot":{"emoji":"🎫","category":"productivity","api_base":"https://github.com/festoinc/jira-ai"}}
---

# Jira-AI Skill

The jira-ai skill provides comprehensive command-line access to Atlassian Jira and Confluence platforms, allowing agents to manage issues, projects, users, and documentation efficiently.

## Installation

To install jira-ai, run:
```bash
npm install -g jira-ai
```

## Authentication Setup

Before using jira-ai, you need to configure your Jira credentials:

1. Create a `.env` file with the following values:
   ```
   JIRA_HOST=your-domain.atlassian.net
   JIRA_USER_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   ```

2. Authenticate using the .env file:
   ```bash
   jira-ai auth --from-file path/to/.env
   ```

## Configuration

You can manage settings using the settings command:

```bash
jira-ai settings --help
```

Apply settings from a YAML file:
```bash
jira-ai settings --apply my-settings.yaml
```

Validate settings:
```bash
jira-ai settings --validate my-settings.yaml
```

## Commands Overview

### Top-Level Commands

| Command | Description |
| :--- | :--- |
| `jira-ai auth` | Set up Jira authentication credentials |
| `jira-ai settings` | View, validate, or apply configuration settings |
| `jira-ai about` | Show information about the tool |
| `jira-ai help` | Display help for commands |

### Issue Management (`issue`)

| Command | Description |
| :--- | :--- |
| `jira-ai issue get <issue-id>` | Retrieve comprehensive issue data |
| `jira-ai issue create` | Create a new Jira issue |
| `jira-ai issue search <jql-query>` | Execute a JQL search query |
| `jira-ai issue transition <issue-id> <to-status>` | Change the status of a Jira issue |
| `jira-ai issue update <issue-id>` | Update a Jira issue's description |
| `jira-ai issue comment <issue-id>` | Add a new comment to a Jira issue |
| `jira-ai issue stats <issue-ids>` | Calculate time-based metrics for issues |
| `jira-ai issue assign <issue-id> <account-id>` | Assign or reassign a Jira issue |
| `jira-ai issue label add <issue-id> <labels>` | Add labels to a Jira issue |
| `jira-ai issue label remove <issue-id> <labels>` | Remove labels from a Jira issue |

### Project Management (`project`)

| Command | Description |
| :--- | :--- |
| `jira-ai project list` | List all accessible Jira projects |
| `jira-ai project statuses <project-key>` | Fetch workflow statuses for a project |
| `jira-ai project types <project-key>` | List issue types available for a project |

### User Management (`user`)

| Command | Description |
| :--- | :--- |
| `jira-ai user me` | Show profile details for authenticated user |
| `jira-ai user search [project-key]` | Search and list users |
| `jira-ai user worklog <person> <timeframe>` | Retrieve worklogs for a user |

### Organization Management (`org`)

| Command | Description |
| :--- | :--- |
| `jira-ai org list` | List all saved Jira organization profiles |
| `jira-ai org use <alias>` | Switch the active Jira organization profile |
| `jira-ai org add <alias>` | Add a new Jira organization profile |
| `jira-ai org remove <alias>` | Delete credentials for an organization |

### Confluence Commands (`confl`)

| Command | Description |
| :--- | :--- |
| `jira-ai confl get <url>` | Download Confluence page content |
| `jira-ai confl spaces` | List all allowed Confluence spaces |
| `jira-ai confl pages <space-key>` | Display pages within a space |
| `jira-ai confl create <space> <title> [parent-page]` | Create a new Confluence page |
| `jira-ai confl comment <url>` | Add a comment to a Confluence page |
| `jira-ai confl update <url>` | Update a Confluence page |

## Usage Examples

### Search for issues assigned to the current user
```bash
jira-ai issue search "assignee = currentUser()"
```

### Get details of a specific issue
```bash
jira-ai issue get PROJ-123
```

### Create a new issue
```bash
jira-ai issue create --project "PROJ" --summary "New task" --issuetype "Story"
```

### Transition an issue to a new status
```bash
jira-ai issue transition PROJ-123 "In Progress"
```

### Add a comment to an issue
```bash
jira-ai issue comment PROJ-123 --file comment.md
```

### List all projects
```bash
jira-ai project list
```

### Get worklogs for a user
```bash
jira-ai user worklog john.doe@example.com 2w
```

## Configuration Options

The jira-ai tool supports extensive configuration through settings files. You can define:

- Allowed Jira projects
- Allowed commands
- Allowed Confluence spaces
- Default behaviors for various operations

Example settings structure:
```yaml
defaults:
  allowed-jira-projects:
    - all                     # Allow all projects
  allowed-commands:
    - all                     # Allow all commands
  allowed-confluence-spaces:
    - all                     # Allow all Confluence spaces

organizations:
  work:
    allowed-jira-projects:
      - PROJ                  # Allow specific project
      - key: PM               # Project-specific config
        commands:
          - issue.get         # Only allow reading issues
        filters:
          participated:
            was_assignee: true
    allowed-commands:
      - issue                 # All issue commands
      - project.list          # Only project list
      - user.me               # Only user me
    allowed-confluence-spaces:
      - DOCS
```

## Benefits

- **Efficient API Usage**: Minimizes the number of API calls needed to perform common operations
- **Batch Operations**: Process multiple items at once to reduce API usage
- **Smart Filtering**: Use JQL to retrieve only the specific data needed
- **Local Processing**: Handle operations locally before sending targeted requests to Jira
- **Configuration-Based Access Control**: Define allowed commands and projects to prevent unauthorized operations
- **Specific Command Targeting**: Get only the information needed, reducing payload sizes and API usage

## Security Considerations

- Store API tokens securely in environment files
- Use configuration-based access controls to limit operations
- Regularly rotate API tokens
- Limit permissions to the minimum required for operations