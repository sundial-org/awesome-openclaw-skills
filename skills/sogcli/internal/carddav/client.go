// Package carddav provides a CardDAV client for contact operations.
package carddav

import (
	"context"
	"fmt"
	"net/http"
	"strings"

	"github.com/emersion/go-vcard"
	"github.com/emersion/go-webdav"
	"github.com/emersion/go-webdav/carddav"
)

// Client wraps a CardDAV client with convenience methods.
type Client struct {
	client *carddav.Client
	email  string
	url    string
}

// Config holds CardDAV connection configuration.
type Config struct {
	URL      string // CardDAV server URL
	Email    string // Account email (for auth)
	Password string // Account password
}

// Contact represents a contact/vCard.
type Contact struct {
	UID         string   `json:"uid"`
	FullName    string   `json:"full_name"`
	FirstName   string   `json:"first_name,omitempty"`
	LastName    string   `json:"last_name,omitempty"`
	Emails      []string `json:"emails,omitempty"`
	Phones      []string `json:"phones,omitempty"`
	Org         string   `json:"org,omitempty"`
	Title       string   `json:"title,omitempty"`
	Note        string   `json:"note,omitempty"`
	Birthday    string   `json:"birthday,omitempty"`
	Addresses   []string `json:"addresses,omitempty"`
	URL         string   `json:"url,omitempty"`
	ETag        string   `json:"etag,omitempty"`
}

// AddressBook represents an address book.
type AddressBook struct {
	Path        string `json:"path"`
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
}

// Connect establishes a connection to a CardDAV server.
func Connect(cfg Config) (*Client, error) {
	httpClient := webdav.HTTPClientWithBasicAuth(http.DefaultClient, cfg.Email, cfg.Password)

	client, err := carddav.NewClient(httpClient, cfg.URL)
	if err != nil {
		return nil, fmt.Errorf("failed to create CardDAV client: %w", err)
	}

	return &Client{
		client: client,
		email:  cfg.Email,
		url:    cfg.URL,
	}, nil
}

// Close closes the client connection.
func (c *Client) Close() error {
	// CardDAV is stateless HTTP, nothing to close
	return nil
}

// FindAddressBooks discovers available address books.
func (c *Client) FindAddressBooks(ctx context.Context) ([]AddressBook, error) {
	// First find the address book home set
	principal, err := c.client.FindCurrentUserPrincipal(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to find principal: %w", err)
	}

	homeSet, err := c.client.FindAddressBookHomeSet(ctx, principal)
	if err != nil {
		return nil, fmt.Errorf("failed to find address book home set: %w", err)
	}

	books, err := c.client.FindAddressBooks(ctx, homeSet)
	if err != nil {
		return nil, fmt.Errorf("failed to find address books: %w", err)
	}

	result := make([]AddressBook, 0, len(books))
	for _, book := range books {
		result = append(result, AddressBook{
			Path:        book.Path,
			Name:        book.Name,
			Description: book.Description,
		})
	}
	return result, nil
}

// ListContacts retrieves all contacts from an address book.
func (c *Client) ListContacts(ctx context.Context, bookPath string) ([]Contact, error) {
	query := &carddav.AddressBookQuery{
		DataRequest: carddav.AddressDataRequest{
			Props: []string{
				vcard.FieldUID,
				vcard.FieldFormattedName,
				vcard.FieldName,
				vcard.FieldEmail,
				vcard.FieldTelephone,
				vcard.FieldOrganization,
				vcard.FieldTitle,
				vcard.FieldNote,
				vcard.FieldBirthday,
				vcard.FieldAddress,
				vcard.FieldURL,
			},
		},
	}

	objects, err := c.client.QueryAddressBook(ctx, bookPath, query)
	if err != nil {
		return nil, fmt.Errorf("failed to query address book: %w", err)
	}

	contacts := make([]Contact, 0, len(objects))
	for _, obj := range objects {
		contact := parseVCard(obj.Card)
		contact.ETag = obj.ETag
		contacts = append(contacts, contact)
	}

	return contacts, nil
}

// GetContact retrieves a single contact by UID.
func (c *Client) GetContact(ctx context.Context, bookPath, uid string) (*Contact, error) {
	query := &carddav.AddressBookQuery{
		DataRequest: carddav.AddressDataRequest{
			AllProp: true,
		},
		PropFilters: []carddav.PropFilter{{
			Name:        vcard.FieldUID,
			TextMatches: []carddav.TextMatch{{Text: uid}},
		}},
	}

	objects, err := c.client.QueryAddressBook(ctx, bookPath, query)
	if err != nil {
		return nil, fmt.Errorf("failed to query address book: %w", err)
	}

	if len(objects) == 0 {
		return nil, fmt.Errorf("contact not found: %s", uid)
	}

	contact := parseVCard(objects[0].Card)
	contact.ETag = objects[0].ETag
	return &contact, nil
}

// SearchContacts searches for contacts matching a query.
func (c *Client) SearchContacts(ctx context.Context, bookPath, searchQuery string) ([]Contact, error) {
	query := &carddav.AddressBookQuery{
		DataRequest: carddav.AddressDataRequest{
			AllProp: true,
		},
		PropFilters: []carddav.PropFilter{{
			Name:        vcard.FieldFormattedName,
			TextMatches: []carddav.TextMatch{{Text: searchQuery, MatchType: carddav.MatchContains}},
		}},
	}

	objects, err := c.client.QueryAddressBook(ctx, bookPath, query)
	if err != nil {
		return nil, fmt.Errorf("failed to search address book: %w", err)
	}

	contacts := make([]Contact, 0, len(objects))
	for _, obj := range objects {
		contact := parseVCard(obj.Card)
		contact.ETag = obj.ETag
		contacts = append(contacts, contact)
	}

	return contacts, nil
}

// CreateContact creates a new contact.
func (c *Client) CreateContact(ctx context.Context, bookPath string, contact *Contact) error {
	card := createVCard(contact)
	_, err := c.client.PutAddressObject(ctx, bookPath+"/"+contact.UID+".vcf", card)
	if err != nil {
		return fmt.Errorf("failed to create contact: %w", err)
	}
	return nil
}

// UpdateContact updates an existing contact.
func (c *Client) UpdateContact(ctx context.Context, bookPath string, contact *Contact) error {
	card := createVCard(contact)
	_, err := c.client.PutAddressObject(ctx, bookPath+"/"+contact.UID+".vcf", card)
	if err != nil {
		return fmt.Errorf("failed to update contact: %w", err)
	}
	return nil
}

// DeleteContact deletes a contact.
func (c *Client) DeleteContact(ctx context.Context, bookPath, uid string) error {
	err := c.client.RemoveAll(ctx, bookPath+"/"+uid+".vcf")
	if err != nil {
		return fmt.Errorf("failed to delete contact: %w", err)
	}
	return nil
}

// parseVCard parses a vCard into a Contact.
func parseVCard(card vcard.Card) Contact {
	contact := Contact{}

	// UID
	if field := card.Get(vcard.FieldUID); field != nil {
		contact.UID = field.Value
	}

	// Full name (FN)
	if field := card.Get(vcard.FieldFormattedName); field != nil {
		contact.FullName = field.Value
	}

	// Structured name (N) - format: Family;Given;Additional;Prefix;Suffix
	if field := card.Get(vcard.FieldName); field != nil {
		parts := strings.Split(field.Value, ";")
		if len(parts) >= 1 {
			contact.LastName = parts[0]
		}
		if len(parts) >= 2 {
			contact.FirstName = parts[1]
		}
	}

	// Emails
	for _, field := range card[vcard.FieldEmail] {
		contact.Emails = append(contact.Emails, field.Value)
	}

	// Phones
	for _, field := range card[vcard.FieldTelephone] {
		contact.Phones = append(contact.Phones, field.Value)
	}

	// Organization
	if field := card.Get(vcard.FieldOrganization); field != nil {
		contact.Org = field.Value
	}

	// Title
	if field := card.Get(vcard.FieldTitle); field != nil {
		contact.Title = field.Value
	}

	// Note
	if field := card.Get(vcard.FieldNote); field != nil {
		contact.Note = field.Value
	}

	// Birthday
	if field := card.Get(vcard.FieldBirthday); field != nil {
		contact.Birthday = field.Value
	}

	// Addresses
	for _, field := range card[vcard.FieldAddress] {
		addr := field.Value
		// Format address nicely if it has semicolons (vCard format)
		addr = strings.ReplaceAll(addr, ";", ", ")
		addr = strings.Trim(addr, ", ")
		if addr != "" {
			contact.Addresses = append(contact.Addresses, addr)
		}
	}

	// URL
	if field := card.Get(vcard.FieldURL); field != nil {
		contact.URL = field.Value
	}

	return contact
}

// createVCard creates a vCard from a Contact.
func createVCard(contact *Contact) vcard.Card {
	card := make(vcard.Card)

	// Version (required)
	card.SetValue(vcard.FieldVersion, "4.0")

	// UID
	card.SetValue(vcard.FieldUID, contact.UID)

	// Full name (FN) - required
	if contact.FullName != "" {
		card.SetValue(vcard.FieldFormattedName, contact.FullName)
	} else if contact.FirstName != "" || contact.LastName != "" {
		card.SetValue(vcard.FieldFormattedName, strings.TrimSpace(contact.FirstName+" "+contact.LastName))
	}

	// Structured name (N)
	if contact.FirstName != "" || contact.LastName != "" {
		nameField := &vcard.Field{
			Value: contact.LastName + ";" + contact.FirstName + ";;;",
		}
		card.Set(vcard.FieldName, nameField)
	}

	// Emails
	for _, email := range contact.Emails {
		field := &vcard.Field{Value: email}
		card.Add(vcard.FieldEmail, field)
	}

	// Phones
	for _, phone := range contact.Phones {
		field := &vcard.Field{Value: phone}
		card.Add(vcard.FieldTelephone, field)
	}

	// Organization
	if contact.Org != "" {
		card.SetValue(vcard.FieldOrganization, contact.Org)
	}

	// Title
	if contact.Title != "" {
		card.SetValue(vcard.FieldTitle, contact.Title)
	}

	// Note
	if contact.Note != "" {
		card.SetValue(vcard.FieldNote, contact.Note)
	}

	// Birthday
	if contact.Birthday != "" {
		card.SetValue(vcard.FieldBirthday, contact.Birthday)
	}

	// Addresses
	for _, addr := range contact.Addresses {
		field := &vcard.Field{Value: addr}
		card.Add(vcard.FieldAddress, field)
	}

	// URL
	if contact.URL != "" {
		card.SetValue(vcard.FieldURL, contact.URL)
	}

	return card
}
