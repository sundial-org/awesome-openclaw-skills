package cli

import (
	"context"
	"encoding/json"
	"errors"
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/visionik/mogcli/internal/testutil"
)

func TestOneNoteNotebooksCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list notebooks",
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "nb-123", "displayName": "Work Notebook"},
					{"id": "nb-456", "displayName": "Personal"},
				},
			}),
			wantInOut: "Work Notebook",
		},
		{
			name: "JSON output",
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "nb-123", "displayName": "Notebook"},
				},
			}),
			wantInOut: `"displayName": "Notebook"`,
		},
		{
			name:    "API error",
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

			cmd := &OneNoteNotebooksCmd{}
			var output string
			err := error(nil)
			output = captureOutput(func() {
				err = cmd.Run(tt.root)
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

func TestOneNoteSectionsCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *OneNoteSectionsCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list sections",
			cmd:  &OneNoteSectionsCmd{NotebookID: "nb-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "sec-123", "displayName": "Meeting Notes"},
					{"id": "sec-456", "displayName": "Ideas"},
				},
			}),
			wantInOut: "Meeting Notes",
		},
		{
			name: "JSON output",
			cmd:  &OneNoteSectionsCmd{NotebookID: "nb-123"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "sec-123", "displayName": "Section"},
				},
			}),
			wantInOut: `"displayName": "Section"`,
		},
		{
			name:    "API error",
			cmd:     &OneNoteSectionsCmd{NotebookID: "nb-123"},
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

func TestOneNotePagesCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *OneNotePagesCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list pages",
			cmd:  &OneNotePagesCmd{SectionID: "sec-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "page-123", "title": "Project Planning"},
					{"id": "page-456", "title": "Sprint Notes"},
				},
			}),
			wantInOut: "Project Planning",
		},
		{
			name: "JSON output",
			cmd:  &OneNotePagesCmd{SectionID: "sec-123"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "page-123", "title": "Page"},
				},
			}),
			wantInOut: `"title": "Page"`,
		},
		{
			name:    "API error",
			cmd:     &OneNotePagesCmd{SectionID: "sec-123"},
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

func TestOneNoteGetCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *OneNoteGetCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:     "successful get page content",
			cmd:      &OneNoteGetCmd{PageID: "page-123"},
			root:     &Root{},
			mockResp: []byte("<html><body><p>Page content</p></body></html>"),
			wantInOut: "Page content",
		},
		{
			name:      "get with HTML output",
			cmd:       &OneNoteGetCmd{PageID: "page-123", HTML: true},
			root:      &Root{},
			mockResp:  []byte("<html><body><p>Page content</p></body></html>"),
			wantInOut: "<html>",
		},
		{
			name:      "get with JSON flag shows raw",
			cmd:       &OneNoteGetCmd{PageID: "page-123"},
			root:      &Root{JSON: true},
			mockResp:  []byte("<html><body><p>Content</p></body></html>"),
			wantInOut: "<html>",
		},
		{
			name:    "API error",
			cmd:     &OneNoteGetCmd{PageID: "page-123"},
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

func TestOneNoteSearchCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *OneNoteSearchCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful search",
			cmd:  &OneNoteSearchCmd{Query: "meeting"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "page-123", "title": "Meeting Notes"},
				},
			}),
			wantInOut: "Meeting Notes",
		},
		{
			name: "JSON output",
			cmd:  &OneNoteSearchCmd{Query: "test"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "page-123", "title": "Test Page"},
				},
			}),
			wantInOut: `"title": "Test Page"`,
		},
		{
			name:    "API error",
			cmd:     &OneNoteSearchCmd{Query: "test"},
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

func TestOneNoteCreateNotebookCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *OneNoteCreateNotebookCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful create notebook",
			cmd:  &OneNoteCreateNotebookCmd{Name: "New Notebook"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":          "nb-new-123",
				"displayName": "New Notebook",
			}),
			wantInOut: "Notebook created",
		},
		{
			name: "JSON output",
			cmd:  &OneNoteCreateNotebookCmd{Name: "Test"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":          "nb-new",
				"displayName": "Test",
			}),
			wantInOut: `"displayName": "Test"`,
		},
		{
			name:    "API error",
			cmd:     &OneNoteCreateNotebookCmd{Name: "Fail"},
			root:    &Root{},
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

func TestOneNoteCreateSectionCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *OneNoteCreateSectionCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful create section",
			cmd:  &OneNoteCreateSectionCmd{NotebookID: "nb-123", Name: "New Section"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":          "sec-new-123",
				"displayName": "New Section",
			}),
			wantInOut: "Section created",
		},
		{
			name: "JSON output",
			cmd:  &OneNoteCreateSectionCmd{NotebookID: "nb-123", Name: "Test"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":          "sec-new",
				"displayName": "Test",
			}),
			wantInOut: `"displayName": "Test"`,
		},
		{
			name:    "API error",
			cmd:     &OneNoteCreateSectionCmd{NotebookID: "nb-123", Name: "Fail"},
			root:    &Root{},
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

func TestOneNoteCreatePageCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *OneNoteCreatePageCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful create page",
			cmd:  &OneNoteCreatePageCmd{SectionID: "sec-123", Title: "New Page"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":    "page-new-123",
				"title": "New Page",
			}),
			wantInOut: "Page created",
		},
		{
			name: "create page with content",
			cmd:  &OneNoteCreatePageCmd{SectionID: "sec-123", Title: "Content Page", Content: "Some content here"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":    "page-new-456",
				"title": "Content Page",
			}),
			wantInOut: "Page created",
		},
		{
			name: "JSON output",
			cmd:  &OneNoteCreatePageCmd{SectionID: "sec-123", Title: "Test"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":    "page-new",
				"title": "Test",
			}),
			wantInOut: `"title": "Test"`,
		},
		{
			name:    "API error",
			cmd:     &OneNoteCreatePageCmd{SectionID: "sec-123", Title: "Fail"},
			root:    &Root{},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				PostHTMLFunc: func(ctx context.Context, path string, html string) ([]byte, error) {
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

func TestOneNoteDeleteCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *OneNoteDeleteCmd
		root      *Root
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful delete",
			cmd:       &OneNoteDeleteCmd{PageID: "page-123"},
			root:      &Root{},
			wantInOut: "Page deleted",
		},
		{
			name: "JSON output",
			cmd:  &OneNoteDeleteCmd{PageID: "page-123"},
			root: &Root{JSON: true},
			wantInOut: `"success": true`,
		},
		{
			name:    "API error",
			cmd:     &OneNoteDeleteCmd{PageID: "page-123"},
			root:    &Root{},
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

// Test escapeHTML function
func TestEscapeHTML(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string
	}{
		{name: "empty string", input: "", expected: ""},
		{name: "no special chars", input: "Hello World", expected: "Hello World"},
		{name: "ampersand", input: "A & B", expected: "A &amp; B"},
		{name: "less than", input: "A < B", expected: "A &lt; B"},
		{name: "greater than", input: "A > B", expected: "A &gt; B"},
		{name: "double quote", input: `Say "Hello"`, expected: "Say &quot;Hello&quot;"},
		{name: "single quote", input: "It's fine", expected: "It&#39;s fine"},
		{name: "mixed", input: `<a href="test">&</a>`, expected: "&lt;a href=&quot;test&quot;&gt;&amp;&lt;/a&gt;"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := escapeHTML(tt.input)
			assert.Equal(t, tt.expected, result)
		})
	}
}

// Test type unmarshaling
func TestNotebook_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "nb-123",
		"displayName": "My Notebook"
	}`

	var nb Notebook
	err := json.Unmarshal([]byte(jsonData), &nb)
	require.NoError(t, err)
	assert.Equal(t, "nb-123", nb.ID)
	assert.Equal(t, "My Notebook", nb.DisplayName)
}

func TestSection_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "sec-123",
		"displayName": "My Section"
	}`

	var sec Section
	err := json.Unmarshal([]byte(jsonData), &sec)
	require.NoError(t, err)
	assert.Equal(t, "sec-123", sec.ID)
	assert.Equal(t, "My Section", sec.DisplayName)
}

func TestPage_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "page-123",
		"title": "My Page"
	}`

	var page Page
	err := json.Unmarshal([]byte(jsonData), &page)
	require.NoError(t, err)
	assert.Equal(t, "page-123", page.ID)
	assert.Equal(t, "My Page", page.Title)
}
