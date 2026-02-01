// sog - Standards Ops Gadget
//
// Open-standards CLI for mail, calendar, contacts, tasks, and files.
// IMAP/SMTP/CalDAV/CardDAV/WebDAV alternative to gog (Google) and mog (Microsoft).
package main

import (
	"fmt"
	"os"

	"github.com/alecthomas/kong"
	"github.com/visionik/sogcli/internal/cli"
)

var version = "dev"

func main() {
	// Handle --ai-help before kong parsing
	for _, arg := range os.Args[1:] {
		if arg == "--ai-help" || arg == "-ai-help" {
			fmt.Println(cli.AIHelpText)
			os.Exit(0)
		}
	}

	var root cli.Root
	ctx := kong.Parse(&root,
		kong.Name("sog"),
		kong.Description("Standards Ops Gadget — IMAP/SMTP/CalDAV/CardDAV/WebDAV CLI"),
		kong.UsageOnError(),
		kong.Vars{
			"version": version,
		},
		kong.PostBuild(func(k *kong.Kong) error {
			// Add --ai-help to the help text manually
			return nil
		}),
	)

	err := ctx.Run(&root)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}
}
