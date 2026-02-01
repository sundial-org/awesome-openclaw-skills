package cli

import (
	"context"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/visionik/sogcli/internal/config"
	"github.com/visionik/sogcli/internal/imap"
	"github.com/visionik/sogcli/internal/smtp"
)

// MailCmd handles reading and sending mail.
type MailCmd struct {
	List    MailListCmd    `cmd:"" help:"List messages in a folder"`
	Get     MailGetCmd     `cmd:"" help:"Get a message by UID"`
	Search  MailSearchCmd  `cmd:"" help:"Search messages"`
	Send    MailSendCmd    `cmd:"" help:"Send a message"`
	Reply   MailReplyCmd   `cmd:"" help:"Reply to a message"`
	Forward MailForwardCmd `cmd:"" help:"Forward a message"`
	Move    MailMoveCmd    `cmd:"" help:"Move a message to another folder"`
	Copy    MailCopyCmd    `cmd:"" help:"Copy a message to another folder"`
	Flag    MailFlagCmd    `cmd:"" help:"Set a flag on a message"`
	Unflag  MailUnflagCmd  `cmd:"" help:"Remove a flag from a message"`
	Delete  MailDeleteCmd  `cmd:"" help:"Delete a message"`
}

// MailListCmd lists messages in a folder.
type MailListCmd struct {
	Folder string `arg:"" optional:"" default:"INBOX" help:"Folder to list"`
	Max    int    `help:"Maximum messages to return" default:"20"`
	Unseen bool   `help:"Only show unread messages"`
}

// Run executes the mail list command.
func (c *MailListCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified. Use --account or set a default")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	client, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer client.Close()

	messages, err := client.ListMessages(c.Folder, c.Max, c.Unseen)
	if err != nil {
		return fmt.Errorf("failed to list messages: %w", err)
	}

	if len(messages) == 0 {
		fmt.Println("No messages found.")
		return nil
	}

	// Output
	if root.JSON {
		// TODO: Use output formatter
		for _, m := range messages {
			fmt.Printf(`{"uid":%d,"from":"%s","date":"%s","subject":"%s","seen":%t}`+"\n",
				m.UID, m.From, m.Date, m.Subject, m.Seen)
		}
	} else {
		fmt.Printf("%-8s %-12s %-24s %s\n", "UID", "DATE", "FROM", "SUBJECT")
		for _, m := range messages {
			marker := " "
			if !m.Seen {
				marker = "*"
			}
			from := m.From
			if len(from) > 24 {
				from = from[:21] + "..."
			}
			subject := m.Subject
			if len(subject) > 50 {
				subject = subject[:47] + "..."
			}
			fmt.Printf("%s%-7d %-12s %-24s %s\n", marker, m.UID, m.Date, from, subject)
		}
	}

	return nil
}

// MailGetCmd fetches a message by UID.
type MailGetCmd struct {
	UID     uint32 `arg:"" help:"Message UID"`
	Folder  string `help:"Folder containing the message" default:"INBOX"`
	Headers bool   `help:"Show headers only"`
	Raw     bool   `help:"Output raw RFC822 format"`
}

// Run executes the mail get command.
func (c *MailGetCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified. Use --account or set a default")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	client, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer client.Close()

	msg, err := client.GetMessage(c.Folder, c.UID, c.Headers)
	if err != nil {
		return fmt.Errorf("failed to get message: %w", err)
	}

	if root.JSON {
		fmt.Printf(`{"uid":%d,"from":"%s","date":"%s","subject":"%s","body":"%s"}`+"\n",
			msg.UID, msg.From, msg.Date, msg.Subject, msg.Body)
	} else {
		fmt.Printf("From: %s\n", msg.From)
		fmt.Printf("Date: %s\n", msg.Date)
		fmt.Printf("Subject: %s\n", msg.Subject)
		if !c.Headers && msg.Body != "" {
			fmt.Println("")
			fmt.Println(msg.Body)
		}
	}

	return nil
}

// MailSearchCmd searches messages.
type MailSearchCmd struct {
	Query  string `arg:"" help:"IMAP SEARCH query"`
	Folder string `help:"Folder to search" default:"INBOX"`
	Max    int    `help:"Maximum results" default:"20"`
}

// Run executes the mail search command.
func (c *MailSearchCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified. Use --account or set a default")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	client, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer client.Close()

	messages, err := client.SearchMessages(c.Folder, c.Query, c.Max)
	if err != nil {
		return fmt.Errorf("failed to search: %w", err)
	}

	if len(messages) == 0 {
		fmt.Println("No messages found.")
		return nil
	}

	if root.JSON {
		for _, m := range messages {
			fmt.Printf(`{"uid":%d,"from":"%s","date":"%s","subject":"%s","seen":%t}`+"\n",
				m.UID, m.From, m.Date, m.Subject, m.Seen)
		}
	} else {
		fmt.Printf("%-8s %-12s %-24s %s\n", "UID", "DATE", "FROM", "SUBJECT")
		for _, m := range messages {
			marker := " "
			if !m.Seen {
				marker = "*"
			}
			from := m.From
			if len(from) > 24 {
				from = from[:21] + "..."
			}
			subject := m.Subject
			if len(subject) > 50 {
				subject = subject[:47] + "..."
			}
			fmt.Printf("%s%-7d %-12s %-24s %s\n", marker, m.UID, m.Date, from, subject)
		}
	}

	return nil
}

// MailSendCmd sends a message.
type MailSendCmd struct {
	To       string `help:"Recipients (comma-separated)" required:""`
	Cc       string `help:"CC recipients (comma-separated)"`
	Bcc      string `help:"BCC recipients (comma-separated)"`
	Subject  string `help:"Subject line" required:""`
	Body     string `help:"Body (plain text)"`
	BodyFile string `help:"Body file path (plain text; '-' for stdin)" name:"body-file"`
}

// Run executes the mail send command.
func (c *MailSendCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified. Use --account or set a default")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	// Get body content
	body := c.Body
	if c.BodyFile != "" {
		var data []byte
		if c.BodyFile == "-" {
			data, err = io.ReadAll(os.Stdin)
		} else {
			data, err = os.ReadFile(c.BodyFile)
		}
		if err != nil {
			return fmt.Errorf("failed to read body: %w", err)
		}
		body = string(data)
	}

	if body == "" {
		return fmt.Errorf("--body or --body-file is required")
	}

	// Parse comma-separated recipients
	to := parseRecipients(c.To)
	cc := parseRecipients(c.Cc)
	bcc := parseRecipients(c.Bcc)

	// Create SMTP client
	smtpClient := smtp.NewClient(smtp.Config{
		Host:     acct.SMTP.Host,
		Port:     acct.SMTP.Port,
		TLS:      acct.SMTP.TLS,
		StartTLS: acct.SMTP.StartTLS,
		Insecure: acct.SMTP.Insecure,
		NoTLS:    acct.SMTP.NoTLS,
		Email:    email,
		Password: password,
	})

	// Send
	msg := &smtp.Message{
		From:    email,
		To:      to,
		Cc:      cc,
		Bcc:     bcc,
		Subject: c.Subject,
		Body:    body,
	}

	if err := smtpClient.Send(context.Background(), msg); err != nil {
		return fmt.Errorf("failed to send: %w", err)
	}

	fmt.Printf("Sent to %v\n", to)
	return nil
}

// parseRecipients splits a comma-separated string into trimmed recipients.
func parseRecipients(s string) []string {
	if s == "" {
		return nil
	}
	parts := strings.Split(s, ",")
	result := make([]string, 0, len(parts))
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if p != "" {
			result = append(result, p)
		}
	}
	return result
}

// MailMoveCmd moves a message to another folder.
type MailMoveCmd struct {
	UID    uint32 `arg:"" help:"Message UID"`
	Folder string `arg:"" help:"Destination folder"`
	From   string `help:"Source folder" default:"INBOX"`
}

// Run executes the mail move command.
func (c *MailMoveCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	client, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer client.Close()

	if err := client.MoveMessage(c.From, c.UID, c.Folder); err != nil {
		return err
	}

	fmt.Printf("Moved message %d to %s\n", c.UID, c.Folder)
	return nil
}

// MailCopyCmd copies a message to another folder.
type MailCopyCmd struct {
	UID    uint32 `arg:"" help:"Message UID"`
	Folder string `arg:"" help:"Destination folder"`
	From   string `help:"Source folder" default:"INBOX"`
}

// Run executes the mail copy command.
func (c *MailCopyCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	client, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer client.Close()

	if err := client.CopyMessage(c.From, c.UID, c.Folder); err != nil {
		return err
	}

	fmt.Printf("Copied message %d to %s\n", c.UID, c.Folder)
	return nil
}

// MailFlagCmd sets a flag on a message.
type MailFlagCmd struct {
	UID    uint32 `arg:"" help:"Message UID"`
	Flag   string `arg:"" help:"Flag to set (seen, flagged, answered, deleted, draft)"`
	Folder string `help:"Folder containing the message" default:"INBOX"`
}

// Run executes the mail flag command.
func (c *MailFlagCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	client, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer client.Close()

	if err := client.SetFlag(c.Folder, c.UID, c.Flag, true); err != nil {
		return err
	}

	fmt.Printf("Set %s flag on message %d\n", c.Flag, c.UID)
	return nil
}

// MailUnflagCmd removes a flag from a message.
type MailUnflagCmd struct {
	UID    uint32 `arg:"" help:"Message UID"`
	Flag   string `arg:"" help:"Flag to remove (seen, flagged, answered, deleted, draft)"`
	Folder string `help:"Folder containing the message" default:"INBOX"`
}

// Run executes the mail unflag command.
func (c *MailUnflagCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	client, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer client.Close()

	if err := client.SetFlag(c.Folder, c.UID, c.Flag, false); err != nil {
		return err
	}

	fmt.Printf("Removed %s flag from message %d\n", c.Flag, c.UID)
	return nil
}

// MailDeleteCmd deletes a message.
type MailDeleteCmd struct {
	UID    uint32 `arg:"" help:"Message UID"`
	Folder string `help:"Folder containing the message" default:"INBOX"`
}

// Run executes the mail delete command.
func (c *MailDeleteCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	client, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer client.Close()

	// TODO: Confirmation prompt if not --force

	if err := client.DeleteMessage(c.Folder, c.UID); err != nil {
		return err
	}

	fmt.Printf("Deleted message %d\n", c.UID)
	return nil
}

// MailReplyCmd replies to a message.
type MailReplyCmd struct {
	UID     uint32 `arg:"" help:"Message UID to reply to"`
	Body    string `help:"Reply body (plain text)" required:""`
	All     bool   `help:"Reply to all recipients" name:"all"`
	Folder  string `help:"Folder containing the message" default:"INBOX"`
}

// Run executes the mail reply command.
func (c *MailReplyCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	// Get original message
	imapClient, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer imapClient.Close()

	original, err := imapClient.GetMessage(c.Folder, c.UID, false)
	if err != nil {
		return fmt.Errorf("failed to get message: %w", err)
	}

	// Build reply
	to := original.From
	subject := original.Subject
	if !strings.HasPrefix(strings.ToLower(subject), "re:") {
		subject = "Re: " + subject
	}

	// Send via SMTP
	smtpClient := smtp.NewClient(smtp.Config{
		Host:     acct.SMTP.Host,
		Port:     acct.SMTP.Port,
		TLS:      acct.SMTP.TLS,
		StartTLS: acct.SMTP.StartTLS,
		Insecure: acct.SMTP.Insecure,
		NoTLS:    acct.SMTP.NoTLS,
		Email:    email,
		Password: password,
	})

	msg := &smtp.Message{
		From:    email,
		To:      []string{to},
		Subject: subject,
		Body:    c.Body,
	}

	if err := smtpClient.Send(context.Background(), msg); err != nil {
		return fmt.Errorf("failed to send: %w", err)
	}

	// Mark original as answered
	_ = imapClient.SetFlag(c.Folder, c.UID, "answered", true)

	fmt.Printf("Replied to %s\n", to)
	return nil
}

// MailForwardCmd forwards a message.
type MailForwardCmd struct {
	UID    uint32 `arg:"" help:"Message UID to forward"`
	To     string `help:"Forward to (comma-separated)" required:""`
	Body   string `help:"Additional message (plain text)"`
	Folder string `help:"Folder containing the message" default:"INBOX"`
}

// Run executes the mail forward command.
func (c *MailForwardCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return err
	}

	password, err := cfg.GetPassword(email)
	if err != nil {
		return fmt.Errorf("failed to get password: %w", err)
	}

	// Get original message
	imapClient, err := imap.Connect(imap.Config{
		Host:     acct.IMAP.Host,
		Port:     acct.IMAP.Port,
		TLS:      acct.IMAP.TLS,
		Insecure: acct.IMAP.Insecure,
		NoTLS:    acct.IMAP.NoTLS,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer imapClient.Close()

	original, err := imapClient.GetMessage(c.Folder, c.UID, false)
	if err != nil {
		return fmt.Errorf("failed to get message: %w", err)
	}

	// Build forwarded message
	subject := original.Subject
	if !strings.HasPrefix(strings.ToLower(subject), "fwd:") {
		subject = "Fwd: " + subject
	}

	body := c.Body
	if body != "" {
		body += "\n\n"
	}
	body += "---------- Forwarded message ----------\n"
	body += fmt.Sprintf("From: %s\n", original.From)
	body += fmt.Sprintf("Date: %s\n", original.Date)
	body += fmt.Sprintf("Subject: %s\n\n", original.Subject)
	body += original.Body

	// Send via SMTP
	smtpClient := smtp.NewClient(smtp.Config{
		Host:     acct.SMTP.Host,
		Port:     acct.SMTP.Port,
		TLS:      acct.SMTP.TLS,
		StartTLS: acct.SMTP.StartTLS,
		Insecure: acct.SMTP.Insecure,
		NoTLS:    acct.SMTP.NoTLS,
		Email:    email,
		Password: password,
	})

	to := parseRecipients(c.To)

	msg := &smtp.Message{
		From:    email,
		To:      to,
		Subject: subject,
		Body:    body,
	}

	if err := smtpClient.Send(context.Background(), msg); err != nil {
		return fmt.Errorf("failed to send: %w", err)
	}

	fmt.Printf("Forwarded to %v\n", to)
	return nil
}
