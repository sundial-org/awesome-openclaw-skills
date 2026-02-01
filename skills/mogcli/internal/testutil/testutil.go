// Package testutil provides testing utilities for mogcli.
package testutil

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/visionik/mogcli/internal/config"
)

// MockResponse represents a mock API response.
type MockResponse struct {
	StatusCode int
	Body       interface{}
	Headers    map[string]string
}

// MockServer creates a test server that returns predefined responses.
type MockServer struct {
	*httptest.Server
	Responses map[string]MockResponse
	Requests  []RecordedRequest
}

// RecordedRequest stores details of a request made to the mock server.
type RecordedRequest struct {
	Method string
	Path   string
	Body   []byte
}

// NewMockServer creates a new mock server with the given responses.
// The responses map uses the format "METHOD /path" as keys.
func NewMockServer(responses map[string]MockResponse) *MockServer {
	ms := &MockServer{
		Responses: responses,
		Requests:  []RecordedRequest{},
	}

	ms.Server = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Record the request
		var body []byte
		if r.Body != nil {
			body, _ = readBody(r)
		}
		ms.Requests = append(ms.Requests, RecordedRequest{
			Method: r.Method,
			Path:   r.URL.Path,
			Body:   body,
		})

		// Look for a matching response
		key := r.Method + " " + r.URL.Path
		resp, ok := ms.Responses[key]
		if !ok {
			// Try without query params
			key = r.Method + " " + r.URL.Path
			resp, ok = ms.Responses[key]
		}
		if !ok {
			w.WriteHeader(http.StatusNotFound)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"error": map[string]string{
					"code":    "NotFound",
					"message": "No mock response for " + key,
				},
			})
			return
		}

		// Set headers
		w.Header().Set("Content-Type", "application/json")
		for k, v := range resp.Headers {
			w.Header().Set(k, v)
		}

		// Set status code
		if resp.StatusCode == 0 {
			resp.StatusCode = http.StatusOK
		}
		w.WriteHeader(resp.StatusCode)

		// Write body
		if resp.Body != nil {
			json.NewEncoder(w).Encode(resp.Body)
		}
	}))

	return ms
}

func readBody(r *http.Request) ([]byte, error) {
	if r.Body == nil {
		return nil, nil
	}
	defer r.Body.Close()
	return nil, nil // Simplified for now
}

// SetupTestConfig creates a temporary config directory with valid tokens.
func SetupTestConfig(t *testing.T) (cleanup func()) {
	t.Helper()

	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)

	// Create config directory
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))

	// Save test tokens (expires far in the future)
	tokens := &config.Tokens{
		AccessToken:  "test-access-token",
		RefreshToken: "test-refresh-token",
		ExpiresAt:    9999999999, // Far future
	}
	require.NoError(t, config.SaveTokens(tokens))

	// Save test config
	cfg := &config.Config{
		ClientID: "test-client-id-12345678901234567890",
	}
	require.NoError(t, config.Save(cfg))

	return func() {
		os.Setenv("HOME", origHome)
	}
}

// GraphValueResponse creates a standard Graph API value response.
func GraphValueResponse(items interface{}) map[string]interface{} {
	return map[string]interface{}{
		"value": items,
	}
}

// GraphErrorResponse creates a standard Graph API error response.
func GraphErrorResponse(code, message string) map[string]interface{} {
	return map[string]interface{}{
		"error": map[string]string{
			"code":    code,
			"message": message,
		},
	}
}
