package discover

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDiscoverGmail(t *testing.T) {
	result, err := Discover("test@gmail.com")
	require.NoError(t, err)
	require.NotNil(t, result)
	
	assert.Equal(t, "imap.gmail.com", result.IMAP.Host)
	assert.Equal(t, 993, result.IMAP.Port)
	assert.Equal(t, "smtp.gmail.com", result.SMTP.Host)
	assert.Equal(t, 587, result.SMTP.Port)
}

func TestDiscoverCustomDomain(t *testing.T) {
	// Test discovery for a domain with mail servers
	result, err := Discover("test@entrenext.com")
	require.NoError(t, err)
	require.NotNil(t, result)
	
	// Should find IMAP and SMTP servers
	require.NotNil(t, result.IMAP)
	require.NotNil(t, result.SMTP)
	assert.NotEmpty(t, result.IMAP.Host)
	assert.NotEmpty(t, result.SMTP.Host)
}

func TestDiscoverInvalidEmail(t *testing.T) {
	_, err := Discover("invalid-email")
	assert.Error(t, err)
}

func TestIsGoogleDomain(t *testing.T) {
	assert.True(t, isGoogleDomain("gmail.com"))
	assert.True(t, isGoogleDomain("googlemail.com"))
}

func TestIsMicrosoftDomain(t *testing.T) {
	assert.True(t, isMicrosoftDomain("outlook.com"))
	assert.True(t, isMicrosoftDomain("hotmail.com"))
	assert.True(t, isMicrosoftDomain("live.com"))
}
