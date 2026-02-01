package cli

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"time"

	"github.com/visionik/mogcli/internal/graph"
)

// TasksCmd handles Microsoft To-Do operations.
type TasksCmd struct {
	Lists  TasksListsCmd  `cmd:"" help:"List task lists"`
	List   TasksListCmd   `cmd:"" help:"List tasks in a list"`
	Add    TasksAddCmd    `cmd:"" aliases:"create" help:"Add a task"`
	Update TasksUpdateCmd `cmd:"" help:"Update a task"`
	Done   TasksDoneCmd   `cmd:"" aliases:"complete" help:"Mark task as done"`
	Undo   TasksUndoCmd   `cmd:"" help:"Mark task as not done"`
	Delete TasksDeleteCmd `cmd:"" aliases:"rm" help:"Delete a task"`
	Clear  TasksClearCmd  `cmd:"" help:"Clear completed tasks"`
}

// TasksListsCmd lists task lists.
type TasksListsCmd struct{}

// Run executes tasks lists.
func (c *TasksListsCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	data, err := client.Get(ctx, "/me/todo/lists", nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []TaskList `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, list := range resp.Value {
		marker := " "
		if list.IsOwner {
			marker = "*"
		}
		fmt.Printf("%s %-30s %s\n", marker, list.DisplayName, graph.FormatID(list.ID))
	}
	return nil
}

// TasksListCmd lists tasks.
type TasksListCmd struct {
	ListID string `arg:"" optional:"" help:"Task list ID (default: default list)"`
	All    bool   `help:"Include completed tasks"`
}

// Run executes tasks list.
func (c *TasksListCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()

	// Get list ID
	listID := c.ListID
	if listID == "" {
		// Get default list
		data, err := client.Get(ctx, "/me/todo/lists", nil)
		if err != nil {
			return err
		}
		var resp struct {
			Value []TaskList `json:"value"`
		}
		if err := json.Unmarshal(data, &resp); err != nil {
			return err
		}
		if len(resp.Value) == 0 {
			return fmt.Errorf("no task lists found")
		}
		listID = resp.Value[0].ID
	} else {
		listID = graph.ResolveID(listID)
	}

	query := url.Values{}
	if !c.All {
		query.Set("$filter", "status ne 'completed'")
	}

	path := fmt.Sprintf("/me/todo/lists/%s/tasks", listID)
	data, err := client.Get(ctx, path, query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Task `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	if len(resp.Value) == 0 {
		fmt.Println("No tasks")
		return nil
	}

	for _, task := range resp.Value {
		status := "○"
		if task.Status == "completed" {
			status = "✓"
		}
		importance := " "
		if task.Importance == "high" {
			importance = "!"
		}
		due := ""
		if task.DueDateTime != nil {
			due = task.DueDateTime.DateTime[:10]
		}
		fmt.Printf("%s%s %-10s %s  %s\n", status, importance, due, task.Title, graph.FormatID(task.ID))
	}
	return nil
}

// TasksAddCmd adds a task.
type TasksAddCmd struct {
	Title     string `arg:"" help:"Task title"`
	ListID    string `help:"Task list ID" name:"list"`
	Due       string `help:"Due date (YYYY-MM-DD or 'tomorrow')"`
	Notes     string `help:"Task notes"`
	Important bool   `help:"Mark as important"`
}

// Run executes tasks add.
func (c *TasksAddCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()

	// Get list ID
	listID := c.ListID
	if listID == "" {
		data, err := client.Get(ctx, "/me/todo/lists", nil)
		if err != nil {
			return err
		}
		var resp struct {
			Value []TaskList `json:"value"`
		}
		if err := json.Unmarshal(data, &resp); err != nil {
			return err
		}
		if len(resp.Value) == 0 {
			return fmt.Errorf("no task lists found")
		}
		listID = resp.Value[0].ID
	} else {
		listID = graph.ResolveID(listID)
	}

	task := map[string]interface{}{
		"title": c.Title,
	}

	if c.Due != "" {
		dueDate := c.Due
		if c.Due == "tomorrow" {
			dueDate = time.Now().AddDate(0, 0, 1).Format("2006-01-02")
		} else if c.Due == "today" {
			dueDate = time.Now().Format("2006-01-02")
		}
		task["dueDateTime"] = map[string]string{
			"dateTime": dueDate + "T00:00:00",
			"timeZone": "UTC",
		}
	}

	if c.Notes != "" {
		task["body"] = map[string]string{
			"content":     c.Notes,
			"contentType": "text",
		}
	}

	if c.Important {
		task["importance"] = "high"
	}

	path := fmt.Sprintf("/me/todo/lists/%s/tasks", listID)
	data, err := client.Post(ctx, path, task)
	if err != nil {
		return err
	}

	var created Task
	if err := json.Unmarshal(data, &created); err != nil {
		return err
	}

	fmt.Printf("✓ Task created: %s (%s)\n", created.Title, graph.FormatID(created.ID))
	return nil
}

// TasksUpdateCmd updates a task.
type TasksUpdateCmd struct {
	TaskID    string `arg:"" help:"Task ID"`
	ListID    string `help:"Task list ID" name:"list"`
	Title     string `help:"New title"`
	Due       string `help:"New due date"`
	Notes     string `help:"New notes"`
	Important bool   `help:"Mark as important"`
}

// Run executes tasks update.
func (c *TasksUpdateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()

	listID := c.ListID
	if listID == "" {
		return fmt.Errorf("--list is required for update")
	}
	listID = graph.ResolveID(listID)

	updates := make(map[string]interface{})

	if c.Title != "" {
		updates["title"] = c.Title
	}
	if c.Due != "" {
		updates["dueDateTime"] = map[string]string{
			"dateTime": c.Due + "T00:00:00",
			"timeZone": "UTC",
		}
	}
	if c.Notes != "" {
		updates["body"] = map[string]string{"content": c.Notes, "contentType": "text"}
	}
	if c.Important {
		updates["importance"] = "high"
	}

	if len(updates) == 0 {
		return fmt.Errorf("no updates specified")
	}

	path := fmt.Sprintf("/me/todo/lists/%s/tasks/%s", listID, graph.ResolveID(c.TaskID))
	_, err = client.Patch(ctx, path, updates)
	if err != nil {
		return err
	}

	fmt.Println("✓ Task updated")
	return nil
}

// TasksDoneCmd marks a task as done.
type TasksDoneCmd struct {
	TaskID string `arg:"" help:"Task ID"`
	ListID string `help:"Task list ID" name:"list"`
}

// Run executes tasks done.
func (c *TasksDoneCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()

	listID := c.ListID
	if listID == "" {
		return fmt.Errorf("--list is required")
	}
	listID = graph.ResolveID(listID)

	body := map[string]interface{}{
		"status": "completed",
	}

	path := fmt.Sprintf("/me/todo/lists/%s/tasks/%s", listID, graph.ResolveID(c.TaskID))
	_, err = client.Patch(ctx, path, body)
	if err != nil {
		return err
	}

	fmt.Println("✓ Task completed")
	return nil
}

// TasksUndoCmd marks a task as not done.
type TasksUndoCmd struct {
	TaskID string `arg:"" help:"Task ID"`
	ListID string `help:"Task list ID" name:"list"`
}

// Run executes tasks undo.
func (c *TasksUndoCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()

	listID := c.ListID
	if listID == "" {
		return fmt.Errorf("--list is required")
	}
	listID = graph.ResolveID(listID)

	body := map[string]interface{}{
		"status": "notStarted",
	}

	path := fmt.Sprintf("/me/todo/lists/%s/tasks/%s", listID, graph.ResolveID(c.TaskID))
	_, err = client.Patch(ctx, path, body)
	if err != nil {
		return err
	}

	fmt.Println("✓ Task uncompleted")
	return nil
}

// TasksDeleteCmd deletes a task.
type TasksDeleteCmd struct {
	TaskID string `arg:"" help:"Task ID"`
	ListID string `help:"Task list ID" name:"list"`
}

// Run executes tasks delete.
func (c *TasksDeleteCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()

	listID := c.ListID
	if listID == "" {
		return fmt.Errorf("--list is required")
	}
	listID = graph.ResolveID(listID)

	path := fmt.Sprintf("/me/todo/lists/%s/tasks/%s", listID, graph.ResolveID(c.TaskID))
	if err := client.Delete(ctx, path); err != nil {
		return err
	}

	fmt.Println("✓ Task deleted")
	return nil
}

// TasksClearCmd clears completed tasks.
type TasksClearCmd struct {
	ListID string `arg:"" optional:"" help:"Task list ID"`
}

// Run executes tasks clear.
func (c *TasksClearCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()

	listID := c.ListID
	if listID == "" {
		data, err := client.Get(ctx, "/me/todo/lists", nil)
		if err != nil {
			return err
		}
		var resp struct {
			Value []TaskList `json:"value"`
		}
		if err := json.Unmarshal(data, &resp); err != nil {
			return err
		}
		if len(resp.Value) == 0 {
			return fmt.Errorf("no task lists found")
		}
		listID = resp.Value[0].ID
	} else {
		listID = graph.ResolveID(listID)
	}

	// Get completed tasks
	query := url.Values{}
	query.Set("$filter", "status eq 'completed'")

	path := fmt.Sprintf("/me/todo/lists/%s/tasks", listID)
	data, err := client.Get(ctx, path, query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Task `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	// Delete each completed task
	count := 0
	for _, task := range resp.Value {
		delPath := fmt.Sprintf("/me/todo/lists/%s/tasks/%s", listID, task.ID)
		if err := client.Delete(ctx, delPath); err != nil {
			fmt.Printf("Failed to delete %s: %v\n", task.Title, err)
			continue
		}
		count++
	}

	fmt.Printf("✓ Cleared %d completed tasks\n", count)
	return nil
}

// TaskList represents a task list.
type TaskList struct {
	ID          string `json:"id"`
	DisplayName string `json:"displayName"`
	IsOwner     bool   `json:"isOwner"`
}

// Task represents a task.
type Task struct {
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Status      string    `json:"status"`
	Importance  string    `json:"importance"`
	DueDateTime *DateTime `json:"dueDateTime"`
	Body        *TaskBody `json:"body"`
}

// DateTime represents a datetime.
type DateTime struct {
	DateTime string `json:"dateTime"`
	TimeZone string `json:"timeZone"`
}

// TaskBody represents task body.
type TaskBody struct {
	Content     string `json:"content"`
	ContentType string `json:"contentType"`
}
