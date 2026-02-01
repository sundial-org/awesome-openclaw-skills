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

func TestWordListCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *WordListCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list documents",
			cmd:  &WordListCmd{Max: 50},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":                   "file-123",
						"name":                 "Report.docx",
						"size":                 4096,
						"lastModifiedDateTime": "2024-01-15T10:30:00Z",
						"webUrl":               "https://onedrive.com/file",
					},
				},
			}),
			wantInOut: "Report.docx",
		},
		{
			name: "no documents found",
			cmd:  &WordListCmd{Max: 50},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
			wantInOut: "No Word documents found",
		},
		{
			name: "filters non-docx files",
			cmd:  &WordListCmd{Max: 50},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "file-1", "name": "Report.docx", "size": 1024, "lastModifiedDateTime": "2024-01-15T10:30:00Z"},
					{"id": "file-2", "name": "Image.docx.png", "size": 2048, "lastModifiedDateTime": "2024-01-15T10:30:00Z"},
				},
			}),
			wantInOut: "Report.docx",
		},
		{
			name: "JSON output",
			cmd:  &WordListCmd{Max: 50},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "file-123", "name": "Test.docx"},
				},
			}),
			wantInOut: `"name": "Test.docx"`,
		},
		{
			name:    "API error",
			cmd:     &WordListCmd{Max: 50},
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

func TestWordGetCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *WordGetCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful get document",
			cmd:  &WordGetCmd{ID: "file-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":                   "file-123",
				"name":                 "Document.docx",
				"size":                 4096,
				"createdDateTime":      "2024-01-10T08:00:00Z",
				"lastModifiedDateTime": "2024-01-15T10:30:00Z",
				"webUrl":               "https://onedrive.com/file",
			}),
			wantInOut: "Document.docx",
		},
		{
			name: "JSON output",
			cmd:  &WordGetCmd{ID: "file-123"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-123",
				"name": "Test.docx",
			}),
			wantInOut: `"name": "Test.docx"`,
		},
		{
			name:    "document not found",
			cmd:     &WordGetCmd{ID: "invalid"},
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

func TestWordExportCmd_Run(t *testing.T) {
	tmpDir := t.TempDir()

	t.Run("export docx", func(t *testing.T) {
		outFile := filepath.Join(tmpDir, "export.docx")
		mock := &testutil.MockClient{
			GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
				return []byte("docx content"), nil
			},
		}
		root := &Root{ClientFactory: mockClientFactory(mock)}
		cmd := &WordExportCmd{ID: "file-123", Out: outFile, Format: "docx"}

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
		cmd := &WordExportCmd{ID: "file-123", Out: outFile, Format: "pdf"}

		output := captureOutput(func() {
			err := cmd.Run(root)
			require.NoError(t, err)
		})

		assert.Contains(t, output, "Exported")
		assert.Contains(t, output, "PDF")
	})

	t.Run("JSON output", func(t *testing.T) {
		outFile := filepath.Join(tmpDir, "export2.docx")
		mock := &testutil.MockClient{
			GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
				return []byte("content"), nil
			},
		}
		root := &Root{JSON: true, ClientFactory: mockClientFactory(mock)}
		cmd := &WordExportCmd{ID: "file-123", Out: outFile, Format: "docx"}

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
		cmd := &WordExportCmd{ID: "file-123", Out: "/tmp/out.docx", Format: "docx"}

		err := cmd.Run(root)
		assert.Error(t, err)
	})
}

func TestWordCopyCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *WordCopyCmd
		root      *Root
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful copy",
			cmd:       &WordCopyCmd{ID: "file-123", Name: "Copy.docx"},
			root:      &Root{},
			wantInOut: "Copy initiated",
		},
		{
			name:      "copy with folder",
			cmd:       &WordCopyCmd{ID: "file-123", Name: "Copy.docx", Folder: "folder-123"},
			root:      &Root{},
			wantInOut: "Copy initiated",
		},
		{
			name: "JSON output",
			cmd:  &WordCopyCmd{ID: "file-123", Name: "Copy.docx"},
			root: &Root{JSON: true},
			wantInOut: `"success": true`,
		},
		{
			name:    "API error",
			cmd:     &WordCopyCmd{ID: "file-123", Name: "Copy.docx"},
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

func TestWordCreateCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *WordCreateCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful create",
			cmd:  &WordCreateCmd{Name: "NewDocument"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new-123",
				"name": "NewDocument.docx",
			}),
			wantInOut: "Document created",
		},
		{
			name: "create with .docx extension",
			cmd:  &WordCreateCmd{Name: "Test.docx"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new-456",
				"name": "Test.docx",
			}),
			wantInOut: "Document created",
		},
		{
			name: "create in folder",
			cmd:  &WordCreateCmd{Name: "FolderDoc", Folder: "folder-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new-789",
				"name": "FolderDoc.docx",
			}),
			wantInOut: "Document created",
		},
		{
			name: "JSON output",
			cmd:  &WordCreateCmd{Name: "Test"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":   "file-new",
				"name": "Test.docx",
			}),
			wantInOut: `"name": "Test.docx"`,
		},
		{
			name:    "API error",
			cmd:     &WordCreateCmd{Name: "Fail"},
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
