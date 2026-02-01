package cmd

import (
	"fmt"
	"strings"

	"github.com/spf13/cobra"
	"github.com/visionik/ecto/internal/config"
	"github.com/visionik/libecto"
)

var webhookCmd = &cobra.Command{
	Use:   "webhook",
	Short: "Manage webhooks (create/delete only - Ghost API doesn't support listing)",
}

var webhookCreateCmd = &cobra.Command{
	Use:   "create",
	Short: "Create a new webhook",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		event, _ := cmd.Flags().GetString("event")
		targetURL, _ := cmd.Flags().GetString("target-url")
		name, _ := cmd.Flags().GetString("name")

		if event == "" || targetURL == "" {
			return fmt.Errorf("--event and --target-url are required")
		}

		webhook := &libecto.Webhook{
			Event:     event,
			TargetURL: targetURL,
			Name:      name,
		}

		created, err := client.CreateWebhook(webhook)
		if err != nil {
			return err
		}

		printf("Created webhook: %s (%s -> %s)\n", created.ID, created.Event, created.TargetURL)
		return nil
	},
}

var webhookDeleteCmd = &cobra.Command{
	Use:   "delete <id>",
	Short: "Delete a webhook",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		force, _ := cmd.Flags().GetBool("force")

		if !force {
			printf("Delete webhook %s? [y/N]: ", args[0])
			var answer string
			fmt.Scanln(&answer)
			if strings.ToLower(answer) != "y" {
				println("Cancelled")
				return nil
			}
		}

		if err := client.DeleteWebhook(args[0]); err != nil {
			return err
		}

		printf("Deleted webhook: %s\n", args[0])
		return nil
	},
}

func init() {
	webhookCreateCmd.Flags().String("event", "", "Webhook event (e.g., post.published)")
	webhookCreateCmd.Flags().String("target-url", "", "Target URL for webhook")
	webhookCreateCmd.Flags().String("name", "", "Webhook name (optional)")

	webhookDeleteCmd.Flags().Bool("force", false, "Delete without confirmation")

	webhookCmd.AddCommand(webhookCreateCmd)
	webhookCmd.AddCommand(webhookDeleteCmd)

	rootCmd.AddCommand(webhookCmd)
}
