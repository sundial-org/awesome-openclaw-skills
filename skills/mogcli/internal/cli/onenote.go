package cli

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"

	"github.com/visionik/mogcli/internal/graph"
)

// OneNoteCmd handles OneNote operations.
type OneNoteCmd struct {
	Notebooks      OneNoteNotebooksCmd      `cmd:"" help:"List notebooks"`
	Sections       OneNoteSectionsCmd       `cmd:"" help:"List sections in a notebook"`
	Pages          OneNotePagesCmd          `cmd:"" help:"List pages in a section"`
	Get            OneNoteGetCmd            `cmd:"" help:"Get page content"`
	Search         OneNoteSearchCmd         `cmd:"" help:"Search OneNote"`
	CreateNotebook OneNoteCreateNotebookCmd `cmd:"" name:"create-notebook" help:"Create a new notebook"`
	CreateSection  OneNoteCreateSectionCmd  `cmd:"" name:"create-section" help:"Create a new section"`
	CreatePage     OneNoteCreatePageCmd     `cmd:"" name:"create-page" help:"Create a new page"`
	Delete         OneNoteDeleteCmd         `cmd:"" help:"Delete a page"`
}

// OneNoteNotebooksCmd lists notebooks.
type OneNoteNotebooksCmd struct{}

// Run executes onenote notebooks.
func (c *OneNoteNotebooksCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	data, err := client.Get(ctx, "/me/onenote/notebooks", nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Notebook `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, nb := range resp.Value {
		fmt.Printf("%-40s %s\n", nb.DisplayName, graph.FormatID(nb.ID))
	}
	return nil
}

// OneNoteSectionsCmd lists sections.
type OneNoteSectionsCmd struct {
	NotebookID string `arg:"" help:"Notebook ID"`
}

// Run executes onenote sections.
func (c *OneNoteSectionsCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/onenote/notebooks/%s/sections", graph.ResolveID(c.NotebookID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Section `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, s := range resp.Value {
		fmt.Printf("%-40s %s\n", s.DisplayName, graph.FormatID(s.ID))
	}
	return nil
}

// OneNotePagesCmd lists pages.
type OneNotePagesCmd struct {
	SectionID string `arg:"" help:"Section ID"`
}

// Run executes onenote pages.
func (c *OneNotePagesCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/onenote/sections/%s/pages", graph.ResolveID(c.SectionID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Page `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, p := range resp.Value {
		fmt.Printf("%-40s %s\n", p.Title, graph.FormatID(p.ID))
	}
	return nil
}

// OneNoteGetCmd gets page content.
type OneNoteGetCmd struct {
	PageID string `arg:"" help:"Page ID"`
	HTML   bool   `help:"Output raw HTML"`
}

// Run executes onenote get.
func (c *OneNoteGetCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/onenote/pages/%s/content", graph.ResolveID(c.PageID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	if c.HTML || root.JSON {
		fmt.Println(string(data))
		return nil
	}

	// Strip HTML for text output
	fmt.Println(stripHTML(string(data)))
	return nil
}

// OneNoteSearchCmd searches OneNote.
type OneNoteSearchCmd struct {
	Query string `arg:"" help:"Search query"`
}

// Run executes onenote search.
func (c *OneNoteSearchCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()

	// Search pages
	data, err := client.Get(ctx, "/me/onenote/pages", nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Page `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	fmt.Println("Note: Full-text search requires Graph beta API")
	fmt.Println("Listing all pages instead:")
	for _, p := range resp.Value {
		fmt.Printf("%-40s %s\n", p.Title, graph.FormatID(p.ID))
	}
	return nil
}

// Notebook represents a OneNote notebook.
type Notebook struct {
	ID          string `json:"id"`
	DisplayName string `json:"displayName"`
}

// Section represents a OneNote section.
type Section struct {
	ID          string `json:"id"`
	DisplayName string `json:"displayName"`
}

// Page represents a OneNote page.
type Page struct {
	ID    string `json:"id"`
	Title string `json:"title"`
}

// OneNoteCreateNotebookCmd creates a notebook.
type OneNoteCreateNotebookCmd struct {
	Name string `arg:"" help:"Notebook name"`
}

// Run executes onenote create-notebook.
func (c *OneNoteCreateNotebookCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{
		"displayName": c.Name,
	}

	ctx := context.Background()
	data, err := client.Post(ctx, "/me/onenote/notebooks", body)
	if err != nil {
		return err
	}

	var nb Notebook
	if err := json.Unmarshal(data, &nb); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(nb)
	}

	fmt.Println("✓ Notebook created")
	fmt.Printf("  Name: %s\n", nb.DisplayName)
	fmt.Printf("  ID: %s\n", graph.FormatID(nb.ID))
	return nil
}

// OneNoteCreateSectionCmd creates a section.
type OneNoteCreateSectionCmd struct {
	NotebookID string `arg:"" help:"Notebook ID"`
	Name       string `arg:"" help:"Section name"`
}

// Run executes onenote create-section.
func (c *OneNoteCreateSectionCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{
		"displayName": c.Name,
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/onenote/notebooks/%s/sections", graph.ResolveID(c.NotebookID))

	data, err := client.Post(ctx, path, body)
	if err != nil {
		return err
	}

	var section Section
	if err := json.Unmarshal(data, &section); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(section)
	}

	fmt.Println("✓ Section created")
	fmt.Printf("  Name: %s\n", section.DisplayName)
	fmt.Printf("  ID: %s\n", graph.FormatID(section.ID))
	return nil
}

// OneNoteCreatePageCmd creates a page.
type OneNoteCreatePageCmd struct {
	SectionID string `arg:"" help:"Section ID"`
	Title     string `arg:"" help:"Page title"`
	Content   string `arg:"" optional:"" help:"Page content (optional)"`
}

// Run executes onenote create-page.
func (c *OneNoteCreatePageCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	// OneNote requires HTML presentation format
	htmlContent := fmt.Sprintf(`<!DOCTYPE html>
<html>
  <head>
    <title>%s</title>
  </head>
  <body>
    <p>%s</p>
  </body>
</html>`, escapeHTML(c.Title), escapeHTML(c.Content))

	ctx := context.Background()
	path := fmt.Sprintf("/me/onenote/sections/%s/pages", graph.ResolveID(c.SectionID))

	data, err := client.PostHTML(ctx, path, htmlContent)
	if err != nil {
		return err
	}

	var page Page
	if err := json.Unmarshal(data, &page); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(page)
	}

	fmt.Println("✓ Page created")
	fmt.Printf("  Title: %s\n", page.Title)
	fmt.Printf("  ID: %s\n", graph.FormatID(page.ID))
	return nil
}

// OneNoteDeleteCmd deletes a page.
type OneNoteDeleteCmd struct {
	PageID string `arg:"" help:"Page ID"`
}

// Run executes onenote delete.
func (c *OneNoteDeleteCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/onenote/pages/%s", graph.ResolveID(c.PageID))

	if err := client.Delete(ctx, path); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(map[string]interface{}{"success": true, "deleted": c.PageID})
	}

	fmt.Println("✓ Page deleted")
	return nil
}

// escapeHTML escapes HTML special characters.
func escapeHTML(text string) string {
	if text == "" {
		return ""
	}
	text = strings.ReplaceAll(text, "&", "&amp;")
	text = strings.ReplaceAll(text, "<", "&lt;")
	text = strings.ReplaceAll(text, ">", "&gt;")
	text = strings.ReplaceAll(text, "\"", "&quot;")
	text = strings.ReplaceAll(text, "'", "&#39;")
	return text
}
