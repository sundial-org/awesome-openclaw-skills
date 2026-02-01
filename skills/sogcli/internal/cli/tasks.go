package cli

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/visionik/sogcli/internal/caldav"
)

// TasksCmd handles task operations.
type TasksCmd struct {
	List    TasksListCmd    `cmd:"" help:"List tasks"`
	Add     TasksAddCmd     `cmd:"" aliases:"create" help:"Add a task"`
	Get     TasksGetCmd     `cmd:"" help:"Get task details"`
	Update  TasksUpdateCmd  `cmd:"" help:"Update a task"`
	Done    TasksDoneCmd    `cmd:"" aliases:"complete" help:"Mark task as complete"`
	Undo    TasksUndoCmd    `cmd:"" aliases:"uncomplete,undone" help:"Mark task as incomplete"`
	Delete  TasksDeleteCmd  `cmd:"" aliases:"rm,del" help:"Delete a task"`
	Clear   TasksClearCmd   `cmd:"" help:"Clear completed tasks"`
	Due     TasksDueCmd     `cmd:"" help:"Tasks due by date"`
	Overdue TasksOverdueCmd `cmd:"" help:"Overdue tasks"`
	Lists   TasksListsCmd   `cmd:"" help:"List task lists (calendars)"`
}

// TasksListCmd lists tasks.
type TasksListCmd struct {
	List      string `arg:"" optional:"" help:"Task list path (default: primary)"`
	All       bool   `help:"Include completed tasks"`
	Max       int    `help:"Maximum tasks to return" default:"50"`
}

// Run executes the tasks list command.
func (c *TasksListCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	ctx := context.Background()
	tasks, err := client.ListTasks(ctx, listPath, c.All)
	if err != nil {
		return fmt.Errorf("failed to list tasks: %w", err)
	}

	if len(tasks) == 0 {
		fmt.Println("No tasks found.")
		return nil
	}

	// Limit results
	if c.Max > 0 && len(tasks) > c.Max {
		tasks = tasks[:c.Max]
	}

	if root.JSON {
		return outputTasksJSON(tasks)
	}

	return outputTasksTable(tasks)
}

// TasksAddCmd adds a new task.
type TasksAddCmd struct {
	Title       string   `arg:"" help:"Task title"`
	Due         string   `help:"Due date (YYYY-MM-DD or YYYY-MM-DDTHH:MM)"`
	Priority    int      `help:"Priority (1-9, 1=highest)" short:"p"`
	Description string   `help:"Task description" short:"d"`
	Categories  []string `help:"Categories/tags" short:"c"`
	List        string   `help:"Task list path (default: primary)"`
}

// Run executes the tasks add command.
func (c *TasksAddCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	task := &caldav.Task{
		UID:         generateTaskUID(),
		Summary:     c.Title,
		Description: c.Description,
		Priority:    c.Priority,
		Categories:  c.Categories,
		Status:      caldav.TaskStatusNeedsAction,
	}

	// Parse due date
	if c.Due != "" {
		due, err := parseTaskDate(c.Due)
		if err != nil {
			return fmt.Errorf("invalid --due: %w", err)
		}
		task.Due = due
	}

	ctx := context.Background()
	if err := client.CreateTask(ctx, listPath, task); err != nil {
		return fmt.Errorf("failed to create task: %w", err)
	}

	if root.JSON {
		return outputTasksJSON([]caldav.Task{*task})
	}

	fmt.Printf("Created task: %s (%s)\n", task.Summary, task.UID)
	return nil
}

// TasksGetCmd gets task details.
type TasksGetCmd struct {
	UID  string `arg:"" help:"Task UID"`
	List string `help:"Task list path (default: primary)"`
}

// Run executes the tasks get command.
func (c *TasksGetCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	ctx := context.Background()
	task, err := client.GetTask(ctx, listPath, c.UID)
	if err != nil {
		return fmt.Errorf("failed to get task: %w", err)
	}

	if root.JSON {
		return outputTasksJSON([]caldav.Task{*task})
	}

	return outputTaskDetail(task)
}

// TasksUpdateCmd updates a task.
type TasksUpdateCmd struct {
	UID         string `arg:"" help:"Task UID"`
	Title       string `help:"New title"`
	Due         string `help:"New due date (YYYY-MM-DD)"`
	Priority    int    `help:"New priority (1-9)" short:"p"`
	Description string `help:"New description" short:"d"`
	List        string `help:"Task list path (default: primary)"`
}

// Run executes the tasks update command.
func (c *TasksUpdateCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	ctx := context.Background()
	task, err := client.GetTask(ctx, listPath, c.UID)
	if err != nil {
		return fmt.Errorf("failed to get task: %w", err)
	}

	// Apply updates
	if c.Title != "" {
		task.Summary = c.Title
	}
	if c.Due != "" {
		due, err := parseTaskDate(c.Due)
		if err != nil {
			return fmt.Errorf("invalid --due: %w", err)
		}
		task.Due = due
	}
	if c.Priority > 0 {
		task.Priority = c.Priority
	}
	if c.Description != "" {
		task.Description = c.Description
	}

	if err := client.UpdateTask(ctx, listPath, task); err != nil {
		return fmt.Errorf("failed to update task: %w", err)
	}

	fmt.Printf("Updated task: %s\n", c.UID)
	return nil
}

// TasksDoneCmd marks a task as complete.
type TasksDoneCmd struct {
	UID  string `arg:"" help:"Task UID"`
	List string `help:"Task list path (default: primary)"`
}

// Run executes the tasks done command.
func (c *TasksDoneCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	ctx := context.Background()
	if err := client.CompleteTask(ctx, listPath, c.UID); err != nil {
		return fmt.Errorf("failed to complete task: %w", err)
	}

	fmt.Printf("Completed task: %s\n", c.UID)
	return nil
}

// TasksUndoCmd marks a task as incomplete.
type TasksUndoCmd struct {
	UID  string `arg:"" help:"Task UID"`
	List string `help:"Task list path (default: primary)"`
}

// Run executes the tasks undo command.
func (c *TasksUndoCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	ctx := context.Background()
	if err := client.UncompleteTask(ctx, listPath, c.UID); err != nil {
		return fmt.Errorf("failed to uncomplete task: %w", err)
	}

	fmt.Printf("Uncompleted task: %s\n", c.UID)
	return nil
}

// TasksDeleteCmd deletes a task.
type TasksDeleteCmd struct {
	UID  string `arg:"" help:"Task UID"`
	List string `help:"Task list path (default: primary)"`
}

// Run executes the tasks delete command.
func (c *TasksDeleteCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	ctx := context.Background()
	if err := client.DeleteTask(ctx, listPath, c.UID); err != nil {
		return fmt.Errorf("failed to delete task: %w", err)
	}

	fmt.Printf("Deleted task: %s\n", c.UID)
	return nil
}

// TasksClearCmd clears completed tasks.
type TasksClearCmd struct {
	List string `help:"Task list path (default: primary)"`
}

// Run executes the tasks clear command.
func (c *TasksClearCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	ctx := context.Background()
	tasks, err := client.ListTasks(ctx, listPath, true) // include completed
	if err != nil {
		return fmt.Errorf("failed to list tasks: %w", err)
	}

	count := 0
	for _, t := range tasks {
		if t.Status == caldav.TaskStatusCompleted {
			if err := client.DeleteTask(ctx, listPath, t.UID); err != nil {
				fmt.Printf("Failed to delete %s: %v\n", t.UID, err)
				continue
			}
			count++
		}
	}

	fmt.Printf("Cleared %d completed tasks\n", count)
	return nil
}

// TasksDueCmd lists tasks due by a date.
type TasksDueCmd struct {
	Date string `arg:"" help:"Due date (YYYY-MM-DD, today, tomorrow, +Nd)"`
	List string `help:"Task list path (default: primary)"`
}

// Run executes the tasks due command.
func (c *TasksDueCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	dueBy, err := parseDate(c.Date)
	if err != nil {
		return fmt.Errorf("invalid date: %w", err)
	}
	// Include the full day
	dueBy = dueBy.AddDate(0, 0, 1)

	ctx := context.Background()
	allTasks, err := client.ListTasks(ctx, listPath, false)
	if err != nil {
		return fmt.Errorf("failed to list tasks: %w", err)
	}

	// Filter by due date
	var tasks []caldav.Task
	for _, t := range allTasks {
		if !t.Due.IsZero() && t.Due.Before(dueBy) {
			tasks = append(tasks, t)
		}
	}

	if len(tasks) == 0 {
		fmt.Println("No tasks due.")
		return nil
	}

	if root.JSON {
		return outputTasksJSON(tasks)
	}

	return outputTasksTable(tasks)
}

// TasksOverdueCmd lists overdue tasks.
type TasksOverdueCmd struct {
	List string `help:"Task list path (default: primary)"`
}

// Run executes the tasks overdue command.
func (c *TasksOverdueCmd) Run(root *Root) error {
	client, listPath, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.List != "" {
		listPath = c.List
	}

	now := time.Now()

	ctx := context.Background()
	allTasks, err := client.ListTasks(ctx, listPath, false)
	if err != nil {
		return fmt.Errorf("failed to list tasks: %w", err)
	}

	// Filter overdue
	var tasks []caldav.Task
	for _, t := range allTasks {
		if !t.Due.IsZero() && t.Due.Before(now) {
			tasks = append(tasks, t)
		}
	}

	if len(tasks) == 0 {
		fmt.Println("No overdue tasks.")
		return nil
	}

	if root.JSON {
		return outputTasksJSON(tasks)
	}

	return outputTasksTable(tasks)
}

// TasksListsCmd lists available task lists.
type TasksListsCmd struct{}

// Run executes the tasks lists command.
func (c *TasksListsCmd) Run(root *Root) error {
	client, _, err := getCalDAVClientForTasks(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	calendars, err := client.FindCalendars(ctx)
	if err != nil {
		return fmt.Errorf("failed to list task lists: %w", err)
	}

	if len(calendars) == 0 {
		fmt.Println("No task lists found.")
		return nil
	}

	if root.JSON {
		return outputCalendarsJSON(calendars)
	}

	fmt.Printf("%-50s %s\n", "PATH", "NAME")
	for _, cal := range calendars {
		fmt.Printf("%-50s %s\n", cal.Path, cal.Name)
	}
	return nil
}

// getCalDAVClientForTasks creates a CalDAV client from config for task operations.
func getCalDAVClientForTasks(root *Root) (*caldav.Client, string, error) {
	// Reuse the calendar client - tasks are stored in CalDAV
	return getCalDAVClient(root)
}

// parseTaskDate parses a date string for task due dates.
func parseTaskDate(s string) (time.Time, error) {
	// Try datetime first
	t, err := time.Parse("2006-01-02T15:04", s)
	if err == nil {
		return t, nil
	}

	// Try date only (set to end of day)
	t, err = time.Parse("2006-01-02", s)
	if err == nil {
		return t.Add(23*time.Hour + 59*time.Minute), nil
	}

	// Try relative dates
	return parseDate(s)
}

// generateTaskUID generates a unique identifier for a task.
func generateTaskUID() string {
	return fmt.Sprintf("task-%d@sog", time.Now().UnixNano())
}

// outputTasksJSON outputs tasks as JSON.
func outputTasksJSON(tasks []caldav.Task) error {
	for _, t := range tasks {
		dueStr := ""
		if !t.Due.IsZero() {
			dueStr = t.Due.Format(time.RFC3339)
		}
		fmt.Printf(`{"uid":"%s","summary":"%s","status":"%s","due":"%s","priority":%d}`+"\n",
			t.UID, t.Summary, t.Status, dueStr, t.Priority)
	}
	return nil
}

// outputTasksTable outputs tasks as a table.
func outputTasksTable(tasks []caldav.Task) error {
	fmt.Printf("%-4s %-12s %-8s %s\n", "PRI", "DUE", "STATUS", "SUMMARY")
	for _, t := range tasks {
		pri := "-"
		if t.Priority > 0 {
			pri = fmt.Sprintf("%d", t.Priority)
		}
		due := "-"
		if !t.Due.IsZero() {
			due = t.Due.Format("2006-01-02")
		}
		status := statusShort(t.Status)
		summary := t.Summary
		if len(summary) > 50 {
			summary = summary[:47] + "..."
		}
		fmt.Printf("%-4s %-12s %-8s %s\n", pri, due, status, summary)
	}
	return nil
}

// statusShort returns a short status string.
func statusShort(status string) string {
	switch status {
	case caldav.TaskStatusNeedsAction:
		return "TODO"
	case caldav.TaskStatusInProcess:
		return "DOING"
	case caldav.TaskStatusCompleted:
		return "DONE"
	case caldav.TaskStatusCancelled:
		return "CANCEL"
	default:
		return status
	}
}

// outputTaskDetail outputs a single task in detail.
func outputTaskDetail(task *caldav.Task) error {
	fmt.Printf("UID:         %s\n", task.UID)
	fmt.Printf("Summary:     %s\n", task.Summary)
	fmt.Printf("Status:      %s\n", task.Status)
	if task.Priority > 0 {
		fmt.Printf("Priority:    %d\n", task.Priority)
	}
	if !task.Due.IsZero() {
		fmt.Printf("Due:         %s\n", task.Due.Format("2006-01-02 15:04"))
	}
	if !task.Start.IsZero() {
		fmt.Printf("Start:       %s\n", task.Start.Format("2006-01-02 15:04"))
	}
	if !task.Completed.IsZero() {
		fmt.Printf("Completed:   %s\n", task.Completed.Format("2006-01-02 15:04"))
	}
	if task.Percent > 0 {
		fmt.Printf("Progress:    %d%%\n", task.Percent)
	}
	if len(task.Categories) > 0 {
		fmt.Printf("Categories:  %s\n", strings.Join(task.Categories, ", "))
	}
	if task.Description != "" {
		fmt.Printf("Description: %s\n", task.Description)
	}
	return nil
}
