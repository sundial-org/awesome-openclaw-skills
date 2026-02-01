package config

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestConfigPath(t *testing.T) {
	tests := []struct {
		name    string
		xdgHome string
		want    string
	}{
		{
			name:    "with XDG_CONFIG_HOME",
			xdgHome: "/custom/config",
			want:    "/custom/config/ecto/config.json",
		},
		{
			name:    "without XDG_CONFIG_HOME",
			xdgHome: "",
			want:    filepath.Join(os.Getenv("HOME"), ".config", "ecto", "config.json"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.xdgHome != "" {
				oldXDG := os.Getenv("XDG_CONFIG_HOME")
				os.Setenv("XDG_CONFIG_HOME", tt.xdgHome)
				defer os.Setenv("XDG_CONFIG_HOME", oldXDG)
			} else {
				oldXDG := os.Getenv("XDG_CONFIG_HOME")
				os.Unsetenv("XDG_CONFIG_HOME")
				defer os.Setenv("XDG_CONFIG_HOME", oldXDG)
			}

			got := ConfigPath()
			if tt.xdgHome != "" {
				assert.Equal(t, tt.want, got)
			} else {
				assert.Contains(t, got, ".config/ecto/config.json")
			}
		})
	}
}

func TestLoadFromPath(t *testing.T) {
	tests := []struct {
		name    string
		setup   func(t *testing.T) string
		wantErr bool
		check   func(t *testing.T, cfg *Config)
	}{
		{
			name: "file not found returns empty config",
			setup: func(t *testing.T) string {
				return filepath.Join(t.TempDir(), "nonexistent.json")
			},
			check: func(t *testing.T, cfg *Config) {
				assert.NotNil(t, cfg)
				assert.Empty(t, cfg.Sites)
				assert.Empty(t, cfg.DefaultSite)
			},
		},
		{
			name: "valid config",
			setup: func(t *testing.T) string {
				dir := t.TempDir()
				path := filepath.Join(dir, "config.json")
				data := `{
					"default_site": "mysite",
					"sites": {
						"mysite": {
							"name": "mysite",
							"url": "https://example.ghost.io",
							"api_key": "abc123:def456"
						}
					}
				}`
				os.WriteFile(path, []byte(data), 0644)
				return path
			},
			check: func(t *testing.T, cfg *Config) {
				assert.Equal(t, "mysite", cfg.DefaultSite)
				assert.Len(t, cfg.Sites, 1)
				assert.Equal(t, "https://example.ghost.io", cfg.Sites["mysite"].URL)
			},
		},
		{
			name: "config with null sites",
			setup: func(t *testing.T) string {
				dir := t.TempDir()
				path := filepath.Join(dir, "config.json")
				data := `{"default_site": "test", "sites": null}`
				os.WriteFile(path, []byte(data), 0644)
				return path
			},
			check: func(t *testing.T, cfg *Config) {
				assert.NotNil(t, cfg.Sites)
				assert.Empty(t, cfg.Sites)
			},
		},
		{
			name: "invalid JSON",
			setup: func(t *testing.T) string {
				dir := t.TempDir()
				path := filepath.Join(dir, "config.json")
				os.WriteFile(path, []byte("invalid json"), 0644)
				return path
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			path := tt.setup(t)
			cfg, err := LoadFromPath(path)
			if tt.wantErr {
				require.Error(t, err)
				return
			}
			require.NoError(t, err)
			tt.check(t, cfg)
		})
	}
}

func TestConfig_SaveToPath(t *testing.T) {
	tests := []struct {
		name    string
		config  *Config
		wantErr bool
	}{
		{
			name: "save empty config",
			config: &Config{
				Sites: make(map[string]Site),
			},
		},
		{
			name: "save with sites",
			config: &Config{
				DefaultSite: "mysite",
				Sites: map[string]Site{
					"mysite": {
						Name:   "mysite",
						URL:    "https://example.ghost.io",
						APIKey: "key123:secret456",
					},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			dir := t.TempDir()
			path := filepath.Join(dir, "subdir", "config.json")

			err := tt.config.SaveToPath(path)
			if tt.wantErr {
				require.Error(t, err)
				return
			}
			require.NoError(t, err)

			// Verify file was created
			_, err = os.Stat(path)
			require.NoError(t, err)

			// Load and verify
			loaded, err := LoadFromPath(path)
			require.NoError(t, err)
			assert.Equal(t, tt.config.DefaultSite, loaded.DefaultSite)
			assert.Equal(t, len(tt.config.Sites), len(loaded.Sites))
		})
	}
}

func TestConfig_AddSiteNoSave(t *testing.T) {
	tests := []struct {
		name       string
		initial    *Config
		siteName   string
		url        string
		apiKey     string
		wantSites  int
		wantDefault string
	}{
		{
			name: "add first site becomes default",
			initial: &Config{
				Sites: make(map[string]Site),
			},
			siteName:    "site1",
			url:         "https://site1.ghost.io",
			apiKey:      "key:secret",
			wantSites:   1,
			wantDefault: "site1",
		},
		{
			name: "add second site keeps existing default",
			initial: &Config{
				DefaultSite: "site1",
				Sites: map[string]Site{
					"site1": {Name: "site1", URL: "https://site1.ghost.io", APIKey: "k1:s1"},
				},
			},
			siteName:    "site2",
			url:         "https://site2.ghost.io",
			apiKey:      "k2:s2",
			wantSites:   2,
			wantDefault: "site1",
		},
		{
			name: "update existing site",
			initial: &Config{
				DefaultSite: "site1",
				Sites: map[string]Site{
					"site1": {Name: "site1", URL: "https://old.ghost.io", APIKey: "old:key"},
				},
			},
			siteName:    "site1",
			url:         "https://new.ghost.io",
			apiKey:      "new:key",
			wantSites:   1,
			wantDefault: "site1",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.initial.AddSiteNoSave(tt.siteName, tt.url, tt.apiKey)

			assert.Len(t, tt.initial.Sites, tt.wantSites)
			assert.Equal(t, tt.wantDefault, tt.initial.DefaultSite)
			assert.Equal(t, tt.url, tt.initial.Sites[tt.siteName].URL)
			assert.Equal(t, tt.apiKey, tt.initial.Sites[tt.siteName].APIKey)
		})
	}
}

func TestConfig_RemoveSiteNoSave(t *testing.T) {
	tests := []struct {
		name        string
		initial     *Config
		removeName  string
		wantSites   int
		wantDefault string
	}{
		{
			name: "remove non-default site",
			initial: &Config{
				DefaultSite: "site1",
				Sites: map[string]Site{
					"site1": {Name: "site1"},
					"site2": {Name: "site2"},
				},
			},
			removeName:  "site2",
			wantSites:   1,
			wantDefault: "site1",
		},
		{
			name: "remove default site selects new default",
			initial: &Config{
				DefaultSite: "site1",
				Sites: map[string]Site{
					"site1": {Name: "site1"},
					"site2": {Name: "site2"},
				},
			},
			removeName:  "site1",
			wantSites:   1,
			wantDefault: "site2",
		},
		{
			name: "remove only site clears default",
			initial: &Config{
				DefaultSite: "site1",
				Sites: map[string]Site{
					"site1": {Name: "site1"},
				},
			},
			removeName:  "site1",
			wantSites:   0,
			wantDefault: "",
		},
		{
			name: "remove nonexistent site",
			initial: &Config{
				DefaultSite: "site1",
				Sites: map[string]Site{
					"site1": {Name: "site1"},
				},
			},
			removeName:  "nonexistent",
			wantSites:   1,
			wantDefault: "site1",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.initial.RemoveSiteNoSave(tt.removeName)

			assert.Len(t, tt.initial.Sites, tt.wantSites)
			if tt.wantDefault != "" {
				assert.Equal(t, tt.wantDefault, tt.initial.DefaultSite)
			} else {
				assert.Empty(t, tt.initial.DefaultSite)
			}
		})
	}
}

func TestConfig_SetDefaultNoSave(t *testing.T) {
	tests := []struct {
		name       string
		initial    *Config
		setDefault string
		wantErr    bool
	}{
		{
			name: "set existing site as default",
			initial: &Config{
				DefaultSite: "site1",
				Sites: map[string]Site{
					"site1": {Name: "site1"},
					"site2": {Name: "site2"},
				},
			},
			setDefault: "site2",
			wantErr:    false,
		},
		{
			name: "set nonexistent site as default",
			initial: &Config{
				Sites: map[string]Site{
					"site1": {Name: "site1"},
				},
			},
			setDefault: "nonexistent",
			wantErr:    true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.initial.SetDefaultNoSave(tt.setDefault)
			if tt.wantErr {
				require.Error(t, err)
				assert.Contains(t, err.Error(), "not found")
				return
			}
			require.NoError(t, err)
			assert.Equal(t, tt.setDefault, tt.initial.DefaultSite)
		})
	}
}

func TestConfig_GetSite(t *testing.T) {
	tests := []struct {
		name     string
		config   *Config
		siteName string
		wantURL  string
		wantErr  bool
		errMsg   string
	}{
		{
			name: "get by name",
			config: &Config{
				Sites: map[string]Site{
					"mysite": {Name: "mysite", URL: "https://mysite.ghost.io"},
				},
			},
			siteName: "mysite",
			wantURL:  "https://mysite.ghost.io",
		},
		{
			name: "get default when name is empty",
			config: &Config{
				DefaultSite: "default",
				Sites: map[string]Site{
					"default": {Name: "default", URL: "https://default.ghost.io"},
				},
			},
			siteName: "",
			wantURL:  "https://default.ghost.io",
		},
		{
			name: "error when no site and no default",
			config: &Config{
				Sites: make(map[string]Site),
			},
			siteName: "",
			wantErr:  true,
			errMsg:   "no site specified and no default set",
		},
		{
			name: "error when site not found",
			config: &Config{
				Sites: map[string]Site{
					"other": {Name: "other"},
				},
			},
			siteName: "nonexistent",
			wantErr:  true,
			errMsg:   "not found",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			site, err := tt.config.GetSite(tt.siteName)
			if tt.wantErr {
				require.Error(t, err)
				assert.Contains(t, err.Error(), tt.errMsg)
				return
			}
			require.NoError(t, err)
			assert.Equal(t, tt.wantURL, site.URL)
		})
	}
}

func TestGetActiveClientWithConfig(t *testing.T) {
	tests := []struct {
		name     string
		config   *Config
		siteName string
		envURL   string
		envKey   string
		envSite  string
		wantErr  bool
	}{
		{
			name: "use environment variables",
			config: &Config{
				Sites: make(map[string]Site),
			},
			envURL:   "https://env.ghost.io",
			envKey:   "envid:7365637265746b6579313233",
			wantErr:  false,
		},
		{
			name: "use config site",
			config: &Config{
				DefaultSite: "mysite",
				Sites: map[string]Site{
					"mysite": {
						Name:   "mysite",
						URL:    "https://config.ghost.io",
						APIKey: "configid:7365637265746b6579313233",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "use GHOST_SITE env",
			config: &Config{
				DefaultSite: "default",
				Sites: map[string]Site{
					"default": {Name: "default", URL: "https://default.ghost.io", APIKey: "d:7365637265746b6579313233"},
					"envsite": {Name: "envsite", URL: "https://envsite.ghost.io", APIKey: "e:7365637265746b6579313233"},
				},
			},
			envSite: "envsite",
			wantErr: false,
		},
		{
			name: "error no site configured",
			config: &Config{
				Sites: make(map[string]Site),
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Set up environment
			if tt.envURL != "" {
				oldURL := os.Getenv("GHOST_URL")
				os.Setenv("GHOST_URL", tt.envURL)
				defer os.Setenv("GHOST_URL", oldURL)
			} else {
				os.Unsetenv("GHOST_URL")
			}

			if tt.envKey != "" {
				oldKey := os.Getenv("GHOST_ADMIN_KEY")
				os.Setenv("GHOST_ADMIN_KEY", tt.envKey)
				defer os.Setenv("GHOST_ADMIN_KEY", oldKey)
			} else {
				os.Unsetenv("GHOST_ADMIN_KEY")
			}

			if tt.envSite != "" {
				oldSite := os.Getenv("GHOST_SITE")
				os.Setenv("GHOST_SITE", tt.envSite)
				defer os.Setenv("GHOST_SITE", oldSite)
			} else {
				os.Unsetenv("GHOST_SITE")
			}

			client, err := GetActiveClientWithConfig(tt.config, tt.siteName)
			if tt.wantErr {
				require.Error(t, err)
				return
			}
			require.NoError(t, err)
			assert.NotNil(t, client)
		})
	}
}

func TestSite_Structure(t *testing.T) {
	site := Site{
		Name:   "test",
		URL:    "https://test.ghost.io",
		APIKey: "abc:def",
	}

	assert.Equal(t, "test", site.Name)
	assert.Equal(t, "https://test.ghost.io", site.URL)
	assert.Equal(t, "abc:def", site.APIKey)
}

func TestConfig_Structure(t *testing.T) {
	cfg := &Config{
		DefaultSite: "main",
		Sites: map[string]Site{
			"main": {Name: "main", URL: "https://main.ghost.io", APIKey: "m:m"},
			"dev":  {Name: "dev", URL: "https://dev.ghost.io", APIKey: "d:d"},
		},
	}

	assert.Equal(t, "main", cfg.DefaultSite)
	assert.Len(t, cfg.Sites, 2)
	assert.Contains(t, cfg.Sites, "main")
	assert.Contains(t, cfg.Sites, "dev")
}

// Tests for functions that use ConfigPath()
func TestLoad(t *testing.T) {
	// Setup temp config directory
	tmpDir := t.TempDir()
	oldXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", oldXDG)

	t.Run("load nonexistent config", func(t *testing.T) {
		cfg, err := Load()
		require.NoError(t, err)
		assert.NotNil(t, cfg)
		assert.Empty(t, cfg.Sites)
	})

	t.Run("load existing config", func(t *testing.T) {
		// Create config file
		configDir := filepath.Join(tmpDir, "ecto")
		os.MkdirAll(configDir, 0755)
		configPath := filepath.Join(configDir, "config.json")
		data := `{"default_site": "test", "sites": {"test": {"name": "test", "url": "https://test.ghost.io", "api_key": "k:s"}}}`
		os.WriteFile(configPath, []byte(data), 0600)

		cfg, err := Load()
		require.NoError(t, err)
		assert.Equal(t, "test", cfg.DefaultSite)
		assert.Len(t, cfg.Sites, 1)
	})

	t.Run("load invalid json", func(t *testing.T) {
		configDir := filepath.Join(tmpDir, "ecto")
		configPath := filepath.Join(configDir, "config.json")
		os.WriteFile(configPath, []byte("invalid json"), 0600)

		_, err := Load()
		require.Error(t, err)
	})
}

func TestSave(t *testing.T) {
	tmpDir := t.TempDir()
	oldXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", oldXDG)

	cfg := &Config{
		DefaultSite: "mysite",
		Sites: map[string]Site{
			"mysite": {Name: "mysite", URL: "https://my.ghost.io", APIKey: "m:s"},
		},
	}

	err := cfg.Save()
	require.NoError(t, err)

	// Verify file was created
	configPath := filepath.Join(tmpDir, "ecto", "config.json")
	_, err = os.Stat(configPath)
	require.NoError(t, err)

	// Load and verify
	loaded, err := Load()
	require.NoError(t, err)
	assert.Equal(t, "mysite", loaded.DefaultSite)
}

func TestAddSite(t *testing.T) {
	tmpDir := t.TempDir()
	oldXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", oldXDG)

	cfg := &Config{Sites: make(map[string]Site)}
	err := cfg.AddSite("newsite", "https://new.ghost.io", "n:s")
	require.NoError(t, err)

	assert.Equal(t, "newsite", cfg.DefaultSite)
	assert.Contains(t, cfg.Sites, "newsite")

	// Verify it was saved
	loaded, err := Load()
	require.NoError(t, err)
	assert.Contains(t, loaded.Sites, "newsite")
}

func TestRemoveSite(t *testing.T) {
	tmpDir := t.TempDir()
	oldXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", oldXDG)

	cfg := &Config{
		DefaultSite: "site1",
		Sites: map[string]Site{
			"site1": {Name: "site1", URL: "https://s1.ghost.io", APIKey: "1:1"},
			"site2": {Name: "site2", URL: "https://s2.ghost.io", APIKey: "2:2"},
		},
	}
	// Save first
	err := cfg.Save()
	require.NoError(t, err)

	// Remove site
	err = cfg.RemoveSite("site1")
	require.NoError(t, err)

	assert.NotContains(t, cfg.Sites, "site1")
	assert.Equal(t, "site2", cfg.DefaultSite) // Should pick new default

	// Verify saved
	loaded, err := Load()
	require.NoError(t, err)
	assert.NotContains(t, loaded.Sites, "site1")
}

func TestSetDefault(t *testing.T) {
	tmpDir := t.TempDir()
	oldXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", oldXDG)

	cfg := &Config{
		DefaultSite: "site1",
		Sites: map[string]Site{
			"site1": {Name: "site1", URL: "https://s1.ghost.io", APIKey: "1:1"},
			"site2": {Name: "site2", URL: "https://s2.ghost.io", APIKey: "2:2"},
		},
	}
	err := cfg.Save()
	require.NoError(t, err)

	t.Run("set existing site as default", func(t *testing.T) {
		err := cfg.SetDefault("site2")
		require.NoError(t, err)
		assert.Equal(t, "site2", cfg.DefaultSite)

		// Verify saved
		loaded, err := Load()
		require.NoError(t, err)
		assert.Equal(t, "site2", loaded.DefaultSite)
	})

	t.Run("set nonexistent site as default", func(t *testing.T) {
		err := cfg.SetDefault("nonexistent")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "not found")
	})
}

func TestGetActiveClient(t *testing.T) {
	tmpDir := t.TempDir()
	oldXDG := os.Getenv("XDG_CONFIG_HOME")
	os.Setenv("XDG_CONFIG_HOME", tmpDir)
	defer os.Setenv("XDG_CONFIG_HOME", oldXDG)

	// Clear env vars that might interfere
	oldURL := os.Getenv("GHOST_URL")
	oldKey := os.Getenv("GHOST_ADMIN_KEY")
	oldSite := os.Getenv("GHOST_SITE")
	defer func() {
		if oldURL != "" {
			os.Setenv("GHOST_URL", oldURL)
		}
		if oldKey != "" {
			os.Setenv("GHOST_ADMIN_KEY", oldKey)
		}
		if oldSite != "" {
			os.Setenv("GHOST_SITE", oldSite)
		}
	}()
	os.Unsetenv("GHOST_URL")
	os.Unsetenv("GHOST_ADMIN_KEY")
	os.Unsetenv("GHOST_SITE")

	t.Run("from env vars", func(t *testing.T) {
		os.Setenv("GHOST_URL", "https://env.ghost.io")
		os.Setenv("GHOST_ADMIN_KEY", "envid:0123456789abcdef0123456789abcdef")
		defer func() {
			os.Unsetenv("GHOST_URL")
			os.Unsetenv("GHOST_ADMIN_KEY")
		}()

		client, err := GetActiveClient("")
		require.NoError(t, err)
		assert.NotNil(t, client)
	})

	t.Run("from config", func(t *testing.T) {
		os.Unsetenv("GHOST_URL")
		os.Unsetenv("GHOST_ADMIN_KEY")

		// Create config
		cfg := &Config{
			DefaultSite: "mysite",
			Sites: map[string]Site{
				"mysite": {Name: "mysite", URL: "https://my.ghost.io", APIKey: "m:0123456789abcdef0123456789abcdef"},
			},
		}
		err := cfg.Save()
		require.NoError(t, err)

		client, err := GetActiveClient("")
		require.NoError(t, err)
		assert.NotNil(t, client)
	})

	t.Run("using GHOST_SITE env", func(t *testing.T) {
		os.Unsetenv("GHOST_URL")
		os.Unsetenv("GHOST_ADMIN_KEY")

		cfg := &Config{
			DefaultSite: "default",
			Sites: map[string]Site{
				"default": {Name: "default", URL: "https://default.ghost.io", APIKey: "d:0123456789abcdef0123456789abcdef"},
				"other":   {Name: "other", URL: "https://other.ghost.io", APIKey: "o:0123456789abcdef0123456789abcdef"},
			},
		}
		err := cfg.Save()
		require.NoError(t, err)

		os.Setenv("GHOST_SITE", "other")
		defer os.Unsetenv("GHOST_SITE")

		client, err := GetActiveClient("")
		require.NoError(t, err)
		assert.NotNil(t, client)
	})

	t.Run("no config no env", func(t *testing.T) {
		os.Unsetenv("GHOST_URL")
		os.Unsetenv("GHOST_ADMIN_KEY")
		os.Unsetenv("GHOST_SITE")

		// Clear config
		configPath := filepath.Join(tmpDir, "ecto", "config.json")
		os.Remove(configPath)

		_, err := GetActiveClient("")
		require.Error(t, err)
		assert.Contains(t, err.Error(), "no site specified")
	})

	t.Run("with site name", func(t *testing.T) {
		os.Unsetenv("GHOST_URL")
		os.Unsetenv("GHOST_ADMIN_KEY")

		cfg := &Config{
			DefaultSite: "default",
			Sites: map[string]Site{
				"default": {Name: "default", URL: "https://default.ghost.io", APIKey: "d:0123456789abcdef0123456789abcdef"},
				"other":   {Name: "other", URL: "https://other.ghost.io", APIKey: "o:0123456789abcdef0123456789abcdef"},
			},
		}
		err := cfg.Save()
		require.NoError(t, err)

		client, err := GetActiveClient("other")
		require.NoError(t, err)
		assert.NotNil(t, client)
	})
}

func TestSaveToPath_ErrorHandling(t *testing.T) {
	cfg := &Config{
		DefaultSite: "test",
		Sites: map[string]Site{
			"test": {Name: "test", URL: "https://test.ghost.io", APIKey: "t:s"},
		},
	}

	// Try to save to a directory that exists as a file
	tmpFile, err := os.CreateTemp("", "config-test")
	require.NoError(t, err)
	tmpFile.Close()
	defer os.Remove(tmpFile.Name())

	// Try to save config where the parent "directory" is actually a file
	invalidPath := filepath.Join(tmpFile.Name(), "config.json")
	err = cfg.SaveToPath(invalidPath)
	require.Error(t, err)
}

// Integration test for full workflow
func TestConfig_FullWorkflow(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "config.json")

	// Create new config
	cfg := &Config{Sites: make(map[string]Site)}

	// Add first site (becomes default)
	cfg.AddSiteNoSave("production", "https://prod.ghost.io", "prod:7365637265746b6579313233")
	assert.Equal(t, "production", cfg.DefaultSite)

	// Add second site
	cfg.AddSiteNoSave("staging", "https://staging.ghost.io", "stage:7365637265746b6579313233")
	assert.Equal(t, "production", cfg.DefaultSite) // Still production

	// Change default
	err := cfg.SetDefaultNoSave("staging")
	require.NoError(t, err)
	assert.Equal(t, "staging", cfg.DefaultSite)

	// Save
	err = cfg.SaveToPath(path)
	require.NoError(t, err)

	// Load and verify
	loaded, err := LoadFromPath(path)
	require.NoError(t, err)
	assert.Equal(t, "staging", loaded.DefaultSite)
	assert.Len(t, loaded.Sites, 2)

	// Get site
	site, err := loaded.GetSite("")
	require.NoError(t, err)
	assert.Equal(t, "https://staging.ghost.io", site.URL)

	// Remove site
	loaded.RemoveSiteNoSave("staging")
	assert.Equal(t, "production", loaded.DefaultSite) // Changed to remaining site
}
