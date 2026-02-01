// Package config provides configuration management for the ecto CLI.
// It handles loading, saving, and managing Ghost site configurations.
package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/visionik/libecto"
)

// Site represents a configured Ghost site with connection details.
type Site struct {
	// Name is the friendly identifier for this site.
	Name string `json:"name"`
	// URL is the Ghost site URL (e.g., "https://mysite.ghost.io").
	URL string `json:"url"`
	// APIKey is the Admin API key in "id:secret" format.
	APIKey string `json:"api_key"`
}

// Config holds all configured sites and the default site name.
type Config struct {
	// DefaultSite is the name of the site to use when none is specified.
	DefaultSite string `json:"default_site"`
	// Sites maps site names to their configurations.
	Sites map[string]Site `json:"sites"`
}

// ConfigPath returns the path to the config file.
// It respects XDG_CONFIG_HOME if set, otherwise uses ~/.config/ecto/config.json.
func ConfigPath() string {
	if xdg := os.Getenv("XDG_CONFIG_HOME"); xdg != "" {
		return filepath.Join(xdg, "ecto", "config.json")
	}
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".config", "ecto", "config.json")
}

// Load reads the config file and returns the configuration.
// If the file doesn't exist, it returns an empty configuration.
func Load() (*Config, error) {
	path := ConfigPath()
	data, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return &Config{Sites: make(map[string]Site)}, nil
	}
	if err != nil {
		return nil, err
	}

	var cfg Config
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}
	if cfg.Sites == nil {
		cfg.Sites = make(map[string]Site)
	}
	return &cfg, nil
}

// LoadFromPath reads a config file from a specific path.
// This is useful for testing with custom config locations.
func LoadFromPath(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return &Config{Sites: make(map[string]Site)}, nil
	}
	if err != nil {
		return nil, err
	}

	var cfg Config
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}
	if cfg.Sites == nil {
		cfg.Sites = make(map[string]Site)
	}
	return &cfg, nil
}

// Save writes the config to the config file.
// It creates parent directories if they don't exist.
func (c *Config) Save() error {
	path := ConfigPath()
	return c.SaveToPath(path)
}

// SaveToPath writes the config to a specific path.
// This is useful for testing with custom config locations.
func (c *Config) SaveToPath(path string) error {
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		return err
	}

	data, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, data, 0600)
}

// AddSite adds a new site configuration.
// If this is the first site, it becomes the default.
func (c *Config) AddSite(name, url, apiKey string) error {
	c.Sites[name] = Site{Name: name, URL: url, APIKey: apiKey}
	if c.DefaultSite == "" {
		c.DefaultSite = name
	}
	return c.Save()
}

// AddSiteNoSave adds a site without saving the config.
// This is useful when making multiple changes before a single save.
func (c *Config) AddSiteNoSave(name, url, apiKey string) {
	c.Sites[name] = Site{Name: name, URL: url, APIKey: apiKey}
	if c.DefaultSite == "" {
		c.DefaultSite = name
	}
}

// RemoveSite removes a site configuration by name.
// If the removed site was the default, a new default is selected.
func (c *Config) RemoveSite(name string) error {
	delete(c.Sites, name)
	if c.DefaultSite == name {
		c.DefaultSite = ""
		for k := range c.Sites {
			c.DefaultSite = k
			break
		}
	}
	return c.Save()
}

// RemoveSiteNoSave removes a site without saving the config.
func (c *Config) RemoveSiteNoSave(name string) {
	delete(c.Sites, name)
	if c.DefaultSite == name {
		c.DefaultSite = ""
		for k := range c.Sites {
			c.DefaultSite = k
			break
		}
	}
}

// SetDefault sets the default site.
// It returns an error if the site doesn't exist.
func (c *Config) SetDefault(name string) error {
	if _, ok := c.Sites[name]; !ok {
		return fmt.Errorf("site %q not found", name)
	}
	c.DefaultSite = name
	return c.Save()
}

// SetDefaultNoSave sets the default site without saving.
func (c *Config) SetDefaultNoSave(name string) error {
	if _, ok := c.Sites[name]; !ok {
		return fmt.Errorf("site %q not found", name)
	}
	c.DefaultSite = name
	return nil
}

// GetSite returns a site by name.
// If name is empty, it returns the default site.
// It returns an error if no site is found.
func (c *Config) GetSite(name string) (*Site, error) {
	if name == "" {
		name = c.DefaultSite
	}
	if name == "" {
		return nil, fmt.Errorf("no site specified and no default set")
	}
	site, ok := c.Sites[name]
	if !ok {
		return nil, fmt.Errorf("site %q not found", name)
	}
	return &site, nil
}

// GetActiveClient returns a libecto.Client for the active site.
// It checks environment variables (GHOST_URL, GHOST_ADMIN_KEY) first,
// then falls back to config. GHOST_SITE can override the site name.
func GetActiveClient(siteName string) (*libecto.Client, error) {
	// Check environment variables first
	envURL := os.Getenv("GHOST_URL")
	envKey := os.Getenv("GHOST_ADMIN_KEY")
	envSite := os.Getenv("GHOST_SITE")

	if envURL != "" && envKey != "" {
		return libecto.NewClient(envURL, envKey), nil
	}

	// Use GHOST_SITE env var if set
	if siteName == "" && envSite != "" {
		siteName = envSite
	}

	cfg, err := Load()
	if err != nil {
		return nil, err
	}

	site, err := cfg.GetSite(siteName)
	if err != nil {
		return nil, err
	}

	return libecto.NewClient(site.URL, site.APIKey), nil
}

// GetActiveClientWithConfig returns a client using a pre-loaded config.
// This is useful for testing to avoid loading from the filesystem.
func GetActiveClientWithConfig(cfg *Config, siteName string) (*libecto.Client, error) {
	// Check environment variables first
	envURL := os.Getenv("GHOST_URL")
	envKey := os.Getenv("GHOST_ADMIN_KEY")
	envSite := os.Getenv("GHOST_SITE")

	if envURL != "" && envKey != "" {
		return libecto.NewClient(envURL, envKey), nil
	}

	// Use GHOST_SITE env var if set
	if siteName == "" && envSite != "" {
		siteName = envSite
	}

	site, err := cfg.GetSite(siteName)
	if err != nil {
		return nil, err
	}

	return libecto.NewClient(site.URL, site.APIKey), nil
}
