---
name: local-pandoc
description: Converts Markdown files to PDF files using the pandoc command-line utility. Use when a user asks to convert a .md or markdown file to a .pdf file.
---

# Local Pandoc Conversion Skill

This skill uses the `pandoc` command-line utility to convert documents between numerous markup formats.

## Basic Usage

The fundamental structure of a `pandoc` command is:

```bash
pandoc [options] [input-file]…
```

### Simple Conversion

To convert a Markdown file to HTML:

```bash
pandoc -o output.html input.md
```

### Specifying Formats

While `pandoc` can infer formats from file extensions, you can be explicit with the `-f` (from) and `-t` (to) flags.

```bash
# Convert HTML to Markdown
pandoc -f html -t markdown input.html
```

### Standalone Documents

To create a complete document with a proper header and footer (e.g., a full HTML file), use the `-s` or `--standalone` flag.

```bash
pandoc -s -o output.html input.md
```

## Advanced Examples

The following examples are extracted from the official Pandoc User's Guide.

### PDF Output

To create a PDF, `pandoc` typically uses a LaTeX engine. Ensure one is installed.

```bash
# Basic PDF creation
pandoc input.md -o output.pdf

# Control PDF engine and style via variables
pandoc input.md -o output.pdf --pdf-engine=xelatex -V geometry:margin=1in -V fontsize=12pt
```

### Document Structure & Metadata

Pandoc can automatically generate a table of contents and use document metadata.

```bash
# Create a document with a Table of Contents (up to level 3 headings)
pandoc --toc --toc-depth=3 -o output.docx input.md

# Set metadata fields from the command line
pandoc -M title:"My Report" -M author:"Galactus" -o output.pdf input.md
```

### Templates and Styling

You can control the final output's structure and style with templates and other options.

```bash
# Use a custom template for HTML output
pandoc -s --template=my-template.html -o output.html input.md

# For HTML output, link to a custom CSS file
pandoc -s --css=styles.css -o output.html input.md

# For DOCX output, use a reference document for styling
pandoc --reference-doc=reference.docx -o output.docx input.md
```

### Reading from the Web

Pandoc can directly fetch and convert content from a URL.

```bash
pandoc -f html -t markdown https://www.fsf.org
```

### Other Useful Options

```bash
# Preserve tabs instead of converting them to spaces
pandoc --preserve-tabs ...

# Control line wrapping in the output source code
pandoc --wrap=none ...

# Shift heading levels (e.g., make all H1s into H2s, H2s into H3s)
pandoc --shift-heading-level-by=1 ...
```
This enhanced documentation provides a more robust foundation for using `pandoc`.
