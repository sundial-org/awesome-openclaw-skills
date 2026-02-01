package cmd

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"github.com/visionik/ecto/internal/config"
	"github.com/visionik/libecto"
)

var postsCmd = &cobra.Command{
	Use:   "posts",
	Short: "List posts",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		status, _ := cmd.Flags().GetString("status")
		limit, _ := cmd.Flags().GetInt("limit")
		asJSON, _ := cmd.Flags().GetBool("json")

		resp, err := client.ListPosts(status, limit)
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(resp)
		}

		if len(resp.Posts) == 0 {
			println("No posts found")
			return nil
		}

		for _, p := range resp.Posts {
			printf("[%s] %s - %s (%s)\n", p.Status, p.ID, p.Title, p.Slug)
		}
		return nil
	},
}

var postCmd = &cobra.Command{
	Use:   "post <id|slug>",
	Short: "Get a single post",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")
		showBody, _ := cmd.Flags().GetBool("body")

		post, err := client.GetPost(args[0])
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(map[string]interface{}{"posts": []interface{}{post}})
		}

		printf("ID:        %s\n", post.ID)
		printf("Title:     %s\n", post.Title)
		printf("Slug:      %s\n", post.Slug)
		printf("Status:    %s\n", post.Status)
		printf("Created:   %s\n", post.CreatedAt)
		if post.PublishedAt != "" {
			printf("Published: %s\n", post.PublishedAt)
		}
		if len(post.Tags) > 0 {
			var tagNames []string
			for _, t := range post.Tags {
				tagNames = append(tagNames, t.Name)
			}
			printf("Tags:      %s\n", strings.Join(tagNames, ", "))
		}
		if post.Excerpt != "" && !showBody {
			printf("\nExcerpt:\n%s\n", post.Excerpt)
		}
		if showBody && post.HTML != "" {
			printf("\nBody (HTML):\n%s\n", post.HTML)
		}
		return nil
	},
}

var postCreateCmd = &cobra.Command{
	Use:   "create",
	Short: "Create a new post",
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		title, _ := cmd.Flags().GetString("title")
		status, _ := cmd.Flags().GetString("status")
		mdFile, _ := cmd.Flags().GetString("markdown-file")
		stdinFormat, _ := cmd.Flags().GetString("stdin-format")
		tagsStr, _ := cmd.Flags().GetString("tag")

		if title == "" {
			return fmt.Errorf("--title is required")
		}

		post := &libecto.Post{
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
			post.HTML = libecto.MarkdownToHTML(content)
		}

		// Handle tags
		if tagsStr != "" {
			tagNames := strings.Split(tagsStr, ",")
			for _, name := range tagNames {
				post.Tags = append(post.Tags, libecto.Tag{Name: strings.TrimSpace(name)})
			}
		}

		created, err := client.CreatePost(post)
		if err != nil {
			return err
		}

		printf("Created post: %s (%s)\n", created.ID, created.Slug)
		return nil
	},
}

var postEditCmd = &cobra.Command{
	Use:   "edit <id|slug>",
	Short: "Edit a post",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		// First get the existing post
		existing, err := client.GetPost(args[0])
		if err != nil {
			return err
		}

		update := &libecto.Post{
			UpdatedAt: existing.UpdatedAt, // Required for conflict detection
		}

		if title, _ := cmd.Flags().GetString("title"); title != "" {
			update.Title = title
		}
		if status, _ := cmd.Flags().GetString("status"); status != "" {
			update.Status = status
		}
		if publishAt, _ := cmd.Flags().GetString("publish-at"); publishAt != "" {
			update.PublishedAt = publishAt
			update.Status = "scheduled"
		}
		if mdFile, _ := cmd.Flags().GetString("markdown-file"); mdFile != "" {
			content, err := os.ReadFile(mdFile)
			if err != nil {
				return fmt.Errorf("reading markdown file: %w", err)
			}
			update.HTML = libecto.MarkdownToHTML(content)
		}
		if featureImage, _ := cmd.Flags().GetString("feature-image"); featureImage != "" {
			update.FeatureImage = featureImage
		}

		updated, err := client.UpdatePost(existing.ID, update)
		if err != nil {
			return err
		}

		printf("Updated post: %s\n", updated.ID)
		return nil
	},
}

var postDeleteCmd = &cobra.Command{
	Use:   "delete <id|slug>",
	Short: "Delete a post",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		force, _ := cmd.Flags().GetBool("force")

		// Get post first to get ID and confirm
		post, err := client.GetPost(args[0])
		if err != nil {
			return err
		}

		if !force {
			printf("Delete post %q (%s)? [y/N]: ", post.Title, post.ID)
			var answer string
			fmt.Scanln(&answer)
			if strings.ToLower(answer) != "y" {
				println("Cancelled")
				return nil
			}
		}

		if err := client.DeletePost(post.ID); err != nil {
			return err
		}

		printf("Deleted post: %s\n", post.ID)
		return nil
	},
}

var postPublishCmd = &cobra.Command{
	Use:   "publish <id|slug>",
	Short: "Publish a post",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		updated, err := client.PublishPost(args[0])
		if err != nil {
			return err
		}

		printf("Published post: %s\n", updated.ID)
		return nil
	},
}

var postUnpublishCmd = &cobra.Command{
	Use:   "unpublish <id|slug>",
	Short: "Unpublish a post (set to draft)",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		updated, err := client.UnpublishPost(args[0])
		if err != nil {
			return err
		}

		printf("Unpublished post: %s\n", updated.ID)
		return nil
	},
}

var postScheduleCmd = &cobra.Command{
	Use:   "schedule <id|slug>",
	Short: "Schedule a post for publication",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		at, _ := cmd.Flags().GetString("at")

		if at == "" {
			return fmt.Errorf("--at is required (ISO8601 timestamp)")
		}

		updated, err := client.SchedulePost(args[0], at)
		if err != nil {
			return err
		}

		printf("Scheduled post %s for %s\n", updated.ID, at)
		return nil
	},
}

func outputJSON(v interface{}) error {
	enc := json.NewEncoder(output)
	enc.SetIndent("", "  ")
	return enc.Encode(v)
}

func init() {
	postsCmd.Flags().String("status", "", "Filter by status (draft|published|scheduled|all)")
	postsCmd.Flags().Int("limit", 15, "Number of posts to return")
	postsCmd.Flags().Bool("json", false, "Output as JSON")

	postCmd.Flags().Bool("json", false, "Output as JSON")
	postCmd.Flags().Bool("body", false, "Include full HTML body")

	postCreateCmd.Flags().String("title", "", "Post title (required)")
	postCreateCmd.Flags().String("status", "draft", "Post status (draft|published)")
	postCreateCmd.Flags().String("markdown-file", "", "Path to markdown file for content")
	postCreateCmd.Flags().String("stdin-format", "", "Read content from stdin (markdown)")
	postCreateCmd.Flags().String("tag", "", "Comma-separated tags")

	postEditCmd.Flags().String("title", "", "New title")
	postEditCmd.Flags().String("status", "", "New status")
	postEditCmd.Flags().String("markdown-file", "", "Path to markdown file for new content")
	postEditCmd.Flags().String("publish-at", "", "Schedule for publication (ISO8601)")
	postEditCmd.Flags().String("feature-image", "", "URL for the feature image")

	postDeleteCmd.Flags().Bool("force", false, "Delete without confirmation")

	postScheduleCmd.Flags().String("at", "", "Publication time (ISO8601)")

	postCmd.AddCommand(postCreateCmd)
	postCmd.AddCommand(postEditCmd)
	postCmd.AddCommand(postDeleteCmd)
	postCmd.AddCommand(postPublishCmd)
	postCmd.AddCommand(postUnpublishCmd)
	postCmd.AddCommand(postScheduleCmd)

	rootCmd.AddCommand(postsCmd)
	rootCmd.AddCommand(postCmd)
}
