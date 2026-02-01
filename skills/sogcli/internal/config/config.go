// Package config handles sog configuration and account management.
package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Config holds the sog configuration.
type Config struct {
	Accounts       map[string]Account `json:"accounts"`
	DefaultAccount string             `json:"default_account,omitempty"`
	Storage        string             `json:"storage,omitempty"` // keychain or file
	path           string
}

// Account holds configuration for a mail account.
type Account struct {
	Email   string        `json:"email"`
	IMAP    ServerConfig  `json:"imap"`
	SMTP    ServerConfig  `json:"smtp"`
	CalDAV  CalDAVConfig  `json:"caldav,omitempty"`
	CardDAV CardDAVConfig `json:"carddav,omitempty"`
	WebDAV  WebDAVConfig  `json:"webdav,omitempty"`
}

// CalDAVConfig holds CalDAV server configuration.
type CalDAVConfig struct {
	URL             string `json:"url,omitempty"`
	DefaultCalendar string `json:"default_calendar,omitempty"`
}

// CardDAVConfig holds CardDAV server configuration.
type CardDAVConfig struct {
	URL                string `json:"url,omitempty"`
	DefaultAddressBook string `json:"default_address_book,omitempty"`
}

// WebDAVConfig holds WebDAV server configuration.
type WebDAVConfig struct {
	URL string `json:"url,omitempty"`
}

// ServerConfig holds server connection details.
type ServerConfig struct {
	Host       string `json:"host"`
	Port       int    `json:"port"`
	TLS        bool   `json:"tls,omitempty"`
	StartTLS   bool   `json:"starttls,omitempty"`
	Insecure   bool   `json:"insecure,omitempty"`   // Skip TLS cert verification
	NoTLS      bool   `json:"no_tls,omitempty"`     // Disable TLS entirely
}

// configDir returns the config directory path.
func configDir() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".config", "sog"), nil
}

// configPath returns the config file path.
func configPath() (string, error) {
	dir, err := configDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(dir, "config.json"), nil
}

// Load loads the configuration from disk.
func Load() (*Config, error) {
	path, err := configPath()
	if err != nil {
		return nil, err
	}

	cfg := &Config{
		Accounts: make(map[string]Account),
		path:     path,
	}

	data, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return cfg, nil
	}
	if err != nil {
		return nil, fmt.Errorf("failed to read config: %w", err)
	}

	if err := json.Unmarshal(data, cfg); err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	cfg.path = path

	// Set storage type from config
	if cfg.Storage == "file" {
		SetStorageType(StorageFile)
	} else {
		SetStorageType(StorageKeyring)
	}

	return cfg, nil
}

// Save writes the configuration to disk.
func (c *Config) Save() error {
	dir := filepath.Dir(c.path)
	if err := os.MkdirAll(dir, 0700); err != nil {
		return fmt.Errorf("failed to create config dir: %w", err)
	}

	data, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(c.path, data, 0600); err != nil {
		return fmt.Errorf("failed to write config: %w", err)
	}

	return nil
}

// AddAccount adds an account to the configuration.
func (c *Config) AddAccount(acct Account, password string) error {
	if c.Accounts == nil {
		c.Accounts = make(map[string]Account)
	}

	c.Accounts[acct.Email] = acct

	// Set as default if first account
	if c.DefaultAccount == "" {
		c.DefaultAccount = acct.Email
	}

	// Store password in keyring
	if err := SetPassword(acct.Email, password); err != nil {
		return fmt.Errorf("failed to store password: %w", err)
	}

	return c.Save()
}

// GetAccount retrieves an account by email.
func (c *Config) GetAccount(email string) (*Account, error) {
	acct, ok := c.Accounts[email]
	if !ok {
		return nil, fmt.Errorf("account not found: %s", email)
	}
	return &acct, nil
}

// ListAccounts returns all configured accounts.
func (c *Config) ListAccounts() []Account {
	accounts := make([]Account, 0, len(c.Accounts))
	for _, acct := range c.Accounts {
		accounts = append(accounts, acct)
	}
	return accounts
}

// RemoveAccount removes an account from the configuration.
func (c *Config) RemoveAccount(email string) error {
	if _, ok := c.Accounts[email]; !ok {
		return fmt.Errorf("account not found: %s", email)
	}

	delete(c.Accounts, email)

	// Clear default if removed
	if c.DefaultAccount == email {
		c.DefaultAccount = ""
		// Set new default if accounts remain
		for e := range c.Accounts {
			c.DefaultAccount = e
			break
		}
	}

	// Remove from keyring
	_ = DeletePassword(email) // Ignore error

	return c.Save()
}

// GetPassword retrieves the password for an account.
func (c *Config) GetPassword(email string) (string, error) {
	return GetPassword(email)
}

// GetPasswordForProtocol retrieves the password for an account and protocol.
// Falls back to default password if no protocol-specific password is set.
func (c *Config) GetPasswordForProtocol(email string, protocol Protocol) (string, error) {
	return GetPasswordForProtocol(email, protocol)
}
