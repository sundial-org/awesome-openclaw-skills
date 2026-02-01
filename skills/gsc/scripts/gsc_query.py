#!/usr/bin/env python3
"""
Google Search Console API Query Tool

Queries GSC for search analytics, URL inspection, sitemaps, and more.

Usage:
    python gsc_query.py search-analytics --site https://example.com --days 28
    python gsc_query.py top-queries --site https://example.com --limit 20
    python gsc_query.py top-pages --site https://example.com --limit 20
    python gsc_query.py inspect-url --site https://example.com --url /some/page
    python gsc_query.py sitemaps --site https://example.com
    python gsc_query.py sites
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Required packages not installed. Run:")
    print("  pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)


def get_credentials() -> Credentials:
    """Get credentials from environment variables."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        print("ERROR: Missing credentials. Set these environment variables:")
        print("  GOOGLE_CLIENT_ID")
        print("  GOOGLE_CLIENT_SECRET")
        print("  GOOGLE_REFRESH_TOKEN")
        sys.exit(1)
    
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
    )


def get_service():
    """Build the Search Console service."""
    creds = get_credentials()
    return build("searchconsole", "v1", credentials=creds)


def list_sites():
    """List all sites available in Search Console."""
    service = get_service()
    response = service.sites().list().execute()
    sites = response.get("siteEntry", [])
    
    if not sites:
        print("No sites found in Search Console.")
        return
    
    print(f"Found {len(sites)} site(s):\n")
    for site in sites:
        print(f"  {site['siteUrl']}")
        print(f"    Permission: {site['permissionLevel']}")
        print()


def search_analytics(site_url: str, days: int = 28, dimensions: list = None, 
                     row_limit: int = 1000, start_date: str = None, end_date: str = None):
    """Query search analytics data."""
    service = get_service()
    
    if not end_date:
        end_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=days+3)).strftime("%Y-%m-%d")
    
    if not dimensions:
        dimensions = ["query", "page"]
    
    request = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
        "dataState": "final"
    }
    
    try:
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        return response
    except HttpError as e:
        print(f"ERROR: API request failed: {e}")
        sys.exit(1)


def top_queries(site_url: str, days: int = 28, limit: int = 20):
    """Get top search queries."""
    response = search_analytics(site_url, days=days, dimensions=["query"], row_limit=limit)
    rows = response.get("rows", [])
    
    if not rows:
        print("No query data found.")
        return
    
    print(f"Top {len(rows)} queries (last {days} days):\n")
    print(f"{'Query':<50} {'Clicks':>8} {'Impressions':>12} {'CTR':>8} {'Position':>10}")
    print("-" * 92)
    
    for row in rows:
        query = row["keys"][0][:48]
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        ctr = row.get("ctr", 0) * 100
        position = row.get("position", 0)
        print(f"{query:<50} {clicks:>8} {impressions:>12} {ctr:>7.1f}% {position:>10.1f}")


def top_pages(site_url: str, days: int = 28, limit: int = 20):
    """Get top pages by clicks."""
    response = search_analytics(site_url, days=days, dimensions=["page"], row_limit=limit)
    rows = response.get("rows", [])
    
    if not rows:
        print("No page data found.")
        return
    
    print(f"Top {len(rows)} pages (last {days} days):\n")
    print(f"{'Page':<70} {'Clicks':>8} {'Impressions':>12} {'CTR':>8} {'Position':>10}")
    print("-" * 112)
    
    for row in rows:
        page = row["keys"][0]
        # Truncate long URLs
        if len(page) > 68:
            page = page[:65] + "..."
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        ctr = row.get("ctr", 0) * 100
        position = row.get("position", 0)
        print(f"{page:<70} {clicks:>8} {impressions:>12} {ctr:>7.1f}% {position:>10.1f}")


def query_page_analysis(site_url: str, days: int = 28, limit: int = 50):
    """Get query-page combinations for deeper analysis."""
    response = search_analytics(site_url, days=days, dimensions=["query", "page"], row_limit=limit)
    rows = response.get("rows", [])
    
    if not rows:
        print("No data found.")
        return
    
    # Output as JSON for easier parsing
    print(json.dumps(rows, indent=2))


def low_ctr_opportunities(site_url: str, days: int = 28, min_impressions: int = 100):
    """Find high-impression, low-CTR opportunities."""
    response = search_analytics(site_url, days=days, dimensions=["query", "page"], row_limit=500)
    rows = response.get("rows", [])
    
    if not rows:
        print("No data found.")
        return
    
    # Filter for high impressions, low CTR
    opportunities = [
        row for row in rows 
        if row.get("impressions", 0) >= min_impressions and row.get("ctr", 0) < 0.03
    ]
    
    # Sort by impressions descending
    opportunities.sort(key=lambda x: x.get("impressions", 0), reverse=True)
    
    print(f"Low CTR Opportunities (impressions >= {min_impressions}, CTR < 3%):\n")
    print(f"{'Query':<40} {'Page':<50} {'Impr':>8} {'CTR':>7} {'Pos':>6}")
    print("-" * 115)
    
    for row in opportunities[:20]:
        query = row["keys"][0][:38]
        page = row["keys"][1]
        if len(page) > 48:
            page = "..." + page[-45:]
        impressions = row.get("impressions", 0)
        ctr = row.get("ctr", 0) * 100
        position = row.get("position", 0)
        print(f"{query:<40} {page:<50} {impressions:>8} {ctr:>6.1f}% {position:>6.1f}")


def inspect_url(site_url: str, url: str):
    """Inspect a specific URL's indexing status."""
    service = get_service()
    
    # URL inspection requires the full URL
    if not url.startswith("http"):
        url = site_url.rstrip("/") + "/" + url.lstrip("/")
    
    request = {
        "inspectionUrl": url,
        "siteUrl": site_url
    }
    
    try:
        response = service.urlInspection().index().inspect(body=request).execute()
        result = response.get("inspectionResult", {})
        
        print(f"URL Inspection: {url}\n")
        
        # Index status
        index_status = result.get("indexStatusResult", {})
        print("Index Status:")
        print(f"  Verdict: {index_status.get('verdict', 'Unknown')}")
        print(f"  Coverage State: {index_status.get('coverageState', 'Unknown')}")
        print(f"  Crawled As: {index_status.get('crawledAs', 'Unknown')}")
        print(f"  Last Crawl Time: {index_status.get('lastCrawlTime', 'Unknown')}")
        
        # Mobile usability
        mobile = result.get("mobileUsabilityResult", {})
        if mobile:
            print(f"\nMobile Usability:")
            print(f"  Verdict: {mobile.get('verdict', 'Unknown')}")
        
        # Rich results
        rich = result.get("richResultsResult", {})
        if rich:
            print(f"\nRich Results:")
            print(f"  Verdict: {rich.get('verdict', 'Unknown')}")
            
    except HttpError as e:
        print(f"ERROR: URL inspection failed: {e}")


def list_sitemaps(site_url: str):
    """List all sitemaps for a site."""
    service = get_service()
    
    try:
        response = service.sitemaps().list(siteUrl=site_url).execute()
        sitemaps = response.get("sitemap", [])
        
        if not sitemaps:
            print("No sitemaps found.")
            return
        
        print(f"Sitemaps for {site_url}:\n")
        for sm in sitemaps:
            print(f"  {sm.get('path')}")
            print(f"    Type: {sm.get('type', 'Unknown')}")
            print(f"    Last Submitted: {sm.get('lastSubmitted', 'Unknown')}")
            print(f"    Last Downloaded: {sm.get('lastDownloaded', 'Unknown')}")
            print(f"    Warnings: {sm.get('warnings', 0)}")
            print(f"    Errors: {sm.get('errors', 0)}")
            print()
            
    except HttpError as e:
        print(f"ERROR: Failed to list sitemaps: {e}")


def main():
    parser = argparse.ArgumentParser(description="Google Search Console Query Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # sites command
    subparsers.add_parser("sites", help="List all sites in Search Console")
    
    # search-analytics command
    sa_parser = subparsers.add_parser("search-analytics", help="Raw search analytics query")
    sa_parser.add_argument("--site", required=True, help="Site URL (e.g., https://example.com)")
    sa_parser.add_argument("--days", type=int, default=28, help="Number of days (default: 28)")
    sa_parser.add_argument("--dimensions", nargs="+", default=["query", "page"],
                          help="Dimensions: query, page, country, device, date")
    sa_parser.add_argument("--limit", type=int, default=100, help="Row limit")
    
    # top-queries command
    tq_parser = subparsers.add_parser("top-queries", help="Get top search queries")
    tq_parser.add_argument("--site", required=True, help="Site URL")
    tq_parser.add_argument("--days", type=int, default=28, help="Number of days")
    tq_parser.add_argument("--limit", type=int, default=20, help="Number of results")
    
    # top-pages command
    tp_parser = subparsers.add_parser("top-pages", help="Get top pages")
    tp_parser.add_argument("--site", required=True, help="Site URL")
    tp_parser.add_argument("--days", type=int, default=28, help="Number of days")
    tp_parser.add_argument("--limit", type=int, default=20, help="Number of results")
    
    # opportunities command
    opp_parser = subparsers.add_parser("opportunities", help="Find low-CTR optimization opportunities")
    opp_parser.add_argument("--site", required=True, help="Site URL")
    opp_parser.add_argument("--days", type=int, default=28, help="Number of days")
    opp_parser.add_argument("--min-impressions", type=int, default=100, help="Minimum impressions")
    
    # inspect-url command
    iu_parser = subparsers.add_parser("inspect-url", help="Inspect URL indexing status")
    iu_parser.add_argument("--site", required=True, help="Site URL")
    iu_parser.add_argument("--url", required=True, help="URL to inspect")
    
    # sitemaps command
    sm_parser = subparsers.add_parser("sitemaps", help="List sitemaps")
    sm_parser.add_argument("--site", required=True, help="Site URL")
    
    # query-page command (JSON output)
    qp_parser = subparsers.add_parser("query-page", help="Query-page combinations (JSON)")
    qp_parser.add_argument("--site", required=True, help="Site URL")
    qp_parser.add_argument("--days", type=int, default=28, help="Number of days")
    qp_parser.add_argument("--limit", type=int, default=50, help="Row limit")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "sites":
        list_sites()
    elif args.command == "search-analytics":
        response = search_analytics(args.site, args.days, args.dimensions, args.limit)
        print(json.dumps(response, indent=2))
    elif args.command == "top-queries":
        top_queries(args.site, args.days, args.limit)
    elif args.command == "top-pages":
        top_pages(args.site, args.days, args.limit)
    elif args.command == "opportunities":
        low_ctr_opportunities(args.site, args.days, args.min_impressions)
    elif args.command == "inspect-url":
        inspect_url(args.site, args.url)
    elif args.command == "sitemaps":
        list_sitemaps(args.site)
    elif args.command == "query-page":
        query_page_analysis(args.site, args.days, args.limit)


if __name__ == "__main__":
    main()
