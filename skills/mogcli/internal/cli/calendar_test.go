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

func TestCalendarListCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *CalendarListCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list events",
			cmd:  &CalendarListCmd{Max: 25},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":      "event-123",
						"subject": "Team Meeting",
						"start": map[string]string{
							"dateTime": "2024-01-20T10:00:00",
							"timeZone": "UTC",
						},
						"end": map[string]string{
							"dateTime": "2024-01-20T11:00:00",
							"timeZone": "UTC",
						},
						"location": map[string]string{
							"displayName": "Conference Room A",
						},
					},
				},
			}),
			wantInOut: "Team Meeting",
		},
		{
			name: "no events found",
			cmd:  &CalendarListCmd{Max: 25},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
			wantInOut: "No events found",
		},
		{
			name: "list with specific calendar",
			cmd:  &CalendarListCmd{Max: 25, Calendar: "cal-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
			wantInOut: "No events found",
		},
		{
			name: "list with date range",
			cmd:  &CalendarListCmd{Max: 25, From: "2024-01-01", To: "2024-01-31"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
			wantInOut: "No events found",
		},
		{
			name: "JSON output",
			cmd:  &CalendarListCmd{Max: 25},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "event-123", "subject": "Meeting"},
				},
			}),
			wantInOut: `"subject": "Meeting"`,
		},
		{
			name: "invalid from date",
			cmd:  &CalendarListCmd{Max: 25, From: "invalid-date"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
			wantErr: true,
		},
		{
			name:    "API error",
			cmd:     &CalendarListCmd{Max: 25},
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

func TestCalendarGetCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *CalendarGetCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful get event",
			cmd:  &CalendarGetCmd{ID: "event-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":      "event-123",
				"subject": "Team Meeting",
				"start": map[string]string{
					"dateTime": "2024-01-20T10:00:00",
					"timeZone": "UTC",
				},
				"end": map[string]string{
					"dateTime": "2024-01-20T11:00:00",
					"timeZone": "UTC",
				},
				"organizer": map[string]interface{}{
					"emailAddress": map[string]string{
						"name":    "Organizer Name",
						"address": "organizer@example.com",
					},
				},
			}),
			wantInOut: "Team Meeting",
		},
		{
			name: "get event with JSON output",
			cmd:  &CalendarGetCmd{ID: "event-123"},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":      "event-123",
				"subject": "Meeting",
			}),
			wantInOut: `"subject": "Meeting"`,
		},
		{
			name:    "event not found",
			cmd:     &CalendarGetCmd{ID: "invalid"},
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

func TestCalendarCreateCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *CalendarCreateCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful create event",
			cmd: &CalendarCreateCmd{
				Summary: "New Meeting",
				From:    "2024-01-20T10:00:00",
				To:      "2024-01-20T11:00:00",
			},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":      "event-new-123",
				"subject": "New Meeting",
			}),
			wantInOut: "Event created",
		},
		{
			name: "create event with all options",
			cmd: &CalendarCreateCmd{
				Summary:     "Full Meeting",
				From:        "2024-01-20T10:00:00",
				To:          "2024-01-20T11:00:00",
				Location:    "Room 101",
				Description: "Meeting description",
				Attendees:   []string{"person1@example.com", "person2@example.com"},
				AllDay:      true,
				Calendar:    "cal-123",
			},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"id":      "event-new-456",
				"subject": "Full Meeting",
			}),
			wantInOut: "Event created",
		},
		{
			name: "create event with JSON output",
			cmd: &CalendarCreateCmd{
				Summary: "Meeting",
				From:    "2024-01-20T10:00:00",
				To:      "2024-01-20T11:00:00",
			},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"id":      "event-new",
				"subject": "Meeting",
			}),
			wantInOut: `"id": "event-new"`,
		},
		{
			name: "API error",
			cmd: &CalendarCreateCmd{
				Summary: "Meeting",
				From:    "2024-01-20T10:00:00",
				To:      "2024-01-20T11:00:00",
			},
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

func TestCalendarUpdateCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *CalendarUpdateCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful update",
			cmd: &CalendarUpdateCmd{
				ID:      "event-123",
				Summary: "Updated Meeting",
			},
			wantInOut: "Event updated",
		},
		{
			name: "update with all fields",
			cmd: &CalendarUpdateCmd{
				ID:          "event-123",
				Summary:     "Updated Meeting",
				From:        "2024-01-20T14:00:00",
				To:          "2024-01-20T15:00:00",
				Location:    "New Room",
				Description: "Updated description",
			},
			wantInOut: "Event updated",
		},
		{
			name:    "no updates specified",
			cmd:     &CalendarUpdateCmd{ID: "event-123"},
			wantErr: true,
		},
		{
			name: "API error",
			cmd: &CalendarUpdateCmd{
				ID:      "event-123",
				Summary: "Update",
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

func TestCalendarDeleteCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *CalendarDeleteCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful delete",
			cmd:       &CalendarDeleteCmd{ID: "event-123"},
			wantInOut: "Event deleted",
		},
		{
			name:    "API error",
			cmd:     &CalendarDeleteCmd{ID: "event-123"},
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

func TestCalendarCalendarsCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list calendars",
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":                "cal-123",
						"name":              "Calendar",
						"isDefaultCalendar": true,
					},
					{
						"id":                "cal-456",
						"name":              "Work",
						"isDefaultCalendar": false,
					},
				},
			}),
			wantInOut: "Calendar",
		},
		{
			name: "JSON output",
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "cal-123", "name": "Calendar"},
				},
			}),
			wantInOut: `"name": "Calendar"`,
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

			cmd := &CalendarCalendarsCmd{}
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

func TestCalendarRespondCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *CalendarRespondCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "accept response",
			cmd:       &CalendarRespondCmd{ID: "event-123", Response: "accept"},
			wantInOut: "Responded: accept",
		},
		{
			name:      "decline response",
			cmd:       &CalendarRespondCmd{ID: "event-123", Response: "decline"},
			wantInOut: "Responded: decline",
		},
		{
			name:      "tentative response",
			cmd:       &CalendarRespondCmd{ID: "event-123", Response: "tentative"},
			wantInOut: "Responded: tentative",
		},
		{
			name:      "respond with comment",
			cmd:       &CalendarRespondCmd{ID: "event-123", Response: "accept", Comment: "I'll be there!"},
			wantInOut: "Responded: accept",
		},
		{
			name:    "invalid response",
			cmd:     &CalendarRespondCmd{ID: "event-123", Response: "invalid"},
			wantErr: true,
		},
		{
			name:    "API error",
			cmd:     &CalendarRespondCmd{ID: "event-123", Response: "accept"},
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

func TestCalendarFreeBusyCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *CalendarFreeBusyCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful freebusy",
			cmd: &CalendarFreeBusyCmd{
				Emails: []string{"person@example.com"},
				Start:  "2024-01-20T08:00:00",
				End:    "2024-01-20T18:00:00",
			},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"scheduleId": "person@example.com", "availabilityView": "0000222200"},
				},
			}),
		},
		{
			name: "freebusy with JSON output",
			cmd: &CalendarFreeBusyCmd{
				Emails: []string{"person@example.com"},
				Start:  "2024-01-20T08:00:00",
				End:    "2024-01-20T18:00:00",
			},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
		},
		{
			name: "API error",
			cmd: &CalendarFreeBusyCmd{
				Emails: []string{"person@example.com"},
				Start:  "2024-01-20T08:00:00",
				End:    "2024-01-20T18:00:00",
			},
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

func TestCalendarACLCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *CalendarACLCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list permissions",
			cmd:  &CalendarACLCmd{},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":   "perm-123",
						"role": "write",
						"emailAddress": map[string]string{
							"name":    "User Name",
							"address": "user@example.com",
						},
						"isRemovable": true,
					},
				},
			}),
			wantInOut: "Calendar Permissions",
		},
		{
			name: "list permissions with specific calendar",
			cmd:  &CalendarACLCmd{Calendar: "cal-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
			wantInOut: "No permissions found",
		},
		{
			name: "JSON output",
			cmd:  &CalendarACLCmd{},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "perm-123", "role": "write"},
				},
			}),
			wantInOut: `"role": "write"`,
		},
		{
			name:    "API error",
			cmd:     &CalendarACLCmd{},
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
func TestEvent_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "event-123",
		"subject": "Team Meeting",
		"isAllDay": false,
		"start": {
			"dateTime": "2024-01-20T10:00:00",
			"timeZone": "UTC"
		},
		"end": {
			"dateTime": "2024-01-20T11:00:00",
			"timeZone": "UTC"
		},
		"location": {
			"displayName": "Room A"
		}
	}`

	var event Event
	err := json.Unmarshal([]byte(jsonData), &event)
	require.NoError(t, err)
	assert.Equal(t, "event-123", event.ID)
	assert.Equal(t, "Team Meeting", event.Subject)
	assert.False(t, event.IsAllDay)
	assert.Equal(t, "Room A", event.Location.DisplayName)
}

func TestCalendar_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "cal-123",
		"name": "My Calendar",
		"isDefaultCalendar": true
	}`

	var cal Calendar
	err := json.Unmarshal([]byte(jsonData), &cal)
	require.NoError(t, err)
	assert.Equal(t, "cal-123", cal.ID)
	assert.Equal(t, "My Calendar", cal.Name)
	assert.True(t, cal.IsDefaultCalendar)
}

func TestCalendarPermission_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "perm-123",
		"role": "write",
		"isRemovable": true,
		"isInsideOrganization": true,
		"emailAddress": {
			"name": "Test User",
			"address": "test@example.com"
		}
	}`

	var perm CalendarPermission
	err := json.Unmarshal([]byte(jsonData), &perm)
	require.NoError(t, err)
	assert.Equal(t, "perm-123", perm.ID)
	assert.Equal(t, "write", perm.Role)
	assert.True(t, perm.IsRemovable)
	assert.Equal(t, "test@example.com", perm.EmailAddress.Address)
}

func TestPrintEvent(t *testing.T) {
	event := Event{
		ID:      "event-123-456789012345678901234567890",
		Subject: "Team Meeting",
		Start: &Time{
			DateTime: "2024-01-20T10:00:00.0000000",
			TimeZone: "UTC",
		},
		Location: &Loc{
			DisplayName: "Room A",
		},
	}

	output := captureOutput(func() {
		printEvent(event, false)
	})

	assert.Contains(t, output, "Team Meeting")
	assert.Contains(t, output, "Room A")
}

func TestPrintEventDetail(t *testing.T) {
	event := Event{
		ID:      "event-123-456789012345678901234567890",
		Subject: "Team Meeting",
		Start: &Time{
			DateTime: "2024-01-20T10:00:00.0000000",
			TimeZone: "UTC",
		},
		End: &Time{
			DateTime: "2024-01-20T11:00:00.0000000",
			TimeZone: "UTC",
		},
		Location: &Loc{
			DisplayName: "Room A",
		},
		Organizer: &Org{
			EmailAddress: struct {
				Name    string `json:"name"`
				Address string `json:"address"`
			}{
				Name:    "Organizer",
				Address: "org@example.com",
			},
		},
		Body: &Body{
			ContentType: "text",
			Content:     "Meeting notes",
		},
	}

	output := captureOutput(func() {
		printEventDetail(event, false)
	})

	assert.Contains(t, output, "Team Meeting")
	assert.Contains(t, output, "Room A")
	assert.Contains(t, output, "Organizer")
}
