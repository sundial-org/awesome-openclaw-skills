package cli

import (
	"fmt"
	"os"
	"os/exec"
	"os/signal"
	"syscall"

	"github.com/visionik/sogcli/internal/config"
	"github.com/visionik/sogcli/internal/imap"
)

// IdleCmd watches for new mail using IMAP IDLE.
type IdleCmd struct {
	Folder string `help:"Folder to watch" default:"INBOX"`
	Exec   string `help:"Command to execute on new mail (receives subject as arg)"`
}

// Run executes the idle command.
func (c *IdleCmd) Run(root *Root) error {
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

	fmt.Printf("Watching %s for new mail (Ctrl+C to stop)...\n", c.Folder)

	// Handle interrupt
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigChan
		fmt.Println("\nStopping...")
		client.Close()
		os.Exit(0)
	}()

	// Start IDLE
	err = client.Idle(c.Folder, func(msgNum uint32) {
		fmt.Printf("New message! (count: %d)\n", msgNum)

		if c.Exec != "" {
			cmd := exec.Command("sh", "-c", c.Exec)
			cmd.Stdout = os.Stdout
			cmd.Stderr = os.Stderr
			_ = cmd.Run()
		}
	})

	if err != nil {
		return fmt.Errorf("idle failed: %w", err)
	}

	return nil
}
