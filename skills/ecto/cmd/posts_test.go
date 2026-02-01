package cmd

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)
func TestPostsCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "list posts default",
			args:    []string{"posts"},
			wantOut: []string{"[published]", "post-1", "Post One"},
			wantErr: false,
		},
		{
			name:    "list posts with json",
			args:    []string{"posts", "--json"},
			wantOut: []string{`"posts"`, `"id"`, `"title"`},
			wantErr: false,
		},
		{
			name:    "list posts with status filter",
			args:    []string{"posts", "--status", "draft"},
			wantOut: []string{"post-"},
			wantErr: false,
		},
		{
			name:    "list posts with limit",
			args:    []string{"posts", "--limit", "5"},
			wantOut: []string{"post-"},
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

func TestPostCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "get post by id",
			args:    []string{"post", "post-123"},
			wantOut: []string{"ID:", "post-123", "Title:", "Test Post"},
			wantErr: false,
		},
		{
			name:    "get post with json",
			args:    []string{"post", "post-123", "--json"},
			wantOut: []string{`"posts"`, `"id"`, `"post-123"`},
			wantErr: false,
		},
		{
			name:    "get post with body flag",
			args:    []string{"post", "post-123", "--body"},
			wantOut: []string{"Body (HTML):", "<p>Test content</p>"},
			wantErr: false,
		},
		{
			name:    "get post missing arg",
			args:    []string{"post"},
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

func TestPostCreateCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	// Create a temp markdown file for testing
	tmpDir := t.TempDir()
	mdFile := filepath.Join(tmpDir, "test.md")
	err := os.WriteFile(mdFile, []byte("# Test Content\n\nThis is test content."), 0644)
	require.NoError(t, err)

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
		errMsg  string
	}{
		{
			name:    "create post with title",
			args:    []string{"post", "create", "--title", "My New Post"},
			wantOut: []string{"Created post:", "new-post"},
			wantErr: false,
		},
		{
			name:    "create post with markdown file",
			args:    []string{"post", "create", "--title", "Markdown Post", "--markdown-file", mdFile},
			wantOut: []string{"Created post:"},
			wantErr: false,
		},
		{
			name:    "create post with status",
			args:    []string{"post", "create", "--title", "Draft Post", "--status", "draft"},
			wantOut: []string{"Created post:"},
			wantErr: false,
		},
		{
			name:    "create post with tags",
			args:    []string{"post", "create", "--title", "Tagged Post", "--tag", "news,featured"},
			wantOut: []string{"Created post:"},
			wantErr: false,
		},
		{
			name:    "create post missing title",
			args:    []string{"post", "create"},
			wantErr: true,
			errMsg:  "--title is required",
		},
		{
			name:    "create post with nonexistent markdown file",
			args:    []string{"post", "create", "--title", "Test", "--markdown-file", "/nonexistent/file.md"},
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

func TestPostEditCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tmpDir := t.TempDir()
	mdFile := filepath.Join(tmpDir, "update.md")
	err := os.WriteFile(mdFile, []byte("# Updated Content"), 0644)
	require.NoError(t, err)

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "edit post title",
			args:    []string{"post", "edit", "post-123", "--title", "New Title"},
			wantOut: []string{"Updated post:"},
			wantErr: false,
		},
		{
			name:    "edit post status",
			args:    []string{"post", "edit", "post-123", "--status", "published"},
			wantOut: []string{"Updated post:"},
			wantErr: false,
		},
		{
			name:    "edit post with markdown",
			args:    []string{"post", "edit", "post-123", "--markdown-file", mdFile},
			wantOut: []string{"Updated post:"},
			wantErr: false,
		},
		{
			name:    "edit post with publish-at",
			args:    []string{"post", "edit", "post-123", "--publish-at", "2024-12-01T00:00:00Z"},
			wantOut: []string{"Updated post:"},
			wantErr: false,
		},
		{
			name:    "edit post missing id",
			args:    []string{"post", "edit"},
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

func TestPostDeleteCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "delete post with force",
			args:    []string{"post", "delete", "post-123", "--force"},
			wantOut: []string{"Deleted post:", "post-123"},
			wantErr: false,
		},
		{
			name:    "delete missing id",
			args:    []string{"post", "delete"},
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

func TestPostPublishCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "publish post",
			args:    []string{"post", "publish", "post-123"},
			wantOut: []string{"Published post:"},
			wantErr: false,
		},
		{
			name:    "publish missing id",
			args:    []string{"post", "publish"},
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

func TestPostUnpublishCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "unpublish post",
			args:    []string{"post", "unpublish", "post-123"},
			wantOut: []string{"Unpublished post:"},
			wantErr: false,
		},
		{
			name:    "unpublish missing id",
			args:    []string{"post", "unpublish"},
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

func TestPostScheduleCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
		errMsg  string
	}{
		{
			name:    "schedule post",
			args:    []string{"post", "schedule", "post-123", "--at", "2024-12-01T12:00:00Z"},
			wantOut: []string{"Scheduled post", "2024-12-01T12:00:00Z"},
			wantErr: false,
		},
		{
			name:    "schedule missing at flag",
			args:    []string{"post", "schedule", "post-123"},
			wantErr: true,
			errMsg:  "--at is required",
		},
		{
			name:    "schedule missing id",
			args:    []string{"post", "schedule"},
			wantErr: true,
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

func TestOutputJSON(t *testing.T) {
	tests := []struct {
		name  string
		input interface{}
	}{
		{
			name:  "map output",
			input: map[string]string{"key": "value"},
		},
		{
			name:  "slice output",
			input: []string{"a", "b", "c"},
		},
		{
			name:  "struct output",
			input: struct{ Name string }{Name: "test"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// outputJSON writes to os.Stdout, so we just verify no panic
			// In real tests, we capture stdout via command execution
			err := outputJSON(tt.input)
			assert.NoError(t, err)
		})
	}
}

func TestPostCreateWithStdin(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		stdin   string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "create post with stdin markdown",
			args:    []string{"post", "create", "--title", "Stdin Post", "--stdin-format", "markdown"},
			stdin:   "# Hello World\n\nThis is **bold** text.",
			wantOut: []string{"Created post:", "new-post-123"},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cmd := newTestRootCmd()
			stdin := strings.NewReader(tt.stdin)
			stdout, _, err := executeCommandWithStdin(cmd, stdin, tt.args...)

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

func TestPostsEmptyResponse(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"posts": []interface{}{},
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
	stdout, _, err := executeCommand(cmd, "posts")

	require.NoError(t, err)
	assert.Contains(t, stdout, "No posts found")
}

func TestTagsEmptyResponse(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"tags": []interface{}{},
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
	stdout, _, err := executeCommand(cmd, "tags")

	require.NoError(t, err)
	assert.Contains(t, stdout, "No tags found")
}

func TestUsersEmptyResponse(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"users": []interface{}{},
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
	stdout, _, err := executeCommand(cmd, "users")

	require.NoError(t, err)
	assert.Contains(t, stdout, "No users found")
}

func TestPostsApiError(t *testing.T) {
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
	_, _, err := executeCommand(cmd, "posts")

	require.Error(t, err)
	assert.Contains(t, err.Error(), "Internal server error")
}

func TestPostGetApiError(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"errors": []map[string]string{{"message": "Post not found"}},
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
	_, _, err := executeCommand(cmd, "post", "nonexistent")

	require.Error(t, err)
	assert.Contains(t, err.Error(), "not found")
}

func TestPostCreateApiError(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"errors": []map[string]string{{"message": "Validation failed"}},
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
	_, _, err := executeCommand(cmd, "post", "create", "--title", "Test")

	require.Error(t, err)
	assert.Contains(t, err.Error(), "Validation failed")
}

func TestPostEditApiError(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.Method == "GET" {
			// First get the post
			json.NewEncoder(w).Encode(map[string]interface{}{
				"posts": []map[string]interface{}{{
					"id": "post-123",
					"title": "Test",
					"updated_at": "2024-01-01T00:00:00.000Z",
				}},
			})
		} else {
			w.WriteHeader(http.StatusBadRequest)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"errors": []map[string]string{{"message": "Edit failed"}},
			})
		}
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
	_, _, err := executeCommand(cmd, "post", "edit", "post-123", "--title", "New Title")

	require.Error(t, err)
}

func TestPostDeleteApiError(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.Method == "GET" {
			json.NewEncoder(w).Encode(map[string]interface{}{
				"posts": []map[string]interface{}{{
					"id": "post-123",
					"title": "Test",
				}},
			})
		} else {
			w.WriteHeader(http.StatusForbidden)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"errors": []map[string]string{{"message": "Delete forbidden"}},
			})
		}
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
	_, _, err := executeCommand(cmd, "post", "delete", "post-123", "--force")

	require.Error(t, err)
}
