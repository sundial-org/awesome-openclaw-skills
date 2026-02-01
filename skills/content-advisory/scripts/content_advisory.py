#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Content Advisory CLI - Kids-In-Mind style movie/TV content ratings.

Provides detailed content breakdowns: Sex/Nudity, Violence/Gore, Language
on a 0-10 scale, plus Substance Use, Discussion Topics, and Message.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urljoin
from urllib.request import Request, urlopen

# Data directory
DATA_DIR = Path(os.environ.get("CONTENT_ADVISORY_DATA_DIR", Path.home() / ".clawdbot" / "content-advisory"))
CACHE_FILE = DATA_DIR / "cache.json"

# Kids-In-Mind base URL
KIM_BASE = "https://kids-in-mind.com"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class ContentRating:
    title: str
    year: str = ""
    mpaa: str = ""
    sex_nudity: int = 0
    violence_gore: int = 0
    language: int = 0
    sex_nudity_detail: str = ""
    violence_gore_detail: str = ""
    language_detail: str = ""
    substance_use: str = ""
    discussion_topics: str = ""
    message: str = ""
    url: str = ""
    cached_at: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: dict) -> "ContentRating":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class SearchResult:
    title: str
    year: str
    url: str
    ratings: str = ""  # e.g., "3.5.4"
    mpaa: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


def load_cache() -> dict[str, ContentRating]:
    """Load cache from JSON file."""
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE) as f:
            data = json.load(f)
            return {k: ContentRating.from_dict(v) for k, v in data.items()}
    except (json.JSONDecodeError, KeyError):
        return {}


def save_cache(cache: dict[str, ContentRating]) -> None:
    """Save cache to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({k: v.to_dict() for k, v in cache.items()}, f, indent=2)


def fetch_url(url: str) -> str:
    """Fetch URL content as string."""
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    )
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.reason}") from e
    except URLError as e:
        raise RuntimeError(f"URL error: {e.reason}") from e


def clean_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    # Remove script/style content
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Remove tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode entities
    text = html.unescape(text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_section_by_id(html_content: str, section_id: str) -> str:
    """Extract text from a section with a specific ID."""
    # Look for section with id, then get content until next h2 or section end
    pattern = rf'id="{section_id}"[^>]*>([^<]*)</h2>\s*</div>\s*</div>\s*<div[^>]*>\s*<div[^>]*>(.*?)</div>'
    match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(2)
        return clean_html(content)[:600]
    
    # Fallback: simpler pattern
    pattern2 = rf'id="{section_id}"[^>]*>.*?</h2>.*?<p[^>]*>(.*?)</p>'
    match2 = re.search(pattern2, html_content, re.DOTALL | re.IGNORECASE)
    if match2:
        return clean_html(match2.group(1))[:600]
    
    return ""


def parse_kim_page(html_content: str, url: str) -> ContentRating:
    """Parse a Kids-In-Mind review page."""
    rating = ContentRating(title="", url=url, cached_at=datetime.now().isoformat())
    
    # Extract from title: "Title [Year] [MPAA] - X.Y.Z | Parents' Guide..."
    title_match = re.search(r"<title>([^<]+)</title>", html_content, re.IGNORECASE)
    if title_match:
        title_text = html.unescape(title_match.group(1))
        
        # Parse: "Greenland 2: Migration [2026] [PG-13] - 1.6.4 | Parents' Guide..."
        main_match = re.match(r"(.+?)\s*\[(\d{4})\]\s*\[([^\]]+)\]\s*-\s*(\d+)\.(\d+)\.(\d+)", title_text)
        if main_match:
            rating.title = main_match.group(1).strip()
            rating.year = main_match.group(2)
            rating.mpaa = main_match.group(3)
            rating.sex_nudity = int(main_match.group(4))
            rating.violence_gore = int(main_match.group(5))
            rating.language = int(main_match.group(6))
        else:
            # Try simpler pattern: just get title before | or [
            simple = re.match(r"(.+?)(?:\s*[\|\[]|$)", title_text)
            if simple:
                rating.title = simple.group(1).strip()
    
    # Extract section details using IDs
    rating.sex_nudity_detail = extract_section_by_id(html_content, "sex")
    rating.violence_gore_detail = extract_section_by_id(html_content, "violence")
    rating.language_detail = extract_section_by_id(html_content, "language")
    
    # Extract substance use section
    substance_match = re.search(r'id="substance"[^>]*>.*?SUBSTANCE[^<]*</h2>.*?<p[^>]*>(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
    if substance_match:
        rating.substance_use = clean_html(substance_match.group(1))[:400]
    
    # Extract discussion topics
    topics_match = re.search(r'id="discussion"[^>]*>.*?DISCUSSION[^<]*</h2>.*?<p[^>]*>(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
    if topics_match:
        rating.discussion_topics = clean_html(topics_match.group(1))[:400]
    
    # Extract message
    message_match = re.search(r'id="message"[^>]*>.*?MESSAGE[^<]*</h2>.*?<p[^>]*>(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
    if message_match:
        rating.message = clean_html(message_match.group(1))[:400]
    
    return rating


def search_kim_from_homepage(query: str, limit: int = 10) -> list[SearchResult]:
    """Search for movies by scraping links from Kids-In-Mind homepage and alphabetical pages."""
    results = []
    query_lower = query.lower()
    
    # First try the alphabetical index page for the first letter
    first_letter = query_lower[0] if query_lower else "a"
    index_url = f"{KIM_BASE}/{first_letter}.htm"
    
    urls_to_check = [KIM_BASE, index_url]
    seen_urls = set()
    
    for base_url in urls_to_check:
        try:
            html_content = fetch_url(base_url)
            
            # Find all movie links
            link_pattern = r'href="(/[a-z]/[^"]+\.htm)"[^>]*>([^<]+)'
            for match in re.finditer(link_pattern, html_content, re.IGNORECASE):
                url_path = match.group(1)
                link_text = clean_html(match.group(2))
                
                # Skip non-movie pages
                if any(skip in url_path.lower() for skip in ["/about", "/contact", "/donate", "/terms", "/search"]):
                    continue
                
                full_url = urljoin(KIM_BASE, url_path)
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                
                # Check if query matches
                if query_lower in link_text.lower():
                    # Try to extract year and ratings from link text or URL
                    year = ""
                    mpaa = ""
                    ratings = ""
                    
                    year_match = re.search(r"\[(\d{4})\]", link_text)
                    if year_match:
                        year = year_match.group(1)
                    
                    mpaa_match = re.search(r"\[(G|PG|PG-13|R|NC-17|NR)\]", link_text)
                    if mpaa_match:
                        mpaa = mpaa_match.group(1)
                    
                    ratings_match = re.search(r"(\d+)\.(\d+)\.(\d+)", link_text)
                    if ratings_match:
                        ratings = f"{ratings_match.group(1)}.{ratings_match.group(2)}.{ratings_match.group(3)}"
                    
                    # Clean title
                    title = re.sub(r"\s*\[\d{4}\].*$", "", link_text).strip()
                    
                    results.append(SearchResult(
                        title=title,
                        year=year,
                        url=full_url,
                        ratings=ratings,
                        mpaa=mpaa,
                    ))
                    
                    if len(results) >= limit:
                        return results
        except Exception as e:
            print(f"Error fetching {base_url}: {e}", file=sys.stderr)
            continue
    
    return results


def lookup_title(query: str, year: str | None = None) -> ContentRating | None:
    """Look up content rating for a title."""
    cache = load_cache()
    
    # Check cache first
    cache_key = f"{query.lower()}:{year or ''}"
    if cache_key in cache:
        cached = cache[cache_key]
        try:
            cached_time = datetime.fromisoformat(cached.cached_at)
            if (datetime.now() - cached_time).days < 30:
                return cached
        except (ValueError, TypeError):
            pass
    
    # Search for the title
    search_results = search_kim_from_homepage(query)
    
    if not search_results:
        return None
    
    # Find best match
    query_lower = query.lower()
    best_match = search_results[0]
    
    for result in search_results:
        # Prefer exact title match
        if result.title.lower() == query_lower:
            best_match = result
            break
        # Prefer matching year
        if year and result.year == year:
            best_match = result
            break
    
    # Fetch the page
    try:
        html_content = fetch_url(best_match.url)
        rating = parse_kim_page(html_content, best_match.url)
        
        # Fallback to search result info if parsing failed
        if not rating.title:
            rating.title = best_match.title
        if not rating.year and best_match.year:
            rating.year = best_match.year
        if not rating.mpaa and best_match.mpaa:
            rating.mpaa = best_match.mpaa
        if rating.sex_nudity == 0 and best_match.ratings:
            parts = best_match.ratings.split(".")
            if len(parts) == 3:
                rating.sex_nudity = int(parts[0])
                rating.violence_gore = int(parts[1])
                rating.language = int(parts[2])
        
        # Save to cache
        cache[cache_key] = rating
        save_cache(cache)
        
        return rating
    except Exception as e:
        print(f"Lookup error: {e}", file=sys.stderr)
        return None


def render_bar(value: int, max_val: int = 10) -> str:
    """Render a visual bar for a rating."""
    filled = "▓" * value
    empty = "░" * (max_val - value)
    return f"{filled}{empty}"


def print_rating(rating: ContentRating, json_output: bool = False) -> None:
    """Print content rating in formatted output."""
    if json_output:
        print(json.dumps(rating.to_dict(), indent=2))
        return
    
    # Header
    year_str = f" ({rating.year})" if rating.year else ""
    mpaa_str = f" | {rating.mpaa}" if rating.mpaa else ""
    print(f"\n🎬 {rating.title}{year_str}{mpaa_str}\n")
    
    # Ratings bars
    print("📊 CONTENT RATINGS")
    print(f"   Sex/Nudity:    {rating.sex_nudity:2d} {render_bar(rating.sex_nudity)}")
    print(f"   Violence/Gore: {rating.violence_gore:2d} {render_bar(rating.violence_gore)}")
    print(f"   Language:      {rating.language:2d} {render_bar(rating.language)}")
    
    # Details
    if rating.sex_nudity_detail or rating.violence_gore_detail or rating.language_detail:
        print("\n📋 CATEGORY DETAILS")
        if rating.sex_nudity_detail:
            detail = rating.sex_nudity_detail[:300]
            print(f"   Sex/Nudity: {detail}{'...' if len(rating.sex_nudity_detail) > 300 else ''}")
        if rating.violence_gore_detail:
            detail = rating.violence_gore_detail[:300]
            print(f"   Violence: {detail}{'...' if len(rating.violence_gore_detail) > 300 else ''}")
        if rating.language_detail:
            detail = rating.language_detail[:300]
            print(f"   Language: {detail}{'...' if len(rating.language_detail) > 300 else ''}")
    
    if rating.substance_use:
        print(f"\n💊 SUBSTANCE USE\n   {rating.substance_use[:250]}")
    
    if rating.discussion_topics:
        print(f"\n💬 DISCUSSION TOPICS\n   {rating.discussion_topics[:250]}")
    
    if rating.message:
        print(f"\n📝 MESSAGE\n   {rating.message[:250]}")
    
    if rating.url:
        print(f"\n🔗 Source: {rating.url}")
    
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────────────────────

def cmd_lookup(args: argparse.Namespace) -> int:
    """Look up content rating for a movie."""
    rating = lookup_title(args.title, args.year)
    
    if not rating:
        print(f"❌ Could not find content rating for '{args.title}'", file=sys.stderr)
        print("   Try a different spelling or check kids-in-mind.com directly", file=sys.stderr)
        return 1
    
    print_rating(rating, args.json)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Search for titles."""
    results = search_kim_from_homepage(args.query, args.limit)
    
    if not results:
        print(f"❌ No results found for '{args.query}'", file=sys.stderr)
        return 1
    
    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return 0
    
    print(f"🔍 Search results for '{args.query}':\n")
    for r in results:
        year_str = f" ({r.year})" if r.year else ""
        mpaa_str = f" [{r.mpaa}]" if r.mpaa else ""
        ratings_str = f" - {r.ratings}" if r.ratings else ""
        print(f"  • {r.title}{year_str}{mpaa_str}{ratings_str}")
    return 0


def cmd_clear_cache(args: argparse.Namespace) -> int:
    """Clear the cache."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        print("🗑️  Cache cleared")
    else:
        print("ℹ️  Cache was already empty")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Content Advisory - Kids-In-Mind style movie ratings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # lookup
    p_lookup = subparsers.add_parser("lookup", help="Look up content rating for a movie")
    p_lookup.add_argument("title", help="Movie or show title")
    p_lookup.add_argument("--year", "-y", help="Release year")
    p_lookup.add_argument("--json", action="store_true", help="JSON output")
    p_lookup.set_defaults(func=cmd_lookup)
    
    # search
    p_search = subparsers.add_parser("search", help="Search for titles")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    p_search.add_argument("--json", action="store_true", help="JSON output")
    p_search.set_defaults(func=cmd_search)
    
    # clear-cache
    p_clear = subparsers.add_parser("clear-cache", help="Clear cached results")
    p_clear.set_defaults(func=cmd_clear_cache)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
