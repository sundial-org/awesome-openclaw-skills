# Nudocs Format Reference

Supported document formats for upload (input) and download/export (output).

---

## Input Formats (Upload)

| Format | Extensions | Notes |
|--------|------------|-------|
| Markdown | `.md` | Full CommonMark + GFM tables, footnotes |
| HTML | `.html`, `.xhtml` | Inline styles preserved |
| LaTeX | `.latex`, `.tex` | Math, bibliographies supported |
| reStructuredText | `.rst` | Sphinx directives supported |
| Org mode | `.org` | Emacs org-mode syntax |
| Textile | `.textile` | Legacy markup format |
| DocBook XML | `.xml`, `.dbk` | Technical documentation standard |
| EPUB | `.epub` | E-book format (extracts content) |
| MediaWiki | `.wiki` | Wikipedia-style markup |
| Jupyter Notebook | `.ipynb` | Code cells + markdown cells |
| OpenDocument | `.odt` | LibreOffice/OpenOffice native |
| Microsoft Word | `.doc`, `.docx` | Full formatting support |
| Rich Text | `.rtf` | Cross-platform rich text |
| Plain Text | `.txt` | No formatting |
| PDF | `.pdf` | Text extraction (formatting limited) |

### Input Format Details

**Best fidelity:** Markdown, HTML, LaTeX, DOCX, ODT
**Limited fidelity:** PDF (layout-based, text extraction only)

---

## Output Formats (Download/Export)

| Format | Extensions | Best For |
|--------|------------|----------|
| Markdown | `.md` | Version control, plain text editing |
| HTML | `.html`, `.xhtml` | Web publishing, email |
| LaTeX | `.latex`, `.tex` | Academic papers, typesetting |
| PDF | `.pdf` | Final distribution, printing |
| reStructuredText | `.rst` | Python docs, Sphinx projects |
| Org mode | `.org` | Emacs users, literate programming |
| Textile | `.textile` | Legacy systems |
| DocBook XML | `.xml`, `.dbk` | Technical manuals |
| EPUB | `.epub` | E-readers, digital books |
| Microsoft Word | `.doc`, `.docx` | Business documents, collaboration |
| OpenDocument | `.odt` | Open-source office suites |
| Rich Text | `.rtf` | Cross-platform compatibility |
| Plain Text | `.txt` | Maximum compatibility |
| MediaWiki | `.wiki` | Wiki publishing |
| AsciiDoc | `.adoc`, `.asciidoc` | Technical docs, O'Reilly books |
| Jupyter Notebook | `.ipynb` | Data science, reproducible research |

---

## Format Selection Guide

### Quick Decision Matrix

| Use Case | Recommended Format |
|----------|-------------------|
| Git/version control | Markdown |
| Academic paper | LaTeX → PDF |
| Business report | DOCX or PDF |
| Web publishing | HTML |
| E-book | EPUB |
| Technical docs | AsciiDoc or RST |
| Data science | Jupyter Notebook |
| Universal sharing | PDF |
| Editing collaboration | DOCX |

### Markdown vs DOCX vs PDF

| Aspect | Markdown | DOCX | PDF |
|--------|----------|------|-----|
| Editable | ✅ Plain text | ✅ Rich editor | ❌ Limited |
| Version control | ✅ Excellent | ⚠️ Binary diffs | ❌ Binary |
| Formatting | ⚠️ Basic | ✅ Rich | ✅ Preserved |
| Collaboration | ✅ Git workflows | ✅ Track changes | ❌ Comments only |
| Universal viewing | ⚠️ Needs render | ⚠️ Needs Word | ✅ Any device |
| File size | ✅ Tiny | ⚠️ Medium | ⚠️ Medium-large |

**Use Markdown when:** Source control matters, plain text preferred, technical docs
**Use DOCX when:** Business collaboration, rich formatting needed, non-technical users
**Use PDF when:** Final distribution, print-ready, legal/archival purposes

---

## Round-Trip Considerations

### What Survives Conversion

| Feature | MD↔HTML | MD↔DOCX | DOCX↔PDF | LaTeX↔PDF |
|---------|---------|---------|----------|-----------|
| Headings | ✅ | ✅ | ✅ | ✅ |
| Bold/Italic | ✅ | ✅ | ✅ | ✅ |
| Lists | ✅ | ✅ | ✅ | ✅ |
| Tables | ✅ | ✅ | ✅ | ✅ |
| Images | ✅ | ✅ | ✅ | ✅ |
| Links | ✅ | ✅ | ✅ | ✅ |
| Footnotes | ✅ | ⚠️ | ✅ | ✅ |
| Math equations | ⚠️ | ⚠️ | ✅ | ✅ |
| Custom styles | ❌ | ⚠️ | ✅ | ✅ |
| Page layout | ❌ | ⚠️ | ✅ | ✅ |
| Comments | ❌ | ✅ | ❌ | ❌ |
| Track changes | ❌ | ✅ | ❌ | ❌ |

✅ = Preserved | ⚠️ = Partial/degraded | ❌ = Lost

### Lossless Round-Trips

These conversions preserve content reliably:
- Markdown ↔ HTML ↔ Markdown
- DOCX ↔ ODT ↔ DOCX
- LaTeX → PDF (one-way, high fidelity)
- Markdown → PDF (one-way)

### Lossy Conversions (Avoid for Editing)

- PDF → anything (layout information lost)
- DOCX → Markdown (complex formatting stripped)
- HTML with CSS → Markdown (styling lost)

---

## Best Practices

### For Technical Documentation
```
Source: Markdown or AsciiDoc
Output: HTML (web), PDF (download)
```

### For Academic Writing
```
Source: LaTeX
Output: PDF
Collaboration: Overleaf or Git
```

### For Business Documents
```
Source: DOCX (if collaboration needed)
Output: PDF (for distribution)
```

### For Publishing
```
Source: Markdown or DOCX
Output: EPUB (e-books), HTML (web), PDF (print)
```

---

## gimme Format Examples

```bash
# Upload with explicit format
gimme up paper.tex --format latex

# Download to specific format  
gimme dl abc123 --format pdf
gimme dl abc123 --format docx
gimme dl abc123 --format epub

# Convert between formats
gimme dl abc123 --format md      # Get as Markdown
gimme dl abc123 --format html    # Get as HTML
```

### Format Aliases

| Alias | Resolves To |
|-------|-------------|
| `md` | `markdown` |
| `tex` | `latex` |
| `word` | `docx` |
| `odf` | `odt` |
| `ascii` | `asciidoc` |
| `rst` | `rst` |
| `notebook` | `ipynb` |
