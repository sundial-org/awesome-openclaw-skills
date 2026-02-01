package cmd

import (
	"github.com/spf13/cobra"
	"github.com/visionik/ecto/internal/config"
)

var siteCmd = &cobra.Command{
	Use:   "site",
	Short: "Get site information",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")

		info, err := client.GetSite()
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(map[string]interface{}{"site": info})
		}

		printf("Title:       %s\n", info.Title)
		printf("Description: %s\n", info.Description)
		printf("URL:         %s\n", info.URL)
		printf("Version:     %s\n", info.Version)
		if info.Logo != "" {
			printf("Logo:        %s\n", info.Logo)
		}
		return nil
	},
}

var settingsCmd = &cobra.Command{
	Use:   "settings",
	Short: "Get site settings",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")

		settings, err := client.GetSettings()
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(settings)
		}

		for _, s := range settings.Settings {
			switch v := s.Value.(type) {
			case nil:
				printf("%s: \n", s.Key)
			case bool:
				printf("%s: %t\n", s.Key, v)
			case string:
				printf("%s: %s\n", s.Key, v)
			default:
				printf("%s: %v\n", s.Key, v)
			}
		}
		return nil
	},
}

func init() {
	siteCmd.Flags().Bool("json", false, "Output as JSON")
	settingsCmd.Flags().Bool("json", false, "Output as JSON")

	rootCmd.AddCommand(siteCmd)
	rootCmd.AddCommand(settingsCmd)
}
