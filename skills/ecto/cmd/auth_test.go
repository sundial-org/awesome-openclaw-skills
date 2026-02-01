package cmd

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/ecto/internal/config"
)

func TestAuthAddCmd(t *testing.T) {
	// Use a temp config directory
	tmpDir := t.TempDir()
	origXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", origXDG)

	// Clear env vars to avoid interference
	origURL := os.Getenv("GHOST_URL")
	origKey := os.Getenv("GHOST_ADMIN_KEY")
	os.Unsetenv("GHOST_URL")
	os.Unsetenv("GHOST_ADMIN_KEY")
	defer func() {
		os.Setenv("GHOST_URL", origURL)
		os.Setenv("GHOST_ADMIN_KEY", origKey)
	}()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
		errMsg  string
	}{
		{
			name:    "add site",
			args:    []string{"auth", "add", "mysite", "--url", "https://mysite.ghost.io", "--key", "abc:def123456789012345678901234567"},
			wantOut: []string{"Added site", "mysite", "Set as default site"},
			wantErr: false,
		},
		{
			name:    "add site missing url",
			args:    []string{"auth", "add", "mysite", "--key", "abc:def123456789012345678901234567"},
			wantErr: true,
			errMsg:  "--url and --key are required",
		},
		{
			name:    "add site missing key",
			args:    []string{"auth", "add", "mysite", "--url", "https://mysite.ghost.io"},
			wantErr: true,
			errMsg:  "--url and --key are required",
		},
		{
			name:    "add site missing name",
			args:    []string{"auth", "add"},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Clean up config between tests
			configPath := filepath.Join(tmpDir, "ecto", "config.json")
			os.Remove(configPath)

			cmd := newTestRootCmd()
			stdout, _, err := executeCommand(cmd, tt.args...)

			if tt.wantErr {
				require.Error(t, err)
				if tt.errMsg != "" {
					assert.Contains(t, err.Error(), tt.errMsg)
				}
				return
			}
			require.NoError(t, err)

			for _, want := range tt.wantOut {
				assert.Contains(t, stdout, want)
			}

			// Verify config was written
			cfg, err := config.LoadFromPath(configPath)
			require.NoError(t, err)
			assert.Contains(t, cfg.Sites, "mysite")
		})
	}
}

func TestAuthListCmd(t *testing.T) {
	tmpDir := t.TempDir()
	origXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", origXDG)

	// Clear env vars
	origURL := os.Getenv("GHOST_URL")
	origKey := os.Getenv("GHOST_ADMIN_KEY")
	os.Unsetenv("GHOST_URL")
	os.Unsetenv("GHOST_ADMIN_KEY")
	defer func() {
		os.Setenv("GHOST_URL", origURL)
		os.Setenv("GHOST_ADMIN_KEY", origKey)
	}()

	tests := []struct {
		name    string
		setup   func(t *testing.T)
		wantOut []string
	}{
		{
			name: "list empty",
			setup: func(t *testing.T) {
				// Don't create any config
			},
			wantOut: []string{"No sites configured"},
		},
		{
			name: "list sites",
			setup: func(t *testing.T) {
				cfg := &config.Config{
					DefaultSite: "site1",
					Sites: map[string]config.Site{
						"site1": {Name: "site1", URL: "https://site1.ghost.io", APIKey: "k1:s1"},
						"site2": {Name: "site2", URL: "https://site2.ghost.io", APIKey: "k2:s2"},
					},
				}
				configPath := filepath.Join(tmpDir, "ecto", "config.json")
				err := cfg.SaveToPath(configPath)
				require.NoError(t, err)
			},
			wantOut: []string{"* site1:", "site1.ghost.io", "site2:", "site2.ghost.io"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Clean up config between tests
			configPath := filepath.Join(tmpDir, "ecto", "config.json")
			os.Remove(configPath)

			if tt.setup != nil {
				tt.setup(t)
			}

			cmd := newTestRootCmd()
			stdout, _, err := executeCommand(cmd, "auth", "list")
			require.NoError(t, err)

			for _, want := range tt.wantOut {
				assert.Contains(t, stdout, want)
			}
		})
	}
}

func TestAuthDefaultCmd(t *testing.T) {
	tmpDir := t.TempDir()
	origXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", origXDG)

	// Clear env vars
	origURL := os.Getenv("GHOST_URL")
	origKey := os.Getenv("GHOST_ADMIN_KEY")
	os.Unsetenv("GHOST_URL")
	os.Unsetenv("GHOST_ADMIN_KEY")
	defer func() {
		os.Setenv("GHOST_URL", origURL)
		os.Setenv("GHOST_ADMIN_KEY", origKey)
	}()

	// Setup config with multiple sites
	cfg := &config.Config{
		DefaultSite: "site1",
		Sites: map[string]config.Site{
			"site1": {Name: "site1", URL: "https://site1.ghost.io", APIKey: "k1:s1"},
			"site2": {Name: "site2", URL: "https://site2.ghost.io", APIKey: "k2:s2"},
		},
	}
	configPath := filepath.Join(tmpDir, "ecto", "config.json")
	err := cfg.SaveToPath(configPath)
	require.NoError(t, err)

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
		errMsg  string
	}{
		{
			name:    "set default",
			args:    []string{"auth", "default", "site2"},
			wantOut: []string{"Default site set to", "site2"},
			wantErr: false,
		},
		{
			name:    "set nonexistent default",
			args:    []string{"auth", "default", "nonexistent"},
			wantErr: true,
			errMsg:  "not found",
		},
		{
			name:    "missing site name",
			args:    []string{"auth", "default"},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset config
			err := cfg.SaveToPath(configPath)
			require.NoError(t, err)

			cmd := newTestRootCmd()
			stdout, _, err := executeCommand(cmd, tt.args...)

			if tt.wantErr {
				require.Error(t, err)
				if tt.errMsg != "" {
					assert.Contains(t, err.Error(), tt.errMsg)
				}
				return
			}
			require.NoError(t, err)

			for _, want := range tt.wantOut {
				assert.Contains(t, stdout, want)
			}
		})
	}
}

func TestAuthRemoveCmd(t *testing.T) {
	tmpDir := t.TempDir()
	origXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", origXDG)

	// Clear env vars
	origURL := os.Getenv("GHOST_URL")
	origKey := os.Getenv("GHOST_ADMIN_KEY")
	os.Unsetenv("GHOST_URL")
	os.Unsetenv("GHOST_ADMIN_KEY")
	defer func() {
		os.Setenv("GHOST_URL", origURL)
		os.Setenv("GHOST_ADMIN_KEY", origKey)
	}()

	tests := []struct {
		name    string
		setup   func(t *testing.T)
		args    []string
		wantOut []string
		wantErr bool
		errMsg  string
	}{
		{
			name: "remove site",
			setup: func(t *testing.T) {
				cfg := &config.Config{
					DefaultSite: "mysite",
					Sites: map[string]config.Site{
						"mysite": {Name: "mysite", URL: "https://mysite.ghost.io", APIKey: "k:s"},
					},
				}
				configPath := filepath.Join(tmpDir, "ecto", "config.json")
				err := cfg.SaveToPath(configPath)
				require.NoError(t, err)
			},
			args:    []string{"auth", "remove", "mysite"},
			wantOut: []string{"Removed site", "mysite"},
			wantErr: false,
		},
		{
			name: "remove nonexistent site",
			setup: func(t *testing.T) {
				cfg := &config.Config{
					Sites: make(map[string]config.Site),
				}
				configPath := filepath.Join(tmpDir, "ecto", "config.json")
				err := cfg.SaveToPath(configPath)
				require.NoError(t, err)
			},
			args:    []string{"auth", "remove", "nonexistent"},
			wantErr: true,
			errMsg:  "not found",
		},
		{
			name:    "remove missing name",
			args:    []string{"auth", "remove"},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Clean up config between tests
			configPath := filepath.Join(tmpDir, "ecto", "config.json")
			os.Remove(configPath)

			if tt.setup != nil {
				tt.setup(t)
			}

			cmd := newTestRootCmd()
			stdout, _, err := executeCommand(cmd, tt.args...)

			if tt.wantErr {
				require.Error(t, err)
				if tt.errMsg != "" {
					assert.Contains(t, err.Error(), tt.errMsg)
				}
				return
			}
			require.NoError(t, err)

			for _, want := range tt.wantOut {
				assert.Contains(t, stdout, want)
			}
		})
	}
}

// Test auth parent command
func TestAuthCmd(t *testing.T) {
	cmd := newTestRootCmd()
	stdout, _, err := executeCommand(cmd, "auth", "--help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "Manage site authentication")
	assert.Contains(t, stdout, "add")
	assert.Contains(t, stdout, "list")
	assert.Contains(t, stdout, "default")
	assert.Contains(t, stdout, "remove")
}
