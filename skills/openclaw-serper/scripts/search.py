#!/usr/bin/env -S python3 -u
"""
Serper — Google search with full page content extraction via trafilatura.

Two search modes:
  - default:  all time web search (5 results, enriched)
  - current:  past week web + news (3 results each, enriched)

Locale is controlled via --gl and --hl flags.
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, List, Dict, Any

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

try:
    import trafilatura
except ImportError:
    print(json.dumps({
        "error": "trafilatura is required but not installed",
        "fix": "pip install trafilatura",
    }, indent=2), flush=True)
    sys.exit(1)


# =============================================================================
# Auto-load .env from skill directory
# =============================================================================
def _load_env_file():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    if line.startswith("export "):
                        line = line[7:]
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value

_load_env_file()


# =============================================================================
# Configuration
# =============================================================================

FETCH_TIMEOUT = 3
USER_AGENT = "Mozilla/5.0 (compatible; Serper/3.0)"

SERP_SEARCH_URL = "https://google.serper.dev/search"
SERP_NEWS_URL = "https://google.serper.dev/news"

# Trafilatura config — shared across all threads
_traf_config = trafilatura.settings.use_config()
_traf_config.set("DEFAULT", "DOWNLOAD_TIMEOUT", str(FETCH_TIMEOUT))


def get_api_key() -> str:
    key = os.environ.get("SERPER_API_KEY") or os.environ.get("SERP_API_KEY")
    if not key:
        print(json.dumps({
            "error": "Missing Serper API key",
            "how_to_fix": [
                "1. Get a free key at https://serper.dev (2,500 queries free)",
                '2. Add SERPER_API_KEY="your-key" to .env in the skill directory',
            ],
        }, indent=2), flush=True)
        sys.exit(1)
    if len(key) < 10:
        print(json.dumps({"error": "Serper API key appears invalid (too short)"}), flush=True)
        sys.exit(1)
    return key


# =============================================================================
# Content extraction via trafilatura
# =============================================================================

def _extract_content(url: str) -> Optional[str]:
    """Fetch a URL and extract clean readable text using trafilatura."""
    try:
        downloaded = trafilatura.fetch_url(url, config=_traf_config)
        if not downloaded:
            return None
        return trafilatura.extract(downloaded, include_links=False, include_images=False,
                                   include_tables=True, deduplicate=True) or None
    except Exception:
        return None


# =============================================================================
# Serper API
# =============================================================================

def _serper_post(endpoint: str, api_key: str, payload: dict) -> dict:
    """POST to Serper API and return parsed JSON."""
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    data = json.dumps(payload).encode("utf-8")
    req = Request(endpoint, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        msgs = {
            401: "Invalid or expired API key.",
            429: "Rate limit exceeded. Wait and retry.",
        }
        raise Exception(msgs.get(e.code, f"Serper HTTP {e.code}: {body[:300]}"))
    except URLError as e:
        raise Exception(f"Network error: {e.reason}")
    except Exception as e:
        raise Exception(f"Request failed: {e}")


def serper_web_search(query: str, api_key: str, num: int = 5,
                      gl: Optional[str] = None, hl: str = "en",
                      tbs: Optional[str] = None) -> List[Dict[str, Any]]:
    """Web search via Serper. Returns list of result dicts."""
    payload: Dict[str, Any] = {"q": query, "num": num, "hl": hl, "autocorrect": True}
    if gl and gl != "world":
        payload["gl"] = gl
    if tbs:
        payload["tbs"] = tbs

    data = _serper_post(SERP_SEARCH_URL, api_key, payload)
    results = []

    kg = data.get("knowledgeGraph")
    if kg and "title" in kg:
        attrs = ""
        if "attributes" in kg:
            attrs = " | ".join(f"{k}: {v}" for k, v in kg["attributes"].items())
        results.append({
            "title": kg["title"],
            "snippet": attrs or kg.get("description", ""),
            "source": "knowledge_graph",
        })

    for item in data.get("organic", [])[:num]:
        r = {
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "source": "web",
        }
        if item.get("date"):
            r["date"] = item["date"]
        results.append(r)

    return results


def serper_news_search(query: str, api_key: str, num: int = 3,
                       gl: Optional[str] = None, hl: str = "en") -> List[Dict[str, Any]]:
    """News search via Serper. Returns list of result dicts."""
    payload: Dict[str, Any] = {"q": query, "num": num, "hl": hl}
    if gl and gl != "world":
        payload["gl"] = gl

    data = _serper_post(SERP_NEWS_URL, api_key, payload)
    results = []
    for item in data.get("news", [])[:num]:
        r = {
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "source": "news",
        }
        if item.get("date"):
            r["date"] = item["date"]
        results.append(r)
    return results


# =============================================================================
# Content enrichment — concurrent fetch, streamed as JSON array
# =============================================================================

def enrich_and_stream(results: List[Dict[str, Any]]):
    """Fetch full page content concurrently, print each as JSON array element in order."""
    futures = {}
    pool = ThreadPoolExecutor(max_workers=max(1, len(results)))
    for i, r in enumerate(results):
        if r.get("url"):
            futures[i] = pool.submit(_extract_content, r["url"])

    for i, r in enumerate(results):
        out: Dict[str, Any] = {"title": r["title"]}
        if r.get("url"):
            out["url"] = r["url"]
        out["source"] = r["source"]
        if r.get("date"):
            out["date"] = r["date"]

        if r["source"] == "knowledge_graph":
            out["content"] = r["snippet"]
        else:
            content = None
            if i in futures:
                try:
                    content = futures[i].result(timeout=FETCH_TIMEOUT)
                except Exception:
                    content = None
            out["content"] = content if content else r["snippet"]

        print("," + json.dumps(out, ensure_ascii=False), flush=True)

    pool.shutdown(wait=False)


def search_current(query: str, api_key: str, locale: Dict[str, Optional[str]]) -> List[Dict[str, Any]]:
    """Current/news mode: past week web + news search, 3 results each."""
    all_results = []
    seen_urls = set()

    for r in serper_web_search(query, api_key, num=3, gl=locale["gl"], hl=locale["hl"], tbs="qdr:w"):
        if r["source"] == "knowledge_graph":
            all_results.append(r)
        elif r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            all_results.append(r)

    for r in serper_news_search(query, api_key, num=3, gl=locale["gl"], hl=locale["hl"]):
        url = r.get("url", "")
        if url not in seen_urls:
            seen_urls.add(url)
            all_results.append(r)

    return all_results


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Serper — Google search with full content extraction",
    )
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument(
        "--mode", "-m",
        default="default",
        choices=["default", "current"],
        help="Search mode: default (all-time, 5 results) or current (past week + news, 3 each)",
    )
    parser.add_argument("--gl", default="world", help="Country code for Google (e.g. de, us, at, ch). Default: world")
    parser.add_argument("--hl", default="en", help="Language code for results (e.g. en, de)")

    args = parser.parse_args()
    api_key = get_api_key()
    locale = {"gl": args.gl, "hl": args.hl}

    if args.mode == "current":
        results = search_current(args.query, api_key, locale)
    else:
        results = serper_web_search(args.query, api_key, num=5, gl=locale["gl"], hl=locale["hl"])

    if not results:
        print(json.dumps({"error": "No results found", "query": args.query}), flush=True)
        sys.exit(1)

    # JSON array — first element is search metadata
    meta = {
        "query": args.query,
        "mode": args.mode,
        "locale": locale,
        "results": [
            {k: r[k] for k in ("title", "url", "source") if k in r}
            for r in results
        ],
    }
    print("[" + json.dumps(meta, ensure_ascii=False), flush=True)
    enrich_and_stream(results)
    print("]", flush=True)


if __name__ == "__main__":
    main()
