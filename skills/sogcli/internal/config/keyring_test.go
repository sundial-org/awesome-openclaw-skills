package config

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestSanitizeEnvKey(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"user@example.com", "USER_EXAMPLE_COM"},
		{"test@sub.domain.org", "TEST_SUB_DOMAIN_ORG"},
		{"user-name@test.io", "USER_NAME_TEST_IO"},
		{"simple", "SIMPLE"},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got := sanitizeEnvKey(tt.input)
			assert.Equal(t, tt.expected, got)
		})
	}
}
