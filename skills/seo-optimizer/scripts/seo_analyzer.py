#!/usr/bin/env python3
"""
SEO Analyzer Script
Analyzes HTML files for common SEO issues and generates a detailed report.
"""

import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
import json


class SEOHTMLParser(HTMLParser):
    """Parser to extract SEO-relevant information from HTML."""

    def __init__(self):
        super().__init__()
        self.title = None
        self.meta_tags = {}
        self.headings = {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []}
        self.images = []
        self.links = []
        self.current_tag = None
        self.has_lang = False
        self.has_viewport = False
        self.has_charset = False
        self.og_tags = {}
        self.twitter_tags = {}
        self.schema_markup = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Check for lang attribute on html tag
        if tag == 'html' and 'lang' in attrs_dict:
            self.has_lang = True

        # Title tag
        if tag == 'title':
            self.current_tag = 'title'

        # Meta tags
        if tag == 'meta':
            name = attrs_dict.get('name', '').lower()
            property_attr = attrs_dict.get('property', '').lower()
            content = attrs_dict.get('content', '')

            if name == 'description':
                self.meta_tags['description'] = content
            elif name == 'keywords':
                self.meta_tags['keywords'] = content
            elif name == 'robots':
                self.meta_tags['robots'] = content
            elif name == 'viewport':
                self.has_viewport = True
            elif attrs_dict.get('charset'):
                self.has_charset = True

            # Open Graph tags
            if property_attr.startswith('og:'):
                self.og_tags[property_attr] = content

            # Twitter Card tags
            if name.startswith('twitter:'):
                self.twitter_tags[name] = content

        # Headings
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_tag = tag

        # Images
        if tag == 'img':
            self.images.append({
                'src': attrs_dict.get('src', ''),
                'alt': attrs_dict.get('alt', ''),
                'title': attrs_dict.get('title', '')
            })

        # Links
        if tag == 'a':
            href = attrs_dict.get('href', '')
            if href:
                self.links.append({
                    'href': href,
                    'rel': attrs_dict.get('rel', ''),
                    'title': attrs_dict.get('title', '')
                })

        # Schema.org markup
        if 'itemscope' in attrs_dict or 'itemtype' in attrs_dict:
            self.schema_markup.append(attrs_dict.get('itemtype', 'itemscope'))

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        if self.current_tag == 'title':
            self.title = data
        elif self.current_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.headings[self.current_tag].append(data)

    def handle_endtag(self, tag):
        if tag in ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_tag = None


def analyze_html_file(filepath):
    """Analyze a single HTML file for SEO issues."""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = SEOHTMLParser()
    parser.feed(content)

    issues = []
    warnings = []
    good_practices = []

    # Title analysis
    if not parser.title:
        issues.append("Missing <title> tag")
    elif len(parser.title) < 30:
        warnings.append(f"Title too short ({len(parser.title)} chars). Recommended: 50-60 characters")
    elif len(parser.title) > 60:
        warnings.append(f"Title too long ({len(parser.title)} chars). May be truncated in search results")
    else:
        good_practices.append(f"Title length optimal ({len(parser.title)} chars)")

    # Meta description
    if 'description' not in parser.meta_tags:
        issues.append("Missing meta description")
    else:
        desc_len = len(parser.meta_tags['description'])
        if desc_len < 120:
            warnings.append(f"Meta description too short ({desc_len} chars). Recommended: 150-160 characters")
        elif desc_len > 160:
            warnings.append(f"Meta description too long ({desc_len} chars). May be truncated in search results")
        else:
            good_practices.append(f"Meta description length optimal ({desc_len} chars)")

    # HTML lang attribute
    if not parser.has_lang:
        issues.append("Missing 'lang' attribute on <html> tag")
    else:
        good_practices.append("HTML lang attribute present")

    # Charset
    if not parser.has_charset:
        warnings.append("Missing charset meta tag")

    # Viewport
    if not parser.has_viewport:
        warnings.append("Missing viewport meta tag (important for mobile SEO)")
    else:
        good_practices.append("Viewport meta tag present")

    # Heading structure
    h1_count = len(parser.headings['h1'])
    if h1_count == 0:
        issues.append("Missing H1 heading")
    elif h1_count > 1:
        warnings.append(f"Multiple H1 headings ({h1_count}). Recommended: exactly 1 H1 per page")
    else:
        good_practices.append("Exactly one H1 heading")

    # Check heading hierarchy
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    has_content = [len(parser.headings[tag]) > 0 for tag in heading_tags]
    if any(has_content):
        first_used = has_content.index(True)
        if first_used > 0:
            warnings.append(f"Heading hierarchy starts at H{first_used + 1} instead of H1")

    # Image alt attributes
    images_without_alt = [img for img in parser.images if not img['alt']]
    if images_without_alt:
        issues.append(f"{len(images_without_alt)} image(s) missing alt attributes")
    if parser.images and not images_without_alt:
        good_practices.append("All images have alt attributes")

    # Open Graph tags
    required_og = ['og:title', 'og:description', 'og:image', 'og:url']
    missing_og = [tag for tag in required_og if tag not in parser.og_tags]
    if missing_og:
        warnings.append(f"Missing Open Graph tags: {', '.join(missing_og)}")
    else:
        good_practices.append("All essential Open Graph tags present")

    # Twitter Card tags
    if 'twitter:card' not in parser.twitter_tags:
        warnings.append("Missing Twitter Card tags")
    else:
        good_practices.append("Twitter Card tags present")

    # Schema markup
    if not parser.schema_markup:
        warnings.append("No schema.org structured data found")
    else:
        good_practices.append(f"Schema.org markup found: {', '.join(set(parser.schema_markup))}")

    # Canonical URL
    if '<link rel="canonical"' not in content.lower():
        warnings.append("Missing canonical URL")

    # Check for common issues
    if len(content) < 300:
        warnings.append("Page content is very short (< 300 characters). Search engines prefer substantial content")

    return {
        'file': filepath,
        'title': parser.title,
        'meta_description': parser.meta_tags.get('description', ''),
        'h1_count': h1_count,
        'h1_content': parser.headings['h1'],
        'total_headings': sum(len(v) for v in parser.headings.values()),
        'total_images': len(parser.images),
        'images_without_alt': len(images_without_alt),
        'total_links': len(parser.links),
        'has_og_tags': bool(parser.og_tags),
        'has_twitter_tags': bool(parser.twitter_tags),
        'has_schema': bool(parser.schema_markup),
        'issues': issues,
        'warnings': warnings,
        'good_practices': good_practices
    }


def scan_directory(directory):
    """Scan a directory for HTML files and analyze them."""
    html_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.html', '.htm')):
                html_files.append(os.path.join(root, file))

    return html_files


def generate_report(results, output_format='text'):
    """Generate a report from analysis results."""

    if output_format == 'json':
        return json.dumps(results, indent=2)

    # Text report
    report = []
    report.append("=" * 80)
    report.append("SEO ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")

    for result in results:
        report.append(f"\nFile: {result['file']}")
        report.append("-" * 80)

        # Summary
        report.append(f"\nTitle: {result['title'] or '(missing)'}")
        report.append(f"Meta Description: {result['meta_description'] or '(missing)'}")
        report.append(f"H1 Count: {result['h1_count']}")
        if result['h1_content']:
            report.append(f"H1 Content: {', '.join(result['h1_content'])}")
        report.append(f"Total Headings: {result['total_headings']}")
        report.append(f"Total Images: {result['total_images']}")
        report.append(f"Images without alt: {result['images_without_alt']}")
        report.append(f"Total Links: {result['total_links']}")

        # Issues
        if result['issues']:
            report.append("\n🔴 CRITICAL ISSUES:")
            for issue in result['issues']:
                report.append(f"  - {issue}")

        # Warnings
        if result['warnings']:
            report.append("\n⚠️  WARNINGS:")
            for warning in result['warnings']:
                report.append(f"  - {warning}")

        # Good practices
        if result['good_practices']:
            report.append("\n✅ GOOD PRACTICES:")
            for practice in result['good_practices']:
                report.append(f"  - {practice}")

        report.append("")

    # Overall summary
    report.append("\n" + "=" * 80)
    report.append("OVERALL SUMMARY")
    report.append("=" * 80)

    total_issues = sum(len(r['issues']) for r in results)
    total_warnings = sum(len(r['warnings']) for r in results)
    total_good = sum(len(r['good_practices']) for r in results)

    report.append(f"\nTotal files analyzed: {len(results)}")
    report.append(f"Total critical issues: {total_issues}")
    report.append(f"Total warnings: {total_warnings}")
    report.append(f"Total good practices: {total_good}")

    if total_issues > 0:
        report.append("\n⚠️  Action required: Fix critical issues first")
    elif total_warnings > 0:
        report.append("\n✓ Good foundation. Consider addressing warnings for optimal SEO")
    else:
        report.append("\n✅ Excellent! SEO best practices are being followed")

    return "\n".join(report)


def main():
    if len(sys.argv) < 2:
        print("Usage: python seo_analyzer.py <file_or_directory> [--json]")
        print("\nAnalyzes HTML files for SEO issues")
        print("\nOptions:")
        print("  --json    Output results in JSON format")
        sys.exit(1)

    target = sys.argv[1]
    output_format = 'json' if '--json' in sys.argv else 'text'

    # Determine if target is file or directory
    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        files = scan_directory(target)
        if not files:
            print(f"No HTML files found in {target}")
            sys.exit(1)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)

    # Analyze files
    results = []
    for file in files:
        try:
            result = analyze_html_file(file)
            results.append(result)
        except Exception as e:
            print(f"Error analyzing {file}: {e}", file=sys.stderr)

    # Generate and print report
    report = generate_report(results, output_format)
    print(report)


if __name__ == '__main__':
    main()
