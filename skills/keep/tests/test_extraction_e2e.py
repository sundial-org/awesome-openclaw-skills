#!/usr/bin/env python3
"""Test end-to-end document extraction with Keeper."""
from pathlib import Path
from keep import Keeper

# Get path relative to this test file
DATA_DIR = Path(__file__).parent / "data"

# Create temporary memory
mem = Keeper(store_path=Path(__file__).parent / "test_extraction_store")

print("Testing PDF indexing...")
pdf_uri = f"file://{(DATA_DIR / 'ancrenewisse.pdf').resolve()}"
pdf_item = mem.update(pdf_uri, source_tags={"type": "medieval", "format": "pdf"})
print(f"✓ PDF indexed")
print(f"  ID: {pdf_item.id}")
print(f"  Summary length: {len(pdf_item.summary)} chars")
print(f"  Summary: {pdf_item.summary[:200]}...")

print("\nTesting HTML indexing...")
html_uri = f"file://{(DATA_DIR / 'mn61.html').resolve()}"
html_item = mem.update(html_uri, source_tags={"type": "buddhist", "format": "html"})
print(f"✓ HTML indexed")
print(f"  ID: {html_item.id}")
print(f"  Summary length: {len(html_item.summary)} chars")
print(f"  Summary: {html_item.summary[:200]}...")

print("\nTesting search across formats...")
results = mem.find("advice to Rāhula", limit=2)
print(f"Found {len(results)} results for 'advice to Rāhula'")
for r in results:
    print(f"  [{r.score:.3f}] {r.tags.get('format', 'unknown')}: {r.summary[:100]}...")

# Cleanup
import shutil
shutil.rmtree(Path(__file__).parent / "test_extraction_store")
print("\n✓ Test complete, cleaned up temp store")
