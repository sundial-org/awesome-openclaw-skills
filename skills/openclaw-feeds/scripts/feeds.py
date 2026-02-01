#!/usr/bin/env -S python3 -u
"""
Feeds — RSS news aggregator skill.

Three categories:
  - news:    general tech, science, culture feeds
  - games:   gaming news (DE + US)
  - finance: markets, business, economy

Fetches all feeds for a category concurrently, extracts entries,
and streams structured JSON output.
"""

import json
import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

try:
    import feedparser
except ImportError:
    print(json.dumps({
        "error": "feedparser is required but not installed",
        "fix": "pip install feedparser",
    }, indent=2), flush=True)
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

FETCH_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (compatible; Feeds/1.0)"

# Feed lists — edit scripts/lists.py to customize sources
from lists import NEWS_FEEDS, GAMES_FEEDS, FINANCE_FEEDS

CATEGORY_MAP = {
    "news": NEWS_FEEDS,
    "games": GAMES_FEEDS,
    "finance": FINANCE_FEEDS,
}


# =============================================================================
# Helpers
# =============================================================================

def get_domain(url: str) -> str:
    """Extract clean domain name from a URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc

        if "feedburner.com" in domain:
            path_parts = parsed.path.strip("/").split("/")
            if path_parts:
                return path_parts[0]

        if domain.startswith("www."):
            domain = domain[4:]

        parts = domain.split(".")
        if len(parts) > 2:
            domain = ".".join(parts[-2:])

        return domain
    except Exception:
        return url.replace("https://", "").replace("http://", "").split("/")[0]


def clean_html(text: str) -> str:
    """Strip HTML tags from text. Minimal, no deps."""
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =============================================================================
# Feed fetching
# =============================================================================

def fetch_feed(feed_url: str) -> List[Dict[str, Any]]:
    """Fetch and parse a single RSS feed. Returns list of entry dicts."""
    try:
        req = Request(feed_url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            raw = resp.read()
    except (HTTPError, URLError, Exception):
        return []

    try:
        feed = feedparser.parse(raw)
    except Exception:
        return []

    domain = get_domain(feed_url)
    entries = []

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        if not title:
            continue

        link = entry.get("link", "")
        published = entry.get("published", entry.get("updated", ""))
        summary = clean_html(entry.get("summary", ""))

        # Truncate long summaries
        if len(summary) > 500:
            summary = summary[:497] + "..."

        entries.append({
            "title": title,
            "url": link,
            "source": domain,
            "date": published,
            "summary": summary,
        })

    return entries


def fetch_all_feeds(feeds: List[str]) -> List[Dict[str, Any]]:
    """Fetch all feeds concurrently. Returns combined list of entries."""
    all_entries: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=min(20, len(feeds))) as pool:
        futures = {pool.submit(fetch_feed, url): url for url in feeds}

        for future in as_completed(futures):
            try:
                entries = future.result()
                if entries:
                    all_entries.extend(entries)
            except Exception:
                continue

    return all_entries


# =============================================================================
# Output
# =============================================================================

def stream_output(category: str, entries: List[Dict[str, Any]]):
    """Stream results as JSON array — metadata first, then entries."""
    sources = sorted(set(e["source"] for e in entries))

    meta = {
        "category": category,
        "total_entries": len(entries),
        "sources": sources,
        "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    }

    print("[" + json.dumps(meta, ensure_ascii=False), flush=True)

    for entry in entries:
        print("," + json.dumps(entry, ensure_ascii=False), flush=True)

    print("]", flush=True)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Feeds — RSS news aggregator",
    )
    parser.add_argument(
        "--category", "-c",
        required=True,
        choices=["news", "games", "finance"],
        help="Feed category: news, games, or finance",
    )

    args = parser.parse_args()
    feeds = CATEGORY_MAP[args.category]

    entries = fetch_all_feeds(feeds)

    if not entries:
        print(json.dumps({"error": "No entries found", "category": args.category}), flush=True)
        sys.exit(1)

    stream_output(args.category, entries)


if __name__ == "__main__":
    main()
