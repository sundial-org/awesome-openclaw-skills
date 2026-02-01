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

func TestTasksListsCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list task lists",
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "list-123", "displayName": "My Tasks", "isOwner": true},
					{"id": "list-456", "displayName": "Work", "isOwner": false},
				},
			}),
			wantInOut: "My Tasks",
		},
		{
			name: "JSON output",
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "list-123", "displayName": "Tasks"},
				},
			}),
			wantInOut: `"displayName": "Tasks"`,
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

			cmd := &TasksListsCmd{}
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

func TestTasksListCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *TasksListCmd
		root      *Root
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful list tasks",
			cmd:  &TasksListCmd{},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{
						"id":         "task-123",
						"title":      "Complete project",
						"status":     "notStarted",
						"importance": "high",
						"dueDateTime": map[string]string{
							"dateTime": "2024-01-20T00:00:00",
							"timeZone": "UTC",
						},
					},
				},
			}),
			wantInOut: "Complete project",
		},
		{
			name: "list tasks with specific list ID",
			cmd:  &TasksListCmd{ListID: "list-123"},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "task-123", "title": "Task", "status": "notStarted"},
				},
			}),
			wantInOut: "Task",
		},
		{
			name: "list all tasks including completed",
			cmd:  &TasksListCmd{All: true},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "task-123", "title": "Completed Task", "status": "completed"},
				},
			}),
			wantInOut: "Completed Task",
		},
		{
			name: "no tasks found",
			cmd:  &TasksListCmd{},
			root: &Root{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
			wantInOut: "No tasks",
		},
		{
			name: "JSON output",
			cmd:  &TasksListCmd{},
			root: &Root{JSON: true},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "task-123", "title": "Task"},
				},
			}),
			wantInOut: `"title": "Task"`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			callCount := 0
			mock := &testutil.MockClient{
				GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
					callCount++
					if tt.mockErr != nil {
						return nil, tt.mockErr
					}
					// First call is for task lists (when no ListID specified)
					if callCount == 1 && tt.cmd.ListID == "" {
						return mustJSON(map[string]interface{}{
							"value": []map[string]interface{}{
								{"id": "list-default-123", "displayName": "Tasks"},
							},
						}), nil
					}
					return tt.mockResp, nil
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

func TestTasksAddCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *TasksAddCmd
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful add task",
			cmd:  &TasksAddCmd{Title: "New Task"},
			mockResp: mustJSON(map[string]interface{}{
				"id":    "task-new-123",
				"title": "New Task",
			}),
			wantInOut: "Task created",
		},
		{
			name: "add task with all options",
			cmd: &TasksAddCmd{
				Title:     "Full Task",
				ListID:    "list-123",
				Due:       "2024-01-20",
				Notes:     "Task notes",
				Important: true,
			},
			mockResp: mustJSON(map[string]interface{}{
				"id":    "task-new-456",
				"title": "Full Task",
			}),
			wantInOut: "Task created",
		},
		{
			name: "add task with tomorrow due",
			cmd:  &TasksAddCmd{Title: "Tomorrow Task", Due: "tomorrow"},
			mockResp: mustJSON(map[string]interface{}{
				"id":    "task-new-789",
				"title": "Tomorrow Task",
			}),
			wantInOut: "Task created",
		},
		{
			name: "add task with today due",
			cmd:  &TasksAddCmd{Title: "Today Task", Due: "today"},
			mockResp: mustJSON(map[string]interface{}{
				"id":    "task-new-789",
				"title": "Today Task",
			}),
			wantInOut: "Task created",
		},
		{
			name:    "API error",
			cmd:     &TasksAddCmd{Title: "Task"},
			mockErr: errors.New("API error"),
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			callCount := 0
			mock := &testutil.MockClient{
				GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
					return mustJSON(map[string]interface{}{
						"value": []map[string]interface{}{
							{"id": "list-default-123", "displayName": "Tasks"},
						},
					}), nil
				},
				PostFunc: func(ctx context.Context, path string, body interface{}) ([]byte, error) {
					callCount++
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

func TestTasksUpdateCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *TasksUpdateCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful update title",
			cmd: &TasksUpdateCmd{
				TaskID: "task-123",
				ListID: "list-123",
				Title:  "Updated Title",
			},
			wantInOut: "Task updated",
		},
		{
			name: "update all fields",
			cmd: &TasksUpdateCmd{
				TaskID:    "task-123",
				ListID:    "list-123",
				Title:     "Updated",
				Due:       "2024-01-25",
				Notes:     "New notes",
				Important: true,
			},
			wantInOut: "Task updated",
		},
		{
			name: "no list ID specified",
			cmd: &TasksUpdateCmd{
				TaskID: "task-123",
				Title:  "Update",
			},
			wantErr: true,
		},
		{
			name: "no updates specified",
			cmd: &TasksUpdateCmd{
				TaskID: "task-123",
				ListID: "list-123",
			},
			wantErr: true,
		},
		{
			name: "API error",
			cmd: &TasksUpdateCmd{
				TaskID: "task-123",
				ListID: "list-123",
				Title:  "Update",
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

func TestTasksDoneCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *TasksDoneCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful mark done",
			cmd:       &TasksDoneCmd{TaskID: "task-123", ListID: "list-123"},
			wantInOut: "Task completed",
		},
		{
			name:    "no list ID specified",
			cmd:     &TasksDoneCmd{TaskID: "task-123"},
			wantErr: true,
		},
		{
			name:    "API error",
			cmd:     &TasksDoneCmd{TaskID: "task-123", ListID: "list-123"},
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

func TestTasksUndoCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *TasksUndoCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful mark undone",
			cmd:       &TasksUndoCmd{TaskID: "task-123", ListID: "list-123"},
			wantInOut: "Task uncompleted",
		},
		{
			name:    "no list ID specified",
			cmd:     &TasksUndoCmd{TaskID: "task-123"},
			wantErr: true,
		},
		{
			name:    "API error",
			cmd:     &TasksUndoCmd{TaskID: "task-123", ListID: "list-123"},
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

func TestTasksDeleteCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *TasksDeleteCmd
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name:      "successful delete",
			cmd:       &TasksDeleteCmd{TaskID: "task-123", ListID: "list-123"},
			wantInOut: "Task deleted",
		},
		{
			name:    "no list ID specified",
			cmd:     &TasksDeleteCmd{TaskID: "task-123"},
			wantErr: true,
		},
		{
			name:    "API error",
			cmd:     &TasksDeleteCmd{TaskID: "task-123", ListID: "list-123"},
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

func TestTasksClearCmd_Run(t *testing.T) {
	tests := []struct {
		name      string
		cmd       *TasksClearCmd
		mockResp  []byte
		mockErr   error
		wantErr   bool
		wantInOut string
	}{
		{
			name: "successful clear completed",
			cmd:  &TasksClearCmd{ListID: "list-123"},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "task-1", "title": "Completed 1", "status": "completed"},
					{"id": "task-2", "title": "Completed 2", "status": "completed"},
				},
			}),
			wantInOut: "Cleared 2 completed tasks",
		},
		{
			name: "clear without list ID uses default",
			cmd:  &TasksClearCmd{},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{
					{"id": "task-1", "title": "Completed", "status": "completed"},
				},
			}),
			wantInOut: "Cleared 1 completed tasks",
		},
		{
			name: "no completed tasks",
			cmd:  &TasksClearCmd{ListID: "list-123"},
			mockResp: mustJSON(map[string]interface{}{
				"value": []map[string]interface{}{},
			}),
			wantInOut: "Cleared 0 completed tasks",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mock := &testutil.MockClient{
				GetFunc: func(ctx context.Context, path string, query url.Values) ([]byte, error) {
					if tt.mockErr != nil {
						return nil, tt.mockErr
					}
					// Return task lists for default list lookup
					if path == "/me/todo/lists" {
						return mustJSON(map[string]interface{}{
							"value": []map[string]interface{}{
								{"id": "list-default-123", "displayName": "Tasks"},
							},
						}), nil
					}
					return tt.mockResp, nil
				},
				DeleteFunc: func(ctx context.Context, path string) error {
					return nil
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
func TestTaskList_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "list-123",
		"displayName": "My Tasks",
		"isOwner": true
	}`

	var list TaskList
	err := json.Unmarshal([]byte(jsonData), &list)
	require.NoError(t, err)
	assert.Equal(t, "list-123", list.ID)
	assert.Equal(t, "My Tasks", list.DisplayName)
	assert.True(t, list.IsOwner)
}

func TestTask_Unmarshal(t *testing.T) {
	jsonData := `{
		"id": "task-123",
		"title": "Complete project",
		"status": "notStarted",
		"importance": "high",
		"dueDateTime": {
			"dateTime": "2024-01-20T00:00:00",
			"timeZone": "UTC"
		},
		"body": {
			"content": "Task notes",
			"contentType": "text"
		}
	}`

	var task Task
	err := json.Unmarshal([]byte(jsonData), &task)
	require.NoError(t, err)
	assert.Equal(t, "task-123", task.ID)
	assert.Equal(t, "Complete project", task.Title)
	assert.Equal(t, "notStarted", task.Status)
	assert.Equal(t, "high", task.Importance)
	assert.NotNil(t, task.DueDateTime)
	assert.Equal(t, "2024-01-20T00:00:00", task.DueDateTime.DateTime)
	assert.NotNil(t, task.Body)
	assert.Equal(t, "Task notes", task.Body.Content)
}
