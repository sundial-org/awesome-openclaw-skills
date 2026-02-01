// Package cmd implements the ecto CLI commands for managing Ghost.io sites.
// It provides commands for authentication, content management, and site configuration.
package cmd

import (
	"fmt"
	"io"
	"os"

	"github.com/spf13/cobra"
)

var siteName string

// output is the writer for command output. It defaults to os.Stdout
// but can be overridden for testing.
var output io.Writer = os.Stdout

// SetOutput sets the writer for command output.
// This is primarily used for testing.
func SetOutput(w io.Writer) {
	output = w
}

// ResetOutput resets the output writer to os.Stdout.
func ResetOutput() {
	output = os.Stdout
}

// printf writes formatted output to the current output writer.
func printf(format string, a ...interface{}) {
	fmt.Fprintf(output, format, a...)
}

// println writes a line to the current output writer.
func println(a ...interface{}) {
	fmt.Fprintln(output, a...)
}

var aiHelp bool

var rootCmd = &cobra.Command{
	Use:   "ecto",
	Short: "CLI for Ghost.io Admin API",
	Long: `ecto is a command-line tool for managing Ghost.io sites.

Configure a site:
  ecto auth add mysite --url https://mysite.ghost.io --key your-admin-api-key

Then use commands like:
  ecto posts
  ecto post create --title "My Post" --markdown-file content.md
  ecto site`,
	Run: func(cmd *cobra.Command, args []string) {
		if aiHelp {
			printAIHelp()
			return
		}
		cmd.Help()
	},
}

func printAIHelp() {
	help := `# ecto - Ghost.io Admin API CLI

## Overview
ecto is a command-line tool for managing Ghost.io blogs via the Admin API.
It supports multi-site configuration, markdown-to-HTML conversion, and JSON output for scripting.

## Authentication
Ghost Admin API uses JWT authentication with keys in format: {id}:{secret}
Get your key from Ghost Admin → Settings → Integrations → Add Custom Integration.

### Setup
ecto auth add <name> --url <ghost-url> --key <admin-api-key>
ecto auth list
ecto auth default <name>
ecto auth remove <name>

Environment variable overrides:
- GHOST_URL: Ghost site URL
- GHOST_ADMIN_KEY: Admin API key (id:secret format)
- GHOST_SITE: Site name from config

## Content Management

### Posts
ecto posts [--status draft|published|scheduled|all] [--limit N] [--json]
ecto post <id|slug> [--json] [--body]
ecto post create --title "Title" [--markdown-file file.md] [--stdin-format markdown] [--tag tag1,tag2] [--status draft|published]
ecto post edit <id|slug> [--title "New Title"] [--markdown-file file.md] [--status draft|published]
ecto post delete <id|slug> [--force]
ecto post publish <id|slug>
ecto post unpublish <id|slug>
ecto post schedule <id|slug> --at "2025-01-25T10:00:00Z"

### Pages
ecto pages [--status draft|published|all] [--limit N] [--json]
ecto page <id|slug> [--json] [--body]
ecto page create --title "Title" [--markdown-file file.md] [--status draft|published]
ecto page edit <id|slug> [--title "New Title"] [--markdown-file file.md]
ecto page delete <id|slug> [--force]
ecto page publish <id|slug>

### Tags
ecto tags [--json]
ecto tag <id|slug> [--json]
ecto tag create --name "Tag Name" [--description "desc"]
ecto tag edit <id|slug> [--name "New Name"] [--description "desc"]
ecto tag delete <id|slug> [--force]

### Images
ecto image upload <path> [--json]
Returns the uploaded image URL. Note: Ghost API does not support listing images.

## Site Information
ecto site [--json]
ecto settings [--json]
ecto users [--json]
ecto user <id|slug> [--json]
ecto newsletters [--json]
ecto newsletter <id> [--json]

## Webhooks
Note: Ghost API only supports create/delete, not listing webhooks.
ecto webhook create --event <event> --target-url <url> [--name "Hook Name"]
ecto webhook delete <id> [--force]

Webhook events: post.published, post.unpublished, post.added, post.deleted, page.published, etc.

## Multi-Site Usage
Use --site flag to specify which configured site to use:
ecto posts --site blog2
ecto post create --title "Test" --site staging

## Output Formats
All read commands support --json for machine-readable output:
ecto posts --json | jq '.posts[].title'

## Common Workflows

### Create and publish a post from markdown:
ecto post create --title "My Post" --markdown-file post.md --tag blog --status published

### Pipe content from stdin:
echo "# Hello World" | ecto post create --title "Quick Post" --stdin-format markdown

### Schedule a post:
ecto post create --title "Future Post" --markdown-file post.md
ecto post schedule future-post --at "2025-02-01T09:00:00Z"

### Batch operations with JSON:
for id in $(ecto posts --status draft --json | jq -r '.posts[].id'); do
  ecto post publish "$id"
done

## Configuration
Config file: ~/.config/ecto/config.json
{
  "default_site": "mysite",
  "sites": {
    "mysite": {
      "name": "mysite",
      "url": "https://mysite.ghost.io",
      "api_key": "id:secret"
    }
  }
}

## Error Handling
- Returns non-zero exit code on errors
- Error messages include API error details when available
- Use --force to skip confirmation prompts on destructive operations

## Limitations
- Ghost API does not support listing images or webhooks
- Member/subscription management not implemented (Admin API limitation)
- Read-only access to users (cannot create/modify via API)
`
	fmt.Fprint(output, help)
}

// Execute runs the root command and exits on error.
// This is the main entry point for the CLI.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

// RootCmd returns the root command for testing purposes.
func RootCmd() *cobra.Command {
	return rootCmd
}

func init() {
	rootCmd.PersistentFlags().StringVar(&siteName, "site", "", "site name to use (default: configured default)")
	rootCmd.PersistentFlags().BoolVar(&aiHelp, "ai-help", false, "show detailed help for LLM/AI agents")
}
