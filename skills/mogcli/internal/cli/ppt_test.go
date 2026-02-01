package cli

import (
	"context"
	"errors"
	"net/url"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/mogcli/internal/testutil"
)

func TestPPTListCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *PPTListCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list presentations",
			cmd:  &PPTListCmd{Max: 50},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":                   "file-123",
						"name":                 "Presentation.pptx",
						"size":                 8192,
						"lastModifiedDateTime": "2024-01-15T10:30:00Z",
						"webUrl":               "https://onedrive.com/file",
					},
				},
			}),
			wantInOut: "Presentation.pptx",
		},
		{
			name: "no presentations found",
			cmd:  &PPTListCmd{Max: 50},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
			wantInOut: "No PowerPoint presentations found",
		},
		{
			name: "filters non-pptx files",
			cmd:  &PPTListCmd{Max: 50},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "file-1", "name": "Slides.pptx", "size": 1024, "lastModifiedDateTime": "2024-01-15T10:30:00Z"},
					{"id": "file-2", "name": "Image.pptx.png", "size": 2048, "lastModifiedDateTime": "2024-01-15T10:30:00Z"},
				},
			}),
			wantInOut: "Slides.pptx",
		},
		{
			name: "JSON output",
			cmd:  &PPTListCmd{Max: 50},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "file-123", "name": "Test.pptx"},
				},
			}),
			wantInOut: `"name": "Test.pptx"`,
		},
		{
			name:    "API error",
			cmd:     &PPTListCmd{Max: 50},
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

func TestPPTGetCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *PPTGetCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful get presentation",
			cmd:  &PPTGetCmd{ID: "file-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":                   "file-123",
				"name":                 "Presentation.pptx",
				"size":                 8192,
				"createdDateTime":      "2024-01-10T08:00:00Z",
				"lastModifiedDateTime": "2024-01-15T10:30:00Z",
				"webUrl":               "https://onedrive.com/file",
			}),
			wantInOut: "Presentation.pptx",
		},
		{
			name: "JSON output",
			cmd:  &PPTGetCmd{ID: "file-123"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-123",
				"name": "Test.pptx",
			}),
			wantInOut: `"name": "Test.pptx"`,
		},
		{
			name:    "presentation not found",
			cmd:     &PPTGetCmd{ID: "invalid"},
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

func TestPPTExportCmd_Run(t *testing.T) {
	tmpDir := t.TempDir()

	t.Run("export pptx", func(t *testing.T) {
		outFile := filepath.Join(tmpDir, "export.pptx")
		mock := &testutil.MockClient{
			GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
				return []byte("pptx content"), nil
			},
		}
		root := &Root{ClientFactory: mockClientFactory(mock)}
		cmd := &PPTExportCmd{ID: "file-123", Out: outFile, Format: "pptx"}

		output := captureOutput(func() {
			err := cmd.Run(root)
			require.NoError(t, err)
		})

		assert.Contains(t, output, "Exported")
		assert.FileExists(t, outFile)
	})

	t.Run("export pdf", func(t *testing.T) {
		outFile := filepath.Join(tmpDir, "export.pdf")
		mock := &testutil.MockClient{
			GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
				return []byte("pdf content"), nil
			},
		}
		root := &Root{ClientFactory: mockClientFactory(mock)}
		cmd := &PPTExportCmd{ID: "file-123", Out: outFile, Format: "pdf"}

		output := captureOutput(func() {
			err := cmd.Run(root)
			require.NoError(t, err)
		})

		assert.Contains(t, output, "Exported")
		assert.Contains(t, output, "PDF")
	})

	t.Run("JSON output", func(t *testing.T) {
		outFile := filepath.Join(tmpDir, "export2.pptx")
		mock := &testutil.MockClient{
			GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
				return []byte("content"), nil
			},
		}
		root := &Root{JSON: true, ClientFactory: mockClientFactory(mock)}
		cmd := &PPTExportCmd{ID: "file-123", Out: outFile, Format: "pptx"}

		output := captureOutput(func() {
			err := cmd.Run(root)
			require.NoError(t, err)
		})

		assert.Contains(t, output, `"success": true`)
	})

	t.Run("API error", func(t *testing.T) {
		mock := &testutil.MockClient{
			GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
				return nil, errors.New("API error")
			},
		}
		root := &Root{ClientFactory: mockClientFactory(mock)}
		cmd := &PPTExportCmd{ID: "file-123", Out: "/tmp/out.pptx", Format: "pptx"}

		err := cmd.Run(root)
		assert.Error(t, err)
	})
}

func TestPPTCopyCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *PPTCopyCmd
		root      *Root
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful copy",
			cmd:       &PPTCopyCmd{ID: "file-123", Name: "Copy.pptx"},
			root:      &Root{},
			wantInOut: "Copy initiated",
		},
		{
			name:      "copy with folder",
			cmd:       &PPTCopyCmd{ID: "file-123", Name: "Copy.pptx", Folder: "folder-123"},
			root:      &Root{},
			wantInOut: "Copy initiated",
		},
		{
			name: "JSON output",
			cmd:  &PPTCopyCmd{ID: "file-123", Name: "Copy.pptx"},
			root: &Root{JSON: true},
			wantInOut: `"success": true`,
		},
		{
			name:    "API error",
			cmd:     &PPTCopyCmd{ID: "file-123", Name: "Copy.pptx"},
			root:    &Root{},
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

func TestPPTCreateCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *PPTCreateCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful create",
			cmd:  &PPTCreateCmd{Name: "NewPresentation"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new-123",
				"name": "NewPresentation.pptx",
			}),
			wantInOut: "Presentation created",
		},
		{
			name: "create with .pptx extension",
			cmd:  &PPTCreateCmd{Name: "Test.pptx"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new-456",
				"name": "Test.pptx",
			}),
			wantInOut: "Presentation created",
		},
		{
			name: "create in folder",
			cmd:  &PPTCreateCmd{Name: "FolderPPT", Folder: "folder-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new-789",
				"name": "FolderPPT.pptx",
			}),
			wantInOut: "Presentation created",
		},
		{
			name: "JSON output",
			cmd:  &PPTCreateCmd{Name: "Test"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new",
				"name": "Test.pptx",
			}),
			wantInOut: `"name": "Test.pptx"`,
		},
		{
			name:    "API error",
			cmd:     &PPTCreateCmd{Name: "Fail"},
			root:    &Root{},
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
