// mog - Microsoft Ops Gadget
//
// CLI for Microsoft 365 — Mail, Calendar, Drive, Contacts, Tasks, Word, PowerPoint, Excel, OneNote
// Go port of the original Node.js version.
package main

import (
	"fmt"
	"os"

	"github.com/alecthomas/kong"
	"github.com/visionik/mogcli/internal/cli"
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
		kong.Name("mog"),
		kong.Description("Microsoft Ops Gadget — CLI for Microsoft 365"),
		kong.UsageOnError(),
		kong.Vars{
			"version": version,
		},
	)

	err := ctx.Run(&root)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}
}
