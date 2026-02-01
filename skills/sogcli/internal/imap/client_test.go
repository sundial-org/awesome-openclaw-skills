package imap

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConfigDefaults(t *testing.T) {
	cfg := Config{
		Host:     "imap.example.com",
		Port:     993,
		TLS:      true,
		Email:    "user@example.com",
		Password: "secret",
	}

	assert.Equal(t, "imap.example.com", cfg.Host)
	assert.Equal(t, 993, cfg.Port)
	assert.True(t, cfg.TLS)
	assert.False(t, cfg.Insecure)
	assert.False(t, cfg.NoTLS)
}

func TestConfigInsecure(t *testing.T) {
	cfg := Config{
		Host:     "localhost",
		Port:     3993,
		TLS:      true,
		Insecure: true,
		Email:    "test@localhost",
	}

	assert.True(t, cfg.TLS)
	assert.True(t, cfg.Insecure)
}

func TestConfigNoTLS(t *testing.T) {
	cfg := Config{
		Host:  "localhost",
		Port:  3143,
		NoTLS: true,
		Email: "test@localhost",
	}

	assert.True(t, cfg.NoTLS)
	assert.False(t, cfg.TLS)
}

func TestMessageStruct(t *testing.T) {
	msg := Message{
		UID:     12345,
		Subject: "Test Subject",
		From:    "sender@example.com",
		To:      "recipient@example.com",
		Date:    "Jan 20",
		Seen:    true,
		Body:    "Hello, World!",
	}

	assert.Equal(t, uint32(12345), msg.UID)
	assert.Equal(t, "Test Subject", msg.Subject)
	assert.Equal(t, "sender@example.com", msg.From)
	assert.Equal(t, "recipient@example.com", msg.To)
	assert.Equal(t, "Jan 20", msg.Date)
	assert.True(t, msg.Seen)
	assert.Equal(t, "Hello, World!", msg.Body)
}

func TestMessageUnread(t *testing.T) {
	msg := Message{
		UID:     1,
		Subject: "Unread message",
		Seen:    false,
	}

	assert.False(t, msg.Seen)
}
