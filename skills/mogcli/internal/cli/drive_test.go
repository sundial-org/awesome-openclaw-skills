package cli

import (
	"context"
	"encoding/json"
	"errors"
	"net/url"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/mogcli/internal/testutil"
)

func TestDriveLsCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *DriveLsCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list root",
			cmd:  &DriveLsCmd{},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":   "file-123",
						"name": "Document.docx",
						"size": 1024,
					},
					{
						"id":     "folder-456",
						"name":   "Projects",
						"folder": map[string]int{"childCount": 5},
					},
				},
			}),
			wantInOut: "Document.docx",
		},
		{
			name: "list with path",
			cmd:  &DriveLsCmd{Path: "Documents"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "file-123", "name": "File.txt", "size": 512},
				},
			}),
			wantInOut: "File.txt",
		},
		{
			name: "list with ID (long path)",
			cmd:  &DriveLsCmd{Path: "01234567890123456789012345"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
		},
		{
			name: "JSON output",
			cmd:  &DriveLsCmd{},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "file-123", "name": "File.txt"},
				},
			}),
			wantInOut: `"name": "File.txt"`,
		},
		{
			name:    "API error",
			cmd:     &DriveLsCmd{},
			root:    &Root{},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
					return tt.mockResp, tt.mockErr
				},
			}
			tt.root.ClientFactory = mockClientFactory(mock)

			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = tt.cmd.Run(tt.root)
			})

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tt.wantInOut != "" {
					assert.Contains(t, output, tt.wantInOut)
				}
			}
		})
	}
}

func TestDriveSearchCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *DriveSearchCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful search",
			cmd:  &DriveSearchCmd{Query: "report", Max: 25},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "file-123", "name": "Report.docx", "size": 2048},
				},
			}),
			wantInOut: "Report.docx",
		},
		{
			name: "search with JSON output",
			cmd:  &DriveSearchCmd{Query: "test", Max: 25},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "file-123", "name": "Test.txt"},
				},
			}),
			wantInOut: `"name": "Test.txt"`,
		},
		{
			name:    "API error",
			cmd:     &DriveSearchCmd{Query: "test", Max: 25},
			root:    &Root{},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
					return tt.mockResp, tt.mockErr
				},
			}
			tt.root.ClientFactory = mockClientFactory(mock)

			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = tt.cmd.Run(tt.root)
			})

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tt.wantInOut != "" {
					assert.Contains(t, output, tt.wantInOut)
				}
			}
		})
	}
}

func TestDriveGetCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *DriveGetCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful get",
			cmd:  &DriveGetCmd{ID: "file-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":                   "file-123",
				"name":                 "Document.docx",
				"size":                 4096,
				"createdDateTime":      "2024-01-15T10:00:00Z",
				"lastModifiedDateTime": "2024-01-20T15:30:00Z",
				"webUrl":               "https://onedrive.com/file",
			}),
			wantInOut: "Document.docx",
		},
		{
			name: "get with JSON output",
			cmd:  &DriveGetCmd{ID: "file-123"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-123",
				"name": "File.txt",
			}),
			wantInOut: `"name": "File.txt"`,
		},
		{
			name:    "file not found",
			cmd:     &DriveGetCmd{ID: "invalid"},
			root:    &Root{},
			mockErr: errors.New("ResourceNotFound"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
					return tt.mockResp, tt.mockErr
				},
			}
			tt.root.ClientFactory = mockClientFactory(mock)

			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = tt.cmd.Run(tt.root)
			})

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tt.wantInOut != "" {
					assert.Contains(t, output, tt.wantInOut)
				}
			}
		})
	}
}

func TestDriveDownloadCmd_Run(t *testing.T) {
	tmpDir := t.TempDir()
	outFile := filepath.Join(tmpDir, "downloaded.txt")

	mock := &testutil.MockClient{
		GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
			return []byte("File content"), nil
		},
	}
	root := &Root{ClientFactory: mockClientFactory(mock)}

	cmd := &DriveDownloadCmd{
		ID:  "file-123",
		Out: outFile,
	}

	output := captureOutput(func() {
		err := cmd.Run(root)
		require.NoError(t, err)
	})

	assert.Contains(t, output, "Downloaded")
	assert.FileExists(t, outFile)
	content, _ := os.ReadFile(outFile)
	assert.Equal(t, "File content", string(content))
}

func TestDriveDownloadCmd_APIError(t *testing.T) {
	mock := &testutil.MockClient{
		GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
			return nil, errors.New("API error")
		},
	}
	root := &Root{ClientFactory: mockClientFactory(mock)}

	cmd := &DriveDownloadCmd{
		ID:  "file-123",
		Out: "/tmp/out.txt",
	}

	err := cmd.Run(root)
	assert.Error(t, err)
}

func TestDriveUploadCmd_Run(t *testing.T) {
	tmpDir := t.TempDir()
	srcFile := filepath.Join(tmpDir, "upload.txt")
	require.NoError(t, os.WriteFile(srcFile, []byte("Upload content"), 0644))

	tests := []struct {
		name      string
		cmd       *DriveUploadCmd
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful upload",
			cmd:  &DriveUploadCmd{Path: srcFile},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new-123",
				"name": "upload.txt",
			}),
			wantInOut: "Uploaded",
		},
		{
			name: "upload with custom name",
			cmd:  &DriveUploadCmd{Path: srcFile, Name: "renamed.txt"},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new-123",
				"name": "renamed.txt",
			}),
			wantInOut: "Uploaded",
		},
		{
			name: "upload to folder",
			cmd:  &DriveUploadCmd{Path: srcFile, Folder: "folder-123"},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new-123",
				"name": "upload.txt",
			}),
			wantInOut: "Uploaded",
		},
		{
			name:    "file not found",
			cmd:     &DriveUploadCmd{Path: "/nonexistent/file.txt"},
			wantErr: true,
		},
		{
			name:    "API error",
			cmd:     &DriveUploadCmd{Path: srcFile},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				PutFunc: func(ctx context.Context, path string, data []byte, contentType string) ([]byte, error) {
					return tt.mockResp, tt.mockErr
				},
			}
			root := &Root{ClientFactory: mockClientFactory(mock)}

			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = tt.cmd.Run(root)
			})

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tt.wantInOut != "" {
					assert.Contains(t, output, tt.wantInOut)
				}
			}
		})
	}
}

func TestDriveMkdirCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *DriveMkdirCmd
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful mkdir",
			cmd:  &DriveMkdirCmd{Name: "NewFolder"},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "folder-new-123",
				"name": "NewFolder",
			}),
			wantInOut: "Created folder",
		},
		{
			name: "mkdir with parent",
			cmd:  &DriveMkdirCmd{Name: "SubFolder", Parent: "parent-123"},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "folder-new-456",
				"name": "SubFolder",
			}),
			wantInOut: "Created folder",
		},
		{
			name:    "API error",
			cmd:     &DriveMkdirCmd{Name: "Folder"},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				PostFunc: func(ctx context.Context, path string, body interface{}) ([]byte, error) {
					return tt.mockResp, tt.mockErr
				},
			}
			root := &Root{ClientFactory: mockClientFactory(mock)}

			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = tt.cmd.Run(root)
			})

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tt.wantInOut != "" {
					assert.Contains(t, output, tt.wantInOut)
				}
			}
		})
	}
}

func TestDriveMoveCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *DriveMoveCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful move",
			cmd:       &DriveMoveCmd{ID: "file-123", Destination: "folder-456"},
			wantInOut: "File moved",
		},
		{
			name:    "API error",
			cmd:     &DriveMoveCmd{ID: "file-123", Destination: "folder-456"},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				PatchFunc: func(ctx context.Context, path string, body interface{}) ([]byte, error) {
					return []byte(`{}`), tt.mockErr
				},
			}
			root := &Root{ClientFactory: mockClientFactory(mock)}

			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = tt.cmd.Run(root)
			})

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tt.wantInOut != "" {
					assert.Contains(t, output, tt.wantInOut)
				}
			}
		})
	}
}

func TestDriveCopyCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *DriveCopyCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful copy",
			cmd:       &DriveCopyCmd{ID: "file-123", Name: "Copy of File.txt"},
			wantInOut: "Copy initiated",
		},
		{
			name:    "API error",
			cmd:     &DriveCopyCmd{ID: "file-123", Name: "Copy"},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				PostFunc: func(ctx context.Context, path string, body interface{}) ([]byte, error) {
					return []byte(`{}`), tt.mockErr
				},
			}
			root := &Root{ClientFactory: mockClientFactory(mock)}

			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = tt.cmd.Run(root)
			})

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tt.wantInOut != "" {
					assert.Contains(t, output, tt.wantInOut)
				}
			}
		})
	}
}

func TestDriveRenameCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *DriveRenameCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful rename",
			cmd:       &DriveRenameCmd{ID: "file-123", Name: "NewName.txt"},
			wantInOut: "Renamed to: NewName.txt",
		},
		{
			name:    "API error",
			cmd:     &DriveRenameCmd{ID: "file-123", Name: "New"},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				PatchFunc: func(ctx context.Context, path string, body interface{}) ([]byte, error) {
					return []byte(`{}`), tt.mockErr
				},
			}
			root := &Root{ClientFactory: mockClientFactory(mock)}

			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = tt.cmd.Run(root)
			})

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tt.wantInOut != "" {
					assert.Contains(t, output, tt.wantInOut)
				}
			}
		})
	}
}

func TestDriveDeleteCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *DriveDeleteCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful delete",
			cmd:       &DriveDeleteCmd{ID: "file-123"},
			wantInOut: "File deleted",
		},
		{
			name:    "API error",
			cmd:     &DriveDeleteCmd{ID: "file-123"},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				DeleteFunc: func(ctx context.Context, path string) error {
					return tt.mockErr
				},
			}
			root := &Root{ClientFactory: mockClientFactory(mock)}

			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = tt.cmd.Run(root)
			})

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tt.wantInOut != "" {
					assert.Contains(t, output, tt.wantInOut)
				}
			}
		})
	}
}

// Test type unmarshaling
func TestDriveItem_Unmarshal(t *testing.T) {
	tests := []struct {
		name string
		json string
		want DriveItem
	}{
		{
			name: "file item",
			json: `{
				"id": "file-123",
				"name": "Document.docx",
				"size": 4096,
				"createdDateTime": "2024-01-15T10:00:00Z",
				"lastModifiedDateTime": "2024-01-20T15:30:00Z",
				"webUrl": "https://onedrive.com/file",
				"file": {"mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
			}`,
			want: DriveItem{ID: "file-123", Name: "Document.docx", Size: 4096},
		},
		{
			name: "folder item",
			json: `{
				"id": "folder-123",
				"name": "Projects",
				"size": 0,
				"folder": {"childCount": 5}
			}`,
			want: DriveItem{ID: "folder-123", Name: "Projects"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var item DriveItem
			err := json.Unmarshal([]byte(tt.json), &item)
			require.NoError(t, err)
			assert.Equal(t, tt.want.ID, item.ID)
			assert.Equal(t, tt.want.Name, item.Name)
		})
	}
}

func TestFormatSize(t *testing.T) {
	tests := []struct {
		bytes    int64
		expected string
	}{
		{0, "0 B"},
		{512, "512 B"},
		{1024, "1.0 KB"},
		{1536, "1.5 KB"},
		{1048576, "1.0 MB"},
		{1073741824, "1.0 GB"},
	}

	for _, tt := range tests {
		t.Run(tt.expected, func(t *testing.T) {
			result := formatSize(tt.bytes)
			assert.Equal(t, tt.expected, result)
		})
	}
}
