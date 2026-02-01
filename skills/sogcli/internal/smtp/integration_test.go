//go:build integration

package smtp

import (
	"os"
	"testing"

	"github.com/stretchr/testify/require"
)

// Integration tests run against GreenMail
// Run with: go test -tags=integration ./...

func getTestConfig() Config {
	host := os.Getenv("TEST_SMTP_HOST")
	if host == "" {
		host = "localhost"
	}
	return Config{
		Host:     host,
		Port:     3025,
		NoTLS:    true,
		Email:    "sender@test.com",
		Password: "test",
	}
}

func TestIntegrationConnect(t *testing.T) {
	cfg := getTestConfig()
	client := NewClient(cfg)

	err := client.TestConnection()
	require.NoError(t, err)
}

func TestIntegrationSend(t *testing.T) {
	cfg := getTestConfig()
	client := NewClient(cfg)

	msg := &Message{
		From:    "sender@test.com",
		To:      []string{"recipient@test.com"},
		Subject: "Integration Test",
		Body:    "This is a test message from integration tests.",
	}

	err := client.Send(msg)
	require.NoError(t, err)
}

func TestIntegrationSendWithCC(t *testing.T) {
	cfg := getTestConfig()
	client := NewClient(cfg)

	msg := &Message{
		From:    "sender@test.com",
		To:      []string{"to@test.com"},
		Cc:      []string{"cc@test.com"},
		Subject: "Test with CC",
		Body:    "Testing CC recipients.",
	}

	err := client.Send(msg)
	require.NoError(t, err)
}

func TestIntegrationSendWithBCC(t *testing.T) {
	cfg := getTestConfig()
	client := NewClient(cfg)

	msg := &Message{
		From:    "sender@test.com",
		To:      []string{"to@test.com"},
		Bcc:     []string{"bcc@test.com"},
		Subject: "Test with BCC",
		Body:    "Testing BCC recipients.",
	}

	err := client.Send(msg)
	require.NoError(t, err)
}
