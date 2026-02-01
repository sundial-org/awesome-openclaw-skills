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

// WordCmd handles Word document operations.
type WordCmd struct {
	List   WordListCmd   `cmd:"" help:"List Word documents"`
	Get    WordGetCmd    `cmd:"" help:"Get document metadata"`
	Export WordExportCmd `cmd:"" help:"Export a document"`
	Copy   WordCopyCmd   `cmd:"" help:"Copy a document"`
	Create WordCreateCmd `cmd:"" help:"Create a new document"`
}

// WordListCmd lists documents.
type WordListCmd struct {
	Max int `help:"Maximum results" default:"50"`
}

// Run executes word list.
func (c *WordListCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$top", fmt.Sprintf("%d", c.Max))
	query.Set("$orderby", "lastModifiedDateTime desc")

	data, err := client.Get(ctx, "/me/drive/root/search(q='.docx')", query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []DriveItem `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	// Filter to only .docx files
	var docs []DriveItem
	for _, item := range resp.Value {
		if strings.HasSuffix(strings.ToLower(item.Name), ".docx") {
			docs = append(docs, item)
		}
	}

	if root.JSON {
		return outputJSON(docs)
	}

	if len(docs) == 0 {
		fmt.Println("No Word documents found")
		return nil
	}

	fmt.Println("Word Documents")
	fmt.Println()
	for _, doc := range docs {
		fmt.Printf("📝 %s  %s  %s\n", doc.Name, formatSize(doc.Size), doc.LastModifiedDateTime[:10])
		fmt.Printf("   ID: %s\n", graph.FormatID(doc.ID))
		if root.Verbose && doc.WebURL != "" {
			fmt.Printf("   URL: %s\n", doc.WebURL)
		}
	}
	fmt.Printf("\n%d document(s)\n", len(docs))
	return nil
}

// WordGetCmd gets document metadata.
type WordGetCmd struct {
	ID string `arg:"" help:"Document ID"`
}

// Run executes word get.
func (c *WordGetCmd) Run(root *Root) error {
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

// WordExportCmd exports a document.
type WordExportCmd struct {
	ID     string `arg:"" help:"Document ID"`
	Out    string `help:"Output path" required:""`
	Format string `help:"Export format (docx, pdf)" default:"docx"`
}

// Run executes word export.
func (c *WordExportCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	docID := graph.ResolveID(c.ID)

	format := strings.ToLower(c.Format)
	var path string

	if format == "pdf" {
		path = fmt.Sprintf("/me/drive/items/%s/content?format=pdf", docID)
	} else {
		path = fmt.Sprintf("/me/drive/items/%s/content", docID)
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

// WordCopyCmd copies a document.
type WordCopyCmd struct {
	ID     string `arg:"" help:"Document ID"`
	Name   string `arg:"" help:"New name"`
	Folder string `help:"Destination folder ID"`
}

// Run executes word copy.
func (c *WordCopyCmd) Run(root *Root) error {
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

// WordCreateCmd creates a document.
type WordCreateCmd struct {
	Name   string `arg:"" help:"Document name"`
	Folder string `help:"Destination folder ID"`
}

// Run executes word create.
func (c *WordCreateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	// Ensure .docx extension
	name := c.Name
	if !strings.HasSuffix(strings.ToLower(name), ".docx") {
		name += ".docx"
	}

	ctx := context.Background()
	var path string
	if c.Folder != "" {
		path = fmt.Sprintf("/me/drive/items/%s:/%s:/content", graph.ResolveID(c.Folder), name)
	} else {
		path = fmt.Sprintf("/me/drive/root:/%s:/content", name)
	}

	// Create empty docx
	data, err := client.Put(ctx, path, []byte{}, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
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

	fmt.Println("✓ Document created")
	fmt.Printf("  Name: %s\n", item.Name)
	fmt.Printf("  ID: %s\n", graph.FormatID(item.ID))
	return nil
}
