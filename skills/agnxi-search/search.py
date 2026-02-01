#!/usr/bin/env python3
import sys
import urllib.request
import xml.etree.ElementTree as ET
import re
from html.parser import HTMLParser

# Configuration
SITEMAP_URL = "https://agnxi.com/sitemap.xml"
CACHE_FILE = "agnxi_sitemap_cache.xml"

def fetch_sitemap():
    """Fetches the sitemap from Agnxi.com."""
    try:
        with urllib.request.urlopen(SITEMAP_URL) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching sitemap: {e}", file=sys.stderr)
        return None

def parse_sitemap(xml_content, query):
    """Parses sitemap XML and filters based on query."""
    try:
        root = ET.fromstring(xml_content)
        # Handle namespaces if present (sitemaps usually have them)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        results = []
        query_terms = query.lower().split()

        for url in root.findall('ns:url', namespace):
            loc = url.find('ns:loc', namespace).text
            
            # Simple heuristic: Check if query terms are in the URL slug
            # This works well for agnostic URLs like agnxi.com/skills/browser-use
            if all(term in loc.lower() for term in query_terms):
                results.append(loc)
        
        return results
    except Exception as e:
        # Fallback for simple XML without namespaces or parsing errors
        print(f"Debug: XML parse warning ({e}). Falling back to simple text search.", file=sys.stderr)
        return [line for line in xml_content.decode('utf-8').splitlines() if query.lower() in line.lower() and '<loc>' in line]

def main():
    if len(sys.argv) < 2:
        print("Usage: python search.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"Searching Agnxi for: '{query}'...")

    xml_content = fetch_sitemap()
    if not xml_content:
        print("Failed to retrieve skill database.")
        sys.exit(1)

    matches = parse_sitemap(xml_content, query)
    
    if matches:
        print(f"\nFound {len(matches)} relevant skills/pages:")
        for link in matches[:10]: # Limit to top 10
            # Clean up the format if it was a fallback line
            clean_link = link.replace('<loc>', '').replace('</loc>', '').strip()
            print(f"- {clean_link}")
        
        if len(matches) > 10:
            print(f"...and {len(matches) - 10} more.")
    else:
        print("No exact matches found in the directory index.")
        print("Try broader keywords or browse directly at https://agnxi.com")

if __name__ == "__main__":
    main()
