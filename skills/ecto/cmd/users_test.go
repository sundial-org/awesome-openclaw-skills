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
func TestUsersCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "list users default",
			args:    []string{"users"},
			wantOut: []string{"user-1", "User One", "user-one"},
			wantErr: false,
		},
		{
			name:    "list users with json",
			args:    []string{"users", "--json"},
			wantOut: []string{`"users"`, `"id"`, `"name"`},
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

func TestUserCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "get user by id",
			args:    []string{"user", "user-123"},
			wantOut: []string{"ID:", "user-123", "Name:", "Test User", "Email:", "test@example.com", "Bio:", "A test user"},
			wantErr: false,
		},
		{
			name:    "get user with json",
			args:    []string{"user", "user-123", "--json"},
			wantOut: []string{`"users"`, `"id"`, `"user-123"`},
			wantErr: false,
		},
		{
			name:    "get user missing arg",
			args:    []string{"user"},
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

func TestUsersEmptyResponseFromServer(t *testing.T) {
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

func TestUsersApiError(t *testing.T) {
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
	_, _, err := executeCommand(cmd, "users")

	require.Error(t, err)
}
