package cli

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"path/filepath"

	"github.com/visionik/mogcli/internal/graph"
)

// DriveCmd handles OneDrive operations.
type DriveCmd struct {
	Ls       DriveLsCmd       `cmd:"" help:"List files"`
	Search   DriveSearchCmd   `cmd:"" help:"Search files"`
	Get      DriveGetCmd      `cmd:"" help:"Get file metadata"`
	Download DriveDownloadCmd `cmd:"" help:"Download a file"`
	Upload   DriveUploadCmd   `cmd:"" help:"Upload a file"`
	Mkdir    DriveMkdirCmd    `cmd:"" help:"Create a folder"`
	Move     DriveMoveCmd     `cmd:"" help:"Move a file"`
	Copy     DriveCopyCmd     `cmd:"" help:"Copy a file"`
	Rename   DriveRenameCmd   `cmd:"" help:"Rename a file"`
	Delete   DriveDeleteCmd   `cmd:"" aliases:"rm" help:"Delete a file"`
}

// DriveLsCmd lists files.
type DriveLsCmd struct {
	Path string `arg:"" optional:"" help:"Folder path or ID" default:""`
}

// Run executes drive ls.
func (c *DriveLsCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := "/me/drive/root/children"
	if c.Path != "" {
		if len(c.Path) > 20 {
			// Looks like an ID
			path = fmt.Sprintf("/me/drive/items/%s/children", graph.ResolveID(c.Path))
		} else {
			path = fmt.Sprintf("/me/drive/root:/%s:/children", c.Path)
		}
	}

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []DriveItem `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, item := range resp.Value {
		itemType := "📄"
		if item.Folder != nil {
			itemType = "📁"
		}
		size := ""
		if item.Size > 0 {
			size = formatSize(item.Size)
		}
		fmt.Printf("%s %-40s %8s  %s\n", itemType, item.Name, size, graph.FormatID(item.ID))
	}
	return nil
}

// DriveSearchCmd searches files.
type DriveSearchCmd struct {
	Query string `arg:"" help:"Search query"`
	Max   int    `help:"Maximum results" default:"25"`
}

// Run executes drive search.
func (c *DriveSearchCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$top", fmt.Sprintf("%d", c.Max))

	path := fmt.Sprintf("/me/drive/root/search(q='%s')", url.PathEscape(c.Query))
	data, err := client.Get(ctx, path, query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []DriveItem `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, item := range resp.Value {
		itemType := "📄"
		if item.Folder != nil {
			itemType = "📁"
		}
		fmt.Printf("%s %s  %s\n", itemType, item.Name, graph.FormatID(item.ID))
	}
	return nil
}

// DriveGetCmd gets file metadata.
type DriveGetCmd struct {
	ID string `arg:"" help:"File ID"`
}

// Run executes drive get.
func (c *DriveGetCmd) Run(root *Root) error {
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

// DriveDownloadCmd downloads a file.
type DriveDownloadCmd struct {
	ID  string `arg:"" help:"File ID"`
	Out string `help:"Output path" required:""`
}

// Run executes drive download.
func (c *DriveDownloadCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/content", graph.ResolveID(c.ID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	if err := os.WriteFile(c.Out, data, 0644); err != nil {
		return err
	}

	fmt.Printf("✓ Downloaded: %s\n", c.Out)
	return nil
}

// DriveUploadCmd uploads a file.
type DriveUploadCmd struct {
	Path   string `arg:"" help:"Local file path"`
	Folder string `help:"Destination folder ID"`
	Name   string `help:"Rename file on upload"`
}

// Run executes drive upload.
func (c *DriveUploadCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	data, err := os.ReadFile(c.Path)
	if err != nil {
		return err
	}

	name := c.Name
	if name == "" {
		name = filepath.Base(c.Path)
	}

	ctx := context.Background()
	var path string
	if c.Folder != "" {
		path = fmt.Sprintf("/me/drive/items/%s:/%s:/content", graph.ResolveID(c.Folder), name)
	} else {
		path = fmt.Sprintf("/me/drive/root:/%s:/content", name)
	}

	// For small files, use simple upload
	// Note: This is simplified - large files need chunked upload
	respData, err := client.Put(ctx, path, data, "application/octet-stream")
	if err != nil {
		return err
	}

	var item DriveItem
	if err := json.Unmarshal(respData, &item); err != nil {
		return err
	}

	fmt.Printf("✓ Uploaded: %s (%s)\n", item.Name, graph.FormatID(item.ID))
	return nil
}

// DriveMkdirCmd creates a folder.
type DriveMkdirCmd struct {
	Name   string `arg:"" help:"Folder name"`
	Parent string `help:"Parent folder ID"`
}

// Run executes drive mkdir.
func (c *DriveMkdirCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{
		"name":   c.Name,
		"folder": map[string]interface{}{},
	}

	ctx := context.Background()
	path := "/me/drive/root/children"
	if c.Parent != "" {
		path = fmt.Sprintf("/me/drive/items/%s/children", graph.ResolveID(c.Parent))
	}

	data, err := client.Post(ctx, path, body)
	if err != nil {
		return err
	}

	var item DriveItem
	if err := json.Unmarshal(data, &item); err != nil {
		return err
	}

	fmt.Printf("✓ Created folder: %s (%s)\n", item.Name, graph.FormatID(item.ID))
	return nil
}

// DriveMoveCmd moves a file.
type DriveMoveCmd struct {
	ID          string `arg:"" help:"File ID"`
	Destination string `arg:"" help:"Destination folder ID"`
}

// Run executes drive move.
func (c *DriveMoveCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{
		"parentReference": map[string]string{
			"id": graph.ResolveID(c.Destination),
		},
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s", graph.ResolveID(c.ID))

	_, err = client.Patch(ctx, path, body)
	if err != nil {
		return err
	}

	fmt.Println("✓ File moved")
	return nil
}

// DriveCopyCmd copies a file.
type DriveCopyCmd struct {
	ID   string `arg:"" help:"File ID"`
	Name string `help:"New name for copy" required:""`
}

// Run executes drive copy.
func (c *DriveCopyCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{
		"name": c.Name,
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/copy", graph.ResolveID(c.ID))

	_, err = client.Post(ctx, path, body)
	if err != nil {
		return err
	}

	fmt.Printf("✓ Copy initiated: %s\n", c.Name)
	return nil
}

// DriveRenameCmd renames a file.
type DriveRenameCmd struct {
	ID   string `arg:"" help:"File ID"`
	Name string `arg:"" help:"New name"`
}

// Run executes drive rename.
func (c *DriveRenameCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{
		"name": c.Name,
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s", graph.ResolveID(c.ID))

	_, err = client.Patch(ctx, path, body)
	if err != nil {
		return err
	}

	fmt.Printf("✓ Renamed to: %s\n", c.Name)
	return nil
}

// DriveDeleteCmd deletes a file.
type DriveDeleteCmd struct {
	ID string `arg:"" help:"File ID"`
}

// Run executes drive delete.
func (c *DriveDeleteCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s", graph.ResolveID(c.ID))

	if err := client.Delete(ctx, path); err != nil {
		return err
	}

	fmt.Println("✓ File deleted")
	return nil
}

// DriveItem represents a OneDrive item.
type DriveItem struct {
	ID                   string      `json:"id"`
	Name                 string      `json:"name"`
	Size                 int64       `json:"size"`
	CreatedDateTime      string      `json:"createdDateTime"`
	LastModifiedDateTime string      `json:"lastModifiedDateTime"`
	WebURL               string      `json:"webUrl"`
	Folder               *FolderInfo `json:"folder,omitempty"`
	File                 *FileInfo   `json:"file,omitempty"`
}

// FolderInfo represents folder information.
type FolderInfo struct {
	ChildCount int `json:"childCount"`
}

// FileInfo represents file information.
type FileInfo struct {
	MimeType string `json:"mimeType"`
}

func formatSize(bytes int64) string {
	const unit = 1024
	if bytes < unit {
		return fmt.Sprintf("%d B", bytes)
	}
	div, exp := int64(unit), 0
	for n := bytes / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %cB", float64(bytes)/float64(div), "KMGTPE"[exp])
}
