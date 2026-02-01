#!/usr/bin/env python3
"""
Sitemap Generator Script
Generates an XML sitemap for a website by crawling HTML files.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom


def get_html_files(directory, base_url):
    """
    Recursively find all HTML files and generate URLs.

    Args:
        directory: Root directory to scan
        base_url: Base URL of the website (e.g., https://example.com)

    Returns:
        List of tuples (file_path, url, last_modified)
    """
    html_files = []
    base_path = Path(directory).resolve()

    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and common build/dependency folders
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'vendor', '__pycache__']]

        for file in files:
            if file.endswith(('.html', '.htm')):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(base_path)

                # Convert file path to URL
                url_path = str(relative_path).replace(os.sep, '/')

                # Handle index.html - map to directory URL
                if file.lower() in ['index.html', 'index.htm']:
                    url_path = str(relative_path.parent).replace(os.sep, '/')
                    if url_path == '.':
                        url_path = ''
                else:
                    # Remove .html extension for cleaner URLs (optional)
                    url_path = url_path.rsplit('.', 1)[0]

                # Construct full URL
                url = f"{base_url.rstrip('/')}/{url_path.lstrip('/')}"

                # Get last modified time
                last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)

                html_files.append((str(file_path), url, last_modified))

    return html_files


def estimate_priority(url, file_path):
    """
    Estimate priority based on URL depth and file location.

    Args:
        url: The URL of the page
        file_path: The file system path

    Returns:
        Priority value between 0.0 and 1.0
    """
    # Count URL segments (depth)
    path = url.split('?')[0].split('#')[0]  # Remove query and fragment
    segments = [s for s in path.split('/') if s]

    # Homepage gets highest priority
    if len(segments) <= 1 or 'index' in file_path.lower():
        return 1.0
    # Second-level pages
    elif len(segments) == 2:
        return 0.8
    # Third-level pages
    elif len(segments) == 3:
        return 0.6
    # Deeper pages
    else:
        return 0.4


def estimate_changefreq(file_path):
    """
    Estimate change frequency based on file location and name.

    Args:
        file_path: The file system path

    Returns:
        Change frequency string
    """
    path_lower = file_path.lower()

    # Blog posts and news change frequently
    if any(keyword in path_lower for keyword in ['blog', 'news', 'article', 'post']):
        return 'weekly'
    # Main pages change occasionally
    elif any(keyword in path_lower for keyword in ['index', 'home', 'about', 'contact']):
        return 'monthly'
    # Other pages change rarely
    else:
        return 'yearly'


def generate_sitemap_xml(html_files, base_url, include_priority=True, include_changefreq=True):
    """
    Generate XML sitemap from HTML files.

    Args:
        html_files: List of tuples (file_path, url, last_modified)
        base_url: Base URL of the website
        include_priority: Whether to include priority tags
        include_changefreq: Whether to include changefreq tags

    Returns:
        XML string of the sitemap
    """
    # Create root element
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

    # Sort by URL to ensure consistent ordering
    html_files.sort(key=lambda x: x[1])

    for file_path, url, last_modified in html_files:
        # Create url element
        url_elem = ET.SubElement(urlset, 'url')

        # Add loc (required)
        loc = ET.SubElement(url_elem, 'loc')
        loc.text = url

        # Add lastmod (recommended)
        lastmod = ET.SubElement(url_elem, 'lastmod')
        lastmod.text = last_modified.strftime('%Y-%m-%d')

        # Add changefreq (optional)
        if include_changefreq:
            changefreq = ET.SubElement(url_elem, 'changefreq')
            changefreq.text = estimate_changefreq(file_path)

        # Add priority (optional)
        if include_priority:
            priority = ET.SubElement(url_elem, 'priority')
            priority.text = str(estimate_priority(url, file_path))

    # Convert to pretty-printed XML string
    xml_string = ET.tostring(urlset, encoding='unicode')
    dom = minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent='  ')

    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_sitemap.py <directory> <base_url> [output_file]")
        print("\nGenerates an XML sitemap for all HTML files in the directory")
        print("\nArguments:")
        print("  directory     Directory to scan for HTML files")
        print("  base_url      Base URL of the website (e.g., https://example.com)")
        print("  output_file   Output file path (default: sitemap.xml)")
        print("\nOptions:")
        print("  --no-priority     Exclude priority tags")
        print("  --no-changefreq   Exclude changefreq tags")
        print("\nExample:")
        print("  python generate_sitemap.py ./public https://example.com")
        sys.exit(1)

    directory = sys.argv[1]
    base_url = sys.argv[2]
    output_file = 'sitemap.xml'

    # Check for output file in arguments
    for arg in sys.argv[3:]:
        if not arg.startswith('--'):
            output_file = arg
            break

    # Check options
    include_priority = '--no-priority' not in sys.argv
    include_changefreq = '--no-changefreq' not in sys.argv

    # Validate directory
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)

    # Get HTML files
    print(f"Scanning {directory} for HTML files...")
    html_files = get_html_files(directory, base_url)

    if not html_files:
        print("No HTML files found")
        sys.exit(1)

    print(f"Found {len(html_files)} HTML file(s)")

    # Generate sitemap
    print("Generating sitemap...")
    sitemap_xml = generate_sitemap_xml(html_files, base_url, include_priority, include_changefreq)

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sitemap_xml)

    print(f"✅ Sitemap generated successfully: {output_file}")
    print(f"\nURLs included:")
    for _, url, _ in html_files[:10]:  # Show first 10
        print(f"  - {url}")
    if len(html_files) > 10:
        print(f"  ... and {len(html_files) - 10} more")

    print(f"\nNext steps:")
    print(f"1. Upload {output_file} to your website root")
    print(f"2. Add to robots.txt: Sitemap: {base_url}/sitemap.xml")
    print(f"3. Submit to search engines (Google Search Console, Bing Webmaster Tools)")


if __name__ == '__main__':
    main()
