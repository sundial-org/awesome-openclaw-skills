# Detailed Examples

This document provides comprehensive examples of using the `request_approval` tool in various scenarios.

## Example 1: Deleting Files

**Scenario**: User asks "Delete the old log files to free up space"

**Step-by-step workflow**:

1. **Investigate first**:
   - Check what files exist: `ls -lh logs/`
   - Find: logs/2024-01/ directory
   - Contains: 1,234 files
   - Total size: 2.3GB
   - Last modified: 2 weeks ago

2. **Call request_approval**:
   - operation: "Delete the logs/2024-01/ directory"
   - context: "Contains 1,234 log files totaling 2.3GB from January 2024. These are archived application logs. A backup exists in S3 bucket 'company-logs'. Deleting will free up 2.3GB of disk space."
   - reasoning: "Disk usage is at 92% capacity. These logs are archived in S3 and no longer needed locally. The application is showing warnings about low disk space."

3. **Wait for response**:
   - If approved: "Approval granted. You may proceed with the operation."
   - If denied: "Approval denied: Please verify the S3 backup first."

4. **Act on response**:
   - If approved: Execute `rm -rf logs/2024-01/` and confirm to user
   - If denied: Tell user "The deletion was cancelled because the approver wants to verify the S3 backup first. Would you like me to check if the backup exists?"

## Example 2: Creating a Pull Request

**Scenario**: You've fixed a bug and need to create a PR

**Workflow**:

1. **Review changes**:
   - Files modified: auth.py, middleware.py, tests/test_auth.py
   - Lines changed: +47, -12
   - Branch: feature/fix-auth-bug → main

2. **Call request_approval**:
   - operation: "Create pull request: 'Fix authentication bug #1234'"
   - context: "PR will merge feature/fix-auth-bug into main branch. Changes: 3 files modified (auth.py, middleware.py, tests/test_auth.py), +47 lines, -12 lines. Adds validation for expired tokens and handles edge case where tokens expire during request processing."
   - reasoning: "Bug #1234 causes users with expired tokens to see a 500 error instead of being redirected to login. This PR fixes the issue and adds test coverage. All tests pass locally."

3. **Handle response**:
   - If approved: Create the PR using `gh pr create --title "Fix authentication bug #1234" --body "..."`
   - If denied: "Approval denied: Please add integration tests first."
     - Tell user: "The PR was not created because the reviewer wants integration tests added first. Should I add those tests now?"

## Example 3: Production Deployment

**Scenario**: User asks "Deploy version 2.4.1 to production"

**Workflow**:

1. **Gather context**:
   - Current production version: 2.4.0
   - New version: 2.4.1
   - Changes: Bug fixes for issues #1234, #1235, #1236
   - Staging status: Deployed 48 hours ago, all tests passing
   - Affected services: api-server, worker, scheduler, notifications
   - Expected downtime: ~30 seconds

2. **Call request_approval**:
   - operation: "Deploy version 2.4.1 to production environment"
   - context: "Deployment will update 4 backend services (api-server, worker, scheduler, notifications) and restart them. Expected downtime: ~30 seconds. Current version: 2.4.0. Staging deployment has been running for 48 hours with all tests passing. No customer-reported issues in staging."
   - reasoning: "This release includes critical bug fixes for issues #1234, #1235, and #1236 affecting 12% of users. The bugs cause intermittent failures in the checkout flow. Changes have been thoroughly tested in staging."

3. **Handle response**:
   - If approved: Execute deployment commands
   - If denied: "Approval denied: Please schedule during maintenance window (tonight 2-4am)."
     - Tell user: "The deployment was not approved for immediate execution. The approver requested it be scheduled during tonight's maintenance window (2-4am). Should I schedule it for then?"

## Example 4: Database Migration

**Scenario**: Running a database migration that modifies schema

**Workflow**:

1. **Review migration**:
   - Migration file: migrations/2024_01_add_user_preferences.sql
   - Actions: Add new table `user_preferences`, add foreign key to `users` table
   - Affected rows: 0 (new table, no existing data)
   - Reversible: Yes (down migration exists)

2. **Call request_approval**:
   - operation: "Run database migration: 2024_01_add_user_preferences"
   - context: "This migration creates a new table 'user_preferences' with columns id, user_id, preferences (jsonb), created_at, updated_at. It adds a foreign key constraint to the users table. No existing data will be modified. A rollback migration is available. Estimated execution time: <5 seconds."
   - reasoning: "User preferences feature requires a dedicated table to store per-user settings. The migration has been tested in dev and staging environments without issues."

3. **Handle response**:
   - If approved: Run migration, verify success, inform user
   - If denied: "Approval denied: Please run during low-traffic hours."
     - Explain to user and offer to schedule for later

## Example 5: Modifying Production Config

**Scenario**: Changing an environment variable in production

**Workflow**:

1. **Identify change**:
   - File: config/production.env
   - Variable: DATABASE_URL
   - Old value: postgres://prod-db:5432/app
   - New value: postgres://prod-db-replica:5432/app
   - Impact: Switches read operations to replica

2. **Call request_approval**:
   - operation: "Modify environment variable DATABASE_URL in production config"
   - context: "Current value: postgres://prod-db:5432/app\nNew value: postgres://prod-db-replica:5432/app\nThis switches the application to use the read replica database for read operations. The primary database will still handle writes. Services will need to be restarted for the change to take effect."
   - reasoning: "Primary database is under heavy load (85% CPU usage). Switching read operations to the replica will distribute the load and improve response times. The replica is fully synced and healthy."

3. **Handle response**:
   - If approved: Update config file, note that restart is needed
   - If denied: "Approval denied: The replica is currently 5 minutes behind. Wait for sync."
     - Inform user and monitor replica lag

## Example 6: Conditional Approval

**Scenario**: Only request approval in production, not in dev/staging

**Workflow**:

1. **Determine environment**:
   - Check current branch or environment variable
   - Production detected

2. **Conditional logic**:
   - If production: Call `request_approval` (as shown above)
   - If dev/staging: Proceed directly without approval

3. **Tell the user**:
   - Production: "I've requested approval for this operation. Waiting for response..."
   - Dev/Staging: "This is a development environment, so I'm proceeding directly without approval."

## Example 7: Bulk File Operations

**Scenario**: Deleting multiple files matching a pattern

**Workflow**:

1. **Find files**:
   - Pattern: `*.tmp` files
   - Found: 156 files across 23 directories
   - Total size: 487 MB
   - Oldest: 45 days ago

2. **Call request_approval**:
   - operation: "Delete 156 temporary files matching *.tmp pattern"
   - context: "Found 156 .tmp files across 23 directories, totaling 487 MB. Files are distributed throughout the project. Oldest file is 45 days old. These are temporary build artifacts and cache files that are safe to delete."
   - reasoning: "Cleaning up temporary files to reduce repository size and improve clone times. All files have .tmp extension indicating they are temporary. None are tracked in git."

3. **Handle response**:
   - If approved: Delete files, report count
   - If denied: Explain cancellation and ask for guidance

## Example 8: Installing Dependencies

**Scenario**: User asks to install a new npm package

**Workflow**:

1. **Identify package**:
   - Package: lodash@4.17.21
   - Type: Production dependency
   - Size: 1.4 MB
   - License: MIT

2. **Call request_approval**:
   - operation: "Install npm package: lodash@4.17.21"
   - context: "Package: lodash@4.17.21 (production dependency)\nSize: 1.4 MB\nLicense: MIT\nThis will modify package.json and package-lock.json. The package provides utility functions for data manipulation."
   - reasoning: "User requested lodash for array manipulation in the data processing module. This is a widely-used, well-maintained package with 50M+ weekly downloads."

3. **Handle response**:
   - If approved: Run `npm install lodash@4.17.21`
   - If denied: "Approval denied: Use native JavaScript methods instead."
     - Inform user and discuss alternatives

## Common Patterns

### Pattern 1: Gather Info → Request → Wait → Act

Always follow this sequence:
1. Gather information about what will be changed
2. Request approval with detailed context
3. Wait for the response
4. Act based on approval/denial

### Pattern 2: Provide Alternatives When Denied

If denied, offer alternatives:
- "Would you like me to [alternative approach] instead?"
- "Should I schedule this for later?"
- "Can I do [safer version] instead?"

### Pattern 3: Include Rollback Information

When available, mention rollback options:
- "A rollback script is available if needed"
- "This change can be reverted by restoring from backup"
- "The previous configuration is saved in [location]"

### Pattern 4: Quantify Everything

Always include numbers:
- File counts
- Sizes (MB, GB)
- Affected records
- Time estimates
- Impact metrics

This helps approvers make informed decisions quickly.
