package cmd

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestPagesCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "list pages default",
			args:    []string{"pages"},
			wantOut: []string{"[published]", "page-1", "Page One"},
			wantErr: false,
		},
		{
			name:    "list pages with json",
			args:    []string{"pages", "--json"},
			wantOut: []string{`"pages"`, `"id"`, `"title"`},
			wantErr: false,
		},
		{
			name:    "list pages with status filter",
			args:    []string{"pages", "--status", "draft"},
			wantOut: []string{"page-"},
			wantErr: false,
		},
		{
			name:    "list pages with limit",
			args:    []string{"pages", "--limit", "10"},
			wantOut: []string{"page-"},
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

func TestPageCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "get page by id",
			args:    []string{"page", "page-123"},
			wantOut: []string{"ID:", "page-123", "Title:", "Test Page"},
			wantErr: false,
		},
		{
			name:    "get page with json",
			args:    []string{"page", "page-123", "--json"},
			wantOut: []string{`"pages"`, `"id"`, `"page-123"`},
			wantErr: false,
		},
		{
			name:    "get page missing arg",
			args:    []string{"page"},
			wantErr: true,
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

func TestPageCreateCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tmpDir := t.TempDir()
	mdFile := filepath.Join(tmpDir, "page.md")
	err := os.WriteFile(mdFile, []byte("# Page Content\n\nThis is page content."), 0644)
	require.NoError(t, err)

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
		errMsg  string
	}{
		{
			name:    "create page with title",
			args:    []string{"page", "create", "--title", "My New Page"},
			wantOut: []string{"Created page:", "new-page"},
			wantErr: false,
		},
		{
			name:    "create page with markdown file",
			args:    []string{"page", "create", "--title", "Markdown Page", "--markdown-file", mdFile},
			wantOut: []string{"Created page:"},
			wantErr: false,
		},
		{
			name:    "create page with status",
			args:    []string{"page", "create", "--title", "Draft Page", "--status", "draft"},
			wantOut: []string{"Created page:"},
			wantErr: false,
		},
		{
			name:    "create page missing title",
			args:    []string{"page", "create"},
			wantErr: true,
			errMsg:  "--title is required",
		},
		{
			name:    "create page with nonexistent markdown file",
			args:    []string{"page", "create", "--title", "Test", "--markdown-file", "/nonexistent/file.md"},
			wantErr: true,
			errMsg:  "reading markdown file",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
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

func TestPageEditCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tmpDir := t.TempDir()
	mdFile := filepath.Join(tmpDir, "update.md")
	err := os.WriteFile(mdFile, []byte("# Updated Page Content"), 0644)
	require.NoError(t, err)

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "edit page title",
			args:    []string{"page", "edit", "page-123", "--title", "New Title"},
			wantOut: []string{"Updated page:"},
			wantErr: false,
		},
		{
			name:    "edit page status",
			args:    []string{"page", "edit", "page-123", "--status", "published"},
			wantOut: []string{"Updated page:"},
			wantErr: false,
		},
		{
			name:    "edit page with markdown",
			args:    []string{"page", "edit", "page-123", "--markdown-file", mdFile},
			wantOut: []string{"Updated page:"},
			wantErr: false,
		},
		{
			name:    "edit page missing id",
			args:    []string{"page", "edit"},
			wantErr: true,
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

func TestPageDeleteCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "delete page with force",
			args:    []string{"page", "delete", "page-123", "--force"},
			wantOut: []string{"Deleted page:", "page-123"},
			wantErr: false,
		},
		{
			name:    "delete missing id",
			args:    []string{"page", "delete"},
			wantErr: true,
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

func TestPagePublishCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "publish page",
			args:    []string{"page", "publish", "page-123"},
			wantOut: []string{"Published page:"},
			wantErr: false,
		},
		{
			name:    "publish missing id",
			args:    []string{"page", "publish"},
			wantErr: true,
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

func TestPagesEmptyResponse(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"pages": []interface{}{},
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
	stdout, _, err := executeCommand(cmd, "pages")

	require.NoError(t, err)
	assert.Contains(t, stdout, "No pages found")
}

func TestPagesApiError(t *testing.T) {
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
	_, _, err := executeCommand(cmd, "pages")

	require.Error(t, err)
}

func TestPageGetApiError(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"errors": []map[string]string{{"message": "Page not found"}},
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
	_, _, err := executeCommand(cmd, "page", "nonexistent")

	require.Error(t, err)
}
