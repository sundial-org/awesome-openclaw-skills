package cmd

import (
	"github.com/spf13/cobra"
	"github.com/visionik/ecto/internal/config"
)

var imageCmd = &cobra.Command{
	Use:   "image",
	Short: "Manage images",
}

var imageUploadCmd = &cobra.Command{
	Use:   "upload <path>",
	Short: "Upload an image",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		client, err := config.GetActiveClient(siteName)
		if err != nil {
			return err
		}

		asJSON, _ := cmd.Flags().GetBool("json")

		resp, err := client.UploadImage(args[0])
		if err != nil {
			return err
		}

		if asJSON {
			return outputJSON(resp)
		}

		if len(resp.Images) > 0 {
			printf("Uploaded: %s\n", resp.Images[0].URL)
		}
		return nil
	},
}

func init() {
	imageUploadCmd.Flags().Bool("json", false, "Output as JSON")

	imageCmd.AddCommand(imageUploadCmd)
	rootCmd.AddCommand(imageCmd)
}
