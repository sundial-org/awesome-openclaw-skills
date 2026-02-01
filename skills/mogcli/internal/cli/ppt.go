package cli

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"strings"

	"github.com/visionik/mogcli/internal/graph"
)

// PPTCmd handles PowerPoint operations.
type PPTCmd struct {
	List   PPTListCmd   `cmd:"" help:"List PowerPoint presentations"`
	Get    PPTGetCmd    `cmd:"" help:"Get presentation metadata"`
	Export PPTExportCmd `cmd:"" help:"Export a presentation"`
	Copy   PPTCopyCmd   `cmd:"" help:"Copy a presentation"`
	Create PPTCreateCmd `cmd:"" help:"Create a new presentation"`
}

// PPTListCmd lists presentations.
type PPTListCmd struct {
	Max int `help:"Maximum results" default:"50"`
}

// Run executes ppt list.
func (c *PPTListCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$top", fmt.Sprintf("%d", c.Max))
	query.Set("$orderby", "lastModifiedDateTime desc")

	data, err := client.Get(ctx, "/me/drive/root/search(q='.pptx')", query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []DriveItem `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	// Filter to only .pptx files
	var presentations []DriveItem
	for _, item := range resp.Value {
		if strings.HasSuffix(strings.ToLower(item.Name), ".pptx") {
			presentations = append(presentations, item)
		}
	}

	if root.JSON {
		return outputJSON(presentations)
	}

	if len(presentations) == 0 {
		fmt.Println("No PowerPoint presentations found")
		return nil
	}

	fmt.Println("PowerPoint Presentations")
	fmt.Println()
	for _, ppt := range presentations {
		fmt.Printf("📊 %s  %s  %s\n", ppt.Name, formatSize(ppt.Size), ppt.LastModifiedDateTime[:10])
		fmt.Printf("   ID: %s\n", graph.FormatID(ppt.ID))
		if root.Verbose && ppt.WebURL != "" {
			fmt.Printf("   URL: %s\n", ppt.WebURL)
		}
	}
	fmt.Printf("\n%d presentation(s)\n", len(presentations))
	return nil
}

// PPTGetCmd gets presentation metadata.
type PPTGetCmd struct {
	ID string `arg:"" help:"Presentation ID"`
}

// Run executes ppt get.
func (c *PPTGetCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s", graph.ResolveID(c.ID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var item DriveItem
	if err := json.Unmarshal(data, &item); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(item)
	}

	fmt.Printf("ID:       %s\n", graph.FormatID(item.ID))
	fmt.Printf("Name:     %s\n", item.Name)
	fmt.Printf("Size:     %s\n", formatSize(item.Size))
	fmt.Printf("Created:  %s\n", item.CreatedDateTime)
	fmt.Printf("Modified: %s\n", item.LastModifiedDateTime)
	if item.WebURL != "" {
		fmt.Printf("URL:      %s\n", item.WebURL)
	}
	return nil
}

// PPTExportCmd exports a presentation.
type PPTExportCmd struct {
	ID     string `arg:"" help:"Presentation ID"`
	Out    string `help:"Output path" required:""`
	Format string `help:"Export format (pptx, pdf)" default:"pptx"`
}

// Run executes ppt export.
func (c *PPTExportCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	pptID := graph.ResolveID(c.ID)

	format := strings.ToLower(c.Format)
	var path string

	if format == "pdf" {
		path = fmt.Sprintf("/me/drive/items/%s/content?format=pdf", pptID)
	} else {
		path = fmt.Sprintf("/me/drive/items/%s/content", pptID)
	}

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	if err := os.WriteFile(c.Out, data, 0644); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(map[string]interface{}{"success": true, "path": c.Out, "format": format})
	}

	fmt.Println("✓ Exported")
	fmt.Printf("  Format: %s\n", strings.ToUpper(format))
	fmt.Printf("  Saved to: %s\n", c.Out)
	return nil
}

// PPTCopyCmd copies a presentation.
type PPTCopyCmd struct {
	ID     string `arg:"" help:"Presentation ID"`
	Name   string `arg:"" help:"New name"`
	Folder string `help:"Destination folder ID"`
}

// Run executes ppt copy.
func (c *PPTCopyCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{
		"name": c.Name,
	}
	if c.Folder != "" {
		body["parentReference"] = map[string]string{
			"id": graph.ResolveID(c.Folder),
		}
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/copy", graph.ResolveID(c.ID))

	_, err = client.Post(ctx, path, body)
	if err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(map[string]interface{}{"success": true, "name": c.Name})
	}

	fmt.Println("✓ Copy initiated")
	fmt.Printf("  Name: %s\n", c.Name)
	return nil
}

// PPTCreateCmd creates a presentation.
type PPTCreateCmd struct {
	Name   string `arg:"" help:"Presentation name"`
	Folder string `help:"Destination folder ID"`
}

// Run executes ppt create.
func (c *PPTCreateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	// Ensure .pptx extension
	name := c.Name
	if !strings.HasSuffix(strings.ToLower(name), ".pptx") {
		name += ".pptx"
	}

	ctx := context.Background()
	var path string
	if c.Folder != "" {
		path = fmt.Sprintf("/me/drive/items/%s:/%s:/content", graph.ResolveID(c.Folder), name)
	} else {
		path = fmt.Sprintf("/me/drive/root:/%s:/content", name)
	}

	// Create empty pptx
	data, err := client.Put(ctx, path, []byte{}, "application/vnd.openxmlformats-officedocument.presentationml.presentation")
	if err != nil {
		return err
	}

	var item DriveItem
	if err := json.Unmarshal(data, &item); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(item)
	}

	fmt.Println("✓ Presentation created")
	fmt.Printf("  Name: %s\n", item.Name)
	fmt.Printf("  ID: %s\n", graph.FormatID(item.ID))
	return nil
}
