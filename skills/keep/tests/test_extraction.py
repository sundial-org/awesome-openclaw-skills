#!/usr/bin/env python3
"""Test PDF and HTML text extraction."""
from pathlib import Path
from keep.providers.documents import FileDocumentProvider

# Get path relative to this test file
DATA_DIR = Path(__file__).parent / "data"

provider = FileDocumentProvider()

# Test PDF extraction
print("=" * 70)
print("PDF EXTRACTION TEST")
print("=" * 70)
pdf_path = DATA_DIR / "ancrenewisse.pdf"
try:
    doc = provider.fetch(f"file://{Path(pdf_path).resolve()}")
    print(f"✓ Extracted {len(doc.content)} chars from PDF")
    print(f"Content type: {doc.content_type}")
    print(f"First 500 chars:\n{doc.content[:500]}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "=" * 70)
print("HTML EXTRACTION TEST")
print("=" * 70)
html_path = DATA_DIR / "mn61.html"
html_doc = None
try:
    html_doc = provider.fetch(f"file://{Path(html_path).resolve()}")
    print(f"✓ Extracted {len(html_doc.content)} chars from HTML")
    print(f"Content type: {html_doc.content_type}")
    print(f"First 500 chars:\n{html_doc.content[:500]}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "=" * 70)
print("COMPARISON: Raw HTML vs Extracted")
print("=" * 70)
raw_html = html_path.read_text()[:500]
print(f"Raw HTML ({len(raw_html)} chars):\n{raw_html}\n")
if html_doc:
    print(f"Extracted text ({len(html_doc.content[:500])} chars):\n{html_doc.content[:500]}")
else:
    print("(Extraction failed - see error above)")
