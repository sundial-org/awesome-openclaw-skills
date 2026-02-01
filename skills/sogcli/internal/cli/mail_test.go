package cli

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParseRecipients(t *testing.T) {
	tests := []struct {
		input    string
		expected []string
	}{
		{"", nil},
		{"a@example.com", []string{"a@example.com"}},
		{"a@example.com,b@example.com", []string{"a@example.com", "b@example.com"}},
		{"a@example.com, b@example.com", []string{"a@example.com", "b@example.com"}},
		{"  a@example.com  ,  b@example.com  ", []string{"a@example.com", "b@example.com"}},
		{"a@example.com,,b@example.com", []string{"a@example.com", "b@example.com"}},
		{"  ,  ,  ", []string{}},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got := parseRecipients(tt.input)
			assert.Equal(t, tt.expected, got)
		})
	}
}
