// Package cli defines the command-line interface for mog.
package cli

import (
	"fmt"
	"os"

	"github.com/visionik/mogcli/internal/graph"
)

// ClientFactory is a function that creates a Graph client.
// This allows dependency injection for testing.
type ClientFactory func() (graph.Client, error)

// Root is the top-level CLI structure.
type Root struct {
	// Global flags
	AIHelp  bool        `name:"ai-help" help:"Show detailed help for AI/LLM agents"`
	JSON    bool        `help:"Output JSON to stdout (best for scripting)" xor:"format"`
	Plain   bool        `help:"Output stable, parseable text to stdout (TSV; no colors)" xor:"format"`
	Verbose bool        `help:"Show full IDs and extra details" short:"v"`
	Force   bool        `help:"Skip confirmations for destructive commands"`
	NoInput bool        `help:"Never prompt; fail instead (useful for CI)" name:"no-input"`
	Version VersionFlag `name:"version" help:"Print version and exit"`

	// Subcommands
	Auth     AuthCmd     `cmd:"" help:"Authentication"`
	Mail     MailCmd     `cmd:"" aliases:"email" help:"Mail operations"`
	Calendar CalendarCmd `cmd:"" aliases:"cal" help:"Calendar operations"`
	Drive    DriveCmd    `cmd:"" help:"OneDrive file operations"`
	Contacts ContactsCmd `cmd:"" help:"Contact operations"`
	Tasks    TasksCmd    `cmd:"" aliases:"todo" help:"Microsoft To-Do tasks"`
	Excel    ExcelCmd    `cmd:"" help:"Excel spreadsheet operations"`
	OneNote  OneNoteCmd  `cmd:"" aliases:"onenote" help:"OneNote operations"`
	Word     WordCmd     `cmd:"" help:"Word document operations"`
	PPT      PPTCmd      `cmd:"" aliases:"ppt,powerpoint" help:"PowerPoint operations"`

	// ClientFactory allows injecting a custom client factory for testing.
	// If nil, graph.NewClient is used.
	ClientFactory ClientFactory `kong:"-"`
}

// GetClient returns a Graph client using the configured factory or default.
func (r *Root) GetClient() (graph.Client, error) {
	if r.ClientFactory != nil {
		return r.ClientFactory()
	}
	return graph.NewClient()
}

// VersionFlag handles --version.
type VersionFlag string

// BeforeApply prints version and exits.
func (v VersionFlag) BeforeApply() error {
	fmt.Println(v)
	os.Exit(0)
	return nil
}
