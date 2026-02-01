package cli

import (
	"fmt"

	"github.com/visionik/sogcli/internal/config"
	"github.com/visionik/sogcli/internal/imap"
)

// FoldersCmd handles folder management.
type FoldersCmd struct {
	List   FoldersListCmd   `cmd:"" help:"List folders"`
	Create FoldersCreateCmd `cmd:"" help:"Create a folder"`
	Delete FoldersDeleteCmd `cmd:"" help:"Delete a folder"`
	Rename FoldersRenameCmd `cmd:"" help:"Rename a folder"`
}

// FoldersListCmd lists folders.
type FoldersListCmd struct{}

// Run executes the folders list command.
func (c *FoldersListCmd) Run(root *Root) error {
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

	folders, err := client.ListFolders()
	if err != nil {
		return fmt.Errorf("failed to list folders: %w", err)
	}

	for _, f := range folders {
		fmt.Println(f)
	}
	return nil
}

// FoldersCreateCmd creates a folder.
type FoldersCreateCmd struct {
	Name string `arg:"" help:"Folder name to create"`
}

// Run executes the folders create command.
func (c *FoldersCreateCmd) Run(root *Root) error {
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

	if err := client.CreateFolder(c.Name); err != nil {
		return err
	}

	fmt.Printf("Created folder: %s\n", c.Name)
	return nil
}

// FoldersDeleteCmd deletes a folder.
type FoldersDeleteCmd struct {
	Name string `arg:"" help:"Folder name to delete"`
	// Note: Uses global --force flag for confirmation skip
}

// Run executes the folders delete command.
func (c *FoldersDeleteCmd) Run(root *Root) error {
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

	if err := client.DeleteFolder(c.Name); err != nil {
		return err
	}

	fmt.Printf("Deleted folder: %s\n", c.Name)
	return nil
}

// FoldersRenameCmd renames a folder.
type FoldersRenameCmd struct {
	Old string `arg:"" help:"Current folder name"`
	New string `arg:"" help:"New folder name"`
}

// Run executes the folders rename command.
func (c *FoldersRenameCmd) Run(root *Root) error {
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

	if err := client.RenameFolder(c.Old, c.New); err != nil {
		return err
	}

	fmt.Printf("Renamed folder: %s -> %s\n", c.Old, c.New)
	return nil
}
