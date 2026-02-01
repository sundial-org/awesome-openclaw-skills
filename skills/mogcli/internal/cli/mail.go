package cli

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/visionik/mogcli/internal/graph"
)

// MailCmd handles mail operations.
type MailCmd struct {
	List       MailListCmd       `cmd:"" help:"List messages (alias for search *)"`
	Search     MailSearchCmd     `cmd:"" help:"Search messages"`
	Get        MailGetCmd        `cmd:"" help:"Get a message"`
	Send       MailSendCmd       `cmd:"" help:"Send an email"`
	Folders    MailFoldersCmd    `cmd:"" help:"List mail folders"`
	Drafts     MailDraftsCmd     `cmd:"" help:"Draft operations"`
	Attachment MailAttachmentCmd `cmd:"" help:"Attachment operations"`
}

// MailListCmd lists messages (alias for search *).
type MailListCmd struct {
	Max    int    `help:"Maximum results" default:"25"`
	Folder string `help:"Folder ID to list from"`
}

// Run executes mail list (delegates to search *).
func (c *MailListCmd) Run(root *Root) error {
	search := &MailSearchCmd{
		Query:  "*",
		Max:    c.Max,
		Folder: c.Folder,
	}
	return search.Run(root)
}

// MailSearchCmd searches messages.
type MailSearchCmd struct {
	Query  string `arg:"" help:"Search query (use * for all)"`
	Max    int    `help:"Maximum results" default:"25"`
	Folder string `help:"Folder ID to search in"`
}

// Run executes mail search.
func (c *MailSearchCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$top", fmt.Sprintf("%d", c.Max))
	query.Set("$orderby", "receivedDateTime desc")
	query.Set("$select", "id,subject,from,receivedDateTime,isRead,hasAttachments")

	if c.Query != "*" && c.Query != "" {
		query.Set("$search", fmt.Sprintf(`"%s"`, c.Query))
	}

	path := "/me/messages"
	if c.Folder != "" {
		path = fmt.Sprintf("/me/mailFolders/%s/messages", graph.ResolveID(c.Folder))
	}

	data, err := client.Get(ctx, path, query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Message `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	if len(resp.Value) == 0 {
		fmt.Println("No messages found")
		return nil
	}

	for _, msg := range resp.Value {
		printMessage(msg, root.Verbose)
	}

	fmt.Printf("\n%d message(s)\n", len(resp.Value))
	return nil
}

// MailGetCmd gets a message.
type MailGetCmd struct {
	ID string `arg:"" help:"Message ID or slug"`
}

// Run executes mail get.
func (c *MailGetCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/messages/%s", graph.ResolveID(c.ID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var msg Message
	if err := json.Unmarshal(data, &msg); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(msg)
	}

	printMessageDetail(msg, root.Verbose)
	return nil
}

// MailSendCmd sends an email.
type MailSendCmd struct {
	To               []string `help:"Recipient(s)" required:""`
	Cc               []string `help:"CC recipient(s)"`
	Bcc              []string `help:"BCC recipient(s)"`
	Subject          string   `help:"Subject line" required:""`
	Body             string   `help:"Message body"`
	BodyFile         string   `help:"Read body from file (- for stdin)" name:"body-file"`
	BodyHTML         string   `help:"HTML body" name:"body-html"`
	ReplyToMessageID string   `help:"Reply to message ID" name:"reply-to-message-id"`
}

// Run executes mail send.
func (c *MailSendCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := c.Body
	contentType := "text"

	if c.BodyHTML != "" {
		body = c.BodyHTML
		contentType = "html"
	} else if c.BodyFile != "" {
		var data []byte
		if c.BodyFile == "-" {
			data, err = io.ReadAll(os.Stdin)
		} else {
			data, err = os.ReadFile(c.BodyFile)
		}
		if err != nil {
			return fmt.Errorf("failed to read body file: %w", err)
		}
		body = string(data)
	}

	if body == "" {
		return fmt.Errorf("message body is required (use --body, --body-file, or --body-html)")
	}

	ctx := context.Background()

	// Reply to existing message
	if c.ReplyToMessageID != "" {
		messageID := graph.ResolveID(c.ReplyToMessageID)
		replyMsg := map[string]interface{}{
			"message": map[string]interface{}{
				"body": map[string]string{
					"contentType": contentType,
					"content":     body,
				},
				"toRecipients":  formatRecipients(c.To),
				"ccRecipients":  formatRecipients(c.Cc),
				"bccRecipients": formatRecipients(c.Bcc),
			},
			"comment": body,
		}
		_, err = client.Post(ctx, fmt.Sprintf("/me/messages/%s/reply", messageID), replyMsg)
		if err != nil {
			return err
		}
	} else {
		msg := map[string]interface{}{
			"message": map[string]interface{}{
				"subject": c.Subject,
				"body": map[string]string{
					"contentType": contentType,
					"content":     body,
				},
				"toRecipients":  formatRecipients(c.To),
				"ccRecipients":  formatRecipients(c.Cc),
				"bccRecipients": formatRecipients(c.Bcc),
			},
		}
		_, err = client.Post(ctx, "/me/sendMail", msg)
		if err != nil {
			return err
		}
	}

	fmt.Println("✓ Email sent successfully")
	return nil
}

// MailFoldersCmd lists mail folders.
type MailFoldersCmd struct{}

// Run executes mail folders.
func (c *MailFoldersCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	data, err := client.Get(ctx, "/me/mailFolders", nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []MailFolder `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	fmt.Printf("%-10s %-20s %s\n", "UNREAD", "NAME", "ID")
	for _, f := range resp.Value {
		slug := graph.FormatID(f.ID)
		fmt.Printf("%-10d %-20s %s\n", f.UnreadItemCount, f.DisplayName, slug)
		if root.Verbose {
			fmt.Printf("           Full ID: %s\n", f.ID)
		}
	}
	return nil
}

// MailDraftsCmd handles draft operations.
type MailDraftsCmd struct {
	List   MailDraftsListCmd   `cmd:"" help:"List drafts"`
	Create MailDraftsCreateCmd `cmd:"" help:"Create a draft"`
	Send   MailDraftsSendCmd   `cmd:"" help:"Send a draft"`
	Delete MailDraftsDeleteCmd `cmd:"" help:"Delete a draft"`
}

// MailDraftsListCmd lists drafts.
type MailDraftsListCmd struct {
	Max int `help:"Maximum results" default:"25"`
}

// Run executes drafts list.
func (c *MailDraftsListCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$top", fmt.Sprintf("%d", c.Max))

	data, err := client.Get(ctx, "/me/mailFolders/drafts/messages", query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Message `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	if len(resp.Value) == 0 {
		fmt.Println("No drafts")
		return nil
	}

	for _, msg := range resp.Value {
		printMessage(msg, root.Verbose)
	}
	return nil
}

// MailDraftsCreateCmd creates a draft.
type MailDraftsCreateCmd struct {
	To       []string `help:"Recipient(s)"`
	Subject  string   `help:"Subject line"`
	Body     string   `help:"Message body"`
	BodyFile string   `help:"Read body from file" name:"body-file"`
}

// Run executes drafts create.
func (c *MailDraftsCreateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := c.Body
	if c.BodyFile != "" {
		data, err := os.ReadFile(c.BodyFile)
		if err != nil {
			return err
		}
		body = string(data)
	}

	msg := map[string]interface{}{
		"subject": c.Subject,
		"body": map[string]string{
			"contentType": "text",
			"content":     body,
		},
		"toRecipients": formatRecipients(c.To),
	}

	ctx := context.Background()
	data, err := client.Post(ctx, "/me/messages", msg)
	if err != nil {
		return err
	}

	var created Message
	if err := json.Unmarshal(data, &created); err != nil {
		return err
	}

	fmt.Printf("✓ Draft created: %s\n", graph.FormatID(created.ID))
	return nil
}

// MailDraftsSendCmd sends a draft.
type MailDraftsSendCmd struct {
	ID string `arg:"" help:"Draft ID"`
}

// Run executes drafts send.
func (c *MailDraftsSendCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/messages/%s/send", graph.ResolveID(c.ID))
	_, err = client.Post(ctx, path, nil)
	if err != nil {
		return err
	}

	fmt.Println("✓ Draft sent")
	return nil
}

// MailDraftsDeleteCmd deletes a draft.
type MailDraftsDeleteCmd struct {
	ID string `arg:"" help:"Draft ID"`
}

// Run executes drafts delete.
func (c *MailDraftsDeleteCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/messages/%s", graph.ResolveID(c.ID))
	if err := client.Delete(ctx, path); err != nil {
		return err
	}

	fmt.Println("✓ Draft deleted")
	return nil
}

// MailAttachmentCmd handles attachment operations.
type MailAttachmentCmd struct {
	List     MailAttachmentListCmd     `cmd:"" help:"List attachments"`
	Download MailAttachmentDownloadCmd `cmd:"" help:"Download an attachment"`
}

// MailAttachmentListCmd lists attachments.
type MailAttachmentListCmd struct {
	MessageID string `arg:"" help:"Message ID"`
}

// Run executes attachment list.
func (c *MailAttachmentListCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/messages/%s/attachments", graph.ResolveID(c.MessageID))
	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Attachment `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, a := range resp.Value {
		fmt.Printf("%s  %s (%d bytes)\n", graph.FormatID(a.ID), a.Name, a.Size)
	}
	return nil
}

// MailAttachmentDownloadCmd downloads an attachment.
type MailAttachmentDownloadCmd struct {
	MessageID    string `arg:"" help:"Message ID"`
	AttachmentID string `arg:"" help:"Attachment ID"`
	Out          string `help:"Output file path" required:""`
}

// Run executes attachment download.
func (c *MailAttachmentDownloadCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/messages/%s/attachments/%s",
		graph.ResolveID(c.MessageID), graph.ResolveID(c.AttachmentID))
	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var att Attachment
	if err := json.Unmarshal(data, &att); err != nil {
		return err
	}

	if err := os.WriteFile(c.Out, att.ContentBytes, 0644); err != nil {
		return err
	}

	fmt.Printf("✓ Downloaded: %s\n", c.Out)
	return nil
}

// Message represents an email message.
type Message struct {
	ID               string       `json:"id"`
	Subject          string       `json:"subject"`
	From             *EmailAddr   `json:"from"`
	ToRecipients     []EmailAddr  `json:"toRecipients"`
	ReceivedDateTime string       `json:"receivedDateTime"`
	IsRead           bool         `json:"isRead"`
	HasAttachments   bool         `json:"hasAttachments"`
	Body             *MessageBody `json:"body"`
}

// EmailAddr represents an email address.
type EmailAddr struct {
	EmailAddress struct {
		Name    string `json:"name"`
		Address string `json:"address"`
	} `json:"emailAddress"`
}

// MessageBody represents the body of a message.
type MessageBody struct {
	ContentType string `json:"contentType"`
	Content     string `json:"content"`
}

// MailFolder represents a mail folder.
type MailFolder struct {
	ID              string `json:"id"`
	DisplayName     string `json:"displayName"`
	UnreadItemCount int    `json:"unreadItemCount"`
	TotalItemCount  int    `json:"totalItemCount"`
}

// Attachment represents an attachment.
type Attachment struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	Size         int    `json:"size"`
	ContentType  string `json:"contentType"`
	ContentBytes []byte `json:"contentBytes"`
}

func formatRecipients(emails []string) []map[string]interface{} {
	var result []map[string]interface{}
	for _, email := range emails {
		result = append(result, map[string]interface{}{
			"emailAddress": map[string]string{
				"address": email,
			},
		})
	}
	return result
}

func printMessage(msg Message, verbose bool) {
	read := "●"
	if msg.IsRead {
		read = " "
	}
	attach := "  "
	if msg.HasAttachments {
		attach = "📎"
	}

	from := "Unknown"
	if msg.From != nil && msg.From.EmailAddress.Address != "" {
		from = msg.From.EmailAddress.Name
		if from == "" {
			from = msg.From.EmailAddress.Address
		}
	}
	if len(from) > 20 {
		from = from[:20]
	}

	date := formatMessageDate(msg.ReceivedDateTime)
	subject := msg.Subject
	if subject == "" {
		subject = "(no subject)"
	}

	fmt.Printf("%s %s %-8s %-20s %s\n", read, attach, date, from, subject)
	fmt.Printf("  ID: %s\n", graph.FormatID(msg.ID))
	if verbose {
		fmt.Printf("  Full: %s\n", msg.ID)
	}
}

func printMessageDetail(msg Message, verbose bool) {
	fmt.Printf("ID:      %s\n", graph.FormatID(msg.ID))
	if verbose {
		fmt.Printf("Full ID: %s\n", msg.ID)
	}
	fmt.Printf("Subject: %s\n", msg.Subject)
	if msg.From != nil {
		fmt.Printf("From:    %s <%s>\n", msg.From.EmailAddress.Name, msg.From.EmailAddress.Address)
	}
	fmt.Printf("Date:    %s\n", msg.ReceivedDateTime)
	fmt.Printf("Read:    %v\n", msg.IsRead)
	if msg.Body != nil {
		fmt.Println("\n--- Body ---")
		content := msg.Body.Content
		if msg.Body.ContentType == "html" {
			content = stripHTML(content)
		}
		fmt.Println(content)
	}
}

func formatMessageDate(dateStr string) string {
	t, err := time.Parse(time.RFC3339, dateStr)
	if err != nil {
		return dateStr[:10]
	}

	now := time.Now()
	diff := now.Sub(t)

	if diff < 24*time.Hour && t.Day() == now.Day() {
		return t.Format("15:04")
	} else if diff < 7*24*time.Hour {
		return t.Format("Mon")
	}
	return t.Format("Jan 2")
}

func stripHTML(html string) string {
	// Simple HTML stripping - remove tags
	result := html
	for {
		start := strings.Index(result, "<")
		if start == -1 {
			break
		}
		end := strings.Index(result[start:], ">")
		if end == -1 {
			break
		}
		result = result[:start] + result[start+end+1:]
	}
	return strings.TrimSpace(result)
}

func outputJSON(v interface{}) error {
	data, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return err
	}
	fmt.Println(string(data))
	return nil
}
