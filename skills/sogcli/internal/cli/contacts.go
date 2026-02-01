package cli

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/visionik/sogcli/internal/carddav"
	"github.com/visionik/sogcli/internal/config"
)

// ContactsCmd handles contact operations.
type ContactsCmd struct {
	List   ContactsListCmd   `cmd:"" help:"List contacts"`
	Get    ContactsGetCmd    `cmd:"" help:"Get contact details"`
	Search ContactsSearchCmd `cmd:"" help:"Search contacts"`
	Create ContactsCreateCmd `cmd:"" help:"Create a contact"`
	Update ContactsUpdateCmd `cmd:"" help:"Update a contact"`
	Delete ContactsDeleteCmd `cmd:"" help:"Delete a contact"`
	Books  ContactsBooksCmd  `cmd:"" name:"books" help:"List address books"`
}

// ContactsListCmd lists contacts in an address book.
type ContactsListCmd struct {
	AddressBook string `arg:"" optional:"" help:"Address book path (default: primary)"`
	Max         int    `help:"Maximum contacts to return" default:"100"`
}

// Run executes the contacts list command.
func (c *ContactsListCmd) Run(root *Root) error {
	client, bookPath, err := getCardDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.AddressBook != "" {
		bookPath = c.AddressBook
	}

	ctx := context.Background()
	contacts, err := client.ListContacts(ctx, bookPath)
	if err != nil {
		return fmt.Errorf("failed to list contacts: %w", err)
	}

	if len(contacts) == 0 {
		fmt.Println("No contacts found.")
		return nil
	}

	// Limit results
	if c.Max > 0 && len(contacts) > c.Max {
		contacts = contacts[:c.Max]
	}

	if root.JSON {
		return outputContactsJSON(contacts)
	}

	return outputContactsTable(contacts)
}

// ContactsGetCmd gets contact details.
type ContactsGetCmd struct {
	UID         string `arg:"" help:"Contact UID"`
	AddressBook string `help:"Address book path (default: primary)"`
}

// Run executes the contacts get command.
func (c *ContactsGetCmd) Run(root *Root) error {
	client, bookPath, err := getCardDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.AddressBook != "" {
		bookPath = c.AddressBook
	}

	ctx := context.Background()
	contact, err := client.GetContact(ctx, bookPath, c.UID)
	if err != nil {
		return fmt.Errorf("failed to get contact: %w", err)
	}

	if root.JSON {
		return outputContactsJSON([]carddav.Contact{*contact})
	}

	return outputContactDetail(contact)
}

// ContactsSearchCmd searches for contacts.
type ContactsSearchCmd struct {
	Query       string `arg:"" help:"Search query (name)"`
	AddressBook string `help:"Address book path (default: primary)"`
}

// Run executes the contacts search command.
func (c *ContactsSearchCmd) Run(root *Root) error {
	client, bookPath, err := getCardDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.AddressBook != "" {
		bookPath = c.AddressBook
	}

	ctx := context.Background()
	contacts, err := client.SearchContacts(ctx, bookPath, c.Query)
	if err != nil {
		return fmt.Errorf("failed to search contacts: %w", err)
	}

	if len(contacts) == 0 {
		fmt.Println("No contacts found.")
		return nil
	}

	if root.JSON {
		return outputContactsJSON(contacts)
	}

	return outputContactsTable(contacts)
}

// ContactsCreateCmd creates a contact.
type ContactsCreateCmd struct {
	Name        string   `arg:"" help:"Full name"`
	Email       []string `help:"Email addresses" short:"e"`
	Phone       []string `help:"Phone numbers" short:"p"`
	Org         string   `help:"Organization"`
	Title       string   `help:"Job title"`
	Note        string   `help:"Note"`
	AddressBook string   `help:"Address book path (default: primary)"`
}

// Run executes the contacts create command.
func (c *ContactsCreateCmd) Run(root *Root) error {
	client, bookPath, err := getCardDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.AddressBook != "" {
		bookPath = c.AddressBook
	}

	// Parse name into first/last
	firstName, lastName := parseName(c.Name)

	contact := &carddav.Contact{
		UID:       generateContactUID(),
		FullName:  c.Name,
		FirstName: firstName,
		LastName:  lastName,
		Emails:    c.Email,
		Phones:    c.Phone,
		Org:       c.Org,
		Title:     c.Title,
		Note:      c.Note,
	}

	ctx := context.Background()
	if err := client.CreateContact(ctx, bookPath, contact); err != nil {
		return fmt.Errorf("failed to create contact: %w", err)
	}

	if root.JSON {
		return outputContactsJSON([]carddav.Contact{*contact})
	}

	fmt.Printf("Created contact: %s (%s)\n", contact.FullName, contact.UID)
	return nil
}

// ContactsUpdateCmd updates a contact.
type ContactsUpdateCmd struct {
	UID         string   `arg:"" help:"Contact UID"`
	Name        string   `help:"Full name"`
	Email       []string `help:"Email addresses (replaces existing)" short:"e"`
	Phone       []string `help:"Phone numbers (replaces existing)" short:"p"`
	Org         string   `help:"Organization"`
	Title       string   `help:"Job title"`
	Note        string   `help:"Note"`
	AddressBook string   `help:"Address book path (default: primary)"`
}

// Run executes the contacts update command.
func (c *ContactsUpdateCmd) Run(root *Root) error {
	client, bookPath, err := getCardDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.AddressBook != "" {
		bookPath = c.AddressBook
	}

	ctx := context.Background()
	contact, err := client.GetContact(ctx, bookPath, c.UID)
	if err != nil {
		return fmt.Errorf("failed to get contact: %w", err)
	}

	// Apply updates
	if c.Name != "" {
		contact.FullName = c.Name
		contact.FirstName, contact.LastName = parseName(c.Name)
	}
	if len(c.Email) > 0 {
		contact.Emails = c.Email
	}
	if len(c.Phone) > 0 {
		contact.Phones = c.Phone
	}
	if c.Org != "" {
		contact.Org = c.Org
	}
	if c.Title != "" {
		contact.Title = c.Title
	}
	if c.Note != "" {
		contact.Note = c.Note
	}

	if err := client.UpdateContact(ctx, bookPath, contact); err != nil {
		return fmt.Errorf("failed to update contact: %w", err)
	}

	fmt.Printf("Updated contact: %s\n", c.UID)
	return nil
}

// ContactsDeleteCmd deletes a contact.
type ContactsDeleteCmd struct {
	UID         string `arg:"" help:"Contact UID"`
	AddressBook string `help:"Address book path (default: primary)"`
}

// Run executes the contacts delete command.
func (c *ContactsDeleteCmd) Run(root *Root) error {
	client, bookPath, err := getCardDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	if c.AddressBook != "" {
		bookPath = c.AddressBook
	}

	ctx := context.Background()
	if err := client.DeleteContact(ctx, bookPath, c.UID); err != nil {
		return fmt.Errorf("failed to delete contact: %w", err)
	}

	fmt.Printf("Deleted contact: %s\n", c.UID)
	return nil
}

// ContactsBooksCmd lists available address books.
type ContactsBooksCmd struct{}

// Run executes the contacts books command.
func (c *ContactsBooksCmd) Run(root *Root) error {
	client, _, err := getCardDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	books, err := client.FindAddressBooks(ctx)
	if err != nil {
		return fmt.Errorf("failed to list address books: %w", err)
	}

	if len(books) == 0 {
		fmt.Println("No address books found.")
		return nil
	}

	if root.JSON {
		return outputAddressBooksJSON(books)
	}

	fmt.Printf("%-50s %s\n", "PATH", "NAME")
	for _, book := range books {
		fmt.Printf("%-50s %s\n", book.Path, book.Name)
	}
	return nil
}

// getCardDAVClient creates a CardDAV client from config.
func getCardDAVClient(root *Root) (*carddav.Client, string, error) {
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

	if acct.CardDAV.URL == "" {
		return nil, "", fmt.Errorf("no CardDAV URL configured for %s. Run: sog auth add %s --carddav-url <url>", email, email)
	}

	password, err := cfg.GetPasswordForProtocol(email, config.ProtocolCardDAV)
	if err != nil {
		return nil, "", fmt.Errorf("failed to get password: %w", err)
	}

	client, err := carddav.Connect(carddav.Config{
		URL:      acct.CardDAV.URL,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return nil, "", fmt.Errorf("failed to connect to CardDAV: %w", err)
	}

	return client, acct.CardDAV.DefaultAddressBook, nil
}

// parseName splits a full name into first and last name.
func parseName(fullName string) (first, last string) {
	parts := strings.Fields(fullName)
	if len(parts) == 0 {
		return "", ""
	}
	if len(parts) == 1 {
		return parts[0], ""
	}
	return parts[0], strings.Join(parts[1:], " ")
}

// generateContactUID generates a unique identifier for a contact.
func generateContactUID() string {
	return fmt.Sprintf("%d@sog", time.Now().UnixNano())
}

// outputContactsJSON outputs contacts as JSON.
func outputContactsJSON(contacts []carddav.Contact) error {
	for _, c := range contacts {
		emails := strings.Join(c.Emails, ",")
		phones := strings.Join(c.Phones, ",")
		fmt.Printf(`{"uid":"%s","full_name":"%s","emails":"%s","phones":"%s","org":"%s"}`+"\n",
			c.UID, c.FullName, emails, phones, c.Org)
	}
	return nil
}

// outputContactsTable outputs contacts as a table.
func outputContactsTable(contacts []carddav.Contact) error {
	fmt.Printf("%-30s %-30s %-20s\n", "NAME", "EMAIL", "PHONE")
	for _, c := range contacts {
		name := c.FullName
		if len(name) > 30 {
			name = name[:27] + "..."
		}
		email := ""
		if len(c.Emails) > 0 {
			email = c.Emails[0]
		}
		if len(email) > 30 {
			email = email[:27] + "..."
		}
		phone := ""
		if len(c.Phones) > 0 {
			phone = c.Phones[0]
		}
		fmt.Printf("%-30s %-30s %-20s\n", name, email, phone)
	}
	return nil
}

// outputContactDetail outputs a single contact in detail.
func outputContactDetail(contact *carddav.Contact) error {
	fmt.Printf("UID:       %s\n", contact.UID)
	fmt.Printf("Name:      %s\n", contact.FullName)
	if contact.FirstName != "" || contact.LastName != "" {
		fmt.Printf("           (First: %s, Last: %s)\n", contact.FirstName, contact.LastName)
	}
	if len(contact.Emails) > 0 {
		fmt.Printf("Email:     %s\n", strings.Join(contact.Emails, ", "))
	}
	if len(contact.Phones) > 0 {
		fmt.Printf("Phone:     %s\n", strings.Join(contact.Phones, ", "))
	}
	if contact.Org != "" {
		fmt.Printf("Org:       %s\n", contact.Org)
	}
	if contact.Title != "" {
		fmt.Printf("Title:     %s\n", contact.Title)
	}
	if len(contact.Addresses) > 0 {
		fmt.Printf("Address:   %s\n", strings.Join(contact.Addresses, "; "))
	}
	if contact.Birthday != "" {
		fmt.Printf("Birthday:  %s\n", contact.Birthday)
	}
	if contact.Note != "" {
		fmt.Printf("Note:      %s\n", contact.Note)
	}
	if contact.URL != "" {
		fmt.Printf("URL:       %s\n", contact.URL)
	}
	return nil
}

// outputAddressBooksJSON outputs address books as JSON.
func outputAddressBooksJSON(books []carddav.AddressBook) error {
	for _, b := range books {
		fmt.Printf(`{"path":"%s","name":"%s","description":"%s"}`+"\n", b.Path, b.Name, b.Description)
	}
	return nil
}
