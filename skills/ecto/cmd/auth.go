package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
	"github.com/visionik/ecto/internal/config"
)

var authCmd = &cobra.Command{
	Use:   "auth",
	Short: "Manage site authentication",
}

var authAddCmd = &cobra.Command{
	Use:   "add <name>",
	Short: "Add a new site configuration",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]
		url, _ := cmd.Flags().GetString("url")
		key, _ := cmd.Flags().GetString("key")

		if url == "" || key == "" {
			return fmt.Errorf("--url and --key are required")
		}

		cfg, err := config.Load()
		if err != nil {
			return err
		}

		if err := cfg.AddSite(name, url, key); err != nil {
			return err
		}

		printf("Added site %q\n", name)
		if cfg.DefaultSite == name {
			println("Set as default site")
		}
		return nil
	},
}

var authListCmd = &cobra.Command{
	Use:   "list",
	Short: "List configured sites",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.Load()
		if err != nil {
			return err
		}

		if len(cfg.Sites) == 0 {
			println("No sites configured. Use 'ecto auth add' to add one.")
			return nil
		}

		for name, site := range cfg.Sites {
			marker := "  "
			if name == cfg.DefaultSite {
				marker = "* "
			}
			printf("%s%s: %s\n", marker, name, site.URL)
		}
		return nil
	},
}

var authDefaultCmd = &cobra.Command{
	Use:   "default <name>",
	Short: "Set the default site",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]

		cfg, err := config.Load()
		if err != nil {
			return err
		}

		if err := cfg.SetDefault(name); err != nil {
			return err
		}

		printf("Default site set to %q\n", name)
		return nil
	},
}

var authRemoveCmd = &cobra.Command{
	Use:   "remove <name>",
	Short: "Remove a site configuration",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]

		cfg, err := config.Load()
		if err != nil {
			return err
		}

		if _, ok := cfg.Sites[name]; !ok {
			return fmt.Errorf("site %q not found", name)
		}

		if err := cfg.RemoveSite(name); err != nil {
			return err
		}

		printf("Removed site %q\n", name)
		return nil
	},
}

func init() {
	authAddCmd.Flags().String("url", "", "Ghost site URL")
	authAddCmd.Flags().String("key", "", "Admin API key")

	authCmd.AddCommand(authAddCmd)
	authCmd.AddCommand(authListCmd)
	authCmd.AddCommand(authDefaultCmd)
	authCmd.AddCommand(authRemoveCmd)
	rootCmd.AddCommand(authCmd)
}
