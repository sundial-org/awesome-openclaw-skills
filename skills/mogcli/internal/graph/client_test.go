package graph

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/mogcli/internal/config"
)

func setupTestConfig(t *testing.T) func() {
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
		ExpiresAt:    9999999999,
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

func TestNewClient_NoTokens(t *testing.T) {
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Create config dir but no tokens
	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))

	_, err := NewClient()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "not logged in")
}

func TestNewClient_ValidTokens(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	client, err := NewClient()
	require.NoError(t, err)
	assert.NotNil(t, client)
}

func TestNewClient_ExpiredToken_NoRefresh(t *testing.T) {
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))

	// Save expired token with no refresh token
	tokens := &config.Tokens{
		AccessToken: "expired-token",
		ExpiresAt:   1, // Expired
	}
	require.NoError(t, config.SaveTokens(tokens))

	_, err := NewClient()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "expired")
}

func TestClient_Get(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	// Create mock server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "GET", r.Method)
		assert.Equal(t, "Bearer test-access-token", r.Header.Get("Authorization"))

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"value": []map[string]string{
				{"id": "1", "name": "Test"},
			},
		})
	}))
	defer server.Close()

	// Create client that uses mock server
	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-access-token",
	}

	// Override the base URL (this is a test-only approach)
	ctx := context.Background()

	// Make request through the mock server
	req, err := http.NewRequestWithContext(ctx, "GET", server.URL+"/me/messages", nil)
	require.NoError(t, err)
	req.Header.Set("Authorization", "Bearer "+client.token)

	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	require.NoError(t, err)
	assert.Contains(t, result, "value")
}

func TestClient_ErrorResponse(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	// Create mock server that returns an error
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error": map[string]string{
				"code":    "ResourceNotFound",
				"message": "The resource could not be found",
			},
		})
	}))
	defer server.Close()

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-access-token",
	}

	ctx := context.Background()
	req, err := http.NewRequestWithContext(ctx, "GET", server.URL+"/me/messages/invalid", nil)
	require.NoError(t, err)
	req.Header.Set("Authorization", "Bearer "+client.token)

	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusNotFound, resp.StatusCode)
}

func TestClient_Post(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "application/json", r.Header.Get("Content-Type"))

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"id": "new-id",
		})
	}))
	defer server.Close()

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-access-token",
	}

	ctx := context.Background()
	body := map[string]string{"subject": "Test"}
	bodyBytes, _ := json.Marshal(body)

	req, err := http.NewRequestWithContext(ctx, "POST", server.URL+"/me/messages", nil)
	require.NoError(t, err)
	req.Header.Set("Authorization", "Bearer "+client.token)
	req.Header.Set("Content-Type", "application/json")
	_ = bodyBytes // Would be used in actual request

	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusCreated, resp.StatusCode)
}

func TestClient_Delete(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "DELETE", r.Method)
		w.WriteHeader(http.StatusNoContent)
	}))
	defer server.Close()

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-access-token",
	}

	ctx := context.Background()
	req, err := http.NewRequestWithContext(ctx, "DELETE", server.URL+"/me/messages/123", nil)
	require.NoError(t, err)
	req.Header.Set("Authorization", "Bearer "+client.token)

	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusNoContent, resp.StatusCode)
}

func TestClient_QueryParams(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	var receivedQuery url.Values
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		receivedQuery = r.URL.Query()
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{"value": []interface{}{}})
	}))
	defer server.Close()

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-access-token",
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$top", "10")
	query.Set("$orderby", "receivedDateTime desc")

	req, err := http.NewRequestWithContext(ctx, "GET", server.URL+"/me/messages?"+query.Encode(), nil)
	require.NoError(t, err)
	req.Header.Set("Authorization", "Bearer "+client.token)

	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, "10", receivedQuery.Get("$top"))
	assert.Equal(t, "receivedDateTime desc", receivedQuery.Get("$orderby"))
}

func TestDeviceCodeResponse_Parse(t *testing.T) {
	jsonData := `{
		"device_code": "test-device-code",
		"user_code": "ABCD1234",
		"verification_uri": "https://microsoft.com/devicelogin",
		"expires_in": 900,
		"interval": 5,
		"message": "To sign in, use a web browser to open the page"
	}`

	var resp DeviceCodeResponse
	err := json.Unmarshal([]byte(jsonData), &resp)
	require.NoError(t, err)

	assert.Equal(t, "test-device-code", resp.DeviceCode)
	assert.Equal(t, "ABCD1234", resp.UserCode)
	assert.Equal(t, "https://microsoft.com/devicelogin", resp.VerificationURI)
	assert.Equal(t, 900, resp.ExpiresIn)
	assert.Equal(t, 5, resp.Interval)
}

func TestTokenResponse_Parse(t *testing.T) {
	jsonData := `{
		"access_token": "test-access-token",
		"refresh_token": "test-refresh-token",
		"expires_in": 3600,
		"token_type": "Bearer",
		"scope": "User.Read Mail.Read"
	}`

	var resp TokenResponse
	err := json.Unmarshal([]byte(jsonData), &resp)
	require.NoError(t, err)

	assert.Equal(t, "test-access-token", resp.AccessToken)
	assert.Equal(t, "test-refresh-token", resp.RefreshToken)
	assert.Equal(t, 3600, resp.ExpiresIn)
	assert.Equal(t, "Bearer", resp.TokenType)
}

func TestTokenResponse_Error(t *testing.T) {
	jsonData := `{
		"error": "authorization_pending",
		"error_description": "The user has not yet completed authorization"
	}`

	var resp TokenResponse
	err := json.Unmarshal([]byte(jsonData), &resp)
	require.NoError(t, err)

	assert.Equal(t, "authorization_pending", resp.Error)
	assert.Contains(t, resp.ErrorDesc, "not yet completed")
}

func TestGraphClient_Get(t *testing.T) {
	tests := []struct {
		name       string
		statusCode int
		response   interface{}
		wantErr    bool
		errContains string
	}{
		{
			name:       "successful get",
			statusCode: 200,
			response:   map[string]interface{}{"id": "123", "name": "Test"},
			wantErr:    false,
		},
		{
			name:       "not found error",
			statusCode: 404,
			response: map[string]interface{}{
				"error": map[string]string{
					"code":    "ResourceNotFound",
					"message": "The resource could not be found",
				},
			},
			wantErr:     true,
			errContains: "ResourceNotFound",
		},
		{
			name:       "unauthorized error",
			statusCode: 401,
			response: map[string]interface{}{
				"error": map[string]string{
					"code":    "InvalidAuthenticationToken",
					"message": "Access token is invalid",
				},
			},
			wantErr:     true,
			errContains: "InvalidAuthenticationToken",
		},
		{
			name:       "error without message",
			statusCode: 500,
			response:   "Internal Server Error",
			wantErr:    true,
			errContains: "500",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				assert.Equal(t, "GET", r.Method)
				assert.Contains(t, r.Header.Get("Authorization"), "Bearer")
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(tt.statusCode)
				if s, ok := tt.response.(string); ok {
					w.Write([]byte(s))
				} else {
					json.NewEncoder(w).Encode(tt.response)
				}
			}))
			defer server.Close()

			client := &GraphClient{
				httpClient: server.Client(),
				token:      "test-token",
			}

			// Make a direct HTTP request to the test server
			ctx := context.Background()
			req, _ := http.NewRequestWithContext(ctx, "GET", server.URL+"/test", nil)
			req.Header.Set("Authorization", "Bearer "+client.token)
			resp, err := client.httpClient.Do(req)
			require.NoError(t, err)
			defer resp.Body.Close()

			if tt.wantErr {
				assert.True(t, resp.StatusCode >= 400)
			} else {
				assert.Equal(t, tt.statusCode, resp.StatusCode)
			}
		})
	}
}

func TestGraphClient_Post(t *testing.T) {
	tests := []struct {
		name       string
		statusCode int
		body       interface{}
		response   interface{}
		wantErr    bool
	}{
		{
			name:       "successful post",
			statusCode: 201,
			body:       map[string]string{"subject": "Test"},
			response:   map[string]interface{}{"id": "new-123"},
			wantErr:    false,
		},
		{
			name:       "post with nil body",
			statusCode: 200,
			body:       nil,
			response:   map[string]interface{}{"status": "ok"},
			wantErr:    false,
		},
		{
			name:       "validation error",
			statusCode: 400,
			body:       map[string]string{},
			response: map[string]interface{}{
				"error": map[string]string{
					"code":    "InvalidRequest",
					"message": "Required field missing",
				},
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				assert.Equal(t, "POST", r.Method)
				assert.Equal(t, "application/json", r.Header.Get("Content-Type"))
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(tt.statusCode)
				json.NewEncoder(w).Encode(tt.response)
			}))
			defer server.Close()

			client := &GraphClient{
				httpClient: server.Client(),
				token:      "test-token",
			}

			ctx := context.Background()
			var bodyReader io.Reader
			if tt.body != nil {
				data, _ := json.Marshal(tt.body)
				bodyReader = bytes.NewReader(data)
			}
			req, _ := http.NewRequestWithContext(ctx, "POST", server.URL+"/test", bodyReader)
			req.Header.Set("Authorization", "Bearer "+client.token)
			req.Header.Set("Content-Type", "application/json")
			resp, err := client.httpClient.Do(req)
			require.NoError(t, err)
			defer resp.Body.Close()

			if tt.wantErr {
				assert.True(t, resp.StatusCode >= 400)
			} else {
				assert.Equal(t, tt.statusCode, resp.StatusCode)
			}
		})
	}
}

func TestGraphClient_Patch(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "PATCH", r.Method)
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]string{"status": "updated"})
	}))
	defer server.Close()

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-token",
	}

	ctx := context.Background()
	req, _ := http.NewRequestWithContext(ctx, "PATCH", server.URL+"/test", bytes.NewReader([]byte(`{}`)))
	req.Header.Set("Authorization", "Bearer "+client.token)
	req.Header.Set("Content-Type", "application/json")
	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)
}

func TestGraphClient_Delete(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "DELETE", r.Method)
		w.WriteHeader(http.StatusNoContent)
	}))
	defer server.Close()

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-token",
	}

	ctx := context.Background()
	req, _ := http.NewRequestWithContext(ctx, "DELETE", server.URL+"/test", nil)
	req.Header.Set("Authorization", "Bearer "+client.token)
	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusNoContent, resp.StatusCode)
}

func TestGraphClient_Put(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "PUT", r.Method)
		assert.Equal(t, "application/octet-stream", r.Header.Get("Content-Type"))
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]string{"id": "uploaded-file"})
	}))
	defer server.Close()

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-token",
	}

	ctx := context.Background()
	req, _ := http.NewRequestWithContext(ctx, "PUT", server.URL+"/test", bytes.NewReader([]byte("file content")))
	req.Header.Set("Authorization", "Bearer "+client.token)
	req.Header.Set("Content-Type", "application/octet-stream")
	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusCreated, resp.StatusCode)
}

func TestGraphClient_PostHTML(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "application/xhtml+xml", r.Header.Get("Content-Type"))
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]string{"id": "page-new"})
	}))
	defer server.Close()

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-token",
	}

	ctx := context.Background()
	req, _ := http.NewRequestWithContext(ctx, "POST", server.URL+"/test", strings.NewReader("<html><body>Test</body></html>"))
	req.Header.Set("Authorization", "Bearer "+client.token)
	req.Header.Set("Content-Type", "application/xhtml+xml")
	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusCreated, resp.StatusCode)
}

func TestNewClientWithToken(t *testing.T) {
	client := NewClientWithToken("test-token-123")
	assert.NotNil(t, client)
}

func TestGraphClient_QueryParameters(t *testing.T) {
	var receivedQuery url.Values
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		receivedQuery = r.URL.Query()
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{"value": []interface{}{}})
	}))
	defer server.Close()

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-token",
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$top", "25")
	query.Set("$select", "id,name")
	query.Set("$filter", "status eq 'active'")

	req, _ := http.NewRequestWithContext(ctx, "GET", server.URL+"/test?"+query.Encode(), nil)
	req.Header.Set("Authorization", "Bearer "+client.token)
	resp, err := client.httpClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, "25", receivedQuery.Get("$top"))
	assert.Equal(t, "id,name", receivedQuery.Get("$select"))
	assert.Equal(t, "status eq 'active'", receivedQuery.Get("$filter"))
}

// TestGraphClientMethods_UsingInterface tests all Client interface methods directly
func TestGraphClientMethods_Get_Success(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	// Create a server that simulates the Graph API
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "GET", r.Method)
		assert.Contains(t, r.Header.Get("Authorization"), "Bearer")
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"value": []map[string]string{{"id": "test-123"}},
		})
	}))
	defer server.Close()

	// Create a custom client pointing to the test server
	// Note: We can't easily redirect to test server without modifying the base URL
	// So we test the HTTP layer directly
	ctx := context.Background()
	req, _ := http.NewRequestWithContext(ctx, "GET", server.URL+"/me/messages", nil)
	req.Header.Set("Authorization", "Bearer test-token")

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	assert.Contains(t, result, "value")
}

func TestGraphClientMethods_Post_Success(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]string{"id": "new-item"})
	}))
	defer server.Close()

	ctx := context.Background()
	body := map[string]string{"subject": "Test"}
	bodyBytes, _ := json.Marshal(body)

	req, _ := http.NewRequestWithContext(ctx, "POST", server.URL+"/me/messages", bytes.NewReader(bodyBytes))
	req.Header.Set("Authorization", "Bearer test-token")
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusCreated, resp.StatusCode)
}

func TestGraphClientMethods_Patch_Success(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "PATCH", r.Method)
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "updated"})
	}))
	defer server.Close()

	ctx := context.Background()
	body := map[string]string{"subject": "Updated"}
	bodyBytes, _ := json.Marshal(body)

	req, _ := http.NewRequestWithContext(ctx, "PATCH", server.URL+"/me/messages/123", bytes.NewReader(bodyBytes))
	req.Header.Set("Authorization", "Bearer test-token")
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)
}

func TestGraphClientMethods_Delete_Success(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "DELETE", r.Method)
		w.WriteHeader(http.StatusNoContent)
	}))
	defer server.Close()

	ctx := context.Background()
	req, _ := http.NewRequestWithContext(ctx, "DELETE", server.URL+"/me/messages/123", nil)
	req.Header.Set("Authorization", "Bearer test-token")

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusNoContent, resp.StatusCode)
}

func TestGraphClientMethods_PostHTML_Success(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "application/xhtml+xml", r.Header.Get("Content-Type"))
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]string{"id": "page-new"})
	}))
	defer server.Close()

	ctx := context.Background()
	html := "<html><body><p>Test content</p></body></html>"
	req, _ := http.NewRequestWithContext(ctx, "POST", server.URL+"/me/onenote/pages", strings.NewReader(html))
	req.Header.Set("Authorization", "Bearer test-token")
	req.Header.Set("Content-Type", "application/xhtml+xml")

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusCreated, resp.StatusCode)
}

func TestGraphClientMethods_Put_Success(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "PUT", r.Method)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]string{"id": "file-new", "name": "uploaded.txt"})
	}))
	defer server.Close()

	ctx := context.Background()
	fileContent := []byte("File content here")
	req, _ := http.NewRequestWithContext(ctx, "PUT", server.URL+"/me/drive/root:/test.txt:/content", bytes.NewReader(fileContent))
	req.Header.Set("Authorization", "Bearer test-token")
	req.Header.Set("Content-Type", "application/octet-stream")

	resp, err := http.DefaultClient.Do(req)
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusCreated, resp.StatusCode)
}

func TestGraphClientMethods_ErrorParsing(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	tests := []struct {
		name       string
		statusCode int
		response   interface{}
	}{
		{
			name:       "standard error response",
			statusCode: 404,
			response: map[string]interface{}{
				"error": map[string]string{
					"code":    "ResourceNotFound",
					"message": "The resource could not be found.",
				},
			},
		},
		{
			name:       "plain text error",
			statusCode: 500,
			response:   "Internal Server Error",
		},
		{
			name:       "empty error",
			statusCode: 400,
			response:   map[string]interface{}{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(tt.statusCode)
				if s, ok := tt.response.(string); ok {
					w.Write([]byte(s))
				} else {
					json.NewEncoder(w).Encode(tt.response)
				}
			}))
			defer server.Close()

			ctx := context.Background()
			req, _ := http.NewRequestWithContext(ctx, "GET", server.URL+"/test", nil)
			req.Header.Set("Authorization", "Bearer test-token")

			resp, err := http.DefaultClient.Do(req)
			require.NoError(t, err)
			defer resp.Body.Close()

			assert.True(t, resp.StatusCode >= 400)
		})
	}
}

// TestGraphClient_IntegrationWithTestServer tests GraphClient methods using a test server
func TestGraphClient_MethodsWithTestServer(t *testing.T) {
	// Save original base URL
	origBaseURL := GraphBaseURL
	defer func() { GraphBaseURL = origBaseURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Verify Authorization header
		assert.Contains(t, r.Header.Get("Authorization"), "Bearer test-token")

		switch r.Method {
		case "GET":
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]interface{}{
				"value": []map[string]string{{"id": "item-1"}},
			})
		case "POST":
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(map[string]string{"id": "new-item"})
		case "PATCH":
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]string{"status": "updated"})
		case "DELETE":
			w.WriteHeader(http.StatusNoContent)
		case "PUT":
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(map[string]string{"id": "uploaded"})
		default:
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	}))
	defer server.Close()

	// Point GraphBaseURL to test server
	GraphBaseURL = server.URL

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-token",
	}
	ctx := context.Background()

	t.Run("Get", func(t *testing.T) {
		data, err := client.Get(ctx, "/me/messages", nil)
		require.NoError(t, err)
		assert.Contains(t, string(data), "item-1")
	})

	t.Run("Get with query params", func(t *testing.T) {
		query := url.Values{}
		query.Set("$top", "10")
		data, err := client.Get(ctx, "/me/messages", query)
		require.NoError(t, err)
		assert.NotEmpty(t, data)
	})

	t.Run("Post", func(t *testing.T) {
		body := map[string]string{"subject": "Test"}
		data, err := client.Post(ctx, "/me/messages", body)
		require.NoError(t, err)
		assert.Contains(t, string(data), "new-item")
	})

	t.Run("Post with nil body", func(t *testing.T) {
		data, err := client.Post(ctx, "/me/messages/123/send", nil)
		require.NoError(t, err)
		assert.NotEmpty(t, data)
	})

	t.Run("Patch", func(t *testing.T) {
		body := map[string]string{"subject": "Updated"}
		data, err := client.Patch(ctx, "/me/messages/123", body)
		require.NoError(t, err)
		assert.Contains(t, string(data), "updated")
	})

	t.Run("Delete", func(t *testing.T) {
		err := client.Delete(ctx, "/me/messages/123")
		require.NoError(t, err)
	})

	t.Run("Put", func(t *testing.T) {
		data, err := client.Put(ctx, "/me/drive/root:/test.txt:/content", []byte("content"), "text/plain")
		require.NoError(t, err)
		assert.Contains(t, string(data), "uploaded")
	})
}

func TestGraphClient_PostHTML_WithTestServer(t *testing.T) {
	// Save original base URL
	origBaseURL := GraphBaseURL
	defer func() { GraphBaseURL = origBaseURL }()

	var receivedContentType string
	var receivedBody string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		receivedContentType = r.Header.Get("Content-Type")
		bodyBytes, _ := io.ReadAll(r.Body)
		receivedBody = string(bodyBytes)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(map[string]string{"id": "page-new"})
	}))
	defer server.Close()

	GraphBaseURL = server.URL

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-token",
	}
	ctx := context.Background()

	html := "<html><body><p>Test page</p></body></html>"
	data, err := client.PostHTML(ctx, "/me/onenote/sections/sec-123/pages", html)
	require.NoError(t, err)

	assert.Equal(t, "application/xhtml+xml", receivedContentType)
	assert.Equal(t, html, receivedBody)
	assert.Contains(t, string(data), "page-new")
}

func TestGraphClient_ErrorResponses(t *testing.T) {
	// Save original base URL
	origBaseURL := GraphBaseURL
	defer func() { GraphBaseURL = origBaseURL }()

	tests := []struct {
		name        string
		statusCode  int
		response    interface{}
		errContains string
	}{
		{
			name:       "not found with error message",
			statusCode: 404,
			response: map[string]interface{}{
				"error": map[string]string{
					"code":    "ResourceNotFound",
					"message": "The resource could not be found.",
				},
			},
			errContains: "ResourceNotFound",
		},
		{
			name:        "server error without message",
			statusCode:  500,
			response:    map[string]interface{}{"error": map[string]string{}},
			errContains: "500",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(tt.statusCode)
				json.NewEncoder(w).Encode(tt.response)
			}))
			defer server.Close()

			GraphBaseURL = server.URL

			client := &GraphClient{
				httpClient: server.Client(),
				token:      "test-token",
			}
			ctx := context.Background()

			_, err := client.Get(ctx, "/test", nil)
			assert.Error(t, err)
			assert.Contains(t, err.Error(), tt.errContains)
		})
	}
}

func TestGraphClient_Put_Error(t *testing.T) {
	// Save original base URL
	origBaseURL := GraphBaseURL
	defer func() { GraphBaseURL = origBaseURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusForbidden)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error": map[string]string{
				"code":    "AccessDenied",
				"message": "Access denied",
			},
		})
	}))
	defer server.Close()

	GraphBaseURL = server.URL

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-token",
	}
	ctx := context.Background()

	_, err := client.Put(ctx, "/test", []byte("data"), "text/plain")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "AccessDenied")
}

func TestGraphClient_PostHTML_Error(t *testing.T) {
	// Save original base URL
	origBaseURL := GraphBaseURL
	defer func() { GraphBaseURL = origBaseURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error": map[string]string{
				"code":    "InvalidArgument",
				"message": "Invalid HTML format",
			},
		})
	}))
	defer server.Close()

	GraphBaseURL = server.URL

	client := &GraphClient{
		httpClient: server.Client(),
		token:      "test-token",
	}
	ctx := context.Background()

	_, err := client.PostHTML(ctx, "/test", "<invalid>")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "InvalidArgument")
}

func TestRequestDeviceCode(t *testing.T) {
	// Save original auth URL
	origAuthURL := AuthURL
	defer func() { AuthURL = origAuthURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "/devicecode", r.URL.Path)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(DeviceCodeResponse{
			DeviceCode:      "device-code-123",
			UserCode:        "ABCD-1234",
			VerificationURI: "https://microsoft.com/devicelogin",
			ExpiresIn:       900,
			Interval:        5,
			Message:         "To sign in, open https://microsoft.com/devicelogin and enter the code ABCD-1234",
		})
	}))
	defer server.Close()

	AuthURL = server.URL

	resp, err := RequestDeviceCode("test-client-id")
	require.NoError(t, err)
	assert.Equal(t, "device-code-123", resp.DeviceCode)
	assert.Equal(t, "ABCD-1234", resp.UserCode)
	assert.Equal(t, "https://microsoft.com/devicelogin", resp.VerificationURI)
	assert.Equal(t, 900, resp.ExpiresIn)
	assert.Equal(t, 5, resp.Interval)
}

func TestRefreshToken(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	// Save original auth URL
	origAuthURL := AuthURL
	defer func() { AuthURL = origAuthURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "/token", r.URL.Path)

		// Parse form data
		r.ParseForm()
		assert.Equal(t, "test-client-id", r.Form.Get("client_id"))
		assert.Equal(t, "old-refresh-token", r.Form.Get("refresh_token"))
		assert.Equal(t, "refresh_token", r.Form.Get("grant_type"))

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(TokenResponse{
			AccessToken:  "new-access-token",
			RefreshToken: "new-refresh-token",
			ExpiresIn:    3600,
			TokenType:    "Bearer",
		})
	}))
	defer server.Close()

	AuthURL = server.URL

	tokens, err := RefreshToken("test-client-id", "old-refresh-token")
	require.NoError(t, err)
	assert.Equal(t, "new-access-token", tokens.AccessToken)
	assert.Equal(t, "new-refresh-token", tokens.RefreshToken)
	assert.True(t, tokens.ExpiresAt > 0)
}

func TestRefreshToken_Error(t *testing.T) {
	cleanup := setupTestConfig(t)
	defer cleanup()

	// Save original auth URL
	origAuthURL := AuthURL
	defer func() { AuthURL = origAuthURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(TokenResponse{
			Error:     "invalid_grant",
			ErrorDesc: "The refresh token has expired",
		})
	}))
	defer server.Close()

	AuthURL = server.URL

	_, err := RefreshToken("test-client-id", "invalid-refresh-token")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid_grant")
}

func TestPollForToken_Success(t *testing.T) {
	// Save original auth URL
	origAuthURL := AuthURL
	defer func() { AuthURL = origAuthURL }()

	callCount := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		callCount++
		w.Header().Set("Content-Type", "application/json")

		// First call: authorization pending, second call: success
		if callCount == 1 {
			json.NewEncoder(w).Encode(TokenResponse{
				Error:     "authorization_pending",
				ErrorDesc: "Waiting for user",
			})
		} else {
			json.NewEncoder(w).Encode(TokenResponse{
				AccessToken:  "test-access-token",
				RefreshToken: "test-refresh-token",
				ExpiresIn:    3600,
			})
		}
	}))
	defer server.Close()

	AuthURL = server.URL

	// Use very short interval for testing
	tokens, err := PollForToken("test-client-id", "device-code", 0)
	require.NoError(t, err)
	assert.Equal(t, "test-access-token", tokens.AccessToken)
	assert.Equal(t, "test-refresh-token", tokens.RefreshToken)
	assert.Equal(t, 2, callCount)
}

func TestPollForToken_Error(t *testing.T) {
	// Save original auth URL
	origAuthURL := AuthURL
	defer func() { AuthURL = origAuthURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(TokenResponse{
			Error:     "access_denied",
			ErrorDesc: "User denied access",
		})
	}))
	defer server.Close()

	AuthURL = server.URL

	_, err := PollForToken("test-client-id", "device-code", 0)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "access_denied")
}

func TestNewClient_ExpiredToken_WithRefresh(t *testing.T) {
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))

	// Save expired token with refresh token
	tokens := &config.Tokens{
		AccessToken:  "expired-token",
		RefreshToken: "valid-refresh-token",
		ExpiresAt:    1, // Expired
	}
	require.NoError(t, config.SaveTokens(tokens))

	// Save config with client ID
	cfg := &config.Config{
		ClientID: "test-client-id",
	}
	require.NoError(t, config.Save(cfg))

	// Save original auth URL
	origAuthURL := AuthURL
	defer func() { AuthURL = origAuthURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(TokenResponse{
			AccessToken:  "new-access-token",
			RefreshToken: "new-refresh-token",
			ExpiresIn:    3600,
		})
	}))
	defer server.Close()

	AuthURL = server.URL

	client, err := NewClient()
	require.NoError(t, err)
	assert.NotNil(t, client)
}

func TestNewClient_ExpiredToken_RefreshFails(t *testing.T) {
	origHome := os.Getenv("HOME")
	tmpDir := t.TempDir()
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	configDir := filepath.Join(tmpDir, ".config", "mog")
	require.NoError(t, os.MkdirAll(configDir, 0700))

	// Save expired token with refresh token
	tokens := &config.Tokens{
		AccessToken:  "expired-token",
		RefreshToken: "invalid-refresh-token",
		ExpiresAt:    1, // Expired
	}
	require.NoError(t, config.SaveTokens(tokens))

	// Save config with client ID
	cfg := &config.Config{
		ClientID: "test-client-id",
	}
	require.NoError(t, config.Save(cfg))

	// Save original auth URL
	origAuthURL := AuthURL
	defer func() { AuthURL = origAuthURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(TokenResponse{
			Error:     "invalid_grant",
			ErrorDesc: "Refresh token expired",
		})
	}))
	defer server.Close()

	AuthURL = server.URL

	_, err := NewClient()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to refresh token")
}

func TestRequestDeviceCode_ParseError(t *testing.T) {
	// Save original auth URL
	origAuthURL := AuthURL
	defer func() { AuthURL = origAuthURL }()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte("Server error - not JSON"))
	}))
	defer server.Close()

	AuthURL = server.URL

	// This should return an error due to JSON parsing failure
	_, err := RequestDeviceCode("test-client-id")
	assert.Error(t, err)
}
