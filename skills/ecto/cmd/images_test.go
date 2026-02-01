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
func TestImageUploadCmd(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	// Create a temp image file for testing
	tmpDir := t.TempDir()
	imgFile := filepath.Join(tmpDir, "test.png")
	// Create a minimal PNG file (1x1 pixel)
	pngData := []byte{
		0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
		0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
		0xde, 0x00, 0x00, 0x00, 0x0c, 0x49, 0x44, 0x41, 0x54, 0x08, 0xd7, 0x63, 0xf8, 0xff, 0xff, 0x3f,
		0x00, 0x05, 0xfe, 0x02, 0xfe, 0xdc, 0xcc, 0x59, 0xe7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e,
		0x44, 0xae, 0x42, 0x60, 0x82,
	}
	err := os.WriteFile(imgFile, pngData, 0644)
	require.NoError(t, err)

	tests := []struct {
		name    string
		args    []string
		wantOut []string
		wantErr bool
	}{
		{
			name:    "upload image",
			args:    []string{"image", "upload", imgFile},
			wantOut: []string{"Uploaded:", "https://test.ghost.io/images/uploaded.png"},
			wantErr: false,
		},
		{
			name:    "upload image with json",
			args:    []string{"image", "upload", imgFile, "--json"},
			wantOut: []string{`"images"`, `"url"`},
			wantErr: false,
		},
		{
			name:    "upload missing path",
			args:    []string{"image", "upload"},
			wantErr: true,
		},
		{
			name:    "upload nonexistent file",
			args:    []string{"image", "upload", "/nonexistent/image.png"},
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

// Test image parent command
func TestImageCmd(t *testing.T) {
	cmd := newTestRootCmd()
	stdout, _, err := executeCommand(cmd, "image", "--help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "Manage images")
	assert.Contains(t, stdout, "upload")
}

func TestImageUploadApiError(t *testing.T) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"errors": []map[string]string{{"message": "Invalid image"}},
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

	// Create a temp file
	tmpFile, _ := os.CreateTemp("", "test-*.png")
	tmpFile.WriteString("fake image data")
	tmpFile.Close()
	defer os.Remove(tmpFile.Name())

	cmd := newTestRootCmd()
	_, _, err := executeCommand(cmd, "image", "upload", tmpFile.Name())

	require.Error(t, err)
}
