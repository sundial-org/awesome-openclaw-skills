package config

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestConfigDir(t *testing.T) {
	// Save original HOME
	origHome := os.Getenv("HOME")
	defer os.Setenv("HOME", origHome)

	// Set test HOME
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)

	dir, err := ConfigDir()
	require.NoError(t, err)
	assert.Equal(t, filepath.Join(tmpDir, ".config", "mog"), dir)
}

func TestConfig_SaveLoad(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config
	cfg := &Config{
		ClientID: "test-client-id-12345",
	}

	// Save
	err := Save(cfg)
	require.NoError(t, err)

	// Load
	loaded, err := Load()
	require.NoError(t, err)
	assert.Equal(t, cfg.ClientID, loaded.ClientID)
}

func TestConfig_LoadMissing(t *testing.T) {
	// Setup: use temp dir with no config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Load should return empty config, not error
	cfg, err := Load()
	require.NoError(t, err)
	assert.NotNil(t, cfg)
	assert.Empty(t, cfg.ClientID)
}

func TestTokens_SaveLoad(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create tokens
	tokens := &Tokens{
		AccessToken:  "access-token-abc",
		RefreshToken: "refresh-token-xyz",
		ExpiresAt:    1234567890,
	}

	// Save
	err := SaveTokens(tokens)
	require.NoError(t, err)

	// Load
	loaded, err := LoadTokens()
	require.NoError(t, err)
	assert.Equal(t, tokens.AccessToken, loaded.AccessToken)
	assert.Equal(t, tokens.RefreshToken, loaded.RefreshToken)
	assert.Equal(t, tokens.ExpiresAt, loaded.ExpiresAt)
}

func TestTokens_LoadMissing(t *testing.T) {
	// Setup: use temp dir with no tokens
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Load should return error for missing tokens
	_, err := LoadTokens()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "not logged in")
}

func TestTokens_Delete(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Save tokens first
	tokens := &Tokens{
		AccessToken:  "test",
		RefreshToken: "test",
		ExpiresAt:    123,
	}
	err := SaveTokens(tokens)
	require.NoError(t, err)

	// Delete
	err = DeleteTokens()
	require.NoError(t, err)

	// Should not exist anymore
	_, err = LoadTokens()
	assert.Error(t, err)
}

func TestTokens_DeleteMissing(t *testing.T) {
	// Setup: use temp dir with no tokens
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Delete should not error if file doesn't exist
	err := DeleteTokens()
	assert.NoError(t, err)
}

func TestSlugs_SaveLoad(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create slugs
	slugs := &Slugs{
		IDToSlug: map[string]string{
			"long-id-123": "abc123",
			"long-id-456": "def456",
		},
		SlugToID: map[string]string{
			"abc123": "long-id-123",
			"def456": "long-id-456",
		},
	}

	// Save
	err := SaveSlugs(slugs)
	require.NoError(t, err)

	// Load
	loaded, err := LoadSlugs()
	require.NoError(t, err)
	assert.Equal(t, slugs.IDToSlug, loaded.IDToSlug)
	assert.Equal(t, slugs.SlugToID, loaded.SlugToID)
}

func TestSlugs_LoadMissing(t *testing.T) {
	// Setup: use temp dir with no slugs
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Load should return empty slugs, not error
	slugs, err := LoadSlugs()
	require.NoError(t, err)
	assert.NotNil(t, slugs)
	assert.NotNil(t, slugs.IDToSlug)
	assert.NotNil(t, slugs.SlugToID)
	assert.Empty(t, slugs.IDToSlug)
	assert.Empty(t, slugs.SlugToID)
}

func TestConfig_FilePermissions(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Save tokens (should have restricted permissions)
	tokens := &Tokens{AccessToken: "secret"}
	err := SaveTokens(tokens)
	require.NoError(t, err)

	// Check file permissions
	configDir, _ := ConfigDir()
	info, err := os.Stat(filepath.Join(configDir, "tokens.json"))
	require.NoError(t, err)

	// Should be 0600 (owner read/write only)
	assert.Equal(t, os.FileMode(0600), info.Mode().Perm())
}

func TestConfig_LoadCorruptedJSON(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir and corrupt file
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.WriteFile(filepath.Join(configDir, "settings.json"), []byte("{invalid json"), 0600))

	// Load should error
	_, err := Load()
	assert.Error(t, err)
}

func TestTokens_LoadCorruptedJSON(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir and corrupt file
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.WriteFile(filepath.Join(configDir, "tokens.json"), []byte("not json"), 0600))

	// Load should error
	_, err := LoadTokens()
	assert.Error(t, err)
}

func TestSlugs_LoadCorruptedJSON(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir and corrupt file
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.WriteFile(filepath.Join(configDir, "slugs.json"), []byte("{bad"), 0600))

	// Load should error
	_, err := LoadSlugs()
	assert.Error(t, err)
}

func TestSlugs_LoadPartialJSON(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir and partial file (missing maps)
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.WriteFile(filepath.Join(configDir, "slugs.json"), []byte("{}"), 0600))

	// Load should succeed and initialize maps
	slugs, err := LoadSlugs()
	require.NoError(t, err)
	assert.NotNil(t, slugs.IDToSlug)
	assert.NotNil(t, slugs.SlugToID)
}

func TestConfig_SaveCreatesDir(t *testing.T) {
	// Setup: use temp dir with no .config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Save should create directory
	cfg := &Config{ClientID: "test"}
	err := Save(cfg)
	require.NoError(t, err)

	// Verify directory was created
	configDir := filepath.Join(tmpDir, ".config", "mog")
	info, err := os.Stat(configDir)
	require.NoError(t, err)
	assert.True(t, info.IsDir())
}

func TestConfig_GetClientID(t *testing.T) {
	tests := []struct {
		name     string
		cfg      *Config
		expected string
	}{
		{
			name:     "Go format (client_id)",
			cfg:      &Config{ClientID: "go-client-id"},
			expected: "go-client-id",
		},
		{
			name:     "Node format (clientId)",
			cfg:      &Config{ClientIDv2: "node-client-id"},
			expected: "node-client-id",
		},
		{
			name:     "Both formats - Go takes precedence",
			cfg:      &Config{ClientID: "go-id", ClientIDv2: "node-id"},
			expected: "go-id",
		},
		{
			name:     "Empty config",
			cfg:      &Config{},
			expected: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := tt.cfg.GetClientID()
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestTokens_GetExpiresAt(t *testing.T) {
	tests := []struct {
		name     string
		tokens   *Tokens
		expected int64
	}{
		{
			name:     "Go format (expires_at)",
			tokens:   &Tokens{ExpiresAt: 1234567890},
			expected: 1234567890,
		},
		{
			name: "Node format (saved_at + expires_in)",
			tokens: &Tokens{
				SavedAt:   1234567890000, // ms
				ExpiresIn: 3600,          // seconds
			},
			expected: 1234567890 + 3600,
		},
		{
			name:     "Both formats - Go takes precedence",
			tokens:   &Tokens{ExpiresAt: 9999, SavedAt: 1000000, ExpiresIn: 100},
			expected: 9999,
		},
		{
			name:     "Empty tokens",
			tokens:   &Tokens{},
			expected: 0,
		},
		{
			name:     "Node format - missing saved_at",
			tokens:   &Tokens{ExpiresIn: 3600},
			expected: 0,
		},
		{
			name:     "Node format - missing expires_in",
			tokens:   &Tokens{SavedAt: 1234567890000},
			expected: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := tt.tokens.GetExpiresAt()
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestTokens_SaveCreatesDir(t *testing.T) {
	// Setup: use temp dir with no .config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Save should create directory
	tokens := &Tokens{AccessToken: "test"}
	err := SaveTokens(tokens)
	require.NoError(t, err)

	// Verify directory was created
	configDir := filepath.Join(tmpDir, ".config", "mog")
	info, err := os.Stat(configDir)
	require.NoError(t, err)
	assert.True(t, info.IsDir())
}

func TestSlugs_SaveCreatesDir(t *testing.T) {
	// Setup: use temp dir with no .config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Save should create directory
	slugs := &Slugs{
		IDToSlug: map[string]string{"id": "slug"},
		SlugToID: map[string]string{"slug": "id"},
	}
	err := SaveSlugs(slugs)
	require.NoError(t, err)

	// Verify directory was created
	configDir := filepath.Join(tmpDir, ".config", "mog")
	info, err := os.Stat(configDir)
	require.NoError(t, err)
	assert.True(t, info.IsDir())
}

func TestConfigDir_Success(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	dir, err := ConfigDir()
	require.NoError(t, err)
	assert.Contains(t, dir, ".config/mog")
}

func TestLoadTokens_ReadError(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir with a directory named tokens.json (can't read a directory as file)
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.MkdirAll(filepath.Join(configDir, "tokens.json"), 0700))

	_, err := LoadTokens()
	assert.Error(t, err)
}

func TestLoad_ReadError(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir with a directory named settings.json (can't read a directory as file)
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.MkdirAll(filepath.Join(configDir, "settings.json"), 0700))

	_, err := Load()
	assert.Error(t, err)
}

func TestLoadSlugs_ReadError(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir with a directory named slugs.json (can't read a directory as file)
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.MkdirAll(filepath.Join(configDir, "slugs.json"), 0700))

	_, err := LoadSlugs()
	assert.Error(t, err)
}

func TestDeleteTokens_Error(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir with a directory named tokens.json (can't delete a directory with Remove)
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.MkdirAll(filepath.Join(configDir, "tokens.json"), 0700))
	// Put something in the directory so Remove fails
	require.NoError(t, os.WriteFile(filepath.Join(configDir, "tokens.json", "dummy"), []byte("x"), 0600))

	err := DeleteTokens()
	assert.Error(t, err)
}

func TestSlugs_OnlyIDToSlug(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir with partial slugs (only id_to_slug)
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.WriteFile(filepath.Join(configDir, "slugs.json"), []byte(`{"id_to_slug": {"id1": "slug1"}}`), 0600))

	slugs, err := LoadSlugs()
	require.NoError(t, err)
	assert.NotNil(t, slugs.IDToSlug)
	assert.NotNil(t, slugs.SlugToID)
	assert.Equal(t, "slug1", slugs.IDToSlug["id1"])
}

func TestSlugs_OnlySlugToID(t *testing.T) {
	// Setup: use temp dir
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir with partial slugs (only slug_to_id)
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))
	require.NoError(t, os.WriteFile(filepath.Join(configDir, "slugs.json"), []byte(`{"slug_to_id": {"slug1": "id1"}}`), 0600))

	slugs, err := LoadSlugs()
	require.NoError(t, err)
	assert.NotNil(t, slugs.IDToSlug)
	assert.NotNil(t, slugs.SlugToID)
	assert.Equal(t, "id1", slugs.SlugToID["slug1"])
}
