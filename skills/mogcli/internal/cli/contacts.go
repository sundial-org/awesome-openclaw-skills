package cli

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"

	"github.com/visionik/mogcli/internal/graph"
)

// ContactsCmd handles contact operations.
type ContactsCmd struct {
	List      ContactsListCmd      `cmd:"" help:"List contacts"`
	Search    ContactsSearchCmd    `cmd:"" help:"Search contacts"`
	Get       ContactsGetCmd       `cmd:"" help:"Get a contact"`
	Create    ContactsCreateCmd    `cmd:"" help:"Create a contact"`
	Update    ContactsUpdateCmd    `cmd:"" help:"Update a contact"`
	Delete    ContactsDeleteCmd    `cmd:"" help:"Delete a contact"`
	Directory ContactsDirectoryCmd `cmd:"" help:"Search organization directory"`
}

// ContactsListCmd lists contacts.
type ContactsListCmd struct {
	Max int `help:"Maximum results" default:"50"`
}

// Run executes contacts list.
func (c *ContactsListCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$top", fmt.Sprintf("%d", c.Max))
	query.Set("$orderby", "displayName")

	data, err := client.Get(ctx, "/me/contacts", query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Contact `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, c := range resp.Value {
		email := ""
		if len(c.EmailAddresses) > 0 {
			email = c.EmailAddresses[0].Address
		}
		fmt.Printf("%-30s %-30s %s\n", c.DisplayName, email, graph.FormatID(c.ID))
	}
	return nil
}

// ContactsSearchCmd searches contacts.
type ContactsSearchCmd struct {
	Query string `arg:"" help:"Search query"`
}

// Run executes contacts search.
func (c *ContactsSearchCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$filter", fmt.Sprintf("contains(displayName,'%s') or contains(emailAddresses/any(a:a/address),'%s')", c.Query, c.Query))

	data, err := client.Get(ctx, "/me/contacts", query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Contact `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, c := range resp.Value {
		email := ""
		if len(c.EmailAddresses) > 0 {
			email = c.EmailAddresses[0].Address
		}
		fmt.Printf("%-30s %-30s %s\n", c.DisplayName, email, graph.FormatID(c.ID))
	}
	return nil
}

// ContactsGetCmd gets a contact.
type ContactsGetCmd struct {
	ID string `arg:"" help:"Contact ID"`
}

// Run executes contacts get.
func (c *ContactsGetCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/contacts/%s", graph.ResolveID(c.ID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var contact Contact
	if err := json.Unmarshal(data, &contact); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(contact)
	}

	fmt.Printf("ID:    %s\n", graph.FormatID(contact.ID))
	fmt.Printf("Name:  %s\n", contact.DisplayName)
	for _, e := range contact.EmailAddresses {
		fmt.Printf("Email: %s\n", e.Address)
	}
	for _, p := range contact.BusinessPhones {
		fmt.Printf("Phone: %s (business)\n", p)
	}
	if contact.MobilePhone != "" {
		fmt.Printf("Phone: %s (mobile)\n", contact.MobilePhone)
	}
	if contact.CompanyName != "" {
		fmt.Printf("Company: %s\n", contact.CompanyName)
	}
	if contact.JobTitle != "" {
		fmt.Printf("Title: %s\n", contact.JobTitle)
	}
	return nil
}

// ContactsCreateCmd creates a contact.
type ContactsCreateCmd struct {
	Name    string `help:"Display name" required:"" name:"name"`
	Email   string `help:"Email address"`
	Phone   string `help:"Phone number"`
	Company string `help:"Company name"`
	Title   string `help:"Job title"`
}

// Run executes contacts create.
func (c *ContactsCreateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	contact := map[string]interface{}{
		"displayName": c.Name,
	}

	if c.Email != "" {
		contact["emailAddresses"] = []map[string]string{
			{"address": c.Email},
		}
	}

	if c.Phone != "" {
		contact["businessPhones"] = []string{c.Phone}
	}

	if c.Company != "" {
		contact["companyName"] = c.Company
	}

	if c.Title != "" {
		contact["jobTitle"] = c.Title
	}

	ctx := context.Background()
	data, err := client.Post(ctx, "/me/contacts", contact)
	if err != nil {
		return err
	}

	var created Contact
	if err := json.Unmarshal(data, &created); err != nil {
		return err
	}

	fmt.Printf("✓ Contact created: %s (%s)\n", created.DisplayName, graph.FormatID(created.ID))
	return nil
}

// ContactsUpdateCmd updates a contact.
type ContactsUpdateCmd struct {
	ID      string `arg:"" help:"Contact ID"`
	Name    string `help:"Display name"`
	Email   string `help:"Email address"`
	Phone   string `help:"Phone number"`
	Company string `help:"Company name"`
	Title   string `help:"Job title"`
}

// Run executes contacts update.
func (c *ContactsUpdateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	updates := make(map[string]interface{})

	if c.Name != "" {
		updates["displayName"] = c.Name
	}
	if c.Email != "" {
		updates["emailAddresses"] = []map[string]string{{"address": c.Email}}
	}
	if c.Phone != "" {
		updates["businessPhones"] = []string{c.Phone}
	}
	if c.Company != "" {
		updates["companyName"] = c.Company
	}
	if c.Title != "" {
		updates["jobTitle"] = c.Title
	}

	if len(updates) == 0 {
		return fmt.Errorf("no updates specified")
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/contacts/%s", graph.ResolveID(c.ID))

	_, err = client.Patch(ctx, path, updates)
	if err != nil {
		return err
	}

	fmt.Println("✓ Contact updated")
	return nil
}

// ContactsDeleteCmd deletes a contact.
type ContactsDeleteCmd struct {
	ID string `arg:"" help:"Contact ID"`
}

// Run executes contacts delete.
func (c *ContactsDeleteCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/contacts/%s", graph.ResolveID(c.ID))

	if err := client.Delete(ctx, path); err != nil {
		return err
	}

	fmt.Println("✓ Contact deleted")
	return nil
}

// ContactsDirectoryCmd searches the organization directory.
type ContactsDirectoryCmd struct {
	Query string `arg:"" help:"Search query"`
}

// Run executes contacts directory.
func (c *ContactsDirectoryCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$search", fmt.Sprintf(`"displayName:%s" OR "mail:%s"`, c.Query, c.Query))
	query.Set("$top", "25")

	data, err := client.Get(ctx, "/users", query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []DirectoryUser `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	for _, u := range resp.Value {
		fmt.Printf("%-30s %-30s %s\n", u.DisplayName, u.Mail, u.JobTitle)
	}
	return nil
}

// Contact represents a contact.
type Contact struct {
	ID             string        `json:"id"`
	DisplayName    string        `json:"displayName"`
	EmailAddresses []EmailRecord `json:"emailAddresses"`
	BusinessPhones []string      `json:"businessPhones"`
	MobilePhone    string        `json:"mobilePhone"`
	CompanyName    string        `json:"companyName"`
	JobTitle       string        `json:"jobTitle"`
}

// EmailRecord represents an email record.
type EmailRecord struct {
	Address string `json:"address"`
	Name    string `json:"name"`
}

// DirectoryUser represents a directory user.
type DirectoryUser struct {
	ID          string `json:"id"`
	DisplayName string `json:"displayName"`
	Mail        string `json:"mail"`
	JobTitle    string `json:"jobTitle"`
}
