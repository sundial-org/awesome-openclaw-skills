package cmd

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestRootCmd(t *testing.T) {
	tests := []struct {
		name    string
		args    []string
		wantOut []string
	}{
		{
			name:    "help",
			args:    []string{"--help"},
			wantOut: []string{"ecto", "command-line tool", "auth", "posts", "pages", "tags", "users", "site", "settings", "newsletters"},
		},
		{
			name:    "no args shows help",
			args:    []string{},
			wantOut: []string{"ecto", "command-line tool"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cmd := newTestRootCmd()
			stdout, _, err := executeCommand(cmd, tt.args...)
			require.NoError(t, err)

			for _, want := range tt.wantOut {
				assert.Contains(t, stdout, want)
			}
		})
	}
}

func TestRootCmdSiteFlag(t *testing.T) {
	_, cleanup := mockGhostServer(t)
	defer cleanup()

	// Test that --site flag is propagated
	cmd := newTestRootCmd()
	stdout, _, err := executeCommand(cmd, "site", "--site", "testsite")
	// Should work (env vars take precedence in tests)
	require.NoError(t, err)
	assert.Contains(t, stdout, "Test Site")
}

func TestRootCmdReturnsCommand(t *testing.T) {
	cmd := RootCmd()
	require.NotNil(t, cmd)
	assert.Equal(t, "ecto", cmd.Use)
}

func TestExecute(t *testing.T) {
	// Test that Execute doesn't panic with help flag
	// We can't easily test os.Exit behavior, but we can verify the function exists
	// and the command structure is correct
	cmd := RootCmd()
	require.NotNil(t, cmd)

	// Verify all subcommands are registered
	subcommands := []string{"auth", "posts", "post", "pages", "page", "tags", "tag", "users", "user", "site", "settings", "newsletters", "newsletter", "webhook", "image"}
	for _, sub := range subcommands {
		found := false
		for _, c := range cmd.Commands() {
			if c.Use == sub || c.Name() == sub {
				found = true
				break
			}
		}
		assert.True(t, found, "subcommand %s should be registered", sub)
	}
}

func TestRootCmdLongDescription(t *testing.T) {
	cmd := RootCmd()
	assert.Contains(t, cmd.Long, "ecto is a command-line tool")
	assert.Contains(t, cmd.Long, "ecto auth add")
	assert.Contains(t, cmd.Long, "ecto posts")
}

func TestAIHelp(t *testing.T) {
	cmd := newTestRootCmd()
	stdout, _, err := executeCommand(cmd, "--ai-help")

	require.NoError(t, err)
	assert.Contains(t, stdout, "# ecto - Ghost.io Admin API CLI")
	assert.Contains(t, stdout, "## Authentication")
	assert.Contains(t, stdout, "## Content Management")
	assert.Contains(t, stdout, "## Common Workflows")
}
