package smtp

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewClient(t *testing.T) {
	cfg := Config{
		Host:     "smtp.example.com",
		Port:     587,
		TLS:      false,
		StartTLS: true,
		Insecure: false,
		NoTLS:    false,
		Email:    "user@example.com",
		Password: "secret",
	}

	client := NewClient(cfg)

	assert.Equal(t, "smtp.example.com", client.host)
	assert.Equal(t, 587, client.port)
	assert.False(t, client.tls)
	assert.True(t, client.startTLS)
	assert.False(t, client.insecure)
	assert.False(t, client.noTLS)
	assert.Equal(t, "user@example.com", client.email)
	assert.Equal(t, "secret", client.password)
}

func TestNewClientTLS(t *testing.T) {
	cfg := Config{
		Host:     "smtp.example.com",
		Port:     465,
		TLS:      true,
		StartTLS: false,
		Email:    "user@example.com",
		Password: "secret",
	}

	client := NewClient(cfg)

	assert.True(t, client.tls)
	assert.False(t, client.startTLS)
}

func TestNewClientNoTLS(t *testing.T) {
	cfg := Config{
		Host:  "localhost",
		Port:  25,
		NoTLS: true,
		Email: "test@localhost",
	}

	client := NewClient(cfg)

	assert.True(t, client.noTLS)
	assert.False(t, client.tls)
}

func TestMessageRecipients(t *testing.T) {
	msg := &Message{
		From:    "sender@example.com",
		To:      []string{"to1@example.com", "to2@example.com"},
		Cc:      []string{"cc@example.com"},
		Bcc:     []string{"bcc@example.com"},
		Subject: "Test",
		Body:    "Hello",
	}

	// Verify fields are set correctly
	assert.Equal(t, "sender@example.com", msg.From)
	assert.Len(t, msg.To, 2)
	assert.Len(t, msg.Cc, 1)
	assert.Len(t, msg.Bcc, 1)
	assert.Equal(t, "Test", msg.Subject)
	assert.Equal(t, "Hello", msg.Body)
}
