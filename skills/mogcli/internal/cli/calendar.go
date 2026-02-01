package cli

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"time"

	"github.com/visionik/mogcli/internal/graph"
)

// CalendarCmd handles calendar operations.
type CalendarCmd struct {
	List      CalendarListCmd      `cmd:"" help:"List events"`
	Get       CalendarGetCmd       `cmd:"" help:"Get an event"`
	Create    CalendarCreateCmd    `cmd:"" help:"Create an event"`
	Update    CalendarUpdateCmd    `cmd:"" help:"Update an event"`
	Delete    CalendarDeleteCmd    `cmd:"" help:"Delete an event"`
	Calendars CalendarCalendarsCmd `cmd:"" help:"List calendars"`
	Respond   CalendarRespondCmd   `cmd:"" help:"Respond to an event invitation"`
	FreeBusy  CalendarFreeBusyCmd  `cmd:"" help:"Get free/busy information"`
	ACL       CalendarACLCmd       `cmd:"" help:"List calendar permissions"`
}

// CalendarListCmd lists events.
type CalendarListCmd struct {
	Calendar string `help:"Calendar ID (default: primary)"`
	From     string `help:"Start date (ISO format)" default:""`
	To       string `help:"End date (ISO format)" default:""`
	Max      int    `help:"Maximum events" default:"25"`
}

// Run executes calendar list.
func (c *CalendarListCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()

	// Default to today through +30 days
	from := time.Now()
	to := from.AddDate(0, 0, 30)

	if c.From != "" {
		from, err = time.Parse("2006-01-02", c.From)
		if err != nil {
			from, err = time.Parse(time.RFC3339, c.From)
			if err != nil {
				return fmt.Errorf("invalid --from date: %w", err)
			}
		}
	}

	if c.To != "" {
		to, err = time.Parse("2006-01-02", c.To)
		if err != nil {
			to, err = time.Parse(time.RFC3339, c.To)
			if err != nil {
				return fmt.Errorf("invalid --to date: %w", err)
			}
		}
	}

	query := url.Values{}
	query.Set("$top", fmt.Sprintf("%d", c.Max))
	query.Set("$orderby", "start/dateTime")
	query.Set("startDateTime", from.Format(time.RFC3339))
	query.Set("endDateTime", to.Format(time.RFC3339))

	path := "/me/calendarView"
	if c.Calendar != "" {
		path = fmt.Sprintf("/me/calendars/%s/calendarView", graph.ResolveID(c.Calendar))
	}

	data, err := client.Get(ctx, path, query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Event `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	if len(resp.Value) == 0 {
		fmt.Println("No events found")
		return nil
	}

	for _, event := range resp.Value {
		printEvent(event, root.Verbose)
	}
	return nil
}

// CalendarGetCmd gets an event.
type CalendarGetCmd struct {
	ID string `arg:"" help:"Event ID"`
}

// Run executes calendar get.
func (c *CalendarGetCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/events/%s", graph.ResolveID(c.ID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var event Event
	if err := json.Unmarshal(data, &event); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(event)
	}

	printEventDetail(event, root.Verbose)
	return nil
}

// CalendarCreateCmd creates an event.
type CalendarCreateCmd struct {
	Summary   string   `help:"Event title/summary" required:""`
	From      string   `help:"Start time (ISO format)" required:""`
	To        string   `help:"End time (ISO format)" required:""`
	Location  string   `help:"Location"`
	Description string `help:"Event description" name:"description"`
	Attendees []string `help:"Attendee email addresses"`
	AllDay    bool     `help:"All-day event" name:"all-day"`
	Calendar  string   `help:"Calendar ID"`
}

// Run executes calendar create.
func (c *CalendarCreateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	event := map[string]interface{}{
		"subject": c.Summary,
		"start": map[string]string{
			"dateTime": c.From,
			"timeZone": "UTC",
		},
		"end": map[string]string{
			"dateTime": c.To,
			"timeZone": "UTC",
		},
	}

	if c.Location != "" {
		event["location"] = map[string]string{"displayName": c.Location}
	}

	if c.Description != "" {
		event["body"] = map[string]string{
			"contentType": "text",
			"content":     c.Description,
		}
	}

	if len(c.Attendees) > 0 {
		var attendees []map[string]interface{}
		for _, email := range c.Attendees {
			attendees = append(attendees, map[string]interface{}{
				"emailAddress": map[string]string{"address": email},
				"type":         "required",
			})
		}
		event["attendees"] = attendees
	}

	if c.AllDay {
		event["isAllDay"] = true
	}

	ctx := context.Background()
	path := "/me/events"
	if c.Calendar != "" {
		path = fmt.Sprintf("/me/calendars/%s/events", graph.ResolveID(c.Calendar))
	}

	data, err := client.Post(ctx, path, event)
	if err != nil {
		return err
	}

	var created Event
	if err := json.Unmarshal(data, &created); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(created)
	}

	fmt.Printf("✓ Event created: %s (%s)\n", created.Subject, graph.FormatID(created.ID))
	return nil
}

// CalendarUpdateCmd updates an event.
type CalendarUpdateCmd struct {
	ID       string `arg:"" help:"Event ID"`
	Summary  string `help:"New title/summary"`
	From     string `help:"New start time"`
	To       string `help:"New end time"`
	Location string `help:"New location"`
	Description string `help:"New description" name:"description"`
}

// Run executes calendar update.
func (c *CalendarUpdateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	updates := make(map[string]interface{})

	if c.Summary != "" {
		updates["subject"] = c.Summary
	}
	if c.From != "" {
		updates["start"] = map[string]string{"dateTime": c.From, "timeZone": "UTC"}
	}
	if c.To != "" {
		updates["end"] = map[string]string{"dateTime": c.To, "timeZone": "UTC"}
	}
	if c.Location != "" {
		updates["location"] = map[string]string{"displayName": c.Location}
	}
	if c.Description != "" {
		updates["body"] = map[string]string{"contentType": "text", "content": c.Description}
	}

	if len(updates) == 0 {
		return fmt.Errorf("no updates specified")
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/events/%s", graph.ResolveID(c.ID))

	_, err = client.Patch(ctx, path, updates)
	if err != nil {
		return err
	}

	fmt.Println("✓ Event updated")
	return nil
}

// CalendarDeleteCmd deletes an event.
type CalendarDeleteCmd struct {
	ID string `arg:"" help:"Event ID"`
}

// Run executes calendar delete.
func (c *CalendarDeleteCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/events/%s", graph.ResolveID(c.ID))

	if err := client.Delete(ctx, path); err != nil {
		return err
	}

	fmt.Println("✓ Event deleted")
	return nil
}

// CalendarCalendarsCmd lists calendars.
type CalendarCalendarsCmd struct{}

// Run executes calendars list.
func (c *CalendarCalendarsCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	data, err := client.Get(ctx, "/me/calendars", nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Calendar `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, cal := range resp.Value {
		marker := " "
		if cal.IsDefaultCalendar {
			marker = "*"
		}
		fmt.Printf("%s %-30s %s\n", marker, cal.Name, graph.FormatID(cal.ID))
	}
	return nil
}

// CalendarRespondCmd responds to an event invitation.
type CalendarRespondCmd struct {
	ID       string `arg:"" help:"Event ID"`
	Response string `arg:"" help:"Response: accept, decline, tentative"`
	Comment  string `help:"Optional comment"`
}

// Run executes calendar respond.
func (c *CalendarRespondCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	var action string
	switch c.Response {
	case "accept":
		action = "accept"
	case "decline":
		action = "decline"
	case "tentative":
		action = "tentativelyAccept"
	default:
		return fmt.Errorf("invalid response: %s (use accept, decline, or tentative)", c.Response)
	}

	body := map[string]interface{}{
		"sendResponse": true,
	}
	if c.Comment != "" {
		body["comment"] = c.Comment
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/events/%s/%s", graph.ResolveID(c.ID), action)

	_, err = client.Post(ctx, path, body)
	if err != nil {
		return err
	}

	fmt.Printf("✓ Responded: %s\n", c.Response)
	return nil
}

// CalendarFreeBusyCmd gets free/busy information.
type CalendarFreeBusyCmd struct {
	Emails []string `arg:"" help:"Email addresses to check"`
	Start  string   `help:"Start time (ISO format)" required:""`
	End    string   `help:"End time (ISO format)" required:""`
}

// CalendarACLCmd lists calendar permissions.
type CalendarACLCmd struct {
	Calendar string `arg:"" optional:"" help:"Calendar ID (default: primary)"`
}

// Run executes calendar freebusy.
func (c *CalendarFreeBusyCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	var schedules []string
	for _, email := range c.Emails {
		schedules = append(schedules, email)
	}

	body := map[string]interface{}{
		"schedules":                schedules,
		"startTime":                map[string]string{"dateTime": c.Start, "timeZone": "UTC"},
		"endTime":                  map[string]string{"dateTime": c.End, "timeZone": "UTC"},
		"availabilityViewInterval": 30,
	}

	ctx := context.Background()
	data, err := client.Post(ctx, "/me/calendar/getSchedule", body)
	if err != nil {
		return err
	}

	if root.JSON {
		var resp interface{}
		json.Unmarshal(data, &resp)
		return outputJSON(resp)
	}

	fmt.Println(string(data))
	return nil
}

// Event represents a calendar event.
type Event struct {
	ID        string `json:"id"`
	Subject   string `json:"subject"`
	Start     *Time  `json:"start"`
	End       *Time  `json:"end"`
	Location  *Loc   `json:"location"`
	Body      *Body  `json:"body"`
	IsAllDay  bool   `json:"isAllDay"`
	Organizer *Org   `json:"organizer"`
}

// Time represents a datetime with timezone.
type Time struct {
	DateTime string `json:"dateTime"`
	TimeZone string `json:"timeZone"`
}

// Loc represents a location.
type Loc struct {
	DisplayName string `json:"displayName"`
}

// Body represents event body.
type Body struct {
	ContentType string `json:"contentType"`
	Content     string `json:"content"`
}

// Org represents an organizer.
type Org struct {
	EmailAddress struct {
		Name    string `json:"name"`
		Address string `json:"address"`
	} `json:"emailAddress"`
}

// Calendar represents a calendar.
type Calendar struct {
	ID                string `json:"id"`
	Name              string `json:"name"`
	IsDefaultCalendar bool   `json:"isDefaultCalendar"`
}

// CalendarPermission represents a calendar permission (ACL entry).
type CalendarPermission struct {
	ID                  string        `json:"id"`
	Role                string        `json:"role"`
	AllowedRoles        []string      `json:"allowedRoles"`
	EmailAddress        *EmailAddress `json:"emailAddress"`
	IsRemovable         bool          `json:"isRemovable"`
	IsInsideOrganization bool         `json:"isInsideOrganization"`
}

// EmailAddress represents an email address in a permission.
type EmailAddress struct {
	Name    string `json:"name"`
	Address string `json:"address"`
}

// Run executes calendar acl.
func (c *CalendarACLCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := "/me/calendar/calendarPermissions"
	if c.Calendar != "" {
		path = fmt.Sprintf("/me/calendars/%s/calendarPermissions", graph.ResolveID(c.Calendar))
	}

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []CalendarPermission `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	if len(resp.Value) == 0 {
		fmt.Println("No permissions found")
		return nil
	}

	fmt.Println("Calendar Permissions")
	fmt.Println()
	for _, perm := range resp.Value {
		email := "(no email)"
		name := ""
		if perm.EmailAddress != nil {
			if perm.EmailAddress.Address != "" {
				email = perm.EmailAddress.Address
			}
			if perm.EmailAddress.Name != "" {
				name = perm.EmailAddress.Name
			}
		}
		removable := ""
		if !perm.IsRemovable {
			removable = " (locked)"
		}
		if name != "" {
			fmt.Printf("%-12s %s <%s>%s\n", perm.Role, name, email, removable)
		} else {
			fmt.Printf("%-12s %s%s\n", perm.Role, email, removable)
		}
		if root.Verbose {
			fmt.Printf("  ID: %s\n", perm.ID)
		}
	}
	fmt.Printf("\n%d permission(s)\n", len(resp.Value))
	return nil
}

func printEvent(event Event, verbose bool) {
	start := ""
	if event.Start != nil {
		t, _ := time.Parse("2006-01-02T15:04:05.0000000", event.Start.DateTime)
		if event.IsAllDay {
			start = t.Format("Jan 2")
		} else {
			start = t.Format("Jan 2 15:04")
		}
	}

	location := ""
	if event.Location != nil && event.Location.DisplayName != "" {
		location = fmt.Sprintf(" @ %s", event.Location.DisplayName)
	}

	fmt.Printf("%-16s %s%s\n", start, event.Subject, location)
	fmt.Printf("  ID: %s\n", graph.FormatID(event.ID))
	if verbose {
		fmt.Printf("  Full: %s\n", event.ID)
	}
}

func printEventDetail(event Event, verbose bool) {
	fmt.Printf("ID:       %s\n", graph.FormatID(event.ID))
	if verbose {
		fmt.Printf("Full ID:  %s\n", event.ID)
	}
	fmt.Printf("Subject:  %s\n", event.Subject)

	if event.Start != nil {
		fmt.Printf("Start:    %s\n", event.Start.DateTime)
	}
	if event.End != nil {
		fmt.Printf("End:      %s\n", event.End.DateTime)
	}
	if event.Location != nil && event.Location.DisplayName != "" {
		fmt.Printf("Location: %s\n", event.Location.DisplayName)
	}
	if event.Organizer != nil {
		fmt.Printf("Organizer: %s <%s>\n",
			event.Organizer.EmailAddress.Name,
			event.Organizer.EmailAddress.Address)
	}
	if event.Body != nil && event.Body.Content != "" {
		content := event.Body.Content
		if event.Body.ContentType == "html" {
			content = stripHTML(content)
		}
		fmt.Printf("\n%s\n", content)
	}
}
