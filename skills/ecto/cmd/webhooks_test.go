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
func TestWebhookCreateCmd(t *testing.T) {
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
			name:    "create webhook",
			args:    []string{"webhook", "create", "--event", "post.published", "--target-url", "https://example.com/hook"},
			wantOut: []string{"Created webhook:", "webhook-123", "post.published", "https://example.com/hook"},
			wantErr: false,
		},
		{
			name:    "create webhook with name",
			args:    []string{"webhook", "create", "--event", "post.published", "--target-url", "https://example.com/hook", "--name", "My Webhook"},
			wantOut: []string{"Created webhook:"},
			wantErr: false,
		},
		{
			name:    "create webhook missing event",
			args:    []string{"webhook", "create", "--target-url", "https://example.com/hook"},
			wantErr: true,
			errMsg:  "--event and --target-url are required",
		},
		{
			name:    "create webhook missing target-url",
			args:    []string{"webhook", "create", "--event", "post.published"},
			wantErr: true,
			errMsg:  "--event and --target-url are required",
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

func TestWebhookDeleteCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "delete webhook with force",
			args:    []string{"webhook", "delete", "webhook-123", "--force"},
			wantOut: []string{"Deleted webhook:", "webhook-123"},
			wantErr: false,
		},
		{
			name:    "delete missing id",
			args:    []string{"webhook", "delete"},
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

// Test webhook parent command
func TestWebhookCmd(t *testing.T) {
	cmd := newTestRootCmd()
	stdout, _, err := executeCommand(cmd, "webhook", "--help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "Manage webhooks")
	assert.Contains(t, stdout, "create")
	assert.Contains(t, stdout, "delete")
}

func TestWebhookCreateApiError(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"errors": []map[string]string{{"message": "Invalid webhook"}},
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
	_, _, err := executeCommand(cmd, "webhook", "create", "--event", "post.published", "--target-url", "https://example.com")

	require.Error(t, err)
}
