#!/usr/bin/env python3
"""
TechMeme Scraper - Fetches top stories from techmeme.com via RSS
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import requests
import xml.etree.ElementTree as ET

TECHMEME_RSS = "https://www.techmeme.com/feed.xml"
CACHE_FILE = Path.home() / ".cache/technews/stories.json"


def parse_rss(xml_content: str, num_stories: int = 10) -> List[Dict]:
    """Parse TechMeme RSS feed and extract stories."""
    stories = []
    
    try:
        root = ET.fromstring(xml_content)
        
        for item in root.findall(".//item")[:num_stories]:
            title_elem = item.find("title")
            link_elem = item.find("link")
            desc_elem = item.find("description")
            pubdate_elem = item.find("pubDate")
            
            title = title_elem.text if title_elem is not None else ""
            link = link_elem.text if link_elem is not None else ""
            
            # Extract summary from description (strip HTML)
            description = ""
            if desc_elem is not None and desc_elem.text:
                # Simple HTML strip - remove tags
                desc_text = desc_elem.text
                import re
                desc_text = re.sub(r'<[^>]+>', ' ', desc_text)
                description = ' '.join(desc_text.split())[:300]
            
            pubdate = pubdate_elem.text if pubdate_elem is not None else ""
            
            stories.append({
                "title": title,
                "url": link,
                "summary": description,
                "timestamp": pubdate,
                "source": "techmeme"
            })
            
    except ET.ParseError as e:
        # Fallback: try regex parsing
        stories = parse_rss_fallback(xml_content, num_stories)
    
    return stories


def parse_rss_fallback(xml_content: str, num_stories: int = 10) -> List[Dict]:
    """Fallback RSS parser using regex."""
    import re
    stories = []
    
    # Match items
    item_pattern = r'<item>(.*?)</item>'
    items = re.findall(item_pattern, xml_content, re.DOTALL)[:num_stories]
    
    for item in items:
        title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
        link_match = re.search(r'<link>(.*?)</link>', item)
        desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
        date_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
        
        title = title_match.group(1) if title_match else ""
        link = link_match.group(1) if link_match else ""
        
        description = ""
        if desc_match:
            desc_text = re.sub(r'<[^>]+>', ' ', desc_match.group(1))
            description = ' '.join(desc_text.split())[:300]
        
        pubdate = date_match.group(1) if date_match else ""
        
        stories.append({
            "title": title,
            "url": link,
            "summary": description,
            "timestamp": pubdate,
            "source": "techmeme"
        })
    
    return stories


def fetch_techmeme(num_stories: int = 10) -> List[Dict]:
    """Fetch top stories from TechMeme RSS feed."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TechNewsBot/1.0)",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
    
    response = requests.get(TECHMEME_RSS, headers=headers, timeout=30)
    response.raise_for_status()
    
    return parse_rss(response.text, num_stories)


def save_cache(stories: List[Dict]):
    """Cache fetched stories."""
    cache_dir = CACHE_FILE.parent
    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({"cached_at": time.time(), "stories": stories}, f, indent=2)


def load_cache(max_age_hours: int = 2) -> Optional[List[Dict]]:
    """Load cached stories if recent enough."""
    if not CACHE_FILE.exists():
        return None
    
    try:
        with open(CACHE_FILE) as f:
            data = json.load(f)
        
        age = (time.time() - data.get("cached_at", 0)) / 3600
        if age < max_age_hours:
            return data.get("stories", [])
    except (json.JSONDecodeError, OSError):
        pass
    
    return None


def main(num_stories: int = 10, use_cache: bool = True) -> str:
    """Main entry point - returns JSON output."""
    # Try cache first
    if use_cache:
        cached = load_cache()
        if cached:
            return json.dumps({"cached": True, "stories": cached[:num_stories]})
    
    stories = fetch_techmeme(num_stories)
    save_cache(stories)
    
    return json.dumps({"cached": False, "stories": stories})


if __name__ == "__main__":
    import sys
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print(main(num_stories=num))
