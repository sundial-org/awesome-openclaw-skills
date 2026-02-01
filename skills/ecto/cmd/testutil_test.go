package cmd

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"

	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
	"github.com/visionik/libecto"
)

// mockGhostServer creates a test HTTP server that mocks the Ghost Admin API.
// It returns the server and a cleanup function.
func mockGhostServer(t *testing.T) (*httptest.Server, func()) {
	t.Helper()

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		path := r.URL.Path

		// Remove /ghost/api/admin prefix
		apiPath := strings.TrimPrefix(path, "/ghost/api/admin")

		// Helper to check if path is exactly /resource/ (list endpoint)
		isListEndpoint := func(resource string) bool {
			return apiPath == "/"+resource+"/"
		}

		// Helper to check if path is /resource/<id>/ or /resource/slug/<slug>/ (single item)
		isSingleEndpoint := func(resource string) bool {
			prefix := "/" + resource + "/"
			return strings.HasPrefix(apiPath, prefix) && len(apiPath) > len(prefix)
		}

		switch {
		// Posts - list
		case isListEndpoint("posts") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"posts": []libecto.Post{
					{ID: "post-1", Title: "Post One", Slug: "post-one", Status: "published"},
					{ID: "post-2", Title: "Post Two", Slug: "post-two", Status: "draft"},
				},
			})
		// Posts - create
		case isListEndpoint("posts") && r.Method == http.MethodPost:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"posts": []libecto.Post{{
					ID:    "new-post-123",
					Title: "New Post",
					Slug:  "new-post",
				}},
			})
		// Posts - single GET
		case isSingleEndpoint("posts") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"posts": []libecto.Post{{
					ID:        "post-123",
					Title:     "Test Post",
					Slug:      "test-post",
					Status:    "published",
					CreatedAt: "2024-01-01T00:00:00.000Z",
					Excerpt:   "Test excerpt",
					HTML:      "<p>Test content</p>",
					Tags:      []libecto.Tag{{Name: "news"}},
				}},
			})
		// Posts - update
		case isSingleEndpoint("posts") && r.Method == http.MethodPut:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"posts": []libecto.Post{{
					ID:     "post-123",
					Title:  "Updated Post",
					Status: "published",
				}},
			})
		// Posts - delete
		case isSingleEndpoint("posts") && r.Method == http.MethodDelete:
			w.WriteHeader(http.StatusNoContent)

		// Pages - list
		case isListEndpoint("pages") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"pages": []libecto.Page{
					{ID: "page-1", Title: "Page One", Slug: "page-one", Status: "published"},
					{ID: "page-2", Title: "Page Two", Slug: "page-two", Status: "draft"},
				},
			})
		// Pages - create
		case isListEndpoint("pages") && r.Method == http.MethodPost:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"pages": []libecto.Page{{
					ID:    "new-page-123",
					Title: "New Page",
					Slug:  "new-page",
				}},
			})
		// Pages - single GET
		case isSingleEndpoint("pages") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"pages": []libecto.Page{{
					ID:        "page-123",
					Title:     "Test Page",
					Slug:      "test-page",
					Status:    "published",
					CreatedAt: "2024-01-01T00:00:00.000Z",
				}},
			})
		// Pages - update
		case isSingleEndpoint("pages") && r.Method == http.MethodPut:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"pages": []libecto.Page{{
					ID:     "page-123",
					Title:  "Updated Page",
					Status: "published",
				}},
			})
		// Pages - delete
		case isSingleEndpoint("pages") && r.Method == http.MethodDelete:
			w.WriteHeader(http.StatusNoContent)

		// Tags - list
		case isListEndpoint("tags") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"tags": []libecto.Tag{
					{ID: "tag-1", Name: "Tag One", Slug: "tag-one"},
					{ID: "tag-2", Name: "Tag Two", Slug: "tag-two"},
				},
			})
		// Tags - create
		case isListEndpoint("tags") && r.Method == http.MethodPost:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"tags": []libecto.Tag{{
					ID:   "new-tag-123",
					Name: "New Tag",
					Slug: "new-tag",
				}},
			})
		// Tags - single GET
		case isSingleEndpoint("tags") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"tags": []libecto.Tag{{
					ID:          "tag-123",
					Name:        "Test Tag",
					Slug:        "test-tag",
					Description: "A test tag",
				}},
			})
		// Tags - update
		case isSingleEndpoint("tags") && r.Method == http.MethodPut:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"tags": []libecto.Tag{{
					ID:   "tag-123",
					Name: "Updated Tag",
				}},
			})
		// Tags - delete
		case isSingleEndpoint("tags") && r.Method == http.MethodDelete:
			w.WriteHeader(http.StatusNoContent)

		// Users - list
		case isListEndpoint("users") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"users": []libecto.Author{
					{ID: "user-1", Name: "User One", Slug: "user-one"},
					{ID: "user-2", Name: "User Two", Slug: "user-two"},
				},
			})
		// Users - single GET
		case isSingleEndpoint("users") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"users": []libecto.Author{{
					ID:    "user-123",
					Name:  "Test User",
					Slug:  "test-user",
					Email: "test@example.com",
					Bio:   "A test user",
				}},
			})

		// Site
		case apiPath == "/site/":
			json.NewEncoder(w).Encode(map[string]interface{}{
				"site": libecto.Site{
					Title:       "Test Site",
					Description: "A test Ghost site",
					URL:         "https://test.ghost.io",
					Version:     "5.0.0",
					Logo:        "https://test.ghost.io/logo.png",
				},
			})

		// Settings
		case apiPath == "/settings/":
			json.NewEncoder(w).Encode(map[string]interface{}{
				"settings": []libecto.Setting{
					{Key: "title", Value: "Test Site"},
					{Key: "description", Value: "A test description"},
					{Key: "active_timezone", Value: "UTC"},
					{Key: "members_enabled", Value: true},
					{Key: "null_setting", Value: nil},
				},
			})

		// Newsletters - list
		case isListEndpoint("newsletters") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"newsletters": []libecto.Newsletter{
					{ID: "nl-1", Name: "Newsletter One", Slug: "newsletter-one", Status: "active"},
					{ID: "nl-2", Name: "Newsletter Two", Slug: "newsletter-two", Status: "archived"},
				},
			})
		// Newsletters - single GET
		case isSingleEndpoint("newsletters") && r.Method == http.MethodGet:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"newsletters": []libecto.Newsletter{{
					ID:          "newsletter-123",
					Name:        "Test Newsletter",
					Slug:        "test-newsletter",
					Status:      "active",
					Description: "A test newsletter",
				}},
			})

		// Webhooks - create
		case isListEndpoint("webhooks") && r.Method == http.MethodPost:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"webhooks": []libecto.Webhook{{
					ID:        "webhook-123",
					Event:     "post.published",
					TargetURL: "https://example.com/hook",
				}},
			})
		// Webhooks - delete
		case isSingleEndpoint("webhooks") && r.Method == http.MethodDelete:
			w.WriteHeader(http.StatusNoContent)

		// Images - upload
		case apiPath == "/images/upload/" && r.Method == http.MethodPost:
			json.NewEncoder(w).Encode(map[string]interface{}{
				"images": []libecto.Image{{
					URL: "https://test.ghost.io/images/uploaded.png",
					Ref: "uploaded.png",
				}},
			})

		default:
			w.WriteHeader(http.StatusNotFound)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"errors": []map[string]string{{"message": "Not found: " + apiPath}},
			})
		}
	})

	server := httptest.NewServer(handler)

	// Save original env vars
	origURL := os.Getenv("GHOST_URL")
	origKey := os.Getenv("GHOST_ADMIN_KEY")

	// Set test env vars - use a valid hex secret (32 hex chars = 16 bytes)
	os.Setenv("GHOST_URL", server.URL)
	os.Setenv("GHOST_ADMIN_KEY", "testid:0123456789abcdef0123456789abcdef")

	cleanup := func() {
		server.Close()
		os.Setenv("GHOST_URL", origURL)
		os.Setenv("GHOST_ADMIN_KEY", origKey)
	}

	return server, cleanup
}

// executeCommand executes a cobra command and captures output.
func executeCommand(root *cobra.Command, args ...string) (stdout string, stderr string, err error) {
	stdoutBuf := new(bytes.Buffer)
	stderrBuf := new(bytes.Buffer)

	// Capture both cobra output and our custom output
	SetOutput(stdoutBuf)
	defer ResetOutput()

	root.SetOut(stdoutBuf)
	root.SetErr(stderrBuf)
	root.SetArgs(args)

	err = root.Execute()

	return stdoutBuf.String(), stderrBuf.String(), err
}

// executeCommandWithStdin executes a command with custom stdin.
func executeCommandWithStdin(root *cobra.Command, stdin io.Reader, args ...string) (stdout string, stderr string, err error) {
	stdoutBuf := new(bytes.Buffer)
	stderrBuf := new(bytes.Buffer)

	SetOutput(stdoutBuf)
	defer ResetOutput()

	root.SetOut(stdoutBuf)
	root.SetErr(stderrBuf)
	root.SetIn(stdin)
	root.SetArgs(args)

	err = root.Execute()

	return stdoutBuf.String(), stderrBuf.String(), err
}

// newTestRootCmd returns the root command for testing.
// It resets flags to avoid state pollution between tests.
func newTestRootCmd() *cobra.Command {
	cmd := RootCmd()
	resetFlags(cmd)
	return cmd
}

// resetFlags recursively resets all flags on a command and its children.
func resetFlags(cmd *cobra.Command) {
	cmd.Flags().VisitAll(func(f *pflag.Flag) {
		f.Changed = false
		if f.Value.Type() == "bool" {
			f.Value.Set("false")
		} else if f.Value.Type() == "string" {
			f.Value.Set(f.DefValue)
		} else if f.Value.Type() == "int" {
			f.Value.Set(f.DefValue)
		}
	})
	for _, child := range cmd.Commands() {
		resetFlags(child)
	}
}
