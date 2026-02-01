#!/usr/bin/env python3
"""
Article Fetcher - Fetches and extracts content from article URLs
"""

import json
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

# Common user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def get_random_ua() -> str:
    """Get a random user agent for requests."""
    return random.choice(USER_AGENTS)


def fetch_article(url: str, timeout: int = 15) -> Dict:
    """Fetch article content from URL."""
    headers = {
        "User-Agent": get_random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    result = {
        "url": url,
        "success": False,
        "title": "",
        "content": "",
        "word_count": 0,
        "error": None
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract title
        title_elem = soup.select_one("title")
        result["title"] = title_elem.get_text(strip=True) if title_elem else ""
        
        # Try to find main content - common selectors
        content_selectors = [
            "article",
            "[role=main]",
            "main",
            "div.post-content",
            "div.article-content",
            "div.entry-content",
            "div.content",
            "div.story-body",
        ]
        
        content = None
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                content = elem
                break
        
        if not content:
            # Fallback: find largest text block
            paragraphs = soup.select("p")
            if paragraphs:
                content = paragraphs[0].parent
        
        if content:
            # Extract text from paragraphs
            text_parts = []
            for p in content.find_all(["p", "h1", "h2", "h3", "li"]):
                text = p.get_text(strip=True)
                if len(text) > 20:  # Filter out nav elements
                    text_parts.append(text)
            
            result["content"] = " ".join(text_parts)
            result["word_count"] = len(result["content"].split())
            result["success"] = True
            
    except requests.exceptions.Timeout:
        result["error"] = "timeout"
    except requests.exceptions.RequestException as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"parse_error: {str(e)}"
    
    return result


def fetch_multiple(urls: List[str], max_workers: int = 5) -> List[Dict]:
    """Fetch multiple articles in parallel."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_article, url): url for url in urls}
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    return results


def summarize_content(content: str, max_words: int = 100) -> str:
    """Generate a brief summary of article content."""
    if not content:
        return ""
    
    words = content.split()
    if len(words) <= max_words:
        return content
    
    # Simple extractive summary: take first N words
    return " ".join(words[:max_words]) + "..."


def main():
    """Main entry point - reads URLs from stdin or args."""
    import sys
    
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        # Read from stdin
        input_data = sys.stdin.read()
        urls = json.loads(input_data).get("urls", [])
    
    if not urls:
        print(json.dumps({"error": "No URLs provided"}))
        return
    
    results = fetch_multiple(urls)
    
    # Add summaries
    for r in results:
        if r.get("success"):
            r["summary"] = summarize_content(r.get("content", ""))
    
    print(json.dumps({"articles": results}))


if __name__ == "__main__":
    main()
