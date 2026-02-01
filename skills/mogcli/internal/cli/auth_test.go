package cli

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/mogcli/internal/config"
)

func setupAuthTestConfig(t *testing.T) func() {
	t.Helper()

	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)

	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))

	return func() {
		os.Setenv("HOME", origHome)
	}
}

func TestAuthStatusCmd_Run_NotLoggedIn(t *testing.T) {
	cleanup := setupAuthTestConfig(t)
	defer cleanup()

	cmd := &AuthStatusCmd{}
	root := &Root{}

	output := captureOutput(func() {
		err := cmd.Run(root)
		require.NoError(t, err)
	})

	assert.Contains(t, output, "Not logged in")
}

func TestAuthStatusCmd_Run_LoggedIn(t *testing.T) {
	cleanup := setupAuthTestConfig(t)
	defer cleanup()

	// Save tokens
	tokens := &config.Tokens{
		AccessToken:  "test-access-token",
		RefreshToken: "test-refresh-token",
		ExpiresAt:    9999999999, // Far future
	}
	require.NoError(t, config.SaveTokens(tokens))

	// Save config
	cfg := &config.Config{
		ClientID: "test-client-id-12345678901234567890",
	}
	require.NoError(t, config.Save(cfg))

	cmd := &AuthStatusCmd{}
	root := &Root{}

	output := captureOutput(func() {
		err := cmd.Run(root)
		require.NoError(t, err)
	})

	assert.Contains(t, output, "Logged in")
	assert.Contains(t, output, "Token expires")
}

func TestAuthStatusCmd_Run_ExpiredToken(t *testing.T) {
	cleanup := setupAuthTestConfig(t)
	defer cleanup()

	// Save expired tokens
	tokens := &config.Tokens{
		AccessToken:  "test-access-token",
		RefreshToken: "test-refresh-token",
		ExpiresAt:    1, // Far past
	}
	require.NoError(t, config.SaveTokens(tokens))

	cmd := &AuthStatusCmd{}
	root := &Root{}

	output := captureOutput(func() {
		err := cmd.Run(root)
		require.NoError(t, err)
	})

	assert.Contains(t, output, "Logged in")
	assert.Contains(t, output, "Expired")
}

func TestAuthLogoutCmd_Run(t *testing.T) {
	cleanup := setupAuthTestConfig(t)
	defer cleanup()

	// Save tokens first
	tokens := &config.Tokens{
		AccessToken:  "test-access-token",
		RefreshToken: "test-refresh-token",
		ExpiresAt:    9999999999,
	}
	require.NoError(t, config.SaveTokens(tokens))

	cmd := &AuthLogoutCmd{}
	root := &Root{}

	output := captureOutput(func() {
		err := cmd.Run(root)
		require.NoError(t, err)
	})

	assert.Contains(t, output, "Logged out successfully")

	// Verify tokens are deleted
	_, err := config.LoadTokens()
	assert.Error(t, err)
}

func TestAuthLogoutCmd_Run_NoTokens(t *testing.T) {
	cleanup := setupAuthTestConfig(t)
	defer cleanup()

	cmd := &AuthLogoutCmd{}
	root := &Root{}

	// Should succeed even with no tokens
	output := captureOutput(func() {
		err := cmd.Run(root)
		require.NoError(t, err)
	})

	assert.Contains(t, output, "Logged out successfully")
}

// Test AuthLoginCmd struct fields
func TestAuthLoginCmd_Fields(t *testing.T) {
	cmd := &AuthLoginCmd{
		ClientID: "test-client-id-12345678901234567890",
	}

	assert.Equal(t, "test-client-id-12345678901234567890", cmd.ClientID)
}

// Note: AuthLoginCmd.Run() cannot be fully tested without mocking the device code flow
// which requires HTTP mocking. The login flow is tested via integration tests.
