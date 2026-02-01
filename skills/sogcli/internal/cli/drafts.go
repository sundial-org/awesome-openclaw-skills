package cli

import (
	"fmt"

	"github.com/visionik/sogcli/internal/config"
	"github.com/visionik/sogcli/internal/imap"
)

// DraftsCmd handles draft management.
type DraftsCmd struct {
	List   DraftsListCmd   `cmd:"" help:"List drafts"`
	Create DraftsCreateCmd `cmd:"" help:"Create a draft"`
	Send   DraftsSendCmd   `cmd:"" help:"Send a draft"`
	Delete DraftsDeleteCmd `cmd:"" help:"Delete a draft"`
}

// DraftsListCmd lists drafts.
type DraftsListCmd struct {
	Max int `help:"Maximum drafts to return" default:"20"`
}

// Run executes the drafts list command.
func (c *DraftsListCmd) Run(root *Root) error {
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

	drafts, err := client.ListDrafts(c.Max)
	if err != nil {
		return fmt.Errorf("failed to list drafts: %w", err)
	}

	if len(drafts) == 0 {
		fmt.Println("No drafts found.")
		return nil
	}

	fmt.Printf("%-8s %-12s %-24s %s\n", "UID", "DATE", "TO", "SUBJECT")
	for _, d := range drafts {
		to := d.To
		if len(to) > 24 {
			to = to[:21] + "..."
		}
		subject := d.Subject
		if len(subject) > 50 {
			subject = subject[:47] + "..."
		}
		fmt.Printf("%-8d %-12s %-24s %s\n", d.UID, d.Date, to, subject)
	}

	return nil
}

// DraftsCreateCmd creates a new draft.
type DraftsCreateCmd struct {
	To       string `help:"Recipients (comma-separated)"`
	Subject  string `help:"Subject line"`
	Body     string `help:"Body (plain text)"`
	BodyFile string `help:"Body file path (plain text; '-' for stdin)" name:"body-file"`
}

// Run executes the drafts create command.
func (c *DraftsCreateCmd) Run(root *Root) error {
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

	body := c.Body
	// TODO: Read from file if --body-file specified

	draft := &imap.Message{
		From:    email,
		To:      c.To,
		Subject: c.Subject,
		Body:    body,
	}

	uid, err := client.SaveDraft(draft)
	if err != nil {
		return fmt.Errorf("failed to save draft: %w", err)
	}

	if uid > 0 {
		fmt.Printf("Created draft: UID %d\n", uid)
	} else {
		fmt.Println("Created draft")
	}
	return nil
}

// DraftsSendCmd sends a draft.
type DraftsSendCmd struct {
	UID uint32 `arg:"" help:"Draft UID to send"`
}

// Run executes the drafts send command.
func (c *DraftsSendCmd) Run(root *Root) error {
	// TODO: Fetch draft, send via SMTP, delete draft
	fmt.Printf("Sending draft %d... (not yet implemented)\n", c.UID)
	return nil
}

// DraftsDeleteCmd deletes a draft.
type DraftsDeleteCmd struct {
	UID uint32 `arg:"" help:"Draft UID to delete"`
}

// Run executes the drafts delete command.
func (c *DraftsDeleteCmd) Run(root *Root) error {
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

	if err := client.DeleteDraft(c.UID); err != nil {
		return fmt.Errorf("failed to delete draft: %w", err)
	}

	fmt.Printf("Deleted draft %d\n", c.UID)
	return nil
}
