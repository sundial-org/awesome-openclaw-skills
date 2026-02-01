#!/usr/bin/env python3
"""
Swiss Phone Directory CLI - search.ch API wrapper
Search for businesses, people, or reverse-lookup phone numbers in Switzerland.
"""

import argparse
import os
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Optional


API_BASE = "https://search.ch/tel/api/"
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "tel": "http://tel.search.ch/api/spec/result/1.0/",
    "openSearch": "http://a9.com/-/spec/opensearchrss/1.0/"
}


def get_api_key() -> str:
    """Get API key from environment variable."""
    key = os.environ.get("SEARCHCH_API_KEY")
    if not key:
        print("❌ Error: SEARCHCH_API_KEY environment variable not set", file=sys.stderr)
        print("   Set it with: export SEARCHCH_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(1)
    return key


def search(query: str, location: Optional[str] = None, entry_type: str = "all",
           limit: int = 10, lang: str = "de") -> list[dict]:
    """
    Search the Swiss phone directory.
    
    Args:
        query: Search string (name, category, or phone number)
        location: City, ZIP, street, or canton abbreviation
        entry_type: "business", "person", or "all"
        limit: Maximum results (max 200)
        lang: Output language (de, fr, it, en)
    
    Returns:
        List of result dictionaries
    """
    api_key = get_api_key()
    
    params = {
        "was": query,
        "key": api_key,
        "lang": lang,
        "maxnum": min(limit, 200)
    }
    
    if location:
        params["wo"] = location
    
    if entry_type == "business":
        params["privat"] = "0"
        params["firma"] = "1"
    elif entry_type == "person":
        params["privat"] = "1"
        params["firma"] = "0"
    
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            xml_data = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("❌ Error: Invalid API key", file=sys.stderr)
        else:
            print(f"❌ HTTP Error: {e.code}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Network Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    
    return parse_response(xml_data)


def parse_response(xml_data: str) -> list[dict]:
    """Parse the Atom XML response into a list of dictionaries."""
    root = ET.fromstring(xml_data)
    
    # Get total results
    total_el = root.find("openSearch:totalResults", NS)
    total = int(total_el.text) if total_el is not None else 0
    
    results = []
    
    for entry in root.findall("atom:entry", NS):
        result = {}
        
        # Basic info
        result["name"] = get_text(entry, "atom:title")
        result["id"] = get_text(entry, "tel:id")
        result["type"] = get_text(entry, "tel:type")
        
        # Organization details
        org = get_text(entry, "tel:org")
        if org:
            result["org"] = org
        
        firstname = get_text(entry, "tel:firstname")
        lastname = get_text(entry, "tel:name")
        if firstname:
            result["firstname"] = firstname
        if lastname and lastname != result.get("name"):
            result["lastname"] = lastname
        
        occupation = get_text(entry, "tel:occupation")
        if occupation:
            result["occupation"] = occupation
        
        # Address
        street = get_text(entry, "tel:street")
        streetno = get_text(entry, "tel:streetno")
        zip_code = get_text(entry, "tel:zip")
        city = get_text(entry, "tel:city")
        canton = get_text(entry, "tel:canton")
        
        if street:
            result["street"] = f"{street} {streetno}".strip() if streetno else street
        if zip_code:
            result["zip"] = zip_code
        if city:
            result["city"] = city
        if canton:
            result["canton"] = canton
        
        # Phone
        phone = get_text(entry, "tel:phone")
        if phone:
            result["phone"] = format_phone(phone)
        
        # Extra fields (fax, email, website)
        for extra in entry.findall("tel:extra", NS):
            extra_type = extra.get("type", "")
            value = extra.text
            if value:
                value = value.rstrip("*")  # Remove no-promo marker
                if extra_type == "fax":
                    result["fax"] = format_phone(value)
                elif extra_type == "email":
                    result["email"] = value
                elif extra_type == "website":
                    # Parse "label: url" format
                    if ": http" in value:
                        result["website"] = value.split(": ", 1)[1]
                    elif value.startswith("http"):
                        result["website"] = value
                    elif "website" not in result:
                        result["website"] = value
        
        # Categories
        categories = []
        for cat in entry.findall("tel:category", NS):
            if cat.text:
                categories.append(cat.text)
        if categories:
            result["categories"] = categories
        
        # Detail link
        for link in entry.findall("atom:link", NS):
            if link.get("rel") == "alternate" and link.get("type") == "text/html":
                result["url"] = link.get("href")
                break
        
        results.append(result)
    
    return results


def get_text(element: ET.Element, path: str) -> Optional[str]:
    """Get text content of a child element."""
    child = element.find(path, NS)
    return child.text.strip() if child is not None and child.text else None


def format_phone(phone: str) -> str:
    """Format phone number for display."""
    # Remove non-digits except +
    digits = "".join(c for c in phone if c.isdigit() or c == "+")
    
    # Format Swiss numbers
    if digits.startswith("+41") and len(digits) == 12:
        return f"+41 {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"
    elif digits.startswith("0") and len(digits) == 10:
        return f"{digits[0:3]} {digits[3:6]} {digits[6:8]} {digits[8:10]}"
    
    return phone


def print_results(results: list[dict], verbose: bool = False):
    """Print search results in a readable format."""
    if not results:
        print("🔍 Keine Treffer gefunden.")
        return
    
    print(f"📋 {len(results)} Treffer:\n")
    
    for i, r in enumerate(results, 1):
        # Name and type
        type_icon = "🏢" if r.get("type") == "Organisation" else "👤"
        print(f"{type_icon} **{r.get('name', 'Unbekannt')}**")
        
        # Occupation/subtitle
        if r.get("occupation"):
            print(f"   {r['occupation']}")
        
        # Address
        addr_parts = []
        if r.get("street"):
            addr_parts.append(r["street"])
        if r.get("zip") or r.get("city"):
            addr_parts.append(f"{r.get('zip', '')} {r.get('city', '')}".strip())
        if r.get("canton"):
            addr_parts[-1] = f"{addr_parts[-1]} {r['canton']}" if addr_parts else r["canton"]
        if addr_parts:
            print(f"   📍 {', '.join(addr_parts)}")
        
        # Contact
        if r.get("phone"):
            print(f"   📞 {r['phone']}")
        if r.get("fax"):
            print(f"   📠 {r['fax']}")
        if r.get("email"):
            print(f"   ✉️  {r['email']}")
        if r.get("website"):
            print(f"   🔗 {r['website']}")
        
        # Categories
        if r.get("categories") and verbose:
            print(f"   🏷️  {', '.join(r['categories'])}")
        
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Search the Swiss phone directory (search.ch)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "Migros" -l "Zürich"
  %(prog)s search "Müller Hans" -t person
  %(prog)s search "+41442345678"
  %(prog)s search "Restaurant" -l "Bern" -t business -n 5
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search the directory")
    search_parser.add_argument("query", help="Search string (name, category, or phone number)")
    search_parser.add_argument("-l", "--location", help="City, ZIP, street, or canton")
    search_parser.add_argument("-t", "--type", choices=["business", "person", "all"],
                               default="all", help="Entry type filter (default: all)")
    search_parser.add_argument("-n", "--limit", type=int, default=10,
                               help="Max results (default: 10, max: 200)")
    search_parser.add_argument("--lang", choices=["de", "fr", "it", "en"],
                               default="de", help="Output language (default: de)")
    search_parser.add_argument("-v", "--verbose", action="store_true",
                               help="Show categories and extra details")
    search_parser.add_argument("--json", action="store_true",
                               help="Output raw JSON")
    
    args = parser.parse_args()
    
    if args.command == "search":
        results = search(
            query=args.query,
            location=args.location,
            entry_type=args.type,
            limit=args.limit,
            lang=args.lang
        )
        
        if args.json:
            import json
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print_results(results, verbose=args.verbose)


if __name__ == "__main__":
    main()
