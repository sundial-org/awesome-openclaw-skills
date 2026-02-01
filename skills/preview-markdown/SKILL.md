---
name: preview-markdown
description: Render and preview Markdown files in browser with GitHub-flavored formatting and syntax highlighting
user-invocable: true
commands:
  - preview
  - preview-markdown
---

# Preview Markdown Skill

GitHub-flavored Markdown viewer that generates beautiful HTML with syntax highlighting and automatic table of contents.

## Usage

```bash
# Preview a Markdown file
/preview README.md

# Pipe Markdown content (preferred for temporary content)
cat docs.md | /preview
echo "# Hello\n\nThis is **markdown**" | /preview

# With custom background color
/preview article.md --background "#ffffff"
```

**Best Practice:** For temporary or generated content, prefer piping over creating temporary files. This avoids cluttering your filesystem and the content is automatically cleaned up.

## Options

The script works with sensible defaults but supports these flags for flexibility:

- `-o, --output PATH` - Custom output path
- `--no-browser` - Skip browser, output file path only

## Features

- **GitHub-flavored Markdown** rendering with full spec support
- **Syntax highlighting** for code blocks (100+ languages)
- **Automatic TOC** generation from headers
- **Task lists** with checkboxes
- **Tables** with formatting
- **Images and links** fully supported
- **Math equations** (LaTeX via KaTeX)
- **Emoji** support
- **Footnotes** and references
- **Responsive design** adapts to screen size

## When to Use This Skill

Use this skill when the user wants to:

- Preview README or documentation files
- Read formatted Markdown documents
- Verify Markdown rendering before publishing
- Share formatted documentation
- Review pull request descriptions

## Examples

**Natural language requests:**

- "preview this README"
- "show me the documentation"
- "open the markdown file"
- "visualize CONTRIBUTING.md"
- "let me see the formatted docs"

## Technical Details

### File Requirements

- File extensions: `.md`, `.markdown`
- Maximum size: 10MB (configurable)
- Encoding: UTF-8

### Features in Detail

#### GitHub-Flavored Markdown

Supports all GitHub Markdown features:

- Headers (h1-h6)
- Bold, italic, strikethrough
- Ordered and unordered lists
- Code blocks with language specification
- Blockquotes
- Horizontal rules
- Links and images
- Tables

#### Syntax Highlighting

- Automatic language detection
- 100+ programming languages supported
- Theme: GitHub light/dark
- Line numbers optional
- Copy code button

#### Table of Contents

- Auto-generated from headers
- Clickable links to sections
- Hierarchical structure
- Sticky sidebar navigation

#### Task Lists

```markdown
- [x] Completed task
- [ ] Pending task
```

#### Tables

Full support for:

- Header rows
- Alignment (left, center, right)
- Multi-line cells
- Inline formatting

### Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- CDN-dependent: Marked.js, DOMPurify, Mermaid (for diagrams in markdown)

## Output

The skill generates a standalone HTML file at:

```
/tmp/preview-skills/preview-markdown-{filename}.html
```

The file is self-contained and can be:

- Opened directly in any browser
- Shared with others (requires internet for CDN assets)
- Archived for later viewing

## Troubleshooting

### Markdown doesn't render correctly

- Ensure file is valid Markdown format
- Check for unsupported extensions
- Verify UTF-8 encoding

### Code blocks not highlighted

- Specify language after triple backticks
- Check that language is supported
- Example: \`\`\`javascript

### Images don't load

- Use absolute URLs or relative paths
- Ensure images are accessible
- Check image file permissions

### Math equations don't render

- Ensure KaTeX CDN is accessible
- Use proper LaTeX syntax
- Wrap in `$` for inline, `$$` for block

## Development

This skill is standalone and includes all dependencies:

- Shared libraries bundled in `lib/`
- Templates bundled in `templates/`
- External CDN dependencies:
  - marked.js (Markdown parser)
  - DOMPurify (XSS prevention)
  - Mermaid (diagram support)

To modify the skill:

1. Edit `config.sh` for configuration
2. Edit `templates/scripts/markdown-renderer.js` for behavior
3. Edit `templates/styles/markdown.css` for styling
4. Run `run.sh` to test changes
