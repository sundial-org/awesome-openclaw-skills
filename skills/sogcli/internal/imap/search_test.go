package imap

import (
	"testing"
	"time"

	"github.com/emersion/go-imap/v2"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestParseSearchQueryALL(t *testing.T) {
	criteria, err := parseSearchQuery("ALL")
	require.NoError(t, err)
	assert.Nil(t, criteria) // ALL returns nil for fallback
}

func TestParseSearchQueryAllLowercase(t *testing.T) {
	criteria, err := parseSearchQuery("all")
	require.NoError(t, err)
	assert.Nil(t, criteria)
}

func TestParseSearchQueryFROM(t *testing.T) {
	criteria, err := parseSearchQuery("FROM viz")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	require.Len(t, criteria.Header, 1)
	assert.Equal(t, "From", criteria.Header[0].Key)
	assert.Equal(t, "viz", criteria.Header[0].Value)
}

func TestParseSearchQueryTO(t *testing.T) {
	criteria, err := parseSearchQuery("TO user@example.com")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	require.Len(t, criteria.Header, 1)
	assert.Equal(t, "To", criteria.Header[0].Key)
	assert.Equal(t, "user@example.com", criteria.Header[0].Value)
}

func TestParseSearchQuerySUBJECT(t *testing.T) {
	criteria, err := parseSearchQuery("SUBJECT meeting")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	require.Len(t, criteria.Header, 1)
	assert.Equal(t, "Subject", criteria.Header[0].Key)
	assert.Equal(t, "meeting", criteria.Header[0].Value)
}

func TestParseSearchQueryTEXT(t *testing.T) {
	criteria, err := parseSearchQuery("TEXT important")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Contains(t, criteria.Text, "important")
}

func TestParseSearchQueryBODY(t *testing.T) {
	criteria, err := parseSearchQuery("BODY content")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Contains(t, criteria.Text, "content")
}

func TestParseSearchQueryUNSEEN(t *testing.T) {
	criteria, err := parseSearchQuery("UNSEEN")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Contains(t, criteria.NotFlag, imap.FlagSeen)
}

func TestParseSearchQueryUNREAD(t *testing.T) {
	criteria, err := parseSearchQuery("UNREAD")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Contains(t, criteria.NotFlag, imap.FlagSeen)
}

func TestParseSearchQuerySEEN(t *testing.T) {
	criteria, err := parseSearchQuery("SEEN")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Contains(t, criteria.Flag, imap.FlagSeen)
}

func TestParseSearchQueryFLAGGED(t *testing.T) {
	criteria, err := parseSearchQuery("FLAGGED")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Contains(t, criteria.Flag, imap.FlagFlagged)
}

func TestParseSearchQuerySTARRED(t *testing.T) {
	criteria, err := parseSearchQuery("STARRED")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Contains(t, criteria.Flag, imap.FlagFlagged)
}

func TestParseSearchQuerySINCE(t *testing.T) {
	criteria, err := parseSearchQuery("SINCE 1-Jan-2026")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Equal(t, 2026, criteria.Since.Year())
	assert.Equal(t, time.January, criteria.Since.Month())
	assert.Equal(t, 1, criteria.Since.Day())
}

func TestParseSearchQueryBEFORE(t *testing.T) {
	criteria, err := parseSearchQuery("BEFORE 31-Dec-2025")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Equal(t, 2025, criteria.Before.Year())
	assert.Equal(t, time.December, criteria.Before.Month())
	assert.Equal(t, 31, criteria.Before.Day())
}

func TestParseSearchQueryCombined(t *testing.T) {
	criteria, err := parseSearchQuery("FROM viz SUBJECT meeting UNSEEN")
	require.NoError(t, err)
	require.NotNil(t, criteria)

	// Should have 2 header criteria
	require.Len(t, criteria.Header, 2)

	// Check From
	var hasFrom, hasSubject bool
	for _, h := range criteria.Header {
		if h.Key == "From" && h.Value == "viz" {
			hasFrom = true
		}
		if h.Key == "Subject" && h.Value == "meeting" {
			hasSubject = true
		}
	}
	assert.True(t, hasFrom, "should have FROM criteria")
	assert.True(t, hasSubject, "should have SUBJECT criteria")

	// Should have unseen flag
	assert.Contains(t, criteria.NotFlag, imap.FlagSeen)
}

func TestParseSearchQueryUnknownAsText(t *testing.T) {
	criteria, err := parseSearchQuery("foobar")
	require.NoError(t, err)
	require.NotNil(t, criteria)
	assert.Contains(t, criteria.Text, "foobar")
}

func TestParseDateFormats(t *testing.T) {
	tests := []struct {
		input string
		year  int
		month time.Month
		day   int
	}{
		{"1-Jan-2026", 2026, time.January, 1},
		{"01-Jan-2026", 2026, time.January, 1},
		{"2026-01-15", 2026, time.January, 15},
		{"01/15/2026", 2026, time.January, 15},
		{"1/5/2026", 2026, time.January, 5},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got, err := parseDate(tt.input)
			require.NoError(t, err)
			assert.Equal(t, tt.year, got.Year())
			assert.Equal(t, tt.month, got.Month())
			assert.Equal(t, tt.day, got.Day())
		})
	}
}

func TestParseDateInvalid(t *testing.T) {
	_, err := parseDate("not-a-date")
	assert.Error(t, err)
}
