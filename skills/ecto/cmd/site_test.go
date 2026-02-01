package cmd

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)
func TestSiteCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "get site info default",
			args:    []string{"site"},
			wantOut: []string{"Title:", "Test Site", "Description:", "A test Ghost site", "URL:", "https://test.ghost.io", "Version:", "5.0.0", "Logo:"},
			wantErr: false,
		},
		{
			name:    "get site info with json",
			args:    []string{"site", "--json"},
			wantOut: []string{`"site"`, `"title"`, `"Test Site"`},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cmd := newTestRootCmd()
			stdout, _, err := executeCommand(cmd, tt.args...)

			if tt.wantErr {
				require.Error(t, err)
				return
			}
			require.NoError(t, err)

			for _, want := range tt.wantOut {
				assert.Contains(t, stdout, want)
			}
		})
	}
}

func TestSettingsCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "get settings default",
			args:    []string{"settings"},
			wantOut: []string{"title:", "Test Site", "description:", "active_timezone:", "UTC", "members_enabled:", "true"},
			wantErr: false,
		},
		{
			name:    "get settings with json",
			args:    []string{"settings", "--json"},
			wantOut: []string{`"settings"`, `"key"`, `"value"`},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cmd := newTestRootCmd()
			stdout, _, err := executeCommand(cmd, tt.args...)

			if tt.wantErr {
				require.Error(t, err)
				return
			}
			require.NoError(t, err)

			for _, want := range tt.wantOut {
				assert.Contains(t, stdout, want)
			}
		})
	}
}

// Test settings with null values to ensure proper handling
func TestSettingsNullValue(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	cmd := newTestRootCmd()
	stdout, _, err := executeCommand(cmd, "settings")
	require.NoError(t, err)
	
	// null_setting should be formatted with empty value
	assert.Contains(t, stdout, "null_setting:")
}

func TestSiteApiError(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"errors": []map[string]string{{"message": "Internal server error"}},
		})
	})
	server := httptest.NewServer(handler)
	defer server.Close()

	origURL := os.Getenv("GHOST_URL")
	origKey := os.Getenv("GHOST_ADMIN_KEY")
	os.Setenv("GHOST_URL", server.URL)
	os.Setenv("GHOST_ADMIN_KEY", "testid:0123456789abcdef0123456789abcdef")
	defer func() {
		os.Setenv("GHOST_URL", origURL)
		os.Setenv("GHOST_ADMIN_KEY", origKey)
	}()

	cmd := newTestRootCmd()
	_, _, err := executeCommand(cmd, "site")

	require.Error(t, err)
}

func TestSettingsApiError(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"errors": []map[string]string{{"message": "Internal server error"}},
		})
	})
	server := httptest.NewServer(handler)
	defer server.Close()

	origURL := os.Getenv("GHOST_URL")
	origKey := os.Getenv("GHOST_ADMIN_KEY")
	os.Setenv("GHOST_URL", server.URL)
	os.Setenv("GHOST_ADMIN_KEY", "testid:0123456789abcdef0123456789abcdef")
	defer func() {
		os.Setenv("GHOST_URL", origURL)
		os.Setenv("GHOST_ADMIN_KEY", origKey)
	}()

	cmd := newTestRootCmd()
	_, _, err := executeCommand(cmd, "settings")

	require.Error(t, err)
}
