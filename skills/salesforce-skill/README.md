Salesforce Skill for Moltbot
A comprehensive Salesforce CRM skill for Moltbot that enables chat-based management of contacts, accounts, opportunities, leads, cases, and more.
Features

Query records via SOQL with table or JSON output
Create/Update/Delete contacts, accounts, opportunities, leads, cases
Pipeline reporting - stage summaries, closing soon, stale leads
Task management - log calls, view open tasks
Bulk operations - import/export via CSV
Helper script with common workflows

Installation
Option 1: Install from ClawdHub (when published)
bashnpx clawdhub@latest install salesforce
Option 2: Manual Installation

Copy the skill folder to your Moltbot workspace:

bash# For workspace-specific
cp -r salesforce-skill ~/.clawdbot/workspace/skills/salesforce

# Or for all agents
cp -r salesforce-skill ~/.clawdbot/skills/salesforce

Make the helper script executable:

bashchmod +x ~/.clawdbot/skills/salesforce/salesforce-helper.sh
Prerequisites
1. Install Salesforce CLI
```bash# via npm (recommended)
npm install -g @salesforce/cli
```
# or via Homebrew
brew install salesforce-cli
2. Authenticate to Salesforce
```bash# Interactive (opens browser)
sf org login web --alias myorg
```
# Headless (for servers)\
```
sf org login jwt \
  --client-id <consumer_key> \
  --jwt-key-file <path_to_key.pem> \
  --username <your_username> \
  --alias myorg
```
3. Configure Moltbot (optional)
Add to ~/.clawdbot/moltbot.json:
```
json{
  "skills": {
    "entries": {
      "salesforce": {
        "enabled": true,
        "env": {
          "SALESFORCE_TARGET_ORG": "myorg"
        }
      }
    }
  }
}
```
Usage Examples
Via chat with Moltbot:

"Show me the pipeline summary"
"Find contacts at Acme Corp"
"Create a lead for John Smith at NewCo, email john@newco.com"
"What opportunities are closing this month?"
"Update opportunity 006xxx to Negotiation stage"
"Log a call with contact 003xxx - discussed Q2 roadmap"
"Show me stale leads older than 30 days"

File Structure
salesforce/
├── SKILL.md              # Main skill definition (required)
├── salesforce-helper.sh  # Helper script for common operations
└── README.md             # This file
Publishing to ClawdHub

Fork and clone the moltbot/skills repo
Add your skill to skills/<your-username>/salesforce/
Submit a PR

Or use the ClawdHub CLI:
bashcd salesforce-skill
clawdhub publish
Customization
Add Custom Objects
Edit SKILL.md to add instructions for custom Salesforce objects:
### Query Custom Object
```bash
sf data query --query "SELECT Id, Name, Custom_Field__c FROM Custom_Object__c" --target-org myorg
```
Add Workflow Automation
Create additional helper functions in salesforce-helper.sh for your specific workflows.
Troubleshooting
ErrorSolutionsf: command not foundInstall Salesforce CLIINVALID_SESSION_IDRe-authenticate with sf org login webNo target-orgSet default with sf config set target-org myorg
License
MIT
Contributing
PRs welcome! Please test with a Salesforce Developer Edition org before submitting.
