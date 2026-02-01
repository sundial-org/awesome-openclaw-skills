package cli

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/visionik/sogcli/internal/caldav"
	"github.com/visionik/sogcli/internal/config"
)

// CalCmd handles calendar operations.
type CalCmd struct {
	List      CalListCmd      `cmd:"" aliases:"events" help:"List events"`
	Get       CalGetCmd       `cmd:"" aliases:"event" help:"Get event details"`
	Search    CalSearchCmd    `cmd:"" help:"Search events"`
	Today     CalTodayCmd     `cmd:"" help:"Today's events"`
	Week      CalWeekCmd      `cmd:"" help:"This week's events"`
	Create    CalCreateCmd    `cmd:"" help:"Create an event"`
	Update    CalUpdateCmd    `cmd:"" help:"Update an event"`
	Delete    CalDeleteCmd    `cmd:"" help:"Delete an event"`
	Calendars CalCalendarsCmd `cmd:"" help:"List calendars"`
}

// CalListCmd lists events in a calendar.
type CalListCmd struct {
	Calendar string `arg:"" optional:"" help:"Calendar path (default: primary)"`
	From     string `help:"Start date (YYYY-MM-DD or relative: today, tomorrow)" default:"today"`
	To       string `help:"End date (YYYY-MM-DD or relative: +7d, +30d)" default:"+30d"`
	Max      int    `help:"Maximum events to return" default:"50"`
}

// Run executes the cal list command.
func (c *CalListCmd) Run(root *Root) error {
	client, calPath, err := getCalDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.Calendar != "" {
		calPath = c.Calendar
	}

	start, err := parseDate(c.From)
	if err != nil {
		return fmt.Errorf("invalid --from date: %w", err)
	}
	end, err := parseDate(c.To)
	if err != nil {
		return fmt.Errorf("invalid --to date: %w", err)
	}

	ctx := context.Background()
	events, err := client.ListEvents(ctx, calPath, start, end)
	if err != nil {
		return fmt.Errorf("failed to list events: %w", err)
	}

	if len(events) == 0 {
		fmt.Println("No events found.")
		return nil
	}

	// Limit results
	if c.Max > 0 && len(events) > c.Max {
		events = events[:c.Max]
	}

	if root.JSON {
		return outputEventsJSON(events)
	}

	return outputEventsTable(events)
}

// CalTodayCmd lists today's events.
type CalTodayCmd struct {
	Calendar string `arg:"" optional:"" help:"Calendar path (default: primary)"`
}

// Run executes the cal today command.
func (c *CalTodayCmd) Run(root *Root) error {
	cmd := &CalListCmd{
		Calendar: c.Calendar,
		From:     "today",
		To:       "tomorrow",
	}
	return cmd.Run(root)
}

// CalWeekCmd lists this week's events.
type CalWeekCmd struct {
	Calendar string `arg:"" optional:"" help:"Calendar path (default: primary)"`
}

// Run executes the cal week command.
func (c *CalWeekCmd) Run(root *Root) error {
	cmd := &CalListCmd{
		Calendar: c.Calendar,
		From:     "today",
		To:       "+7d",
	}
	return cmd.Run(root)
}

// CalGetCmd gets event details.
type CalGetCmd struct {
	UID      string `arg:"" help:"Event UID"`
	Calendar string `help:"Calendar path (default: primary)"`
}

// Run executes the cal get command.
func (c *CalGetCmd) Run(root *Root) error {
	client, calPath, err := getCalDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.Calendar != "" {
		calPath = c.Calendar
	}

	ctx := context.Background()
	event, err := client.GetEvent(ctx, calPath, c.UID)
	if err != nil {
		return fmt.Errorf("failed to get event: %w", err)
	}

	if root.JSON {
		return outputEventsJSON([]caldav.Event{*event})
	}

	return outputEventDetail(event)
}

// CalSearchCmd searches events.
type CalSearchCmd struct {
	Query    string `arg:"" help:"Search query (matches title, description, location)"`
	Calendar string `help:"Calendar path (default: primary)"`
	From     string `help:"Start date" default:"today"`
	To       string `help:"End date" default:"+365d"`
	Max      int    `help:"Maximum results" default:"50"`
}

// Run executes the cal search command.
func (c *CalSearchCmd) Run(root *Root) error {
	client, calPath, err := getCalDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.Calendar != "" {
		calPath = c.Calendar
	}

	from, err := parseDate(c.From)
	if err != nil {
		return fmt.Errorf("invalid --from: %w", err)
	}
	to, err := parseDate(c.To)
	if err != nil {
		return fmt.Errorf("invalid --to: %w", err)
	}

	ctx := context.Background()
	events, err := client.ListEvents(ctx, calPath, from, to)
	if err != nil {
		return fmt.Errorf("failed to list events: %w", err)
	}

	// Filter by query
	query := strings.ToLower(c.Query)
	var matches []caldav.Event
	for _, e := range events {
		if strings.Contains(strings.ToLower(e.Summary), query) ||
			strings.Contains(strings.ToLower(e.Description), query) ||
			strings.Contains(strings.ToLower(e.Location), query) {
			matches = append(matches, e)
			if len(matches) >= c.Max {
				break
			}
		}
	}

	if len(matches) == 0 {
		fmt.Println("No matching events found.")
		return nil
	}

	if root.JSON {
		return outputEventsJSON(matches)
	}

	return outputEventsTable(matches)
}

// CalCreateCmd creates an event.
type CalCreateCmd struct {
	Title       string   `arg:"" help:"Event title"`
	Start       string   `help:"Start time (YYYY-MM-DDTHH:MM or YYYY-MM-DD for all-day)" required:""`
	End         string   `help:"End time (YYYY-MM-DDTHH:MM or YYYY-MM-DD for all-day)"`
	Duration    string   `help:"Duration (e.g., 1h, 30m) - alternative to --end"`
	Location    string   `help:"Event location"`
	Description string   `help:"Event description"`
	Calendar    string   `help:"Calendar path (default: primary)"`
	Attendees   []string `help:"Attendee email addresses"`
}

// Run executes the cal create command.
func (c *CalCreateCmd) Run(root *Root) error {
	client, calPath, err := getCalDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.Calendar != "" {
		calPath = c.Calendar
	}

	start, allDay, err := parseDateTime(c.Start)
	if err != nil {
		return fmt.Errorf("invalid --start: %w", err)
	}

	var end time.Time
	if c.End != "" {
		end, _, err = parseDateTime(c.End)
		if err != nil {
			return fmt.Errorf("invalid --end: %w", err)
		}
	} else if c.Duration != "" {
		dur, err := time.ParseDuration(c.Duration)
		if err != nil {
			return fmt.Errorf("invalid --duration: %w", err)
		}
		end = start.Add(dur)
	} else if allDay {
		end = start.AddDate(0, 0, 1)
	} else {
		end = start.Add(1 * time.Hour)
	}

	event := &caldav.Event{
		UID:         generateUID(),
		Summary:     c.Title,
		Start:       start,
		End:         end,
		AllDay:      allDay,
		Location:    c.Location,
		Description: c.Description,
		Attendees:   c.Attendees,
	}

	ctx := context.Background()
	if err := client.CreateEvent(ctx, calPath, event); err != nil {
		return fmt.Errorf("failed to create event: %w", err)
	}

	if root.JSON {
		return outputEventsJSON([]caldav.Event{*event})
	}

	fmt.Printf("Created event: %s (%s)\n", event.Summary, event.UID)
	return nil
}

// CalUpdateCmd updates an event.
type CalUpdateCmd struct {
	UID         string `arg:"" help:"Event UID"`
	Title       string `help:"New title"`
	Start       string `help:"New start time"`
	End         string `help:"New end time"`
	Location    string `help:"New location"`
	Description string `help:"New description"`
	Calendar    string `help:"Calendar path (default: primary)"`
}

// Run executes the cal update command.
func (c *CalUpdateCmd) Run(root *Root) error {
	client, calPath, err := getCalDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.Calendar != "" {
		calPath = c.Calendar
	}

	ctx := context.Background()
	event, err := client.GetEvent(ctx, calPath, c.UID)
	if err != nil {
		return fmt.Errorf("failed to get event: %w", err)
	}

	// Apply updates
	if c.Title != "" {
		event.Summary = c.Title
	}
	if c.Start != "" {
		start, allDay, err := parseDateTime(c.Start)
		if err != nil {
			return fmt.Errorf("invalid --start: %w", err)
		}
		event.Start = start
		event.AllDay = allDay
	}
	if c.End != "" {
		end, _, err := parseDateTime(c.End)
		if err != nil {
			return fmt.Errorf("invalid --end: %w", err)
		}
		event.End = end
	}
	if c.Location != "" {
		event.Location = c.Location
	}
	if c.Description != "" {
		event.Description = c.Description
	}

	if err := client.UpdateEvent(ctx, calPath, event); err != nil {
		return fmt.Errorf("failed to update event: %w", err)
	}

	fmt.Printf("Updated event: %s\n", c.UID)
	return nil
}

// CalDeleteCmd deletes an event.
type CalDeleteCmd struct {
	UID      string `arg:"" help:"Event UID"`
	Calendar string `help:"Calendar path (default: primary)"`
}

// Run executes the cal delete command.
func (c *CalDeleteCmd) Run(root *Root) error {
	client, calPath, err := getCalDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.Calendar != "" {
		calPath = c.Calendar
	}

	ctx := context.Background()
	if err := client.DeleteEvent(ctx, calPath, c.UID); err != nil {
		return fmt.Errorf("failed to delete event: %w", err)
	}

	fmt.Printf("Deleted event: %s\n", c.UID)
	return nil
}

// CalCalendarsCmd lists available calendars.
type CalCalendarsCmd struct{}

// Run executes the cal calendars command.
func (c *CalCalendarsCmd) Run(root *Root) error {
	client, _, err := getCalDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	calendars, err := client.FindCalendars(ctx)
	if err != nil {
		return fmt.Errorf("failed to list calendars: %w", err)
	}

	if len(calendars) == 0 {
		fmt.Println("No calendars found.")
		return nil
	}

	if root.JSON {
		return outputCalendarsJSON(calendars)
	}

	fmt.Printf("%-40s %s\n", "PATH", "NAME")
	for _, cal := range calendars {
		fmt.Printf("%-40s %s\n", cal.Path, cal.Name)
	}
	return nil
}

// getCalDAVClient creates a CalDAV client from config.
func getCalDAVClient(root *Root) (*caldav.Client, string, error) {
	cfg, err := config.Load()
	if err != nil {
		return nil, "", fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return nil, "", fmt.Errorf("no account specified. Use --account or set a default")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return nil, "", err
	}

	if acct.CalDAV.URL == "" {
		return nil, "", fmt.Errorf("no CalDAV URL configured for %s. Run: sog auth add %s --caldav-url <url>", email, email)
	}

	password, err := cfg.GetPasswordForProtocol(email, config.ProtocolCalDAV)
	if err != nil {
		return nil, "", fmt.Errorf("failed to get password: %w", err)
	}

	client, err := caldav.Connect(caldav.Config{
		URL:      acct.CalDAV.URL,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return nil, "", fmt.Errorf("failed to connect to CalDAV: %w", err)
	}

	return client, acct.CalDAV.DefaultCalendar, nil
}

// parseDate parses a date string (YYYY-MM-DD, today, tomorrow, +Nd).
func parseDate(s string) (time.Time, error) {
	now := time.Now()
	today := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())

	switch strings.ToLower(s) {
	case "today":
		return today, nil
	case "tomorrow":
		return today.AddDate(0, 0, 1), nil
	case "yesterday":
		return today.AddDate(0, 0, -1), nil
	}

	// Relative: +Nd
	if strings.HasPrefix(s, "+") && strings.HasSuffix(s, "d") {
		var days int
		if _, err := fmt.Sscanf(s, "+%dd", &days); err == nil {
			return today.AddDate(0, 0, days), nil
		}
	}

	// ISO date
	t, err := time.Parse("2006-01-02", s)
	if err != nil {
		return time.Time{}, fmt.Errorf("invalid date format: %s (use YYYY-MM-DD, today, tomorrow, or +Nd)", s)
	}
	return t, nil
}

// parseDateTime parses a datetime string (YYYY-MM-DDTHH:MM or YYYY-MM-DD).
func parseDateTime(s string) (time.Time, bool, error) {
	// Try full datetime first
	t, err := time.Parse("2006-01-02T15:04", s)
	if err == nil {
		return t, false, nil
	}

	// Try date only (all-day event)
	t, err = time.Parse("2006-01-02", s)
	if err == nil {
		return t, true, nil
	}

	return time.Time{}, false, fmt.Errorf("invalid datetime format: %s (use YYYY-MM-DDTHH:MM or YYYY-MM-DD)", s)
}

// generateUID generates a unique identifier for an event.
func generateUID() string {
	return fmt.Sprintf("%d@sog", time.Now().UnixNano())
}

// outputEventsJSON outputs events as JSON.
func outputEventsJSON(events []caldav.Event) error {
	for _, e := range events {
		fmt.Printf(`{"uid":"%s","summary":"%s","start":"%s","end":"%s","location":"%s","all_day":%t}`+"\n",
			e.UID, e.Summary, e.Start.Format(time.RFC3339), e.End.Format(time.RFC3339), e.Location, e.AllDay)
	}
	return nil
}

// outputEventsTable outputs events as a table.
func outputEventsTable(events []caldav.Event) error {
	fmt.Printf("%-20s %-12s %-8s %s\n", "DATE", "TIME", "DURATION", "SUMMARY")
	for _, e := range events {
		date := e.Start.Format("2006-01-02 Mon")
		var timeStr, durStr string
		if e.AllDay {
			timeStr = "all-day"
			durStr = ""
		} else {
			timeStr = e.Start.Format("15:04")
			// Handle missing or invalid end time
			if e.End.IsZero() || e.End.Before(e.Start) {
				durStr = "-"
			} else {
				dur := e.End.Sub(e.Start)
				if dur.Hours() >= 1 {
					durStr = fmt.Sprintf("%.0fh", dur.Hours())
				} else {
					durStr = fmt.Sprintf("%.0fm", dur.Minutes())
				}
			}
		}
		summary := e.Summary
		if len(summary) > 40 {
			summary = summary[:37] + "..."
		}
		fmt.Printf("%-20s %-12s %-8s %s\n", date, timeStr, durStr, summary)
	}
	return nil
}

// outputEventDetail outputs a single event in detail.
func outputEventDetail(event *caldav.Event) error {
	fmt.Printf("UID:         %s\n", event.UID)
	fmt.Printf("Summary:     %s\n", event.Summary)
	if event.AllDay {
		fmt.Printf("Date:        %s (all day)\n", event.Start.Format("2006-01-02 Mon"))
	} else {
		fmt.Printf("Start:       %s\n", event.Start.Format("2006-01-02 15:04 Mon"))
		fmt.Printf("End:         %s\n", event.End.Format("2006-01-02 15:04 Mon"))
		fmt.Printf("Duration:    %s\n", event.End.Sub(event.Start))
	}
	if event.Location != "" {
		fmt.Printf("Location:    %s\n", event.Location)
	}
	if event.Description != "" {
		fmt.Printf("Description: %s\n", event.Description)
	}
	if event.Organizer != "" {
		fmt.Printf("Organizer:   %s\n", event.Organizer)
	}
	if len(event.Attendees) > 0 {
		fmt.Printf("Attendees:   %s\n", strings.Join(event.Attendees, ", "))
	}
	if event.Status != "" {
		fmt.Printf("Status:      %s\n", event.Status)
	}
	return nil
}

// outputCalendarsJSON outputs calendars as JSON.
func outputCalendarsJSON(calendars []caldav.Calendar) error {
	for _, c := range calendars {
		fmt.Printf(`{"path":"%s","name":"%s","description":"%s"}`+"\n", c.Path, c.Name, c.Description)
	}
	return nil
}
