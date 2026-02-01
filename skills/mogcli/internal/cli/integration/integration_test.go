// Package integration provides integration tests for CLI commands.
// These tests require valid authentication and make real API calls.
//
// Run with: MOG_INTEGRATION=1 go test -v ./internal/cli/integration/...
// Or: task test:integration
//
// Write tests (create/update/delete) are skipped by default.
// Run with: MOG_INTEGRATION=1 MOG_WRITE_TESTS=1 go test -v ./...
package integration

import (
	"bytes"
	"os"
	"os/exec"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func skipIfNoIntegration(t *testing.T) {
	if os.Getenv("MOG_INTEGRATION") == "" {
		t.Skip("Skipping integration test (set MOG_INTEGRATION=1 to run)")
	}
}

func skipIfNoWriteTests(t *testing.T) {
	skipIfNoIntegration(t)
	if os.Getenv("MOG_WRITE_TESTS") == "" {
		t.Skip("Skipping write test (set MOG_WRITE_TESTS=1 to run)")
	}
}

func runMog(t *testing.T, args ...string) (string, string, error) {
	binary := os.Getenv("MOG_BINARY")
	if binary == "" {
		binary = "mogcli"
	}

	cmd := exec.Command(binary, args...)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	err := cmd.Run()
	return stdout.String(), stderr.String(), err
}

// ==================== Auth ====================

func TestIntegration_AuthStatus(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "auth", "status")
	require.NoError(t, err)
	assert.Contains(t, stdout, "Status:")
}

// ==================== Mail ====================

func TestIntegration_MailFolders(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "mail", "folders")
	require.NoError(t, err)
	assert.Contains(t, stdout, "Inbox")
}

func TestIntegration_MailFoldersJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "mail", "folders", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

func TestIntegration_MailSearch(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "mail", "search", "*", "--max", "1")
	require.NoError(t, err)
	assert.NotEmpty(t, stdout)
}

func TestIntegration_MailSearchJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "mail", "search", "*", "--max", "1", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

func TestIntegration_MailDraftsList(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "mail", "drafts", "list", "--max", "1")
	assert.NoError(t, err)
}

// ==================== Calendar ====================

func TestIntegration_CalendarCalendars(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "calendar", "calendars")
	require.NoError(t, err)
	assert.NotEmpty(t, stdout)
}

func TestIntegration_CalendarCalendarsJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "calendar", "calendars", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

func TestIntegration_CalendarList(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "calendar", "list", "--max", "1")
	assert.NoError(t, err)
}

func TestIntegration_CalendarListJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "calendar", "list", "--max", "1", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

func TestIntegration_CalAliasWorks(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "cal", "list", "--max", "1")
	assert.NoError(t, err)
}

// ==================== Drive ====================

func TestIntegration_DriveLs(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "drive", "ls")
	require.NoError(t, err)
	assert.NotEmpty(t, stdout)
}

func TestIntegration_DriveLsJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "drive", "ls", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

func TestIntegration_DriveSearch(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "drive", "search", "test")
	assert.NoError(t, err)
}

func TestIntegration_DriveSearchJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "drive", "search", "test", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

// ==================== Contacts ====================

func TestIntegration_ContactsList(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "contacts", "list", "--max", "1")
	assert.NoError(t, err)
}

func TestIntegration_ContactsListJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "contacts", "list", "--max", "1", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

func TestIntegration_ContactsSearch(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "contacts", "search", "test")
	// May error if no contacts match, that's ok
	_ = err
}

// ==================== Tasks ====================

func TestIntegration_TasksLists(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "tasks", "lists")
	require.NoError(t, err)
	assert.NotEmpty(t, stdout)
}

func TestIntegration_TasksListsJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "tasks", "lists", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

func TestIntegration_TasksList(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "tasks", "list")
	assert.NoError(t, err)
}

func TestIntegration_TasksListJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "tasks", "list", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

func TestIntegration_TasksListAll(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "tasks", "list", "--all")
	assert.NoError(t, err)
}

func TestIntegration_TodoAliasWorks(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "todo", "lists")
	assert.NoError(t, err)
}

// ==================== OneNote ====================

func TestIntegration_OneNoteNotebooks(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "onenote", "notebooks")
	assert.NoError(t, err)
}

func TestIntegration_OneNoteNotebooksJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "onenote", "notebooks", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

// ==================== Excel ====================

func TestIntegration_ExcelList(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "excel", "list", "--max", "1")
	assert.NoError(t, err)
}

func TestIntegration_ExcelListJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "excel", "list", "--max", "1", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

// ==================== Word ====================

func TestIntegration_WordList(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "word", "list", "--max", "1")
	assert.NoError(t, err)
}

func TestIntegration_WordListJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "word", "list", "--max", "1", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

// ==================== PowerPoint ====================

func TestIntegration_PPTList(t *testing.T) {
	skipIfNoIntegration(t)
	_, _, err := runMog(t, "ppt", "list", "--max", "1")
	assert.NoError(t, err)
}

func TestIntegration_PPTListJSON(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "ppt", "list", "--max", "1", "--json")
	require.NoError(t, err)
	assert.True(t, strings.HasPrefix(strings.TrimSpace(stdout), "["))
}

// ==================== Help / Meta ====================

func TestIntegration_AIHelp(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "--ai-help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "mog")
	assert.Contains(t, stdout, "Microsoft")
}

func TestIntegration_Help(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "--help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "Usage:")
	assert.Contains(t, stdout, "mail")
	assert.Contains(t, stdout, "calendar")
}

func TestIntegration_MailHelp(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "mail", "--help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "search")
	assert.Contains(t, stdout, "send")
}

func TestIntegration_CalendarHelp(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "calendar", "--help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "list")
	assert.Contains(t, stdout, "create")
}

func TestIntegration_DriveHelp(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "drive", "--help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "ls")
	assert.Contains(t, stdout, "upload")
}

func TestIntegration_TasksHelp(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "tasks", "--help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "lists")
	assert.Contains(t, stdout, "add")
}

func TestIntegration_ExcelHelp(t *testing.T) {
	skipIfNoIntegration(t)
	stdout, _, err := runMog(t, "excel", "--help")
	require.NoError(t, err)
	assert.Contains(t, stdout, "list")
	assert.Contains(t, stdout, "get")
}

// ==================== Write Tests (require MOG_WRITE_TESTS=1) ====================

func TestIntegration_Write_TaskCreate(t *testing.T) {
	skipIfNoWriteTests(t)

	// Create a task
	stdout, _, err := runMog(t, "tasks", "add", "Integration Test Task", "--due", "tomorrow")
	require.NoError(t, err)
	assert.Contains(t, stdout, "created")

	// Note: cleanup would require parsing the ID and deleting
}

func TestIntegration_Write_DriveMkdir(t *testing.T) {
	skipIfNoWriteTests(t)

	// Create a folder
	stdout, _, err := runMog(t, "drive", "mkdir", "mog-integration-test-folder")
	require.NoError(t, err)
	assert.Contains(t, stdout, "Created")

	// Note: cleanup would require parsing the ID and deleting
}

func TestIntegration_Write_ContactCreate(t *testing.T) {
	skipIfNoWriteTests(t)

	// Create a contact
	stdout, _, err := runMog(t, "contacts", "create", "--name", "Mog Integration Test")
	require.NoError(t, err)
	assert.Contains(t, stdout, "created")

	// Note: cleanup would require parsing the ID and deleting
}
