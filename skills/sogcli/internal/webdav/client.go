// Package webdav provides a WebDAV client for file operations.
package webdav

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"path"
	"strings"
	"time"

	"github.com/emersion/go-webdav"
)

// Client wraps a WebDAV client with convenience methods.
type Client struct {
	client *webdav.Client
	url    string
}

// Config holds WebDAV connection configuration.
type Config struct {
	URL      string // WebDAV server URL
	Email    string // Account email (for auth)
	Password string // Account password
}

// FileInfo represents file/folder metadata.
type FileInfo struct {
	Path        string    `json:"path"`
	Name        string    `json:"name"`
	IsDir       bool      `json:"is_dir"`
	Size        int64     `json:"size,omitempty"`
	ContentType string    `json:"content_type,omitempty"`
	Modified    time.Time `json:"modified,omitempty"`
	ETag        string    `json:"etag,omitempty"`
}

// Connect establishes a connection to a WebDAV server.
func Connect(cfg Config) (*Client, error) {
	httpClient := webdav.HTTPClientWithBasicAuth(http.DefaultClient, cfg.Email, cfg.Password)

	client, err := webdav.NewClient(httpClient, cfg.URL)
	if err != nil {
		return nil, fmt.Errorf("failed to create WebDAV client: %w", err)
	}

	return &Client{
		client: client,
		url:    cfg.URL,
	}, nil
}

// Close closes the client connection.
func (c *Client) Close() error {
	// WebDAV is stateless HTTP, nothing to close
	return nil
}

// List lists files and folders at a path.
func (c *Client) List(ctx context.Context, remotePath string) ([]FileInfo, error) {
	infos, err := c.client.ReadDir(ctx, remotePath, false)
	if err != nil {
		return nil, fmt.Errorf("failed to list directory: %w", err)
	}

	files := make([]FileInfo, 0, len(infos))
	for _, info := range infos {
		fi := FileInfo{
			Path:     info.Path,
			Name:     path.Base(info.Path),
			IsDir:    info.IsDir,
			Size:     info.Size,
			Modified: info.ModTime,
			ETag:     info.ETag,
		}
		if info.MIMEType != "" {
			fi.ContentType = info.MIMEType
		}
		files = append(files, fi)
	}

	return files, nil
}

// Stat gets info about a single file or folder.
func (c *Client) Stat(ctx context.Context, remotePath string) (*FileInfo, error) {
	info, err := c.client.Stat(ctx, remotePath)
	if err != nil {
		return nil, fmt.Errorf("failed to stat: %w", err)
	}

	return &FileInfo{
		Path:        info.Path,
		Name:        path.Base(info.Path),
		IsDir:       info.IsDir,
		Size:        info.Size,
		ContentType: info.MIMEType,
		Modified:    info.ModTime,
		ETag:        info.ETag,
	}, nil
}

// Download downloads a file to a local path.
func (c *Client) Download(ctx context.Context, remotePath, localPath string) error {
	reader, err := c.client.Open(ctx, remotePath)
	if err != nil {
		return fmt.Errorf("failed to open remote file: %w", err)
	}
	defer reader.Close()

	file, err := os.Create(localPath)
	if err != nil {
		return fmt.Errorf("failed to create local file: %w", err)
	}
	defer file.Close()

	_, err = io.Copy(file, reader)
	if err != nil {
		return fmt.Errorf("failed to download file: %w", err)
	}

	return nil
}

// DownloadToWriter downloads a file to an io.Writer.
func (c *Client) DownloadToWriter(ctx context.Context, remotePath string, w io.Writer) error {
	reader, err := c.client.Open(ctx, remotePath)
	if err != nil {
		return fmt.Errorf("failed to open remote file: %w", err)
	}
	defer reader.Close()

	_, err = io.Copy(w, reader)
	if err != nil {
		return fmt.Errorf("failed to download file: %w", err)
	}

	return nil
}

// Upload uploads a local file to a remote path.
func (c *Client) Upload(ctx context.Context, localPath, remotePath string) error {
	file, err := os.Open(localPath)
	if err != nil {
		return fmt.Errorf("failed to open local file: %w", err)
	}
	defer file.Close()

	writer, err := c.client.Create(ctx, remotePath)
	if err != nil {
		return fmt.Errorf("failed to create remote file: %w", err)
	}
	defer writer.Close()

	_, err = io.Copy(writer, file)
	if err != nil {
		return fmt.Errorf("failed to upload file: %w", err)
	}

	return nil
}

// UploadFromReader uploads from an io.Reader to a remote path.
func (c *Client) UploadFromReader(ctx context.Context, remotePath string, r io.Reader) error {
	writer, err := c.client.Create(ctx, remotePath)
	if err != nil {
		return fmt.Errorf("failed to create remote file: %w", err)
	}
	defer writer.Close()

	_, err = io.Copy(writer, r)
	if err != nil {
		return fmt.Errorf("failed to upload file: %w", err)
	}
	return nil
}

// Mkdir creates a directory.
func (c *Client) Mkdir(ctx context.Context, remotePath string) error {
	err := c.client.Mkdir(ctx, remotePath)
	if err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}
	return nil
}

// Delete deletes a file or directory.
func (c *Client) Delete(ctx context.Context, remotePath string) error {
	err := c.client.RemoveAll(ctx, remotePath)
	if err != nil {
		return fmt.Errorf("failed to delete: %w", err)
	}
	return nil
}

// Move moves/renames a file or directory.
func (c *Client) Move(ctx context.Context, srcPath, dstPath string) error {
	err := c.client.Move(ctx, srcPath, dstPath, nil)
	if err != nil {
		return fmt.Errorf("failed to move: %w", err)
	}
	return nil
}

// Copy copies a file or directory.
func (c *Client) Copy(ctx context.Context, srcPath, dstPath string) error {
	err := c.client.Copy(ctx, srcPath, dstPath, nil)
	if err != nil {
		return fmt.Errorf("failed to copy: %w", err)
	}
	return nil
}

// FormatSize returns a human-readable file size.
func FormatSize(bytes int64) string {
	const unit = 1024
	if bytes < unit {
		return fmt.Sprintf("%d B", bytes)
	}
	div, exp := int64(unit), 0
	for n := bytes / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %cB", float64(bytes)/float64(div), "KMGTPE"[exp])
}

// IsHidden returns true if the file is hidden (starts with .)
func IsHidden(name string) bool {
	return strings.HasPrefix(name, ".")
}
