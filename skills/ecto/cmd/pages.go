package cmd

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"github.com/visionik/ecto/internal/config"
	"github.com/visionik/libecto"
)

var pagesCmd = &cobra.Command{
	Use:   "pages",
	Short: "List pages",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		status, _ := cmd.Flags().GetString("status")
		limit, _ := cmd.Flags().GetInt("limit")
		asJSON, _ := cmd.Flags().GetBool("json")

		resp, err := client.ListPages(status, limit)
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(resp)
		}

		if len(resp.Pages) == 0 {
			println("No pages found")
			return nil
		}

		for _, p := range resp.Pages {
			printf("[%s] %s - %s (%s)\n", p.Status, p.ID, p.Title, p.Slug)
		}
		return nil
	},
}

var pageCmd = &cobra.Command{
	Use:   "page <id|slug>",
	Short: "Get a single page",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")

		page, err := client.GetPage(args[0])
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(map[string]interface{}{"pages": []interface{}{page}})
		}

		printf("ID:      %s\n", page.ID)
		printf("Title:   %s\n", page.Title)
		printf("Slug:    %s\n", page.Slug)
		printf("Status:  %s\n", page.Status)
		printf("Created: %s\n", page.CreatedAt)
		if page.PublishedAt != "" {
			printf("Published: %s\n", page.PublishedAt)
		}
		return nil
	},
}

var pageCreateCmd = &cobra.Command{
	Use:   "create",
	Short: "Create a new page",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		title, _ := cmd.Flags().GetString("title")
		status, _ := cmd.Flags().GetString("status")
		mdFile, _ := cmd.Flags().GetString("markdown-file")
		stdinFormat, _ := cmd.Flags().GetString("stdin-format")

		if title == "" {
			return fmt.Errorf("--title is required")
		}

		page := &libecto.Page{
			Title:  title,
			Status: status,
		}

		// Read content
		var content []byte
		if mdFile != "" {
			content, err = os.ReadFile(mdFile)
			if err != nil {
				return fmt.Errorf("reading markdown file: %w", err)
			}
		} else if stdinFormat == "markdown" {
			scanner := bufio.NewScanner(os.Stdin)
			var lines []string
			for scanner.Scan() {
				lines = append(lines, scanner.Text())
			}
			content = []byte(strings.Join(lines, "\n"))
		}

		if len(content) > 0 {
			page.HTML = libecto.MarkdownToHTML(content)
		}

		created, err := client.CreatePage(page)
		if err != nil {
			return err
		}

		printf("Created page: %s (%s)\n", created.ID, created.Slug)
		return nil
	},
}

var pageEditCmd = &cobra.Command{
	Use:   "edit <id|slug>",
	Short: "Edit a page",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		existing, err := client.GetPage(args[0])
		if err != nil {
			return err
		}

		update := &libecto.Page{
			UpdatedAt: existing.UpdatedAt,
		}

		if title, _ := cmd.Flags().GetString("title"); title != "" {
			update.Title = title
		}
		if status, _ := cmd.Flags().GetString("status"); status != "" {
			update.Status = status
		}
		if mdFile, _ := cmd.Flags().GetString("markdown-file"); mdFile != "" {
			content, err := os.ReadFile(mdFile)
			if err != nil {
				return fmt.Errorf("reading markdown file: %w", err)
			}
			update.HTML = libecto.MarkdownToHTML(content)
		}

		updated, err := client.UpdatePage(existing.ID, update)
		if err != nil {
			return err
		}

		printf("Updated page: %s\n", updated.ID)
		return nil
	},
}

var pageDeleteCmd = &cobra.Command{
	Use:   "delete <id|slug>",
	Short: "Delete a page",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		force, _ := cmd.Flags().GetBool("force")

		page, err := client.GetPage(args[0])
		if err != nil {
			return err
		}

		if !force {
			printf("Delete page %q (%s)? [y/N]: ", page.Title, page.ID)
			var answer string
			fmt.Scanln(&answer)
			if strings.ToLower(answer) != "y" {
				println("Cancelled")
				return nil
			}
		}

		if err := client.DeletePage(page.ID); err != nil {
			return err
		}

		printf("Deleted page: %s\n", page.ID)
		return nil
	},
}

var pagePublishCmd = &cobra.Command{
	Use:   "publish <id|slug>",
	Short: "Publish a page",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		updated, err := client.PublishPage(args[0])
		if err != nil {
			return err
		}

		printf("Published page: %s\n", updated.ID)
		return nil
	},
}

func init() {
	pagesCmd.Flags().String("status", "", "Filter by status (draft|published|all)")
	pagesCmd.Flags().Int("limit", 15, "Number of pages to return")
	pagesCmd.Flags().Bool("json", false, "Output as JSON")

	pageCmd.Flags().Bool("json", false, "Output as JSON")

	pageCreateCmd.Flags().String("title", "", "Page title (required)")
	pageCreateCmd.Flags().String("status", "draft", "Page status (draft|published)")
	pageCreateCmd.Flags().String("markdown-file", "", "Path to markdown file for content")
	pageCreateCmd.Flags().String("stdin-format", "", "Read content from stdin (markdown)")

	pageEditCmd.Flags().String("title", "", "New title")
	pageEditCmd.Flags().String("status", "", "New status")
	pageEditCmd.Flags().String("markdown-file", "", "Path to markdown file for new content")

	pageDeleteCmd.Flags().Bool("force", false, "Delete without confirmation")

	pageCmd.AddCommand(pageCreateCmd)
	pageCmd.AddCommand(pageEditCmd)
	pageCmd.AddCommand(pageDeleteCmd)
	pageCmd.AddCommand(pagePublishCmd)

	rootCmd.AddCommand(pagesCmd)
	rootCmd.AddCommand(pageCmd)
}
