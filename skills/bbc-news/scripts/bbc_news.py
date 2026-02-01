#!/usr/bin/env python3
"""
BBC News CLI - Fetch and display BBC News stories from RSS feeds
"""
import argparse
import sys
from datetime import datetime

try:
    import feedparser
except ImportError:
    print("Error: feedparser library not found. Install with: pip install feedparser", file=sys.stderr)
    sys.exit(1)

# BBC News RSS feeds
FEEDS = {
    "top": "https://feeds.bbci.co.uk/news/rss.xml",
    "uk": "https://feeds.bbci.co.uk/news/uk/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "politics": "https://feeds.bbci.co.uk/news/politics/rss.xml",
    "health": "https://feeds.bbci.co.uk/news/health/rss.xml",
    "education": "https://feeds.bbci.co.uk/news/education/rss.xml",
    "science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "entertainment": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "england": "https://feeds.bbci.co.uk/news/england/rss.xml",
    "scotland": "https://feeds.bbci.co.uk/news/scotland/rss.xml",
    "wales": "https://feeds.bbci.co.uk/news/wales/rss.xml",
    "northern-ireland": "https://feeds.bbci.co.uk/news/northern_ireland/rss.xml",
    "africa": "https://feeds.bbci.co.uk/news/world/africa/rss.xml",
    "asia": "https://feeds.bbci.co.uk/news/world/asia/rss.xml",
    "australia": "https://feeds.bbci.co.uk/news/world/australia/rss.xml",
    "europe": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "latin-america": "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
    "middle-east": "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
    "us-canada": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
}


def fetch_news(section="top", limit=10, format="text"):
    """Fetch BBC News stories from RSS feed"""
    if section not in FEEDS:
        print(f"Error: Unknown section '{section}'", file=sys.stderr)
        print(f"Available sections: {', '.join(sorted(FEEDS.keys()))}", file=sys.stderr)
        return 1

    feed_url = FEEDS[section]
    feed = feedparser.parse(feed_url)

    if feed.bozo:
        print(f"Error: Failed to parse feed from {feed_url}", file=sys.stderr)
        return 1

    entries = feed.entries[:limit]

    if format == "json":
        import json
        stories = []
        for entry in entries:
            stories.append({
                "title": entry.title,
                "link": entry.link,
                "description": entry.get("description", ""),
                "published": entry.get("published", ""),
            })
        print(json.dumps(stories, indent=2))
    else:
        # Text format
        section_title = feed.feed.get("title", f"BBC News - {section.title()}")
        print(f"\n{section_title}")
        print("=" * len(section_title))
        print()

        for i, entry in enumerate(entries, 1):
            print(f"{i}. {entry.title}")
            if hasattr(entry, "description") and entry.description:
                # Strip HTML tags from description
                import re
                desc = re.sub(r'<[^>]+>', '', entry.description)
                print(f"   {desc}")
            print(f"   🔗 {entry.link}")
            if hasattr(entry, "published"):
                print(f"   📅 {entry.published}")
            print()

    return 0


def list_sections():
    """List all available sections"""
    print("\nAvailable BBC News sections:")
    print("=" * 40)
    print("\nMain Sections:")
    main = ["top", "uk", "world", "business", "politics", "health", 
            "education", "science", "technology", "entertainment"]
    for section in main:
        if section in FEEDS:
            print(f"  • {section}")
    
    print("\nUK Regional:")
    regional = ["england", "scotland", "wales", "northern-ireland"]
    for section in regional:
        if section in FEEDS:
            print(f"  • {section}")
    
    print("\nWorld Regions:")
    world = ["africa", "asia", "australia", "europe", 
             "latin-america", "middle-east", "us-canada"]
    for section in world:
        if section in FEEDS:
            print(f"  • {section}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch BBC News stories from RSS feeds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Top stories (default)
  %(prog)s uk                       # UK news
  %(prog)s world --limit 5          # Top 5 world stories
  %(prog)s technology --json        # Technology news in JSON format
  %(prog)s --list                   # List all available sections
        """
    )
    parser.add_argument(
        "section",
        nargs="?",
        default="top",
        help="News section (default: top)"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=10,
        help="Number of stories to fetch (default: 10)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available sections"
    )

    args = parser.parse_args()

    if args.list:
        list_sections()
        return 0

    return fetch_news(args.section, args.limit, args.format)


if __name__ == "__main__":
    sys.exit(main())
