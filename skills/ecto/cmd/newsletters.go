package cmd

import (
	"github.com/spf13/cobra"
	"github.com/visionik/ecto/internal/config"
)

var newslettersCmd = &cobra.Command{
	Use:   "newsletters",
	Short: "List newsletters",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")

		resp, err := client.ListNewsletters()
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(resp)
		}

		if len(resp.Newsletters) == 0 {
			println("No newsletters found")
			return nil
		}

		for _, n := range resp.Newsletters {
			printf("%s - %s (%s) [%s]\n", n.ID, n.Name, n.Slug, n.Status)
		}
		return nil
	},
}

var newsletterCmd = &cobra.Command{
	Use:   "newsletter <id>",
	Short: "Get a single newsletter",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")

		newsletter, err := client.GetNewsletter(args[0])
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(map[string]interface{}{"newsletters": []interface{}{newsletter}})
		}

		printf("ID:          %s\n", newsletter.ID)
		printf("Name:        %s\n", newsletter.Name)
		printf("Slug:        %s\n", newsletter.Slug)
		printf("Status:      %s\n", newsletter.Status)
		if newsletter.Description != "" {
			printf("Description: %s\n", newsletter.Description)
		}
		return nil
	},
}

func init() {
	newslettersCmd.Flags().Bool("json", false, "Output as JSON")
	newsletterCmd.Flags().Bool("json", false, "Output as JSON")

	rootCmd.AddCommand(newslettersCmd)
	rootCmd.AddCommand(newsletterCmd)
}
