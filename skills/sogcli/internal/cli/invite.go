package cli

import (
	"context"
	"fmt"
	"io"
	"os"
	"strings"
	"time"

	"github.com/visionik/sogcli/internal/config"
	"github.com/visionik/sogcli/internal/itip"
	"github.com/visionik/sogcli/internal/smtp"
)

// InviteCmd handles meeting invitation operations.
type InviteCmd struct {
	Send    InviteSendCmd    `cmd:"" help:"Send a meeting invitation"`
	Reply   InviteReplyCmd   `cmd:"" help:"Reply to a meeting invitation"`
	Cancel  InviteCancelCmd  `cmd:"" help:"Cancel a meeting"`
	Parse   InviteParseCmd   `cmd:"" help:"Parse an .ics file"`
	Preview InvitePreviewCmd `cmd:"" help:"Preview invite without sending"`
}

// InviteSendCmd sends a meeting invitation.
type InviteSendCmd struct {
	Summary     string   `arg:"" help:"Meeting title/summary"`
	Attendees   []string `arg:"" help:"Attendee email addresses"`
	Start       string   `help:"Start time (YYYY-MM-DDTHH:MM or 'tomorrow 2pm')" required:""`
	Duration    string   `help:"Duration (e.g., 1h, 30m, 1h30m)" default:"1h"`
	End         string   `help:"End time (alternative to duration)"`
	Location    string   `help:"Meeting location" short:"l"`
	Description string   `help:"Meeting description" short:"d"`
	Organizer   string   `help:"Organizer name"`
}

// Run executes the invite send command.
func (c *InviteSendCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	// Parse start time
	start, _, err := parseDateTime(c.Start)
	if err != nil {
		return fmt.Errorf("invalid start time: %w", err)
	}

	// Calculate end time
	var end time.Time
	if c.End != "" {
		end, _, err = parseDateTime(c.End)
		if err != nil {
			return fmt.Errorf("invalid end time: %w", err)
		}
	} else {
		dur, err := time.ParseDuration(c.Duration)
		if err != nil {
			return fmt.Errorf("invalid duration: %w", err)
		}
		end = start.Add(dur)
	}

	// Build invite
	inv := &itip.Invite{
		Method:      itip.MethodRequest,
		UID:         itip.GenerateUID(getDomain(email)),
		Summary:     c.Summary,
		Description: c.Description,
		Location:    c.Location,
		Start:       start,
		End:         end,
		Organizer: itip.Participant{
			Email: email,
			Name:  c.Organizer,
		},
		Sequence: 0,
		Created:  time.Now().UTC(),
	}

	for _, att := range c.Attendees {
		inv.Attendees = append(inv.Attendees, itip.Participant{
			Email: att,
			RSVP:  true,
		})
	}

	// Generate iCalendar
	icsData, err := itip.CreateInvite(inv)
	if err != nil {
		return fmt.Errorf("failed to create invite: %w", err)
	}

	// Send via SMTP
	if err := sendInviteEmail(cfg, email, inv, icsData); err != nil {
		return fmt.Errorf("failed to send invite: %w", err)
	}

	if root.JSON {
		fmt.Printf(`{"uid":"%s","summary":"%s","start":"%s","end":"%s","attendees":%d}`+"\n",
			inv.UID, inv.Summary, inv.Start.Format(time.RFC3339), inv.End.Format(time.RFC3339), len(inv.Attendees))
		return nil
	}

	fmt.Printf("Sent meeting invite: %s\n", inv.Summary)
	fmt.Printf("  UID: %s\n", inv.UID)
	fmt.Printf("  When: %s - %s\n", inv.Start.Format("Mon Jan 2 15:04"), inv.End.Format("15:04"))
	if inv.Location != "" {
		fmt.Printf("  Where: %s\n", inv.Location)
	}
	fmt.Printf("  Attendees: %s\n", strings.Join(c.Attendees, ", "))
	return nil
}

// InviteReplyCmd replies to a meeting invitation.
type InviteReplyCmd struct {
	File    string `arg:"" help:".ics file or - for stdin"`
	Status  string `help:"Response: accept, decline, tentative" required:"" enum:"accept,decline,tentative"`
	Comment string `help:"Optional comment with response"`
}

// Run executes the invite reply command.
func (c *InviteReplyCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	// Read .ics file
	var data []byte
	if c.File == "-" {
		data, err = io.ReadAll(os.Stdin)
	} else {
		data, err = os.ReadFile(c.File)
	}
	if err != nil {
		return fmt.Errorf("failed to read file: %w", err)
	}

	// Parse invite
	inv, err := itip.ParseInvite(data)
	if err != nil {
		return fmt.Errorf("failed to parse invite: %w", err)
	}

	// Determine status
	var status itip.ParticipantStatus
	switch c.Status {
	case "accept":
		status = itip.StatusAccepted
	case "decline":
		status = itip.StatusDeclined
	case "tentative":
		status = itip.StatusTentative
	}

	// Create reply
	resp := &itip.Response{
		UID: inv.UID,
		Attendee: itip.Participant{
			Email:  email,
			Status: status,
		},
		Organizer: inv.Organizer,
		Status:    status,
		Comment:   c.Comment,
		Sequence:  inv.Sequence,
	}

	replyData, err := itip.CreateReply(resp)
	if err != nil {
		return fmt.Errorf("failed to create reply: %w", err)
	}

	// Send reply to organizer
	if err := sendReplyEmail(cfg, email, inv, resp, replyData); err != nil {
		return fmt.Errorf("failed to send reply: %w", err)
	}

	fmt.Printf("Sent %s reply to: %s\n", c.Status, inv.Organizer.Email)
	fmt.Printf("  Meeting: %s\n", inv.Summary)
	return nil
}

// InviteCancelCmd cancels a meeting.
type InviteCancelCmd struct {
	UID       string   `arg:"" help:"Meeting UID to cancel"`
	Attendees []string `arg:"" help:"Attendee emails to notify"`
}

// Run executes the invite cancel command.
func (c *InviteCancelCmd) Run(root *Root) error {
	cfg, err := config.Load()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return fmt.Errorf("no account specified")
	}

	organizer := itip.Participant{Email: email}
	var attendees []itip.Participant
	for _, att := range c.Attendees {
		attendees = append(attendees, itip.Participant{Email: att})
	}

	cancelData, err := itip.CreateCancel(c.UID, organizer, attendees, 1)
	if err != nil {
		return fmt.Errorf("failed to create cancel: %w", err)
	}

	// Send cancel to all attendees
	if err := sendCancelEmail(cfg, email, c.UID, c.Attendees, cancelData); err != nil {
		return fmt.Errorf("failed to send cancel: %w", err)
	}

	fmt.Printf("Sent cancellation for meeting: %s\n", c.UID)
	fmt.Printf("  Notified: %s\n", strings.Join(c.Attendees, ", "))
	return nil
}

// InviteParseCmd parses an .ics file.
type InviteParseCmd struct {
	File string `arg:"" help:".ics file or - for stdin"`
}

// Run executes the invite parse command.
func (c *InviteParseCmd) Run(root *Root) error {
	var data []byte
	var err error
	if c.File == "-" {
		data, err = io.ReadAll(os.Stdin)
	} else {
		data, err = os.ReadFile(c.File)
	}
	if err != nil {
		return fmt.Errorf("failed to read file: %w", err)
	}

	inv, err := itip.ParseInvite(data)
	if err != nil {
		return fmt.Errorf("failed to parse: %w", err)
	}

	if root.JSON {
		fmt.Printf(`{"method":"%s","uid":"%s","summary":"%s","start":"%s","end":"%s","organizer":"%s","attendees":%d}`+"\n",
			inv.Method, inv.UID, inv.Summary,
			inv.Start.Format(time.RFC3339), inv.End.Format(time.RFC3339),
			inv.Organizer.Email, len(inv.Attendees))
		return nil
	}

	fmt.Printf("Method:    %s\n", inv.Method)
	fmt.Printf("UID:       %s\n", inv.UID)
	fmt.Printf("Summary:   %s\n", inv.Summary)
	fmt.Printf("Start:     %s\n", inv.Start.Format("Mon Jan 2, 2006 15:04 MST"))
	fmt.Printf("End:       %s\n", inv.End.Format("Mon Jan 2, 2006 15:04 MST"))
	if inv.Location != "" {
		fmt.Printf("Location:  %s\n", inv.Location)
	}
	if inv.Description != "" {
		fmt.Printf("Desc:      %s\n", inv.Description)
	}
	fmt.Printf("Organizer: %s", inv.Organizer.Email)
	if inv.Organizer.Name != "" {
		fmt.Printf(" (%s)", inv.Organizer.Name)
	}
	fmt.Println()
	if len(inv.Attendees) > 0 {
		fmt.Println("Attendees:")
		for _, att := range inv.Attendees {
			status := string(att.Status)
			if status == "" {
				status = "NEEDS-ACTION"
			}
			fmt.Printf("  - %s [%s]", att.Email, status)
			if att.Name != "" {
				fmt.Printf(" (%s)", att.Name)
			}
			fmt.Println()
		}
	}
	return nil
}

// InvitePreviewCmd previews an invite without sending.
type InvitePreviewCmd struct {
	Summary     string   `arg:"" help:"Meeting title/summary"`
	Attendees   []string `arg:"" help:"Attendee email addresses"`
	Start       string   `help:"Start time (YYYY-MM-DDTHH:MM)" required:""`
	Duration    string   `help:"Duration (e.g., 1h, 30m)" default:"1h"`
	Location    string   `help:"Meeting location" short:"l"`
	Description string   `help:"Meeting description" short:"d"`
}

// Run executes the invite preview command.
func (c *InvitePreviewCmd) Run(root *Root) error {
	email := root.Account
	if email == "" {
		cfg, _ := config.Load()
		if cfg != nil {
			email = cfg.DefaultAccount
		}
	}
	if email == "" {
		email = "organizer@example.com"
	}

	start, _, err := parseDateTime(c.Start)
	if err != nil {
		return fmt.Errorf("invalid start time: %w", err)
	}

	dur, err := time.ParseDuration(c.Duration)
	if err != nil {
		return fmt.Errorf("invalid duration: %w", err)
	}
	end := start.Add(dur)

	inv := &itip.Invite{
		Method:      itip.MethodRequest,
		UID:         itip.GenerateUID(getDomain(email)),
		Summary:     c.Summary,
		Description: c.Description,
		Location:    c.Location,
		Start:       start,
		End:         end,
		Organizer:   itip.Participant{Email: email},
		Sequence:    0,
		Created:     time.Now().UTC(),
	}

	for _, att := range c.Attendees {
		inv.Attendees = append(inv.Attendees, itip.Participant{Email: att, RSVP: true})
	}

	icsData, err := itip.CreateInvite(inv)
	if err != nil {
		return fmt.Errorf("failed to create invite: %w", err)
	}

	fmt.Println(string(icsData))
	return nil
}

// Helper functions

func getDomain(email string) string {
	parts := strings.Split(email, "@")
	if len(parts) == 2 {
		return parts[1]
	}
	return "sog.local"
}

func sendInviteEmail(cfg *config.Config, from string, inv *itip.Invite, icsData []byte) error {
	acct, err := cfg.GetAccount(from)
	if err != nil {
		return err
	}

	password, err := cfg.GetPasswordForProtocol(from, config.ProtocolSMTP)
	if err != nil {
		return err
	}

	client, err := smtp.Connect(smtp.Config{
		Host:     acct.SMTP.Host,
		Port:     acct.SMTP.Port,
		Email:    from,
		Password: password,
		StartTLS: acct.SMTP.StartTLS,
		TLS:      acct.SMTP.TLS,
	})
	if err != nil {
		return err
	}
	defer client.Close()

	// Build recipient list
	var to []string
	for _, att := range inv.Attendees {
		to = append(to, att.Email)
	}

	// Create message with calendar attachment
	msg := &smtp.Message{
		From:    from,
		To:      to,
		Subject: fmt.Sprintf("Meeting Invitation: %s", inv.Summary),
		Body:    fmt.Sprintf("You have been invited to: %s\n\nWhen: %s - %s\nWhere: %s\n\n%s",
			inv.Summary,
			inv.Start.Format("Mon Jan 2, 2006 15:04"),
			inv.End.Format("15:04"),
			inv.Location,
			inv.Description),
		CalendarData:   icsData,
		CalendarMethod: string(inv.Method),
	}

	return client.Send(context.Background(), msg)
}

func sendReplyEmail(cfg *config.Config, from string, inv *itip.Invite, resp *itip.Response, replyData []byte) error {
	acct, err := cfg.GetAccount(from)
	if err != nil {
		return err
	}

	password, err := cfg.GetPasswordForProtocol(from, config.ProtocolSMTP)
	if err != nil {
		return err
	}

	client, err := smtp.Connect(smtp.Config{
		Host:     acct.SMTP.Host,
		Port:     acct.SMTP.Port,
		Email:    from,
		Password: password,
		StartTLS: acct.SMTP.StartTLS,
		TLS:      acct.SMTP.TLS,
	})
	if err != nil {
		return err
	}
	defer client.Close()

	statusWord := "responded to"
	switch resp.Status {
	case itip.StatusAccepted:
		statusWord = "accepted"
	case itip.StatusDeclined:
		statusWord = "declined"
	case itip.StatusTentative:
		statusWord = "tentatively accepted"
	}

	msg := &smtp.Message{
		From:           from,
		To:             []string{inv.Organizer.Email},
		Subject:        fmt.Sprintf("Re: %s", inv.Summary),
		Body:           fmt.Sprintf("%s has %s your meeting invitation: %s", from, statusWord, inv.Summary),
		CalendarData:   replyData,
		CalendarMethod: string(itip.MethodReply),
	}

	return client.Send(context.Background(), msg)
}

func sendCancelEmail(cfg *config.Config, from string, uid string, attendees []string, cancelData []byte) error {
	acct, err := cfg.GetAccount(from)
	if err != nil {
		return err
	}

	password, err := cfg.GetPasswordForProtocol(from, config.ProtocolSMTP)
	if err != nil {
		return err
	}

	client, err := smtp.Connect(smtp.Config{
		Host:     acct.SMTP.Host,
		Port:     acct.SMTP.Port,
		Email:    from,
		Password: password,
		StartTLS: acct.SMTP.StartTLS,
		TLS:      acct.SMTP.TLS,
	})
	if err != nil {
		return err
	}
	defer client.Close()

	msg := &smtp.Message{
		From:           from,
		To:             attendees,
		Subject:        "Meeting Cancelled",
		Body:           fmt.Sprintf("The meeting has been cancelled.\n\nUID: %s", uid),
		CalendarData:   cancelData,
		CalendarMethod: string(itip.MethodCancel),
	}

	return client.Send(context.Background(), msg)
}
