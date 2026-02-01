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

func TestContactsListCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *ContactsListCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list contacts",
			cmd:  &ContactsListCmd{Max: 50},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":          "contact-123",
						"displayName": "John Doe",
						"emailAddresses": []map[string]string{
							{"address": "john@example.com"},
						},
					},
				},
			}),
			wantInOut: "John Doe",
		},
		{
			name: "JSON output",
			cmd:  &ContactsListCmd{Max: 50},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "contact-123", "displayName": "Test User"},
				},
			}),
			wantInOut: `"displayName": "Test User"`,
		},
		{
			name:    "API error",
			cmd:     &ContactsListCmd{Max: 50},
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

func TestContactsSearchCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *ContactsSearchCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful search",
			cmd:  &ContactsSearchCmd{Query: "John"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":          "contact-123",
						"displayName": "John Doe",
						"emailAddresses": []map[string]string{
							{"address": "john@example.com"},
						},
					},
				},
			}),
			wantInOut: "John Doe",
		},
		{
			name: "JSON output",
			cmd:  &ContactsSearchCmd{Query: "test"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "contact-123", "displayName": "Test"},
				},
			}),
			wantInOut: `"displayName": "Test"`,
		},
		{
			name:    "API error",
			cmd:     &ContactsSearchCmd{Query: "test"},
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

func TestContactsGetCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *ContactsGetCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful get contact",
			cmd:  &ContactsGetCmd{ID: "contact-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":          "contact-123",
				"displayName": "John Doe",
				"emailAddresses": []map[string]string{
					{"address": "john@example.com"},
				},
				"businessPhones": []string{"555-1234"},
				"mobilePhone":    "555-5678",
				"companyName":    "Acme Inc",
				"jobTitle":       "Engineer",
			}),
			wantInOut: "John Doe",
		},
		{
			name: "JSON output",
			cmd:  &ContactsGetCmd{ID: "contact-123"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":          "contact-123",
				"displayName": "Test User",
			}),
			wantInOut: `"displayName": "Test User"`,
		},
		{
			name:    "contact not found",
			cmd:     &ContactsGetCmd{ID: "invalid"},
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

func TestContactsCreateCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *ContactsCreateCmd
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful create with name only",
			cmd:  &ContactsCreateCmd{Name: "New Contact"},
			mockResp: mustJSON(map[string]interface{}{
				"id":          "contact-new-123",
				"displayName": "New Contact",
			}),
			wantInOut: "Contact created",
		},
		{
			name: "create with all fields",
			cmd: &ContactsCreateCmd{
				Name:    "Full Contact",
				Email:   "full@example.com",
				Phone:   "555-1234",
				Company: "Company Inc",
				Title:   "Manager",
			},
			mockResp: mustJSON(map[string]interface{}{
				"id":          "contact-new-456",
				"displayName": "Full Contact",
			}),
			wantInOut: "Contact created",
		},
		{
			name:    "API error",
			cmd:     &ContactsCreateCmd{Name: "Test"},
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

func TestContactsUpdateCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *ContactsUpdateCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful update name",
			cmd: &ContactsUpdateCmd{
				ID:   "contact-123",
				Name: "Updated Name",
			},
			wantInOut: "Contact updated",
		},
		{
			name: "update all fields",
			cmd: &ContactsUpdateCmd{
				ID:      "contact-123",
				Name:    "Updated",
				Email:   "new@example.com",
				Phone:   "555-9999",
				Company: "New Co",
				Title:   "Director",
			},
			wantInOut: "Contact updated",
		},
		{
			name:    "no updates specified",
			cmd:     &ContactsUpdateCmd{ID: "contact-123"},
			wantErr: true,
		},
		{
			name: "API error",
			cmd: &ContactsUpdateCmd{
				ID:   "contact-123",
				Name: "Update",
			},
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

func TestContactsDeleteCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *ContactsDeleteCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful delete",
			cmd:       &ContactsDeleteCmd{ID: "contact-123"},
			wantInOut: "Contact deleted",
		},
		{
			name:    "API error",
			cmd:     &ContactsDeleteCmd{ID: "contact-123"},
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

func TestContactsDirectoryCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *ContactsDirectoryCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful directory search",
			cmd:  &ContactsDirectoryCmd{Query: "john"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":          "user-123",
						"displayName": "John Smith",
						"mail":        "john.smith@company.com",
						"jobTitle":    "Developer",
					},
				},
			}),
			wantInOut: "John Smith",
		},
		{
			name: "JSON output",
			cmd:  &ContactsDirectoryCmd{Query: "test"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "user-123", "displayName": "Test User"},
				},
			}),
			wantInOut: `"displayName": "Test User"`,
		},
		{
			name:    "API error",
			cmd:     &ContactsDirectoryCmd{Query: "test"},
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

// Test type unmarshaling
func TestContact_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "contact-123",
		"displayName": "John Doe",
		"emailAddresses": [
			{"address": "john@example.com", "name": "John Doe"}
		],
		"businessPhones": ["555-1234", "555-5678"],
		"mobilePhone": "555-9999",
		"companyName": "Acme Inc",
		"jobTitle": "Engineer"
	}`

	var contact Contact
	err := json.Unmarshal([]byte(jsonData), &contact)
	require.NoError(t, err)
	assert.Equal(t, "contact-123", contact.ID)
	assert.Equal(t, "John Doe", contact.DisplayName)
	assert.Len(t, contact.EmailAddresses, 1)
	assert.Equal(t, "john@example.com", contact.EmailAddresses[0].Address)
	assert.Len(t, contact.BusinessPhones, 2)
	assert.Equal(t, "555-9999", contact.MobilePhone)
	assert.Equal(t, "Acme Inc", contact.CompanyName)
	assert.Equal(t, "Engineer", contact.JobTitle)
}

func TestDirectoryUser_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "user-123",
		"displayName": "John Smith",
		"mail": "john.smith@company.com",
		"jobTitle": "Developer"
	}`

	var user DirectoryUser
	err := json.Unmarshal([]byte(jsonData), &user)
	require.NoError(t, err)
	assert.Equal(t, "user-123", user.ID)
	assert.Equal(t, "John Smith", user.DisplayName)
	assert.Equal(t, "john.smith@company.com", user.Mail)
	assert.Equal(t, "Developer", user.JobTitle)
}
