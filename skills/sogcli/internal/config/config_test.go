package config

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestConfigLoadEmpty(t *testing.T) {
	// Use temp dir
	tmpDir := t.TempDir()
	origHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	cfg, err := Load()
	require.NoError(t, err)
	assert.NotNil(t, cfg)
	assert.Empty(t, cfg.Accounts)
	assert.Empty(t, cfg.DefaultAccount)
}

func TestConfigAddAccount(t *testing.T) {
	tmpDir := t.TempDir()
	origHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	cfg, err := Load()
	require.NoError(t, err)

	acct := Account{
		Email: "test@example.com",
		IMAP: ServerConfig{
			Host: "imap.example.com",
			Port: 993,
			TLS:  true,
		},
		SMTP: ServerConfig{
			Host:     "smtp.example.com",
			Port:     587,
			StartTLS: true,
		},
	}

	// Note: AddAccount tries to save to keyring which may fail in test
	// We'll test the config part only
	cfg.Accounts[acct.Email] = acct
	cfg.DefaultAccount = acct.Email

	assert.Len(t, cfg.Accounts, 1)
	assert.Equal(t, "test@example.com", cfg.DefaultAccount)

	got, err := cfg.GetAccount("test@example.com")
	require.NoError(t, err)
	assert.Equal(t, "imap.example.com", got.IMAP.Host)
	assert.Equal(t, 993, got.IMAP.Port)
}

func TestConfigGetAccountNotFound(t *testing.T) {
	tmpDir := t.TempDir()
	origHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	cfg, err := Load()
	require.NoError(t, err)

	_, err = cfg.GetAccount("nonexistent@example.com")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestConfigListAccounts(t *testing.T) {
	tmpDir := t.TempDir()
	origHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	cfg, err := Load()
	require.NoError(t, err)

	// Empty initially
	assert.Empty(t, cfg.ListAccounts())

	// Add accounts
	cfg.Accounts["a@example.com"] = Account{Email: "a@example.com"}
	cfg.Accounts["b@example.com"] = Account{Email: "b@example.com"}

	accounts := cfg.ListAccounts()
	assert.Len(t, accounts, 2)
}

func TestConfigSaveLoad(t *testing.T) {
	tmpDir := t.TempDir()
	origHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create and save
	cfg, err := Load()
	require.NoError(t, err)

	cfg.Accounts["test@example.com"] = Account{
		Email: "test@example.com",
		IMAP: ServerConfig{
			Host: "imap.example.com",
			Port: 993,
		},
	}
	cfg.DefaultAccount = "test@example.com"

	err = cfg.Save()
	require.NoError(t, err)

	// Verify file exists
	configPath := filepath.Join(tmpDir, ".config", "sog", "config.json")
	_, err = os.Stat(configPath)
	require.NoError(t, err)

	// Load again
	cfg2, err := Load()
	require.NoError(t, err)
	assert.Equal(t, "test@example.com", cfg2.DefaultAccount)
	assert.Len(t, cfg2.Accounts, 1)
}

func TestConfigRemoveAccount(t *testing.T) {
	tmpDir := t.TempDir()
	origHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	cfg, err := Load()
	require.NoError(t, err)

	cfg.Accounts["a@example.com"] = Account{Email: "a@example.com"}
	cfg.Accounts["b@example.com"] = Account{Email: "b@example.com"}
	cfg.DefaultAccount = "a@example.com"

	// Remove non-default
	err = cfg.RemoveAccount("b@example.com")
	require.NoError(t, err)
	assert.Len(t, cfg.Accounts, 1)
	assert.Equal(t, "a@example.com", cfg.DefaultAccount)

	// Remove default (should pick new default)
	cfg.Accounts["c@example.com"] = Account{Email: "c@example.com"}
	err = cfg.RemoveAccount("a@example.com")
	require.NoError(t, err)
	assert.Len(t, cfg.Accounts, 1)
	assert.Equal(t, "c@example.com", cfg.DefaultAccount)
}
