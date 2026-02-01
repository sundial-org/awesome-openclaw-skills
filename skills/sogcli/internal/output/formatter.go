// Package output provides output formatting utilities.
package output

import (
	"encoding/json"
	"fmt"
	"io"
	"strings"
)

// Format represents an output format.
type Format int

const (
	// FormatHuman is human-readable output.
	FormatHuman Format = iota
	// FormatJSON is JSON output.
	FormatJSON
	// FormatPlain is plain TSV output.
	FormatPlain
)

// Formatter handles output formatting.
type Formatter struct {
	format Format
	writer io.Writer
}

// New creates a new Formatter.
func New(w io.Writer, json, plain bool) *Formatter {
	f := &Formatter{writer: w, format: FormatHuman}
	if json {
		f.format = FormatJSON
	} else if plain {
		f.format = FormatPlain
	}
	return f
}

// Print outputs data in the configured format.
func (f *Formatter) Print(data any) error {
	switch f.format {
	case FormatJSON:
		return f.printJSON(data)
	case FormatPlain:
		return f.printPlain(data)
	default:
		return f.printHuman(data)
	}
}

func (f *Formatter) printJSON(data any) error {
	enc := json.NewEncoder(f.writer)
	enc.SetIndent("", "  ")
	return enc.Encode(data)
}

func (f *Formatter) printPlain(data any) error {
	// For plain output, convert to TSV-like format
	switch v := data.(type) {
	case []map[string]any:
		for _, row := range v {
			values := make([]string, 0, len(row))
			for _, val := range row {
				values = append(values, fmt.Sprintf("%v", val))
			}
			fmt.Fprintln(f.writer, strings.Join(values, "\t"))
		}
	case map[string]any:
		for k, val := range v {
			fmt.Fprintf(f.writer, "%s\t%v\n", k, val)
		}
	default:
		fmt.Fprintln(f.writer, data)
	}
	return nil
}

func (f *Formatter) printHuman(data any) error {
	// Default: just print
	fmt.Fprintln(f.writer, data)
	return nil
}
