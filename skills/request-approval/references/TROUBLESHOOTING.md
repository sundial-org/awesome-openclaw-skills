# Troubleshooting

This document covers common issues when using the `request_approval` tool and how to resolve them.

## Connection Issues

### Error: "Tool not found"

**Cause**: The MCP server is not properly configured or the agent cannot connect to it.

**Solutions**:
1. Verify Preloop is configured in your agent's MCP settings
2. Check the URL is correct:
   - Production: `https://preloop.ai/mcp/v1`
   - Self-hosted: `https://your-instance.com/mcp/v1`
   - Local: `http://localhost:8000/mcp/v1`
3. Restart your agent after making configuration changes
4. Check network connectivity to the Preloop instance
5. Review agent logs for connection errors

**Testing**:
```bash
# Test if the MCP endpoint is accessible
curl https://preloop.ai/mcp/v1/health

# Should return a success response
```

### Error: "MCP server not responding"

**Cause**: The Preloop instance is down or unreachable.

**Solutions**:
1. Check if the Preloop instance is running
2. Verify your internet connection
3. Check for firewall or proxy blocking the connection
4. Try accessing the Preloop web interface to confirm it's online
5. Contact your Preloop administrator if self-hosted

## Authentication Issues

### Error: "Unauthorized" or "403 Forbidden"

**Cause**: Missing or invalid API token.

**Solutions**:
1. Generate an API token in Preloop:
   - Log in to Preloop
   - Go to Settings → API Tokens
   - Create a new token
   - Copy the token value
2. Add the token to your MCP configuration:
   ```json
   {
     "mcpServers": {
       "preloop": {
         "url": "https://preloop.ai/mcp/v1",
         "headers": {
           "Authorization": "Bearer YOUR_TOKEN_HERE"
         }
       }
     }
   }
   ```
3. Restart your agent

### Error: "Token expired"

**Cause**: Your API token has expired.

**Solutions**:
1. Generate a new API token in Preloop
2. Update your MCP configuration with the new token
3. Restart your agent

## Approval Policy Issues

### Error: "No default approval policy found"

**Cause**: Your Preloop account doesn't have a default approval policy configured.

**Solutions**:
1. Log in to Preloop
2. Navigate to Settings → Approval Policies
3. Create a new approval policy:
   - Name: "Default Agent Approval"
   - Notification method: Slack, email, mobile app, or webhook
   - Approvers: Select users/teams who can approve
   - Timeout: 5 minutes (or your preference)
   - **Check "Set as Default"**
4. Save the policy
5. Try the approval request again

### Error: "Approval policy 'xyz' not found"

**Cause**: You specified a policy name that doesn't exist.

**Solutions**:
1. Check the policy name for typos
2. Verify the policy exists in Preloop (Settings → Approval Policies)
3. Use the exact policy name (case-sensitive)
4. Or omit the `approval_policy` parameter to use the default

## Timeout Issues

### Error: "Approval timed out"

**Cause**: No one approved or declined within the configured timeout period (default 5 minutes).

**What to do**:
1. Treat this as a denial - do NOT proceed with the operation
2. Inform the user: "The approval request timed out after 5 minutes. No one responded to the request."
3. Ask if they want to retry or take a different approach
4. Consider increasing the timeout in the approval policy if this happens frequently

### Approval is taking too long

**Not an error, but...**:

If approvals are consistently slow:
1. Check that approvers are receiving notifications
2. Verify notification channels are working (Slack, email, etc.)
3. Consider adding more approvers to the policy
4. Adjust the timeout if needed for your workflow

## Request Issues

### Error: "Invalid parameters"

**Cause**: Missing or malformed required parameters.

**Solutions**:
1. Verify all required parameters are provided:
   - `operation` (string, required)
   - `context` (string, required)
   - `reasoning` (string, required)
2. Check parameter types (all should be strings)
3. Ensure parameters are not empty

**Example of correct usage**:
```javascript
request_approval(
  operation: "Delete file: config.yml",
  context: "Production config file, 2KB",
  reasoning: "User requested deletion"
)
```

### Error: "Request failed"

**Cause**: Generic error during request processing.

**Solutions**:
1. Check the full error message for details
2. Verify the Preloop instance is healthy
3. Check agent logs for more information
4. Retry the request
5. Contact support if the issue persists

## Notification Issues

### Approvers aren't receiving notifications

**Cause**: Notification channels not configured or disabled.

**Solutions**:
1. Verify the approval policy has notification methods configured
2. Check that approvers have notification preferences enabled:
   - Log in to Preloop
   - Go to Settings → Notification Preferences
   - Enable email, mobile push, or other channels
3. For Slack:
   - Verify the Slack integration is connected
   - Check the webhook URL is correct
   - Test the Slack channel
4. For email:
   - Check spam/junk folders
   - Verify email addresses are correct
   - Check SMTP settings in Preloop

### Mobile notifications not working

**Cause**: Push notification service not configured or device not registered.

**Solutions**:
1. Install the Preloop mobile app (iOS or Android)
2. Log in to your account
3. Grant notification permissions when prompted
4. Verify your device is registered:
   - Open mobile app
   - Go to Settings → Devices
   - Your device should be listed
5. Test with a sample approval request

## Response Issues

### Unclear whether approval was granted

**Problem**: Response message is ambiguous.

**What to do**:
1. Check if the response contains "denied" (case-insensitive) → treat as denial
2. Check if the response contains "approved" or "granted" → treat as approval
3. If still unclear:
   - Err on the side of caution
   - Do NOT proceed with the operation
   - Ask the user for clarification
   - Log the unexpected response format

### Response seems wrong

**Problem**: Approval was granted but you're unsure it should have been.

**What to do**:
1. Trust the approval - the human approver has made their decision
2. Proceed with the operation as approved
3. If you have serious concerns, you can:
   - Inform the user of your concerns
   - Suggest they verify the approval was intentional
   - But ultimately respect the approval if the user confirms

## Common Mistakes

### Mistake 1: Calling approval AFTER the operation

**Wrong**:
```
1. Delete the file
2. Call request_approval
```

**Right**:
```
1. Call request_approval
2. Wait for approval
3. Delete the file
```

### Mistake 2: Proceeding when denied

**Wrong**:
```
Response: "Approval denied"
Agent: *deletes the file anyway*
```

**Right**:
```
Response: "Approval denied"
Agent: "The operation was cancelled because approval was denied."
```

### Mistake 3: Vague descriptions

**Wrong**:
```javascript
request_approval(
  operation: "Delete stuff",
  context: "Some files",
  reasoning: "Cleanup"
)
```

**Right**:
```javascript
request_approval(
  operation: "Delete 47 temporary files in /tmp/cache/",
  context: "47 .tmp files totaling 234 MB, created >30 days ago",
  reasoning: "Disk usage at 90%, cleaning old temp files"
)
```

### Mistake 4: Bundling multiple operations

**Wrong**:
```javascript
request_approval(
  operation: "Delete logs, update config, and restart services",
  ...
)
```

**Right**:
```javascript
// Request 1
request_approval(
  operation: "Delete logs from /var/log/old/",
  ...
)

// Request 2
request_approval(
  operation: "Update production config: database URL",
  ...
)

// Request 3
request_approval(
  operation: "Restart application services",
  ...
)
```

## Getting Help

If you're still stuck:

1. **Check Preloop Status**:
   - Visit status.preloop.ai (if available)
   - Check for known issues or maintenance

2. **Review Logs**:
   - Agent logs for connection/request errors
   - Preloop logs (if self-hosted) for server-side issues

3. **Contact Support**:
   - Documentation: https://docs.preloop.ai
   - Community: https://community.preloop.ai
   - GitHub Issues: https://github.com/preloop/preloop/issues
   - Email: support@preloop.ai (for enterprise customers)

4. **Provide Details**:
   When reporting issues, include:
   - Error message (full text)
   - Agent type and version
   - Preloop instance URL (without tokens)
   - Steps to reproduce
   - Relevant logs (sanitized)

## Debug Checklist

When troubleshooting, verify:

- [ ] Preloop MCP server is configured in agent settings
- [ ] MCP server URL is correct
- [ ] Agent has been restarted after configuration changes
- [ ] Preloop instance is accessible (try opening in browser)
- [ ] API token is valid (if authentication required)
- [ ] Default approval policy is configured in Preloop
- [ ] Approvers have notification preferences enabled
- [ ] All required parameters are provided in request
- [ ] Request includes specific, detailed information
- [ ] Not proceeding with operation if approval denied

If all items are checked and it still doesn't work, contact support with the error details.
