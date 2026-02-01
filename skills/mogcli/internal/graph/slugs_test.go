package graph

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/mogcli/internal/config"
)

func TestFormatID(t *testing.T) {
	// Setup: use temp dir for config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Clear cache
	slugMu.Lock()
	slugCache = nil
	slugMu.Unlock()

	tests := []struct {
		name  string
		input string
		want  int // expected length (8 chars for valid IDs)
	}{
		{"empty", "", 0},
		{"short ID", "abc123", 8},
		{"long ID", "AQMkADAwATMzAGZmAS04MDViLTRiNzgtMDACLTAwCgBGAAADExample", 8},
		{"another long ID", "AQMkADAwATMzAGZmAS04MDViLTRiNzgtMDACLTAwCgBGAAADDifferent", 8},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := FormatID(tt.input)
			assert.Len(t, got, tt.want)
		})
	}
}

func TestFormatID_Consistency(t *testing.T) {
	// Setup: use temp dir for config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Clear cache
	slugMu.Lock()
	slugCache = nil
	slugMu.Unlock()

	id := "AQMkADAwATMzAGZmAS04MDViLTRiNzgtMDACLTAwCgBGAAADTestID123"

	// Same ID should always produce same slug
	slug1 := FormatID(id)
	slug2 := FormatID(id)

	assert.Equal(t, slug1, slug2, "same ID should produce same slug")
}

func TestResolveID(t *testing.T) {
	// Setup: use temp dir for config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Clear cache
	slugMu.Lock()
	slugCache = nil
	slugMu.Unlock()

	tests := []struct {
		name  string
		input string
	}{
		{"empty", ""},
		{"long ID passthrough", "AQMkADAwATMzAGZmAS04MDViLTRiNzgtMDACLTAwCgBGAAADVeryLongID"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ResolveID(tt.input)
			if tt.input == "" {
				assert.Empty(t, got)
			} else if len(tt.input) > 16 {
				assert.Equal(t, tt.input, got, "long IDs should pass through unchanged")
			}
		})
	}
}

func TestResolveID_RoundTrip(t *testing.T) {
	// Setup: use temp dir for config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Clear cache
	slugMu.Lock()
	slugCache = nil
	slugMu.Unlock()

	originalID := "AQMkADAwATMzAGZmAS04MDViLTRiNzgtMDACLTAwCgBGAAADRoundTrip"

	// Format to slug
	slug := FormatID(originalID)
	require.NotEmpty(t, slug)

	// Resolve back to original
	resolved := ResolveID(slug)
	assert.Equal(t, originalID, resolved, "round trip should return original ID")
}

func TestClearSlugs(t *testing.T) {
	// Setup: use temp dir for config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))

	// Add some slugs
	slugMu.Lock()
	slugCache = &config.Slugs{
		IDToSlug: map[string]string{"test": "slug"},
		SlugToID: map[string]string{"slug": "test"},
	}
	slugMu.Unlock()

	// Clear
	err := ClearSlugs()
	require.NoError(t, err)

	// Verify cleared
	slugMu.Lock()
	assert.Empty(t, slugCache.IDToSlug)
	assert.Empty(t, slugCache.SlugToID)
	slugMu.Unlock()
}

func TestFormatID_CollisionHandling(t *testing.T) {
	// Setup: use temp dir for config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Clear cache
	slugMu.Lock()
	slugCache = nil
	slugMu.Unlock()

	// Generate slugs for multiple IDs
	ids := []string{
		"ID_ONE_AAAAAAAAAAAAAAAAAAAAAA",
		"ID_TWO_BBBBBBBBBBBBBBBBBBBBBB",
		"ID_THREE_CCCCCCCCCCCCCCCCCCCC",
	}

	slugs := make(map[string]string)
	for _, id := range ids {
		slug := FormatID(id)
		// Check no duplicate slugs
		for existingID, existingSlug := range slugs {
			if existingSlug == slug && existingID != id {
				t.Errorf("collision: %s and %s both map to %s", existingID, id, slug)
			}
		}
		slugs[id] = slug
	}

	// All slugs should be unique
	uniqueSlugs := make(map[string]bool)
	for _, slug := range slugs {
		if uniqueSlugs[slug] {
			t.Error("duplicate slug found")
		}
		uniqueSlugs[slug] = true
	}
}

func TestResolveID_UnknownSlug(t *testing.T) {
	// Setup: use temp dir for config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Clear cache
	slugMu.Lock()
	slugCache = nil
	slugMu.Unlock()

	// Unknown short string should pass through
	unknown := "xyz12345"
	result := ResolveID(unknown)
	assert.Equal(t, unknown, result, "unknown slug should pass through")
}

func TestFormatID_CachePersistence(t *testing.T) {
	// Setup: use temp dir for config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))

	// Clear cache
	slugMu.Lock()
	slugCache = nil
	slugMu.Unlock()

	id := "PersistenceTestID_XXXXXXXXXXXXXXXX"
	slug1 := FormatID(id)

	// Clear in-memory cache
	slugMu.Lock()
	slugCache = nil
	slugMu.Unlock()

	// Should reload from disk and resolve
	resolved := ResolveID(slug1)
	assert.Equal(t, id, resolved, "should resolve after cache reload")
}

func TestFormatID_SlugLength(t *testing.T) {
	// Setup: use temp dir for config
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Clear cache
	slugMu.Lock()
	slugCache = nil
	slugMu.Unlock()

	// Various ID lengths
	ids := []string{
		"a",
		"short",
		"medium-length-id-here",
		"this-is-a-much-longer-id-that-microsoft-might-use-ABCDEFGHIJKLMNOP",
	}

	for _, id := range ids {
		slug := FormatID(id)
		assert.Len(t, slug, 8, "all slugs should be 8 chars for id: %s", id)
	}
}
