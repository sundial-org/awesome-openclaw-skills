package cmd

import (
	"fmt"
	"strings"

	"github.com/spf13/cobra"
	"github.com/visionik/ecto/internal/config"
	"github.com/visionik/libecto"
)

var tagsCmd = &cobra.Command{
	Use:   "tags",
	Short: "List tags",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		limit, _ := cmd.Flags().GetInt("limit")
		asJSON, _ := cmd.Flags().GetBool("json")

		resp, err := client.ListTags(limit)
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(resp)
		}

		if len(resp.Tags) == 0 {
			println("No tags found")
			return nil
		}

		for _, t := range resp.Tags {
			printf("%s - %s (%s)\n", t.ID, t.Name, t.Slug)
		}
		return nil
	},
}

var tagCmd = &cobra.Command{
	Use:   "tag <id|slug>",
	Short: "Get or manage a tag",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")

		tag, err := client.GetTag(args[0])
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(map[string]interface{}{"tags": []interface{}{tag}})
		}

		printf("ID:          %s\n", tag.ID)
		printf("Name:        %s\n", tag.Name)
		printf("Slug:        %s\n", tag.Slug)
		printf("Description: %s\n", tag.Description)
		return nil
	},
}

var tagCreateCmd = &cobra.Command{
	Use:   "create <name>",
	Short: "Create a new tag",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		slug, _ := cmd.Flags().GetString("slug")
		description, _ := cmd.Flags().GetString("description")

		tag := &libecto.Tag{
			Name:        args[0],
			Slug:        slug,
			Description: description,
		}

		created, err := client.CreateTag(tag)
		if err != nil {
			return err
		}

		printf("Created tag: %s (%s)\n", created.ID, created.Slug)
		return nil
	},
}

var tagEditCmd = &cobra.Command{
	Use:   "edit <id|slug>",
	Short: "Edit a tag",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		existing, err := client.GetTag(args[0])
		if err != nil {
			return err
		}

		update := &libecto.Tag{}

		if name, _ := cmd.Flags().GetString("name"); name != "" {
			update.Name = name
		}
		if description, _ := cmd.Flags().GetString("description"); description != "" {
			update.Description = description
		}

		updated, err := client.UpdateTag(existing.ID, update)
		if err != nil {
			return err
		}

		printf("Updated tag: %s\n", updated.ID)
		return nil
	},
}

var tagDeleteCmd = &cobra.Command{
	Use:   "delete <id|slug>",
	Short: "Delete a tag",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		force, _ := cmd.Flags().GetBool("force")

		tag, err := client.GetTag(args[0])
		if err != nil {
			return err
		}

		if !force {
			printf("Delete tag %q (%s)? [y/N]: ", tag.Name, tag.ID)
			var answer string
			fmt.Scanln(&answer)
			if strings.ToLower(answer) != "y" {
				println("Cancelled")
				return nil
			}
		}

		if err := client.DeleteTag(tag.ID); err != nil {
			return err
		}

		printf("Deleted tag: %s\n", tag.ID)
		return nil
	},
}

func init() {
	tagsCmd.Flags().Int("limit", 15, "Number of tags to return")
	tagsCmd.Flags().Bool("json", false, "Output as JSON")

	tagCmd.Flags().Bool("json", false, "Output as JSON")

	tagCreateCmd.Flags().String("slug", "", "Tag slug")
	tagCreateCmd.Flags().String("description", "", "Tag description")

	tagEditCmd.Flags().String("name", "", "New name")
	tagEditCmd.Flags().String("description", "", "New description")

	tagDeleteCmd.Flags().Bool("force", false, "Delete without confirmation")

	tagCmd.AddCommand(tagCreateCmd)
	tagCmd.AddCommand(tagEditCmd)
	tagCmd.AddCommand(tagDeleteCmd)

	rootCmd.AddCommand(tagsCmd)
	rootCmd.AddCommand(tagCmd)
}
