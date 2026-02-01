package caldav

import (
	"strings"
	"testing"
	"time"

	"github.com/emersion/go-ical"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestParseICalEvent(t *testing.T) {
	tests := []struct {
		name     string
		icalData string
		want     *Event
		wantErr  bool
	}{
		{
			name: "simple event",
			icalData: `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:test-123@example.com
SUMMARY:Team Meeting
DESCRIPTION:Weekly sync
LOCATION:Conference Room A
DTSTART:20260115T100000Z
DTEND:20260115T110000Z
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR`,
			want: &Event{
				UID:         "test-123@example.com",
				Summary:     "Team Meeting",
				Description: "Weekly sync",
				Location:    "Conference Room A",
				Status:      "CONFIRMED",
				AllDay:      false,
			},
			wantErr: false,
		},
		{
			name: "all-day event",
			icalData: `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:allday-456@example.com
SUMMARY:Holiday
DTSTART;VALUE=DATE:20260125
DTEND;VALUE=DATE:20260126
END:VEVENT
END:VCALENDAR`,
			want: &Event{
				UID:     "allday-456@example.com",
				Summary: "Holiday",
				AllDay:  true,
			},
			wantErr: false,
		},
		{
			name: "event with attendees",
			icalData: `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:meeting-789@example.com
SUMMARY:Review
ORGANIZER:mailto:boss@example.com
ATTENDEE:mailto:alice@example.com
ATTENDEE:mailto:bob@example.com
DTSTART:20260120T140000Z
DTEND:20260120T150000Z
END:VEVENT
END:VCALENDAR`,
			want: &Event{
				UID:       "meeting-789@example.com",
				Summary:   "Review",
				Organizer: "boss@example.com",
				Attendees: []string{"alice@example.com", "bob@example.com"},
				AllDay:    false,
			},
			wantErr: false,
		},
		{
			name: "empty calendar",
			icalData: `BEGIN:VCALENDAR
VERSION:2.0
END:VCALENDAR`,
			want:    nil,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cal, err := ical.NewDecoder(strings.NewReader(tt.icalData)).Decode()
			require.NoError(t, err)

			got, err := parseICalEvent(cal)
			if tt.wantErr {
				assert.Error(t, err)
				return
			}
			require.NoError(t, err)

			assert.Equal(t, tt.want.UID, got.UID)
			assert.Equal(t, tt.want.Summary, got.Summary)
			assert.Equal(t, tt.want.Description, got.Description)
			assert.Equal(t, tt.want.Location, got.Location)
			assert.Equal(t, tt.want.Status, got.Status)
			assert.Equal(t, tt.want.AllDay, got.AllDay)
			assert.Equal(t, tt.want.Organizer, got.Organizer)
			assert.Equal(t, tt.want.Attendees, got.Attendees)
		})
	}
}

func TestParseICalEvent_NilCalendar(t *testing.T) {
	_, err := parseICalEvent(nil)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "nil calendar")
}

func TestCreateICalEvent(t *testing.T) {
	tests := []struct {
		name  string
		event *Event
	}{
		{
			name: "simple event",
			event: &Event{
				UID:         "create-test-1@sog",
				Summary:     "Test Event",
				Description: "A test event",
				Location:    "Test Location",
				Start:       time.Date(2026, 1, 15, 10, 0, 0, 0, time.UTC),
				End:         time.Date(2026, 1, 15, 11, 0, 0, 0, time.UTC),
				AllDay:      false,
			},
		},
		{
			name: "all-day event",
			event: &Event{
				UID:     "create-test-2@sog",
				Summary: "All Day Event",
				Start:   time.Date(2026, 1, 20, 0, 0, 0, 0, time.UTC),
				End:     time.Date(2026, 1, 21, 0, 0, 0, 0, time.UTC),
				AllDay:  true,
			},
		},
		{
			name: "event with attendees",
			event: &Event{
				UID:       "create-test-3@sog",
				Summary:   "Meeting",
				Start:     time.Date(2026, 1, 18, 14, 0, 0, 0, time.UTC),
				End:       time.Date(2026, 1, 18, 15, 0, 0, 0, time.UTC),
				Organizer: "organizer@example.com",
				Attendees: []string{"a@example.com", "b@example.com"},
				Status:    "CONFIRMED",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cal := createICalEvent(tt.event)
			require.NotNil(t, cal)

			// Verify it round-trips
			parsed, err := parseICalEvent(cal)
			require.NoError(t, err)

			assert.Equal(t, tt.event.UID, parsed.UID)
			assert.Equal(t, tt.event.Summary, parsed.Summary)
			assert.Equal(t, tt.event.Description, parsed.Description)
			assert.Equal(t, tt.event.Location, parsed.Location)
			assert.Equal(t, tt.event.AllDay, parsed.AllDay)
			assert.Equal(t, tt.event.Organizer, parsed.Organizer)
			assert.Equal(t, tt.event.Attendees, parsed.Attendees)
		})
	}
}

func TestCalendar_String(t *testing.T) {
	cal := Calendar{
		Path:        "/calendars/user/default",
		Name:        "My Calendar",
		Description: "Personal calendar",
	}

	assert.Equal(t, "/calendars/user/default", cal.Path)
	assert.Equal(t, "My Calendar", cal.Name)
	assert.Equal(t, "Personal calendar", cal.Description)
}

func TestEvent_Fields(t *testing.T) {
	event := Event{
		UID:         "test-uid",
		Summary:     "Test Summary",
		Description: "Test Description",
		Location:    "Test Location",
		Start:       time.Date(2026, 1, 15, 10, 0, 0, 0, time.UTC),
		End:         time.Date(2026, 1, 15, 11, 0, 0, 0, time.UTC),
		AllDay:      false,
		Organizer:   "org@example.com",
		Attendees:   []string{"a@example.com", "b@example.com"},
		Status:      "CONFIRMED",
		URL:         "https://example.com/event",
		ETag:        `"etag-123"`,
	}

	assert.Equal(t, "test-uid", event.UID)
	assert.Equal(t, "Test Summary", event.Summary)
	assert.Equal(t, "Test Description", event.Description)
	assert.Equal(t, "Test Location", event.Location)
	assert.Equal(t, time.Hour, event.End.Sub(event.Start))
	assert.False(t, event.AllDay)
	assert.Equal(t, "org@example.com", event.Organizer)
	assert.Len(t, event.Attendees, 2)
	assert.Equal(t, "CONFIRMED", event.Status)
	assert.Equal(t, "https://example.com/event", event.URL)
	assert.Equal(t, `"etag-123"`, event.ETag)
}

func TestConfig_Fields(t *testing.T) {
	cfg := Config{
		URL:      "https://caldav.example.com/",
		Email:    "user@example.com",
		Password: "secret",
	}

	assert.Equal(t, "https://caldav.example.com/", cfg.URL)
	assert.Equal(t, "user@example.com", cfg.Email)
	assert.Equal(t, "secret", cfg.Password)
}
