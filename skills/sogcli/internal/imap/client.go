// Package imap provides IMAP client functionality.
package imap

import (
	"crypto/tls"
	"fmt"
	"strings"
	"time"

	"github.com/emersion/go-imap/v2"
	"github.com/emersion/go-imap/v2/imapclient"
)

// Client wraps an IMAP connection.
type Client struct {
	client *imapclient.Client
	email  string
}

// Config holds IMAP connection configuration.
type Config struct {
	Host     string
	Port     int
	TLS      bool
	Insecure bool // Skip TLS cert verification
	NoTLS    bool // Disable TLS entirely
	Email    string
	Password string
}

// Connect establishes an IMAP connection.
func Connect(cfg Config) (*Client, error) {
	addr := fmt.Sprintf("%s:%d", cfg.Host, cfg.Port)

	var client *imapclient.Client
	var err error

	if cfg.NoTLS {
		// Plain text connection
		client, err = imapclient.DialInsecure(addr, nil)
	} else if cfg.TLS {
		// TLS connection
		tlsConfig := &tls.Config{
			ServerName:         cfg.Host,
			InsecureSkipVerify: cfg.Insecure,
		}
		opts := &imapclient.Options{
			TLSConfig: tlsConfig,
		}
		client, err = imapclient.DialTLS(addr, opts)
	} else {
		client, err = imapclient.DialInsecure(addr, nil)
	}
	if err != nil {
		return nil, fmt.Errorf("failed to connect: %w", err)
	}

	// Login
	if err := client.Login(cfg.Email, cfg.Password).Wait(); err != nil {
		client.Close()
		return nil, fmt.Errorf("failed to login: %w", err)
	}

	return &Client{client: client, email: cfg.Email}, nil
}

// Close closes the IMAP connection.
func (c *Client) Close() error {
	if c.client != nil {
		return c.client.Close()
	}
	return nil
}

// ListFolders returns all mailbox names.
func (c *Client) ListFolders() ([]string, error) {
	listCmd := c.client.List("", "*", nil)
	mailboxes, err := listCmd.Collect()
	if err != nil {
		return nil, fmt.Errorf("failed to list folders: %w", err)
	}

	names := make([]string, len(mailboxes))
	for i, mb := range mailboxes {
		names[i] = mb.Mailbox
	}
	return names, nil
}

// Message represents an email message.
type Message struct {
	UID     uint32
	Subject string
	From    string
	To      string
	Date    string
	Seen    bool
	Body    string
}

// ListMessages returns messages from a folder.
func (c *Client) ListMessages(folder string, max int, unseenOnly bool) ([]Message, error) {
	// Select mailbox
	selectData, err := c.client.Select(folder, nil).Wait()
	if err != nil {
		return nil, fmt.Errorf("failed to select folder: %w", err)
	}

	// If no messages, return early
	if selectData.NumMessages == 0 {
		return nil, nil
	}

	// Build sequence set for last N messages
	start := uint32(1)
	if selectData.NumMessages > uint32(max) {
		start = selectData.NumMessages - uint32(max) + 1
	}
	seqSet := imap.SeqSet{}
	seqSet.AddRange(start, selectData.NumMessages)

	// Fetch messages
	fetchOptions := &imap.FetchOptions{
		Flags:    true,
		Envelope: true,
		UID:      true,
	}

	fetchCmd := c.client.Fetch(seqSet, fetchOptions)
	messages := make([]Message, 0, max)

	for {
		msgData := fetchCmd.Next()
		if msgData == nil {
			break
		}

		buf, err := msgData.Collect()
		if err != nil {
			continue
		}

		m := Message{
			UID: uint32(buf.UID),
		}

		if buf.Envelope != nil {
			m.Subject = buf.Envelope.Subject
			m.Date = buf.Envelope.Date.Format("Jan 02")
			if len(buf.Envelope.From) > 0 {
				from := buf.Envelope.From[0]
				if from.Name != "" {
					m.From = from.Name
				} else {
					m.From = from.Addr()
				}
			}
		}

		for _, f := range buf.Flags {
			if f == imap.FlagSeen {
				m.Seen = true
				break
			}
		}

		messages = append(messages, m)
	}

	if err := fetchCmd.Close(); err != nil {
		return nil, fmt.Errorf("failed to fetch: %w", err)
	}

	return messages, nil
}

// GetMessage fetches a single message by UID.
func (c *Client) GetMessage(folder string, uid uint32, headersOnly bool) (*Message, error) {
	// Select mailbox
	_, err := c.client.Select(folder, nil).Wait()
	if err != nil {
		return nil, fmt.Errorf("failed to select folder: %w", err)
	}

	uidSet := imap.UIDSet{}
	uidSet.AddNum(imap.UID(uid))

	fetchOptions := &imap.FetchOptions{
		Flags:    true,
		Envelope: true,
		UID:      true,
	}

	if !headersOnly {
		fetchOptions.BodySection = []*imap.FetchItemBodySection{{}}
	}

	fetchCmd := c.client.Fetch(uidSet, fetchOptions)

	msgData := fetchCmd.Next()
	if msgData == nil {
		return nil, fmt.Errorf("message not found: %d", uid)
	}

	buf, err := msgData.Collect()
	if err != nil {
		return nil, fmt.Errorf("failed to collect message: %w", err)
	}

	m := &Message{
		UID: uint32(buf.UID),
	}

	if buf.Envelope != nil {
		m.Subject = buf.Envelope.Subject
		m.Date = buf.Envelope.Date.String()
		if len(buf.Envelope.From) > 0 {
			m.From = buf.Envelope.From[0].Addr()
		}
		if len(buf.Envelope.To) > 0 {
			m.To = buf.Envelope.To[0].Addr()
		}
	}

	// Extract body
	if len(buf.BodySection) > 0 {
		m.Body = string(buf.BodySection[0].Bytes)
	}

	if err := fetchCmd.Close(); err != nil {
		return nil, fmt.Errorf("failed to fetch: %w", err)
	}

	return m, nil
}

// SearchMessages searches for messages matching the query.
// Query format: IMAP-style search terms (FROM, TO, SUBJECT, SINCE, BEFORE, TEXT, etc.)
// Examples:
//   - "ALL" - all messages (fallback to list)
//   - "FROM viz" - messages from viz
//   - "SUBJECT meeting" - messages with "meeting" in subject
//   - "SINCE 1-Jan-2026" - messages since date
//   - "FROM viz SUBJECT test" - combined search
func (c *Client) SearchMessages(folder, query string, max int) ([]Message, error) {
	// Parse query into search criteria
	criteria, err := parseSearchQuery(query)
	if err != nil {
		return nil, fmt.Errorf("failed to parse query: %w", err)
	}

	// If criteria is nil (ALL), fall back to ListMessages
	if criteria == nil {
		return c.ListMessages(folder, max, false)
	}

	// Select mailbox
	_, err = c.client.Select(folder, nil).Wait()
	if err != nil {
		return nil, fmt.Errorf("failed to select folder: %w", err)
	}

	// Search for messages
	searchCmd := c.client.Search(criteria, nil)
	searchData, err := searchCmd.Wait()
	if err != nil {
		return nil, fmt.Errorf("failed to search: %w", err)
	}

	// Get UIDs
	uids := searchData.AllUIDs()
	if len(uids) == 0 {
		return nil, nil
	}

	// Limit results (take most recent)
	if len(uids) > max {
		uids = uids[len(uids)-max:]
	}

	// Fetch messages
	fetchOptions := &imap.FetchOptions{
		Flags:    true,
		Envelope: true,
		UID:      true,
	}

	uidSet := imap.UIDSet{}
	for _, uid := range uids {
		uidSet.AddNum(uid)
	}

	fetchCmd := c.client.Fetch(uidSet, fetchOptions)
	messages := make([]Message, 0, len(uids))

	for {
		msgData := fetchCmd.Next()
		if msgData == nil {
			break
		}

		buf, err := msgData.Collect()
		if err != nil {
			continue
		}

		m := Message{
			UID: uint32(buf.UID),
		}

		if buf.Envelope != nil {
			m.Subject = buf.Envelope.Subject
			m.Date = buf.Envelope.Date.Format("Jan 02")
			if len(buf.Envelope.From) > 0 {
				from := buf.Envelope.From[0]
				if from.Name != "" {
					m.From = from.Name
				} else {
					m.From = from.Addr()
				}
			}
		}

		for _, f := range buf.Flags {
			if f == imap.FlagSeen {
				m.Seen = true
				break
			}
		}

		messages = append(messages, m)
	}

	if err := fetchCmd.Close(); err != nil {
		return nil, fmt.Errorf("failed to fetch: %w", err)
	}

	return messages, nil
}

// parseSearchQuery parses a simple search query into IMAP search criteria.
// Returns nil criteria for "ALL" to indicate list-all fallback.
func parseSearchQuery(query string) (*imap.SearchCriteria, error) {
	// Special case: ALL returns nil to trigger fallback
	if strings.ToUpper(strings.TrimSpace(query)) == "ALL" {
		return nil, nil
	}
	
	criteria := &imap.SearchCriteria{}
	
	// Simple parser: look for known keywords
	tokens := strings.Fields(query)
	
	for i := 0; i < len(tokens); i++ {
		keyword := strings.ToUpper(tokens[i])
		
		switch keyword {
		case "FROM":
			if i+1 < len(tokens) {
				i++
				criteria.Header = append(criteria.Header, imap.SearchCriteriaHeaderField{
					Key:   "From",
					Value: tokens[i],
				})
			}
		case "TO":
			if i+1 < len(tokens) {
				i++
				criteria.Header = append(criteria.Header, imap.SearchCriteriaHeaderField{
					Key:   "To",
					Value: tokens[i],
				})
			}
		case "SUBJECT":
			if i+1 < len(tokens) {
				i++
				criteria.Header = append(criteria.Header, imap.SearchCriteriaHeaderField{
					Key:   "Subject",
					Value: tokens[i],
				})
			}
		case "TEXT", "BODY":
			if i+1 < len(tokens) {
				i++
				criteria.Text = append(criteria.Text, tokens[i])
			}
		case "UNSEEN", "UNREAD":
			criteria.NotFlag = append(criteria.NotFlag, imap.FlagSeen)
		case "SEEN", "READ":
			criteria.Flag = append(criteria.Flag, imap.FlagSeen)
		case "FLAGGED", "STARRED":
			criteria.Flag = append(criteria.Flag, imap.FlagFlagged)
		case "SINCE":
			if i+1 < len(tokens) {
				i++
				t, err := parseDate(tokens[i])
				if err == nil {
					criteria.Since = t
				}
			}
		case "BEFORE":
			if i+1 < len(tokens) {
				i++
				t, err := parseDate(tokens[i])
				if err == nil {
					criteria.Before = t
				}
			}
		default:
			// Treat as text search
			criteria.Text = append(criteria.Text, tokens[i])
		}
	}
	
	return criteria, nil
}

// parseDate parses common date formats.
func parseDate(s string) (time.Time, error) {
	formats := []string{
		"2-Jan-2006",
		"02-Jan-2006",
		"2006-01-02",
		"01/02/2006",
		"1/2/2006",
	}
	
	for _, format := range formats {
		if t, err := time.Parse(format, s); err == nil {
			return t, nil
		}
	}
	
	return time.Time{}, fmt.Errorf("unable to parse date: %s", s)
}


// MoveMessage moves a message to a different folder.
func (c *Client) MoveMessage(srcFolder string, uid uint32, dstFolder string) error {
	// Select source mailbox
	_, err := c.client.Select(srcFolder, nil).Wait()
	if err != nil {
		return fmt.Errorf("failed to select folder: %w", err)
	}

	uidSet := imap.UIDSet{}
	uidSet.AddNum(imap.UID(uid))

	// Try MOVE command (handles fallback internally)
	moveCmd := c.client.Move(uidSet, dstFolder)
	_, err = moveCmd.Wait()
	if err != nil {
		return fmt.Errorf("failed to move: %w", err)
	}

	return nil
}

// CopyMessage copies a message to a different folder.
func (c *Client) CopyMessage(srcFolder string, uid uint32, dstFolder string) error {
	// Select source mailbox
	_, err := c.client.Select(srcFolder, nil).Wait()
	if err != nil {
		return fmt.Errorf("failed to select folder: %w", err)
	}

	uidSet := imap.UIDSet{}
	uidSet.AddNum(imap.UID(uid))

	copyCmd := c.client.Copy(uidSet, dstFolder)
	_, err = copyCmd.Wait()
	if err != nil {
		return fmt.Errorf("failed to copy: %w", err)
	}

	return nil
}

// SetFlag adds or removes a flag on a message.
func (c *Client) SetFlag(folder string, uid uint32, flag string, add bool) error {
	// Select mailbox
	_, err := c.client.Select(folder, nil).Wait()
	if err != nil {
		return fmt.Errorf("failed to select folder: %w", err)
	}

	uidSet := imap.UIDSet{}
	uidSet.AddNum(imap.UID(uid))

	// Map flag name to IMAP flag
	var imapFlag imap.Flag
	switch strings.ToLower(flag) {
	case "seen", "read":
		imapFlag = imap.FlagSeen
	case "flagged", "starred":
		imapFlag = imap.FlagFlagged
	case "answered", "replied":
		imapFlag = imap.FlagAnswered
	case "deleted":
		imapFlag = imap.FlagDeleted
	case "draft":
		imapFlag = imap.FlagDraft
	default:
		return fmt.Errorf("unknown flag: %s", flag)
	}

	op := imap.StoreFlagsAdd
	if !add {
		op = imap.StoreFlagsDel
	}

	storeFlags := &imap.StoreFlags{
		Op:     op,
		Silent: true,
		Flags:  []imap.Flag{imapFlag},
	}

	storeCmd := c.client.Store(uidSet, storeFlags, nil)
	if err := storeCmd.Close(); err != nil {
		return fmt.Errorf("failed to set flag: %w", err)
	}

	return nil
}

// DeleteMessage marks a message as deleted and expunges.
func (c *Client) DeleteMessage(folder string, uid uint32) error {
	if err := c.SetFlag(folder, uid, "deleted", true); err != nil {
		return err
	}

	// Expunge
	expungeCmd := c.client.Expunge()
	if err := expungeCmd.Close(); err != nil {
		return fmt.Errorf("failed to expunge: %w", err)
	}

	return nil
}

// CreateFolder creates a new mailbox.
func (c *Client) CreateFolder(name string) error {
	createCmd := c.client.Create(name, nil)
	if err := createCmd.Wait(); err != nil {
		return fmt.Errorf("failed to create folder: %w", err)
	}
	return nil
}

// DeleteFolder deletes a mailbox.
func (c *Client) DeleteFolder(name string) error {
	deleteCmd := c.client.Delete(name)
	if err := deleteCmd.Wait(); err != nil {
		return fmt.Errorf("failed to delete folder: %w", err)
	}
	return nil
}

// RenameFolder renames a mailbox.
func (c *Client) RenameFolder(oldName, newName string) error {
	renameCmd := c.client.Rename(oldName, newName)
	if err := renameCmd.Wait(); err != nil {
		return fmt.Errorf("failed to rename folder: %w", err)
	}
	return nil
}


// SaveDraft saves a message to the Drafts folder.
func (c *Client) SaveDraft(msg *Message) (uint32, error) {
	// Build RFC822 message
	var content strings.Builder
	content.WriteString(fmt.Sprintf("From: %s\r\n", msg.From))
	if msg.To != "" {
		content.WriteString(fmt.Sprintf("To: %s\r\n", msg.To))
	}
	content.WriteString(fmt.Sprintf("Subject: %s\r\n", msg.Subject))
	content.WriteString("MIME-Version: 1.0\r\n")
	content.WriteString("Content-Type: text/plain; charset=utf-8\r\n")
	content.WriteString("\r\n")
	content.WriteString(msg.Body)

	msgBytes := []byte(content.String())

	// Append to Drafts with Draft flag
	appendCmd := c.client.Append("Drafts", int64(len(msgBytes)), &imap.AppendOptions{
		Flags: []imap.Flag{imap.FlagDraft},
	})

	if _, err := appendCmd.Write(msgBytes); err != nil {
		return 0, fmt.Errorf("failed to write draft: %w", err)
	}

	if err := appendCmd.Close(); err != nil {
		return 0, fmt.Errorf("failed to close draft: %w", err)
	}

	data, err := appendCmd.Wait()
	if err != nil {
		return 0, fmt.Errorf("failed to save draft: %w", err)
	}

	if data.UID != 0 {
		return uint32(data.UID), nil
	}

	return 0, nil
}

// ListDrafts returns messages from the Drafts folder.
func (c *Client) ListDrafts(max int) ([]Message, error) {
	return c.ListMessages("Drafts", max, false)
}

// DeleteDraft deletes a draft by UID.
func (c *Client) DeleteDraft(uid uint32) error {
	return c.DeleteMessage("Drafts", uid)
}

// Idle starts IMAP IDLE and calls the callback when new mail arrives.

// Idle starts IMAP IDLE and calls the callback when new mail arrives.
// This is a simplified implementation that uses polling with IDLE keepalive.
func (c *Client) Idle(folder string, callback func(msgCount uint32)) error {
	// Select mailbox
	selectData, err := c.client.Select(folder, nil).Wait()
	if err != nil {
		return fmt.Errorf("failed to select folder: %w", err)
	}

	lastCount := selectData.NumMessages

	for {
		// Start IDLE - this blocks until server sends data or timeout
		idleCmd, err := c.client.Idle()
		if err != nil {
			return fmt.Errorf("failed to start idle: %w", err)
		}

		// Wait for IDLE to complete (server sends untagged response or timeout)
		err = idleCmd.Wait()
		if err != nil {
			idleCmd.Close()
			return fmt.Errorf("idle error: %w", err)
		}

		idleCmd.Close()

		// Check for new messages by doing a NOOP
		status, err := c.client.Status(folder, &imap.StatusOptions{
			NumMessages: true,
		}).Wait()
		if err != nil {
			return fmt.Errorf("status error: %w", err)
		}

		if status.NumMessages != nil && *status.NumMessages > lastCount {
			if callback != nil {
				callback(*status.NumMessages)
			}
			lastCount = *status.NumMessages
		}
	}
}
