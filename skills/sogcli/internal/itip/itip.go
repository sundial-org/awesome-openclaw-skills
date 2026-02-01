// Package itip provides iTIP/iMIP meeting invite support.
// iTIP = iCalendar Transport-Independent Interoperability Protocol (RFC 5546)
// iMIP = iCalendar Message-Based Interoperability Protocol (RFC 6047)
package itip

import (
	"bytes"
	"fmt"
	"strings"
	"time"

	ical "github.com/emersion/go-ical"
)

// Method represents an iTIP method.
type Method string

const (
	MethodRequest Method = "REQUEST" // Invite attendees
	MethodReply   Method = "REPLY"   // Respond to invite
	MethodCancel  Method = "CANCEL"  // Cancel meeting
	MethodCounter Method = "COUNTER" // Propose different time
	MethodRefresh Method = "REFRESH" // Request updated info
)

// ParticipantStatus represents attendee participation status.
type ParticipantStatus string

const (
	StatusNeedsAction ParticipantStatus = "NEEDS-ACTION"
	StatusAccepted    ParticipantStatus = "ACCEPTED"
	StatusDeclined    ParticipantStatus = "DECLINED"
	StatusTentative   ParticipantStatus = "TENTATIVE"
)

// Invite represents a meeting invitation.
type Invite struct {
	Method      Method
	UID         string
	Summary     string
	Description string
	Location    string
	Start       time.Time
	End         time.Time
	Organizer   Participant
	Attendees   []Participant
	Sequence    int
	Created     time.Time
	LastMod     time.Time
}

// Participant represents an organizer or attendee.
type Participant struct {
	Email  string
	Name   string
	Status ParticipantStatus
	RSVP   bool
}

// Response represents a reply to an invitation.
type Response struct {
	UID       string
	Attendee  Participant
	Organizer Participant
	Status    ParticipantStatus
	Comment   string
	Sequence  int
}

// CreateInvite creates an iTIP REQUEST for a new meeting.
func CreateInvite(inv *Invite) ([]byte, error) {
	cal := ical.NewCalendar()
	cal.Props.SetText(ical.PropVersion, "2.0")
	cal.Props.SetText(ical.PropProductID, "-//sog//sogcli//EN")
	cal.Props.SetText(ical.PropMethod, string(MethodRequest))

	event := ical.NewComponent(ical.CompEvent)
	event.Props.SetText(ical.PropUID, inv.UID)
	event.Props.SetText(ical.PropSummary, inv.Summary)
	event.Props.SetDateTime(ical.PropDateTimeStart, inv.Start)
	event.Props.SetDateTime(ical.PropDateTimeEnd, inv.End)
	event.Props.SetDateTime(ical.PropDateTimeStamp, time.Now().UTC())
	event.Props.SetDateTime(ical.PropCreated, inv.Created)
	seqProp := ical.NewProp(ical.PropSequence)
	seqProp.Value = fmt.Sprintf("%d", inv.Sequence)
	event.Props.Set(seqProp)

	if inv.Description != "" {
		event.Props.SetText(ical.PropDescription, inv.Description)
	}
	if inv.Location != "" {
		event.Props.SetText(ical.PropLocation, inv.Location)
	}

	// Organizer
	orgProp := ical.NewProp(ical.PropOrganizer)
	orgProp.Value = "mailto:" + inv.Organizer.Email
	if inv.Organizer.Name != "" {
		orgProp.Params.Set(ical.ParamCommonName, inv.Organizer.Name)
	}
	event.Props.Set(orgProp)

	// Attendees
	for _, att := range inv.Attendees {
		attProp := ical.NewProp(ical.PropAttendee)
		attProp.Value = "mailto:" + att.Email
		if att.Name != "" {
			attProp.Params.Set(ical.ParamCommonName, att.Name)
		}
		attProp.Params.Set(ical.ParamParticipationStatus, string(StatusNeedsAction))
		if att.RSVP {
			attProp.Params.Set(ical.ParamRSVP, "TRUE")
		}
		attProp.Params.Set("ROLE", "REQ-PARTICIPANT")
		event.Props.Set(attProp)
	}

	cal.Children = append(cal.Children, event)

	var buf bytes.Buffer
	if err := ical.NewEncoder(&buf).Encode(cal); err != nil {
		return nil, fmt.Errorf("failed to encode invite: %w", err)
	}

	return buf.Bytes(), nil
}

// CreateReply creates an iTIP REPLY for responding to an invitation.
func CreateReply(resp *Response) ([]byte, error) {
	cal := ical.NewCalendar()
	cal.Props.SetText(ical.PropVersion, "2.0")
	cal.Props.SetText(ical.PropProductID, "-//sog//sogcli//EN")
	cal.Props.SetText(ical.PropMethod, string(MethodReply))

	event := ical.NewComponent(ical.CompEvent)
	event.Props.SetText(ical.PropUID, resp.UID)
	event.Props.SetDateTime(ical.PropDateTimeStamp, time.Now().UTC())
	seqProp := ical.NewProp(ical.PropSequence)
	seqProp.Value = fmt.Sprintf("%d", resp.Sequence)
	event.Props.Set(seqProp)

	// Organizer
	orgProp := ical.NewProp(ical.PropOrganizer)
	orgProp.Value = "mailto:" + resp.Organizer.Email
	if resp.Organizer.Name != "" {
		orgProp.Params.Set(ical.ParamCommonName, resp.Organizer.Name)
	}
	event.Props.Set(orgProp)

	// Attendee (the responder)
	attProp := ical.NewProp(ical.PropAttendee)
	attProp.Value = "mailto:" + resp.Attendee.Email
	if resp.Attendee.Name != "" {
		attProp.Params.Set(ical.ParamCommonName, resp.Attendee.Name)
	}
	attProp.Params.Set(ical.ParamParticipationStatus, string(resp.Status))
	event.Props.Set(attProp)

	if resp.Comment != "" {
		event.Props.SetText(ical.PropComment, resp.Comment)
	}

	cal.Children = append(cal.Children, event)

	var buf bytes.Buffer
	if err := ical.NewEncoder(&buf).Encode(cal); err != nil {
		return nil, fmt.Errorf("failed to encode reply: %w", err)
	}

	return buf.Bytes(), nil
}

// CreateCancel creates an iTIP CANCEL to cancel a meeting.
func CreateCancel(uid string, organizer Participant, attendees []Participant, sequence int) ([]byte, error) {
	cal := ical.NewCalendar()
	cal.Props.SetText(ical.PropVersion, "2.0")
	cal.Props.SetText(ical.PropProductID, "-//sog//sogcli//EN")
	cal.Props.SetText(ical.PropMethod, string(MethodCancel))

	event := ical.NewComponent(ical.CompEvent)
	event.Props.SetText(ical.PropUID, uid)
	event.Props.SetDateTime(ical.PropDateTimeStamp, time.Now().UTC())
	seqProp := ical.NewProp(ical.PropSequence)
	seqProp.Value = fmt.Sprintf("%d", sequence)
	event.Props.Set(seqProp)
	statusProp := ical.NewProp(ical.PropStatus)
	statusProp.Value = "CANCELLED"
	event.Props.Set(statusProp)

	// Organizer
	orgProp := ical.NewProp(ical.PropOrganizer)
	orgProp.Value = "mailto:" + organizer.Email
	if organizer.Name != "" {
		orgProp.Params.Set(ical.ParamCommonName, organizer.Name)
	}
	event.Props.Set(orgProp)

	// Attendees
	for _, att := range attendees {
		attProp := ical.NewProp(ical.PropAttendee)
		attProp.Value = "mailto:" + att.Email
		if att.Name != "" {
			attProp.Params.Set(ical.ParamCommonName, att.Name)
		}
		event.Props.Set(attProp)
	}

	cal.Children = append(cal.Children, event)

	var buf bytes.Buffer
	if err := ical.NewEncoder(&buf).Encode(cal); err != nil {
		return nil, fmt.Errorf("failed to encode cancel: %w", err)
	}

	return buf.Bytes(), nil
}

// ParseInvite parses an iCalendar blob and extracts invite information.
func ParseInvite(data []byte) (*Invite, error) {
	dec := ical.NewDecoder(bytes.NewReader(data))
	cal, err := dec.Decode()
	if err != nil {
		return nil, fmt.Errorf("failed to decode iCalendar: %w", err)
	}

	inv := &Invite{}

	// Get method
	if prop := cal.Props.Get(ical.PropMethod); prop != nil {
		inv.Method = Method(prop.Value)
	}

	// Find VEVENT
	for _, child := range cal.Children {
		if child.Name != ical.CompEvent {
			continue
		}

		if prop := child.Props.Get(ical.PropUID); prop != nil {
			inv.UID = prop.Value
		}
		if prop := child.Props.Get(ical.PropSummary); prop != nil {
			inv.Summary = prop.Value
		}
		if prop := child.Props.Get(ical.PropDescription); prop != nil {
			inv.Description = prop.Value
		}
		if prop := child.Props.Get(ical.PropLocation); prop != nil {
			inv.Location = prop.Value
		}
		if prop := child.Props.Get(ical.PropSequence); prop != nil {
			fmt.Sscanf(prop.Value, "%d", &inv.Sequence)
		}

		// Parse times
		if prop := child.Props.Get(ical.PropDateTimeStart); prop != nil {
			if t, err := prop.DateTime(time.UTC); err == nil {
				inv.Start = t
			}
		}
		if prop := child.Props.Get(ical.PropDateTimeEnd); prop != nil {
			if t, err := prop.DateTime(time.UTC); err == nil {
				inv.End = t
			}
		}
		if prop := child.Props.Get(ical.PropCreated); prop != nil {
			if t, err := prop.DateTime(time.UTC); err == nil {
				inv.Created = t
			}
		}

		// Organizer
		if prop := child.Props.Get(ical.PropOrganizer); prop != nil {
			inv.Organizer = parseParticipant(prop)
		}

		// Attendees
		for _, prop := range child.Props.Values(ical.PropAttendee) {
			inv.Attendees = append(inv.Attendees, parseParticipant(&prop))
		}

		break // Only process first VEVENT
	}

	return inv, nil
}

// parseParticipant extracts participant info from an ORGANIZER or ATTENDEE property.
func parseParticipant(prop *ical.Prop) Participant {
	p := Participant{}

	// Extract email from mailto: URI
	email := prop.Value
	if strings.HasPrefix(strings.ToLower(email), "mailto:") {
		email = email[7:]
	}
	p.Email = email

	// Common name
	if cn := prop.Params.Get(ical.ParamCommonName); cn != "" {
		p.Name = cn
	}

	// Participation status
	if ps := prop.Params.Get(ical.ParamParticipationStatus); ps != "" {
		p.Status = ParticipantStatus(ps)
	}

	// RSVP
	if rsvp := prop.Params.Get(ical.ParamRSVP); strings.ToUpper(rsvp) == "TRUE" {
		p.RSVP = true
	}

	return p
}

// GenerateUID generates a unique identifier for a meeting.
func GenerateUID(domain string) string {
	return fmt.Sprintf("%d-%d@%s", time.Now().UnixNano(), time.Now().Unix(), domain)
}
