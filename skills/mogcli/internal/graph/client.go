// Package graph provides a Microsoft Graph API client with OAuth2 authentication
// and automatic token refresh support.
package graph

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/visionik/mogcli/internal/config"
)

var (
	// GraphBaseURL is the base URL for the Microsoft Graph API.
	// It can be overridden for testing.
	GraphBaseURL = "https://graph.microsoft.com/v1.0"
	// AuthURL is the base URL for OAuth2 authentication.
	AuthURL = "https://login.microsoftonline.com/common/oauth2/v2.0"
)

// Client defines the interface for Microsoft Graph API operations.
type Client interface {
	Get(ctx context.Context, path string, query url.Values) ([]byte, error)
	Post(ctx context.Context, path string, body interface{}) ([]byte, error)
	Patch(ctx context.Context, path string, body interface{}) ([]byte, error)
	Delete(ctx context.Context, path string) error
	PostHTML(ctx context.Context, path string, html string) ([]byte, error)
	Put(ctx context.Context, path string, data []byte, contentType string) ([]byte, error)
}

// GraphClient is the concrete implementation of the Client interface.
type GraphClient struct {
	httpClient *http.Client
	token      string
}

// NewClient creates a new Graph client with the stored access token.
// Returns the Client interface for dependency injection support.
func NewClient() (Client, error) {
	tokens, err := config.LoadTokens()
	if err != nil {
		return nil, err
	}

	// Check if token is expired
	expiresAt := tokens.GetExpiresAt()
	if expiresAt > 0 && time.Now().Unix() >= expiresAt {
		// Try to refresh
		cfg, err := config.Load()
		if err != nil {
			return nil, fmt.Errorf("token expired, please login again")
		}
		clientID := cfg.GetClientID()
		if tokens.RefreshToken == "" || clientID == "" {
			return nil, fmt.Errorf("token expired, please login again")
		}

		newTokens, err := RefreshToken(clientID, tokens.RefreshToken)
		if err != nil {
			return nil, fmt.Errorf("failed to refresh token: %w", err)
		}
		tokens = newTokens
	}

	return &GraphClient{
		httpClient: &http.Client{Timeout: 30 * time.Second},
		token:      tokens.AccessToken,
	}, nil
}

// NewClientWithToken creates a new Graph client with a provided token (useful for testing).
func NewClientWithToken(token string) Client {
	return &GraphClient{
		httpClient: &http.Client{Timeout: 30 * time.Second},
		token:      token,
	}
}

// Get performs a GET request to the Graph API.
func (c *GraphClient) Get(ctx context.Context, path string, query url.Values) ([]byte, error) {
	return c.request(ctx, "GET", path, query, nil)
}

// Post performs a POST request to the Graph API.
func (c *GraphClient) Post(ctx context.Context, path string, body interface{}) ([]byte, error) {
	return c.request(ctx, "POST", path, nil, body)
}

// Patch performs a PATCH request to the Graph API.
func (c *GraphClient) Patch(ctx context.Context, path string, body interface{}) ([]byte, error) {
	return c.request(ctx, "PATCH", path, nil, body)
}

// Delete performs a DELETE request to the Graph API.
func (c *GraphClient) Delete(ctx context.Context, path string) error {
	_, err := c.request(ctx, "DELETE", path, nil, nil)
	return err
}

// PostHTML performs a POST request with HTML/XHTML content (for OneNote pages).
func (c *GraphClient) PostHTML(ctx context.Context, path string, html string) ([]byte, error) {
	u := GraphBaseURL + path

	req, err := http.NewRequestWithContext(ctx, "POST", u, strings.NewReader(html))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/xhtml+xml")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		var errResp struct {
			Error struct {
				Code    string `json:"code"`
				Message string `json:"message"`
			} `json:"error"`
		}
		if json.Unmarshal(respBody, &errResp) == nil && errResp.Error.Message != "" {
			return nil, fmt.Errorf("%s: %s", errResp.Error.Code, errResp.Error.Message)
		}
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

// Put performs a PUT request with raw bytes (for file uploads).
func (c *GraphClient) Put(ctx context.Context, path string, data []byte, contentType string) ([]byte, error) {
	u := GraphBaseURL + path

	req, err := http.NewRequestWithContext(ctx, "PUT", u, bytes.NewReader(data))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", contentType)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		var errResp struct {
			Error struct {
				Code    string `json:"code"`
				Message string `json:"message"`
			} `json:"error"`
		}
		if json.Unmarshal(respBody, &errResp) == nil && errResp.Error.Message != "" {
			return nil, fmt.Errorf("%s: %s", errResp.Error.Code, errResp.Error.Message)
		}
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

func (c *GraphClient) request(ctx context.Context, method, path string, query url.Values, body interface{}) ([]byte, error) {
	u := GraphBaseURL + path
	if query != nil && len(query) > 0 {
		u += "?" + query.Encode()
	}

	var bodyReader io.Reader
	if body != nil {
		data, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal body: %w", err)
		}
		bodyReader = bytes.NewReader(data)
	}

	req, err := http.NewRequestWithContext(ctx, method, u, bodyReader)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		var errResp struct {
			Error struct {
				Code    string `json:"code"`
				Message string `json:"message"`
			} `json:"error"`
		}
		if json.Unmarshal(respBody, &errResp) == nil && errResp.Error.Message != "" {
			return nil, fmt.Errorf("%s: %s", errResp.Error.Code, errResp.Error.Message)
		}
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

// DeviceCodeResponse is the response from the device code request.
type DeviceCodeResponse struct {
	DeviceCode      string `json:"device_code"`
	UserCode        string `json:"user_code"`
	VerificationURI string `json:"verification_uri"`
	ExpiresIn       int    `json:"expires_in"`
	Interval        int    `json:"interval"`
	Message         string `json:"message"`
}

// TokenResponse is the response from the token request.
type TokenResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	ExpiresIn    int    `json:"expires_in"`
	TokenType    string `json:"token_type"`
	Scope        string `json:"scope"`
	Error        string `json:"error"`
	ErrorDesc    string `json:"error_description"`
}

// RequestDeviceCode initiates the device code flow.
func RequestDeviceCode(clientID string) (*DeviceCodeResponse, error) {
	scopes := []string{
		"User.Read",
		"offline_access",
		"Mail.ReadWrite",
		"Mail.Send",
		"Calendars.ReadWrite",
		"Files.ReadWrite.All",
		"Contacts.ReadWrite",
		"Tasks.ReadWrite",
		"Notes.ReadWrite",
	}

	data := url.Values{}
	data.Set("client_id", clientID)
	data.Set("scope", strings.Join(scopes, " "))

	resp, err := http.PostForm(AuthURL+"/devicecode", data)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var dcResp DeviceCodeResponse
	if err := json.Unmarshal(body, &dcResp); err != nil {
		return nil, err
	}

	return &dcResp, nil
}

// PollForToken polls for the token after device code auth.
func PollForToken(clientID, deviceCode string, interval int) (*config.Tokens, error) {
	data := url.Values{}
	data.Set("client_id", clientID)
	data.Set("device_code", deviceCode)
	data.Set("grant_type", "urn:ietf:params:oauth:grant-type:device_code")

	for {
		time.Sleep(time.Duration(interval) * time.Second)

		resp, err := http.PostForm(AuthURL+"/token", data)
		if err != nil {
			return nil, err
		}

		body, err := io.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			return nil, err
		}

		var tokenResp TokenResponse
		if err := json.Unmarshal(body, &tokenResp); err != nil {
			return nil, err
		}

		if tokenResp.Error == "authorization_pending" {
			continue
		}

		if tokenResp.Error != "" {
			return nil, fmt.Errorf("%s: %s", tokenResp.Error, tokenResp.ErrorDesc)
		}

		return &config.Tokens{
			AccessToken:  tokenResp.AccessToken,
			RefreshToken: tokenResp.RefreshToken,
			ExpiresAt:    time.Now().Unix() + int64(tokenResp.ExpiresIn),
		}, nil
	}
}

// RefreshToken refreshes an access token.
func RefreshToken(clientID, refreshToken string) (*config.Tokens, error) {
	data := url.Values{}
	data.Set("client_id", clientID)
	data.Set("refresh_token", refreshToken)
	data.Set("grant_type", "refresh_token")

	resp, err := http.PostForm(AuthURL+"/token", data)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var tokenResp TokenResponse
	if err := json.Unmarshal(body, &tokenResp); err != nil {
		return nil, err
	}

	if tokenResp.Error != "" {
		return nil, fmt.Errorf("%s: %s", tokenResp.Error, tokenResp.ErrorDesc)
	}

	tokens := &config.Tokens{
		AccessToken:  tokenResp.AccessToken,
		RefreshToken: tokenResp.RefreshToken,
		ExpiresAt:    time.Now().Unix() + int64(tokenResp.ExpiresIn),
	}

	// Save the new tokens
	if err := config.SaveTokens(tokens); err != nil {
		return nil, fmt.Errorf("failed to save tokens: %w", err)
	}

	return tokens, nil
}
