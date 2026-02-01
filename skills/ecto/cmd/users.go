package cmd

import (
	"github.com/spf13/cobra"
	"github.com/visionik/ecto/internal/config"
)

var usersCmd = &cobra.Command{
	Use:   "users",
	Short: "List users",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")

		resp, err := client.ListUsers()
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(resp)
		}

		if len(resp.Users) == 0 {
			println("No users found")
			return nil
		}

		for _, u := range resp.Users {
			printf("%s - %s (%s)\n", u.ID, u.Name, u.Slug)
		}
		return nil
	},
}

var userCmd = &cobra.Command{
	Use:   "user <id|slug>",
	Short: "Get a single user",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")

		user, err := client.GetUser(args[0])
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(map[string]interface{}{"users": []interface{}{user}})
		}

		printf("ID:    %s\n", user.ID)
		printf("Name:  %s\n", user.Name)
		printf("Slug:  %s\n", user.Slug)
		printf("Email: %s\n", user.Email)
		if user.Bio != "" {
			printf("Bio:   %s\n", user.Bio)
		}
		return nil
	},
}

func init() {
	usersCmd.Flags().Bool("json", false, "Output as JSON")
	userCmd.Flags().Bool("json", false, "Output as JSON")

	rootCmd.AddCommand(usersCmd)
	rootCmd.AddCommand(userCmd)
}
