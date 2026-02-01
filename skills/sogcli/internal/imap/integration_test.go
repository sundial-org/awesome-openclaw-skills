//go:build integration

package imap

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Integration tests run against GreenMail
// Run with: go test -tags=integration ./...

func getTestConfig() Config {
	host := os.Getenv("TEST_IMAP_HOST")
	if host == "" {
		host = "localhost"
	}
	return Config{
		Host:     host,
		Port:     3143,
		NoTLS:    true,
		Email:    "integration@test.com",
		Password: "test",
	}
}

func TestIntegrationConnect(t *testing.T) {
	cfg := getTestConfig()

	client, err := Connect(cfg)
	require.NoError(t, err)
	require.NotNil(t, client)

	err = client.Close()
	assert.NoError(t, err)
}

func TestIntegrationListFolders(t *testing.T) {
	cfg := getTestConfig()

	client, err := Connect(cfg)
	require.NoError(t, err)
	defer client.Close()

	folders, err := client.ListFolders()
	require.NoError(t, err)
	assert.Contains(t, folders, "INBOX")
}

func TestIntegrationCreateDeleteFolder(t *testing.T) {
	cfg := getTestConfig()

	client, err := Connect(cfg)
	require.NoError(t, err)
	defer client.Close()

	// Create
	err = client.CreateFolder("TestFolder")
	require.NoError(t, err)

	// Verify exists
	folders, err := client.ListFolders()
	require.NoError(t, err)
	assert.Contains(t, folders, "TestFolder")

	// Delete
	err = client.DeleteFolder("TestFolder")
	require.NoError(t, err)

	// Verify gone
	folders, err = client.ListFolders()
	require.NoError(t, err)
	assert.NotContains(t, folders, "TestFolder")
}

func TestIntegrationListMessages(t *testing.T) {
	cfg := getTestConfig()

	client, err := Connect(cfg)
	require.NoError(t, err)
	defer client.Close()

	// Just verify it doesn't error - messages may or may not exist
	_, err = client.ListMessages("INBOX", 10, false)
	require.NoError(t, err)
}

func TestIntegrationRenameFolder(t *testing.T) {
	cfg := getTestConfig()

	client, err := Connect(cfg)
	require.NoError(t, err)
	defer client.Close()

	// Create
	err = client.CreateFolder("OldName")
	require.NoError(t, err)

	// Rename
	err = client.RenameFolder("OldName", "NewName")
	require.NoError(t, err)

	// Verify
	folders, err := client.ListFolders()
	require.NoError(t, err)
	assert.Contains(t, folders, "NewName")
	assert.NotContains(t, folders, "OldName")

	// Cleanup
	err = client.DeleteFolder("NewName")
	require.NoError(t, err)
}

func TestIntegrationSetFlag(t *testing.T) {
	cfg := getTestConfig()

	client, err := Connect(cfg)
	require.NoError(t, err)
	defer client.Close()

	// Need a message to flag - check if we have any
	messages, err := client.ListMessages("INBOX", 1, false)
	require.NoError(t, err)

	if len(messages) > 0 {
		uid := messages[0].UID
		
		// Set seen flag
		err = client.SetFlag("INBOX", uid, "seen", true)
		require.NoError(t, err)

		// Remove seen flag
		err = client.SetFlag("INBOX", uid, "seen", false)
		require.NoError(t, err)
	}
}

func TestIntegrationCopyMove(t *testing.T) {
	cfg := getTestConfig()

	client, err := Connect(cfg)
	require.NoError(t, err)
	defer client.Close()

	// Create test folder
	err = client.CreateFolder("CopyTest")
	require.NoError(t, err)
	defer client.DeleteFolder("CopyTest")

	// Check if we have messages to copy
	messages, err := client.ListMessages("INBOX", 1, false)
	require.NoError(t, err)

	if len(messages) > 0 {
		uid := messages[0].UID

		// Copy message
		err = client.CopyMessage("INBOX", uid, "CopyTest")
		require.NoError(t, err)

		// Verify copy exists
		copied, err := client.ListMessages("CopyTest", 10, false)
		require.NoError(t, err)
		assert.NotEmpty(t, copied)
	}
}

func TestIntegrationGetMessage(t *testing.T) {
	cfg := getTestConfig()

	client, err := Connect(cfg)
	require.NoError(t, err)
	defer client.Close()

	// Check if we have messages
	messages, err := client.ListMessages("INBOX", 1, false)
	require.NoError(t, err)

	if len(messages) > 0 {
		uid := messages[0].UID

		// Get full message
		msg, err := client.GetMessage("INBOX", uid, false)
		require.NoError(t, err)
		assert.NotNil(t, msg)
		assert.Equal(t, uid, msg.UID)

		// Get headers only
		msg, err = client.GetMessage("INBOX", uid, true)
		require.NoError(t, err)
		assert.NotNil(t, msg)
	}
}

func TestIntegrationSearchMessages(t *testing.T) {
	cfg := getTestConfig()

	client, err := Connect(cfg)
	require.NoError(t, err)
	defer client.Close()

	// Test ALL search (fallback)
	_, err = client.SearchMessages("INBOX", "ALL", 10)
	require.NoError(t, err)
	// May have messages or not

	// Test UNSEEN search
	_, err = client.SearchMessages("INBOX", "UNSEEN", 10)
	require.NoError(t, err)

	// Test combined search
	_, err = client.SearchMessages("INBOX", "FROM test SUBJECT test", 10)
	require.NoError(t, err)
}
