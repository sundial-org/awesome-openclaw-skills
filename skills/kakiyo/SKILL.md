---
name: kakiyo
description: Official Kakiyo skill from Kakiyo.com for managing LinkedIn automation campaigns, prospects, and AI agents via Kakiyo MCP server. Use when users want to create outreach campaigns, add prospects, monitor performance, manage AI agents, or automate LinkedIn messaging. Includes 42 tools for campaigns, prospects, agents, analytics, workspaces, webhooks, and DNC management.
---

# Kakiyo LinkedIn Automation

Official skill from Kakiyo.com to control LinkedIn outreach campaigns and AI agents through the Kakiyo MCP server.

## Quick Setup (Agent-Assisted)

**Check if configured:**
```bash
mcporter config get kakiyo
```

If not configured, prompt user: "I need your Kakiyo API key to set this up. Get it from https://app.kakiyo.com → Settings → API Keys → Create API Key (40 characters)."

**Once user provides their API key, run:**
```bash
mcporter config add kakiyo https://api.kakiyo.com/mcp \
  --header "Authorization:Bearer USER_API_KEY"
```

Replace `USER_API_KEY` with the key they provide.

**Verify setup:**
```bash
mcporter call kakiyo.verify_api_key --output json
```

## Available Tools (42 total)

### Agents (5 tools)
Manage LinkedIn automation agents.

**list_agents** - List all agents with status and config
```bash
mcporter call kakiyo.list_agents --output json
```

**get_agent** - Get detailed agent info
```bash
mcporter call kakiyo.get_agent agentId:"agent_123" --output json
```

**update_agent** - Modify agent settings (working hours, limits)
```bash
mcporter call kakiyo.update_agent agentId:"agent_123" workingHours:'{"start":"09:00","end":"17:00"}' --output json
```

**pause_agent** - Stop an agent temporarily
```bash
mcporter call kakiyo.pause_agent agentId:"agent_123" --output json
```

**resume_agent** - Restart a paused agent
```bash
mcporter call kakiyo.resume_agent agentId:"agent_123" --output json
```

### Campaigns (6 tools)
Create and manage outreach campaigns.

**list_campaigns** - List all campaigns with status
```bash
mcporter call kakiyo.list_campaigns --output json
```

**get_campaign_stats** - Get performance metrics
```bash
mcporter call kakiyo.get_campaign_stats campaignId:"camp_123" --output json
```

**create_campaign** - Create new campaign
```bash
mcporter call kakiyo.create_campaign \
  name:"Tech Founders Outreach" \
  productId:"prod_123" \
  promptId:"prompt_456" \
  agentId:"agent_789" \
  --output json
```

**update_campaign** - Modify campaign settings
```bash
mcporter call kakiyo.update_campaign campaignId:"camp_123" name:"New Name" --output json
```

**pause_campaign** - Stop campaign
```bash
mcporter call kakiyo.pause_campaign campaignId:"camp_123" --output json
```

**resume_campaign** - Restart campaign
```bash
mcporter call kakiyo.resume_campaign campaignId:"camp_123" --output json
```

### Prospects (9 tools)
Manage leads and conversations.

**list_prospects** - List prospects with basic filtering
```bash
mcporter call kakiyo.list_prospects limit:50 --output json
```

**get_prospect** - Get full prospect details and conversation
```bash
mcporter call kakiyo.get_prospect prospectId:"pros_123" --output json
```

**add_prospect** - Add single LinkedIn profile to campaign
```bash
mcporter call kakiyo.add_prospect \
  campaignId:"camp_123" \
  name:"John Doe" \
  url:"https://linkedin.com/in/johndoe" \
  --output json
```

**add_prospects_batch** - Add multiple prospects at once
```bash
mcporter call kakiyo.add_prospects_batch \
  campaignId:"camp_123" \
  prospects:'[{"name":"Jane","url":"https://linkedin.com/in/jane"}]' \
  --output json
```

**search_prospects** - Advanced search with filters
```bash
mcporter call kakiyo.search_prospects status:replied limit:20 --output json
```

**list_campaign_prospects** - Get all prospects in a campaign
```bash
mcporter call kakiyo.list_campaign_prospects campaignId:"camp_123" --output json
```

**pause_prospect** - Pause outreach to specific person
```bash
mcporter call kakiyo.pause_prospect prospectId:"pros_123" --output json
```

**resume_prospect** - Resume conversation
```bash
mcporter call kakiyo.resume_prospect prospectId:"pros_123" --output json
```

**qualify_prospect** - Mark prospect as qualified lead
```bash
mcporter call kakiyo.qualify_prospect prospectId:"pros_123" --output json
```

### Analytics (2 tools)
Monitor performance and metrics.

**get_analytics_overview** - Team-wide metrics across all campaigns
```bash
mcporter call kakiyo.get_analytics_overview --output json
```

**get_campaign_analytics** - Detailed metrics for specific campaign
```bash
mcporter call kakiyo.get_campaign_analytics campaignId:"camp_123" --output json
```

### Products (1 tool)
View products/services for campaigns.

**list_products** - List all products
```bash
mcporter call kakiyo.list_products --output json
```

### Prompts (1 tool)
View AI message templates.

**list_prompts** - List all prompt templates
```bash
mcporter call kakiyo.list_prompts --output json
```

### Models (1 tool)
View available AI models.

**list_models** - List AI models for message generation
```bash
mcporter call kakiyo.list_models --output json
```

### Webhooks (5 tools)
Configure event notifications.

**list_webhooks** - List configured webhooks
```bash
mcporter call kakiyo.list_webhooks --output json
```

**create_webhook** - Set up new webhook
```bash
mcporter call kakiyo.create_webhook \
  url:"https://example.com/webhook" \
  events:'["prospect.replied","prospect.qualified"]' \
  --output json
```

**update_webhook** - Modify webhook settings
```bash
mcporter call kakiyo.update_webhook webhookId:"wh_123" url:"https://new-url.com" --output json
```

**delete_webhook** - Remove webhook
```bash
mcporter call kakiyo.delete_webhook webhookId:"wh_123" --output json
```

**list_webhook_events** - List available event types
```bash
mcporter call kakiyo.list_webhook_events --output json
```

### Do Not Contact (4 tools)
Manage blocklist.

**list_dnc** - List all blocked LinkedIn URLs
```bash
mcporter call kakiyo.list_dnc --output json
```

**add_dnc** - Block a profile from all campaigns
```bash
mcporter call kakiyo.add_dnc url:"https://linkedin.com/in/blocked" --output json
```

**remove_dnc** - Unblock a profile
```bash
mcporter call kakiyo.remove_dnc url:"https://linkedin.com/in/unblock" --output json
```

**check_dnc** - Check if URL is blocked
```bash
mcporter call kakiyo.check_dnc url:"https://linkedin.com/in/check" --output json
```

### Workspaces (7 tools)
Manage client workspaces (for agencies).

**list_workspaces** - List all client workspaces
```bash
mcporter call kakiyo.list_workspaces --output json
```

**create_workspace** - Create new client workspace
```bash
mcporter call kakiyo.create_workspace name:"Acme Corp" --output json
```

**delete_workspace** - Delete workspace
```bash
mcporter call kakiyo.delete_workspace workspaceId:"ws_123" --output json
```

**invite_client** - Invite client user via email
```bash
mcporter call kakiyo.invite_client workspaceId:"ws_123" email:"client@example.com" --output json
```

**remove_client** - Remove client from workspace
```bash
mcporter call kakiyo.remove_client workspaceId:"ws_123" userId:"user_123" --output json
```

**assign_agent_to_workspace** - Assign agent to client
```bash
mcporter call kakiyo.assign_agent_to_workspace workspaceId:"ws_123" agentId:"agent_123" --output json
```

**unassign_agent_from_workspace** - Remove agent from workspace
```bash
mcporter call kakiyo.unassign_agent_from_workspace workspaceId:"ws_123" agentId:"agent_123" --output json
```

### Authentication (1 tool)
Verify connection.

**verify_api_key** - Check if API key is valid
```bash
mcporter call kakiyo.verify_api_key --output json
```

## Common Usage Patterns

### Check Campaign Performance
"How are my LinkedIn campaigns doing?"
```bash
mcporter call kakiyo.get_analytics_overview --output json
```

### Find Replied Prospects
"Show me everyone who replied this week"
```bash
mcporter call kakiyo.search_prospects status:replied --output json
```

### Add Prospects to Campaign
"Add these LinkedIn profiles to my Tech Founders campaign"
1. Get campaign ID: `mcporter call kakiyo.list_campaigns`
2. Add prospects: `mcporter call kakiyo.add_prospects_batch campaignId:"..." prospects:'[...]'`

### Pause Agent for Weekend
"Stop my agent for the weekend"
```bash
mcporter call kakiyo.pause_agent agentId:"agent_123" --output json
```

### Agency: Setup New Client
"Create workspace for new client Acme Corp and assign Agent-1"
```bash
mcporter call kakiyo.create_workspace name:"Acme Corp" --output json
mcporter call kakiyo.assign_agent_to_workspace workspaceId:"ws_xxx" agentId:"agent_123" --output json
```

## Troubleshooting

**"Server not found" error:**
Run setup again with correct API key from https://app.kakiyo.com

**Check configuration:**
```bash
mcporter config get kakiyo
```

**Test connection:**
```bash
mcporter call kakiyo.verify_api_key --output json
```

**Re-configure:**
```bash
mcporter config remove kakiyo
mcporter config add kakiyo https://api.kakiyo.com/mcp \
  --header "Authorization:Bearer YOUR_API_KEY"
```

## Best Practices

1. **Check analytics regularly** - Monitor response rates and adjust messaging
2. **Use DNC list** - Respect people who opt out
3. **Pause agents during holidays** - Avoid sending during off-hours
4. **Qualify leads promptly** - Mark prospects as qualified for tracking
5. **Set up webhooks** - Get real-time notifications for important events

## Additional Resources

- Documentation: https://docs.kakiyo.com
- Dashboard: https://app.kakiyo.com
- MCP Server Details: https://docs.kakiyo.com/mcp-server
- API Reference: https://docs.kakiyo.com/api-reference
