#!/usr/bin/env python3
"""Zotero CLI — interact with Zotero libraries via the Web API v3.

Environment variables:
    ZOTERO_API_KEY   — API key (required; create at zotero.org/settings/keys/new)
    ZOTERO_USER_ID   — Numeric user ID for personal library
    ZOTERO_GROUP_ID  — Numeric group ID (use instead of USER_ID for group libraries)

Usage:
    python zotero.py <command> [options]

Commands:
    items       List library items (top-level by default)
    search      Search items by query string
    get         Get full details for an item by key
    collections List collections
    tags        List tags
    children    List child items (attachments/notes) for an item
    add-doi     Add an item by DOI (translates via Zotero's lookup)
    add-isbn    Add an item by ISBN
    add-pmid    Add an item by PubMed ID
    check-pdfs  Report which items have/lack PDF attachments
    crossref    Cross-reference a text file of citations against the library
    find-dois   Find and add missing DOIs via CrossRef lookup
    fetch-pdfs  Fetch open-access PDFs and attach to Zotero items
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.zotero.org"


def get_config():
    api_key = os.environ.get("ZOTERO_API_KEY")
    if not api_key:
        print("Error: ZOTERO_API_KEY environment variable not set", file=sys.stderr)
        print("Create a key at https://www.zotero.org/settings/keys/new", file=sys.stderr)
        sys.exit(1)

    user_id = os.environ.get("ZOTERO_USER_ID")
    group_id = os.environ.get("ZOTERO_GROUP_ID")
    if not user_id and not group_id:
        print("Error: Set ZOTERO_USER_ID or ZOTERO_GROUP_ID", file=sys.stderr)
        sys.exit(1)

    prefix = f"/users/{user_id}" if user_id else f"/groups/{group_id}"
    return api_key, prefix


_MAX_RETRIES = 2
_RETRY_CODES = {429, 503}


def api_request(path, api_key, method="GET", data=None, content_type=None, params=None):
    """Make a Zotero API request with retry on transient failures. Returns (response_body, headers)."""
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "Zotero-API-Key": api_key,
        "Zotero-API-Version": "3",
    }
    if content_type:
        headers["Content-Type"] = content_type

    body = None
    if data is not None:
        if isinstance(data, str):
            body = data.encode("utf-8")
        elif isinstance(data, bytes):
            body = data
        else:
            body = json.dumps(data).encode("utf-8")
            if not content_type:
                headers["Content-Type"] = "application/json"

    last_err = None
    for attempt in range(_MAX_RETRIES + 1):
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_body = resp.read().decode("utf-8")
                resp_headers = dict(resp.headers)
                return resp_body, resp_headers
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in _RETRY_CODES and attempt < _MAX_RETRIES:
                delay = (attempt + 1) * 2  # 2s, 4s
                print(f"⚠  HTTP {e.code} — retrying in {delay}s (attempt {attempt + 1}/{_MAX_RETRIES})...", file=sys.stderr)
                time.sleep(delay)
                continue
            err_body = e.read().decode("utf-8") if e.fp else ""
            if _json_mode:
                _json_error(f"API Error {e.code}: {e.reason}", e.code)
            else:
                print(f"API Error {e.code}: {e.reason}", file=sys.stderr)
                if err_body:
                    print(err_body[:500], file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            last_err = e
            if attempt < _MAX_RETRIES:
                delay = (attempt + 1) * 2
                print(f"⚠  Network error — retrying in {delay}s (attempt {attempt + 1}/{_MAX_RETRIES})...", file=sys.stderr)
                time.sleep(delay)
                continue
            if _json_mode:
                _json_error(f"Network error: {e.reason}", 0)
            else:
                print(f"Network error: {e.reason}", file=sys.stderr)
            sys.exit(1)
    # Should not reach here, but just in case
    if _json_mode:
        _json_error(f"Request failed after {_MAX_RETRIES + 1} attempts", 0)
    else:
        print(f"Request failed after {_MAX_RETRIES + 1} attempts", file=sys.stderr)
    sys.exit(1)


def api_get_json(path, api_key, params=None):
    """GET request, parse JSON, return list/dict."""
    body, headers = api_request(path, api_key, params=params)
    return json.loads(body) if body.strip() else {}, headers


def paginate_all(path, api_key, params=None):
    """Fetch all pages of a paginated endpoint."""
    params = dict(params or {})
    params.setdefault("limit", "100")
    all_items = []
    start = 0
    while True:
        params["start"] = str(start)
        items, headers = api_get_json(path, api_key, params=params)
        if not isinstance(items, list):
            return [items]
        all_items.extend(items)
        total = int(headers.get("Total-Results", len(all_items)))
        if len(all_items) >= total:
            break
        start = len(all_items)
    return all_items


# --- Formatters ---

def fmt_creators(creators):
    parts = []
    for c in creators[:3]:
        name = c.get("lastName", c.get("name", "?"))
        parts.append(name)
    if len(creators) > 3:
        parts.append("et al.")
    return ", ".join(parts)


def fmt_item_short(item):
    d = item["data"]
    creators = fmt_creators(d.get("creators", []))
    year = ""
    if d.get("date"):
        m = re.match(r"(\d{4})", d["date"])
        if m:
            year = m.group(1)
    title = d.get("title", "untitled")
    itype = d.get("itemType", "?")
    key = d.get("key", "?")
    return f"[{key}] {creators} ({year}) {title} [{itype}]"


def fmt_item_full(item):
    d = item["data"]
    lines = [f"Key: {d.get('key', '?')}"]
    lines.append(f"Type: {d.get('itemType', '?')}")
    lines.append(f"Title: {d.get('title', 'untitled')}")
    lines.append(f"Creators: {fmt_creators(d.get('creators', []))}")
    if d.get("date"):
        lines.append(f"Date: {d['date']}")
    if d.get("DOI"):
        lines.append(f"DOI: {d['DOI']}")
    if d.get("ISBN"):
        lines.append(f"ISBN: {d['ISBN']}")
    if d.get("url"):
        lines.append(f"URL: {d['url']}")
    if d.get("abstractNote"):
        lines.append(f"Abstract: {d['abstractNote'][:300]}...")
    if d.get("tags"):
        lines.append(f"Tags: {', '.join(t['tag'] for t in d['tags'])}")
    if d.get("collections"):
        lines.append(f"Collections: {', '.join(d['collections'])}")
    return "\n".join(lines)


# --- JSON mode ---

_json_mode = False


def _enable_json_mode():
    """Enable JSON output globally. Commands that support it will output raw JSON."""
    global _json_mode
    _json_mode = True


def _json_print(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _json_error(message, code=0):
    """Print a structured JSON error to stderr."""
    print(json.dumps({"error": message, "code": code}), file=sys.stderr)


# --- Input Validation ---

def validate_doi(s):
    """Validate DOI format (loose: must start with 10. and have a slash)."""
    if not re.match(r'^10\.\d{4,}/\S+$', s):
        print(f"Invalid DOI format: '{s}'. Expected pattern: 10.xxxx/...", file=sys.stderr)
        return False
    return True


def validate_item_key(s):
    """Validate Zotero item key (8-char alphanumeric)."""
    if not re.match(r'^[A-Za-z0-9]{8}$', s):
        print(f"Invalid item key: '{s}'. Must be 8 alphanumeric characters.", file=sys.stderr)
        return False
    return True


def validate_isbn(s):
    """Validate ISBN format (10 or 13 digits after stripping hyphens)."""
    cleaned = s.replace("-", "").replace(" ", "")
    if not re.match(r'^\d{10}(\d{3})?$', cleaned):
        print(f"Invalid ISBN: '{s}'. Must be 10 or 13 digits.", file=sys.stderr)
        return False
    return True


# --- Commands ---

def cmd_items(args):
    api_key, prefix = get_config()
    params = {"limit": str(args.limit), "sort": args.sort, "direction": args.direction}
    if args.collection:
        path = f"{prefix}/collections/{args.collection}/items/top"
    elif args.top:
        path = f"{prefix}/items/top"
    else:
        path = f"{prefix}/items/top"
    if args.type:
        params["itemType"] = args.type

    items, headers = api_get_json(path, api_key, params=params)
    total = headers.get("Total-Results", "?")
    if _json_mode:
        _json_print({"total": total, "items": [i["data"] for i in items if i["data"].get("itemType") != "attachment"]})
        return
    print(f"Showing {len(items)} of {total} items\n")
    for item in items:
        if item["data"].get("itemType") == "attachment":
            continue
        print(fmt_item_short(item))


def cmd_search(args):
    api_key, prefix = get_config()
    params = {"q": args.query, "limit": str(args.limit)}
    if args.sort and args.sort != "relevance":
        params["sort"] = args.sort
    if args.type:
        params["itemType"] = args.type
    items, headers = api_get_json(f"{prefix}/items", api_key, params=params)
    items = [i for i in items if i["data"].get("itemType") != "attachment"]
    total = headers.get("Total-Results", "?")
    if _json_mode:
        _json_print({"total": total, "items": [i["data"] for i in items]})
        return
    print(f"Found {len(items)} results (of {total} total matches)\n")
    for item in items:
        print(fmt_item_short(item))


def cmd_get(args):
    api_key, prefix = get_config()
    if not validate_item_key(args.key):
        sys.exit(1)
    item, _ = api_get_json(f"{prefix}/items/{args.key}", api_key)
    if _json_mode:
        children, _ = api_get_json(f"{prefix}/items/{args.key}/children", api_key)
        item["children"] = [c["data"] for c in children] if children else []
        _json_print(item.get("data", item))
        return
    print(fmt_item_full(item))
    # Also show children count
    children, _ = api_get_json(f"{prefix}/items/{args.key}/children", api_key)
    if children:
        print(f"\nChildren ({len(children)}):")
        for c in children:
            cd = c["data"]
            ctype = cd.get("itemType", "?")
            if ctype == "attachment":
                ct = cd.get("contentType", "?")
                fname = cd.get("filename", cd.get("title", "?"))
                print(f"  📎 {fname} [{ct}]")
            elif ctype == "note":
                note = cd.get("note", "")[:100]
                print(f"  📝 Note: {note}...")
            else:
                print(f"  {ctype}: {cd.get('title', '?')}")


def cmd_collections(args):
    api_key, prefix = get_config()
    cols = paginate_all(f"{prefix}/collections", api_key)
    if not cols:
        print("No collections found.")
        return
    print(f"Collections ({len(cols)}):\n")
    for c in cols:
        d = c["data"]
        parent = f" (parent: {d['parentCollection']})" if d.get("parentCollection") else ""
        print(f"  [{d['key']}] {d['name']} — {d.get('numItems', 0)} items{parent}")


def cmd_tags(args):
    api_key, prefix = get_config()
    params = {"limit": "100"}
    tags = paginate_all(f"{prefix}/tags", api_key, params=params)
    if not tags:
        print("No tags found.")
        return
    print(f"Tags ({len(tags)}):\n")
    for t in tags:
        tag_name = t.get("tag", t.get("data", {}).get("tag", "?"))
        print(f"  {tag_name}")


def cmd_children(args):
    api_key, prefix = get_config()
    if not validate_item_key(args.key):
        sys.exit(1)
    children, _ = api_get_json(f"{prefix}/items/{args.key}/children", api_key)
    if not children:
        print("No children found.")
        return
    for c in children:
        cd = c["data"]
        ctype = cd.get("itemType", "?")
        if ctype == "attachment":
            ct = cd.get("contentType", "?")
            fname = cd.get("filename", cd.get("title", "?"))
            link = cd.get("linkMode", "?")
            print(f"  📎 [{cd['key']}] {fname} [{ct}] (link: {link})")
        elif ctype == "note":
            note = cd.get("note", "")[:200]
            print(f"  📝 [{cd['key']}] {note}")
        else:
            print(f"  [{cd['key']}] {ctype}: {cd.get('title', '?')}")


def _check_duplicate_by_metadata(api_key, prefix, new_item, identifier, id_type):
    """Check if an item with matching DOI/ISBN or author+title already exists.
    Must be called AFTER metadata translation so we have author/title to search.
    Zotero's q= search doesn't match DOI/ISBN fields, so we search by author name
    and then check the DOI/ISBN fields on results."""
    creators = new_item.get("creators", [])
    title = new_item.get("title", "")

    # Build search query from first author's last name
    search_terms = []
    if creators:
        last_name = creators[0].get("lastName", creators[0].get("name", ""))
        if last_name:
            search_terms.append(last_name)
    # Add a title word for specificity
    if title:
        words = [w for w in title.split() if len(w) > 4 and w.lower() not in ("about", "between", "their", "these", "those", "which", "where", "other")]
        if words:
            search_terms.append(words[0])

    if not search_terms:
        return None

    search_q = " ".join(search_terms)
    items, _ = api_get_json(f"{prefix}/items/top", api_key, params={"q": search_q, "limit": "25"})
    if not isinstance(items, list):
        return None

    for item in items:
        d = item.get("data", {})
        # Match by DOI
        if id_type == "doi" and d.get("DOI"):
            if d["DOI"].lower().strip().rstrip("/") == identifier.lower().strip().rstrip("/"):
                return item
        # Match by ISBN
        if id_type == "isbn" and d.get("ISBN"):
            if identifier.replace("-", "") in d["ISBN"].replace("-", ""):
                return item
        # Match by title similarity (fallback for PMIDs or when DOI field isn't populated)
        if title and d.get("title"):
            if title.lower().strip()[:60] == d["title"].lower().strip()[:60]:
                return item

    return None


def cmd_add_identifier(args):
    """Add items by DOI, ISBN, or PMID using Zotero's translation server.
    Returns: "added", "duplicate", or "failed" (for batch-add integration)."""
    api_key, prefix = get_config()

    # Use Zotero's web translation to get item metadata
    identifier = args.identifier
    id_type = args.id_type  # "doi", "isbn", or "pmid"

    # Input validation
    if id_type == "doi" and not validate_doi(identifier):
        return "failed"
    if id_type == "isbn" and not validate_isbn(identifier):
        return "failed"

    # First, get metadata from the translation server
    if id_type == "doi":
        lookup_url = f"https://doi.org/{identifier}"
    elif id_type == "isbn":
        lookup_url = f"https://www.worldcat.org/isbn/{identifier}"
    elif id_type == "pmid":
        lookup_url = f"https://pubmed.ncbi.nlm.nih.gov/{identifier}/"
    else:
        print(f"Unknown identifier type: {id_type}", file=sys.stderr)
        sys.exit(1)

    # Try the Zotero translation server
    translate_url = "https://translate.zotero.org/web"
    translate_data = json.dumps({"url": lookup_url, "sessionid": "zotero-cli"}).encode("utf-8")
    translate_req = urllib.request.Request(
        translate_url,
        data=translate_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(translate_req, timeout=30) as resp:
            translated = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # Fallback: try search endpoint for DOIs
        if id_type == "doi":
            print(f"Translation server failed ({e.code}). Trying manual DOI metadata...", file=sys.stderr)
            translated = _doi_to_item(identifier)
            if not translated:
                sys.exit(1)
        else:
            print(f"Translation failed: {e.code} {e.reason}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Translation failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not translated:
        print("No metadata found for this identifier.", file=sys.stderr)
        sys.exit(1)

    # translated is a list of items; take the first
    if isinstance(translated, list):
        new_items = translated[:1]
    else:
        new_items = [translated]

    # Duplicate detection (after we have metadata to search by author/title)
    if not getattr(args, "force", False) and new_items:
        existing = _check_duplicate_by_metadata(api_key, prefix, new_items[0], identifier, id_type)
        if existing:
            print(f"⚠️  Already in library: {fmt_item_short(existing)}")
            print(f"    Use --force to add anyway.")
            return "duplicate"

    # Clean items for upload (remove fields Zotero doesn't accept on create)
    for item in new_items:
        for field in ["key", "version", "dateAdded", "dateModified", "relations"]:
            item.pop(field, None)
        # Ensure collections is set if requested
        if args.collection:
            item["collections"] = [args.collection]
        if args.tags:
            existing_tags = item.get("tags", [])
            for tag in args.tags.split(","):
                existing_tags.append({"tag": tag.strip()})
            item["tags"] = existing_tags

    # POST to Zotero
    body, headers = api_request(
        f"{prefix}/items",
        api_key,
        method="POST",
        data=new_items,
        content_type="application/json",
    )

    result = json.loads(body) if body.strip() else {}
    success = result.get("successful", {})
    failed = result.get("failed", {})

    if success:
        for idx, item in success.items():
            print(f"✅ Added: {item['data'].get('title', 'untitled')} [{item['key']}]")
        if not failed:
            return "added"
    if failed:
        for idx, err in failed.items():
            print(f"❌ Failed: {err.get('message', 'unknown error')}", file=sys.stderr)
        return "failed"
    return "added"


def _doi_to_item(doi):
    """Fallback: fetch metadata from CrossRef for a DOI and convert to Zotero format."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"CrossRef lookup failed: {e}", file=sys.stderr)
        return None

    work = data.get("message", {})
    item = {
        "itemType": "journalArticle",
        "title": " ".join(work.get("title", ["Untitled"])),
        "DOI": doi,
        "url": work.get("URL", ""),
        "date": "",
        "creators": [],
        "tags": [],
        "abstractNote": work.get("abstract", ""),
    }

    # Date
    issued = work.get("issued", {}).get("date-parts", [[]])
    if issued and issued[0]:
        parts = issued[0]
        item["date"] = "-".join(str(p) for p in parts)

    # Authors
    for author in work.get("author", []):
        item["creators"].append({
            "creatorType": "author",
            "firstName": author.get("given", ""),
            "lastName": author.get("family", ""),
        })

    # Journal
    container = work.get("container-title", [])
    if container:
        item["publicationTitle"] = container[0]

    item["volume"] = work.get("volume", "")
    item["issue"] = work.get("issue", "")
    item["pages"] = work.get("page", "")

    return [item]


def cmd_check_pdfs(args):
    api_key, prefix = get_config()
    print("Fetching all items (including attachments)...", file=sys.stderr)
    # Fetch ALL items in one paginated sweep (parents + attachments together)
    all_items = paginate_all(f"{prefix}/items", api_key)

    # Separate parents from attachments
    parents = {}
    pdf_parents = set()

    for item in all_items:
        d = item["data"]
        itype = d.get("itemType", "")
        if itype in ("attachment", "note"):
            # Check if this is a PDF attachment with a parent
            if itype == "attachment" and d.get("contentType", "").startswith("application/pdf"):
                parent_key = d.get("parentItem", "")
                if parent_key:
                    pdf_parents.add(parent_key)
        else:
            parents[d["key"]] = item

    with_pdf = [parents[k] for k in parents if k in pdf_parents]
    without_pdf = [parents[k] for k in parents if k not in pdf_parents]

    total = len(with_pdf) + len(without_pdf)
    print(f"\n📊 PDF Attachment Report")
    print(f"{'='*50}")
    print(f"Total items: {total}")
    print(f"With PDF:    {len(with_pdf)} ✅")
    print(f"Without PDF: {len(without_pdf)} ❌")
    print()

    if without_pdf:
        print("Items missing PDFs:")
        for item in without_pdf:
            print(f"  {fmt_item_short(item)}")
            doi = item["data"].get("DOI")
            if doi:
                print(f"    → Try: https://doi.org/{doi}")


def cmd_crossref(args):
    """Cross-reference a text file of citations against the library."""
    api_key, prefix = get_config()

    # Read the citation file
    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract citation patterns: Author (Year), Author et al. (Year), Author & Author (Year)
    patterns = [
        r'([A-Z][a-zé]+(?:\s+(?:et\s+al\.|&\s+[A-Z][a-zé]+))?)\s*\((\d{4})\)',
        r'([A-Z][a-zé]+(?:\s+(?:et\s+al\.|,?\s+(?:and|&)\s+[A-Z][a-zé]+))?),?\s+(\d{4})',
    ]

    citations = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            author = match.group(1).strip().rstrip(",")
            year = match.group(2)
            citations.add((author, year))

    if not citations:
        print("No citations found in file. Expected format: Author (Year)")
        return

    print(f"Found {len(citations)} unique citations in file\n")

    # Fetch all library items
    print("Fetching library...", file=sys.stderr)
    items = paginate_all(f"{prefix}/items/top", api_key)
    items = [i for i in items if i["data"].get("itemType") not in ("attachment", "note")]

    # Build lookup index
    lib_index = {}
    for item in items:
        d = item["data"]
        creators = d.get("creators", [])
        year = ""
        if d.get("date"):
            m = re.match(r"(\d{4})", d["date"])
            if m:
                year = m.group(1)

        for c in creators:
            last = c.get("lastName", c.get("name", ""))
            if last and year:
                lib_index.setdefault((last.lower(), year), []).append(item)

    # Match
    found = []
    missing = []
    for author, year in sorted(citations):
        key = (author.split()[0].lower().rstrip(","), year)  # First author's last name
        if key in lib_index:
            found.append((author, year, lib_index[key][0]))
        else:
            # Try partial match
            matched = False
            for (lib_author, lib_year), lib_items in lib_index.items():
                if lib_year == year and (
                    lib_author.startswith(key[0][:4]) or key[0].startswith(lib_author[:4])
                ):
                    found.append((author, year, lib_items[0]))
                    matched = True
                    break
            if not matched:
                missing.append((author, year))

    print(f"\n📊 Cross-Reference Report")
    print(f"{'='*50}")
    print(f"Citations in file: {len(citations)}")
    print(f"Found in library:  {len(found)} ✅")
    print(f"Missing:           {len(missing)} ❌")

    if found:
        print(f"\n✅ Found ({len(found)}):")
        for author, year, item in found:
            print(f"  {author} ({year}) → {item['data'].get('key', '?')}")

    if missing:
        print(f"\n❌ Missing ({len(missing)}):")
        for author, year in missing:
            print(f"  {author} ({year})")


# --- find-dois helpers ---

CROSSREF_EMAIL = os.environ.get("CROSSREF_EMAIL", "zotero-cli@example.com")
DOI_ITEM_TYPES = {"journalArticle", "conferencePaper"}


def _normalize_text(text):
    """Lowercase, strip punctuation/extra whitespace for comparison."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _title_similarity(a, b):
    """Return SequenceMatcher ratio for two title strings."""
    return difflib.SequenceMatcher(None, _normalize_text(a), _normalize_text(b)).ratio()


def _extract_year(date_str):
    """Extract a 4-digit year from a date string, or None."""
    if not date_str:
        return None
    m = re.match(r"(\d{4})", str(date_str))
    return m.group(1) if m else None


def _first_author_last(item_data):
    """Return the first author's last name from Zotero item data, lowercased."""
    creators = item_data.get("creators", [])
    if not creators:
        return None
    c = creators[0]
    name = c.get("lastName", c.get("name", ""))
    return name.lower().strip() if name else None


def _crossref_search(title, first_author):
    """Query CrossRef for a title+author, return list of work dicts (up to 3)."""
    params = {
        "query.bibliographic": title,
        "rows": "3",
        "mailto": CROSSREF_EMAIL,
    }
    if first_author:
        params["query.author"] = first_author
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("message", {}).get("items", [])
    except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
        print(f"    ⚠  CrossRef request failed: {e}", file=sys.stderr)
        return []


def _match_crossref_result(work, zotero_title, zotero_year, zotero_first_author):
    """Score a CrossRef work against the Zotero item. Returns (doi, score_info) or None."""
    # Title similarity
    cr_title = " ".join(work.get("title", [""]))
    sim = _title_similarity(zotero_title, cr_title)
    if sim < 0.85:
        return None

    # Year match
    issued = work.get("issued", {}).get("date-parts", [[]])
    cr_year = str(issued[0][0]) if issued and issued[0] else None
    if zotero_year and cr_year and zotero_year != cr_year:
        return None
    if zotero_year and not cr_year:
        return None  # Can't confirm year

    # Author match
    if zotero_first_author:
        cr_authors = work.get("author", [])
        author_found = False
        for a in cr_authors:
            family = a.get("family", "").lower()
            if family and zotero_first_author in family or family in zotero_first_author:
                author_found = True
                break
        if not author_found:
            return None

    doi = work.get("DOI", "")
    if not doi:
        return None

    return (doi, {"similarity": round(sim * 100, 1), "cr_title": cr_title, "cr_year": cr_year})


def _patch_item_field(api_key, prefix, item_key, field, value, version):
    """PATCH a single field on a Zotero item."""
    url = f"{API_BASE}{prefix}/items/{item_key}"
    headers = {
        "Zotero-API-Key": api_key,
        "Zotero-API-Version": "3",
        "Content-Type": "application/json",
        "If-Unmodified-Since-Version": str(version),
    }
    body = json.dumps({field: value}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="PATCH")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


def cmd_find_dois(args):
    """Find and add missing DOIs to Zotero items via CrossRef."""
    api_key, prefix = get_config()
    apply_mode = args.apply

    # Fetch items
    print("Fetching library items...", file=sys.stderr)
    if args.collection:
        items = paginate_all(f"{prefix}/collections/{args.collection}/items/top", api_key)
    else:
        items = paginate_all(f"{prefix}/items/top", api_key)

    # Filter to relevant types
    candidates = []
    skipped_has_doi = 0
    skipped_wrong_type = 0

    for item in items:
        d = item["data"]
        itype = d.get("itemType", "")
        if itype not in DOI_ITEM_TYPES:
            skipped_wrong_type += 1
            continue
        if d.get("DOI", "").strip():
            skipped_has_doi += 1
            continue
        candidates.append(item)

    if args.limit:
        candidates = candidates[:args.limit]

    print(f"Found {len(candidates)} items missing DOIs "
          f"(skipped: {skipped_has_doi} already have DOI, {skipped_wrong_type} wrong type)\n")

    if not candidates:
        print("Nothing to do.")
        return

    matched = 0
    unmatched = 0

    for i, item in enumerate(candidates, 1):
        d = item["data"]
        title = d.get("title", "")
        year = _extract_year(d.get("date", ""))
        first_author = _first_author_last(d)
        key = d.get("key", "?")

        print(f"[{i}/{len(candidates)}] {fmt_item_short(item)}")

        if not title:
            print("    ⏭  No title, skipping")
            unmatched += 1
            continue

        works = _crossref_search(title, first_author or "")
        time.sleep(1)  # Polite pool delay

        best_match = None
        for work in works:
            result = _match_crossref_result(work, title, year, first_author)
            if result:
                best_match = result
                break  # Take first qualifying match

        if best_match:
            doi, info = best_match
            print(f"    ✅ Match: {doi} (title similarity: {info['similarity']}%)")
            matched += 1

            if apply_mode:
                try:
                    version = item.get("version", item.get("data", {}).get("version", 0))
                    _patch_item_field(api_key, prefix, key, "DOI", doi, version)
                    print(f"    📝 DOI written to Zotero")
                except urllib.error.HTTPError as e:
                    print(f"    ❌ Failed to write DOI: {e.code} {e.reason}", file=sys.stderr)
                except Exception as e:
                    print(f"    ❌ Failed to write DOI: {e}", file=sys.stderr)
        else:
            print(f"    ❌ No confident match found")
            unmatched += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"📊 find-dois Summary")
    print(f"{'='*50}")
    print(f"Processed:          {len(candidates)}")
    print(f"Matched:            {matched} ✅")
    print(f"Unmatched:          {unmatched} ❌")
    print(f"Already had DOI:    {skipped_has_doi} ⏭️")
    print(f"Wrong item type:    {skipped_wrong_type} ⏭️")
    if matched and not apply_mode:
        print(f"\n💡 This was a dry run. Use --apply to write DOIs to Zotero.")


# --- fetch-pdfs helpers ---

PDF_SOURCES = ["unpaywall", "semanticscholar", "doi"]


def _try_unpaywall(doi):
    """Try Unpaywall for an OA PDF URL. Returns (pdf_url, source_url) or None."""
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi, safe='')}?email={CROSSREF_EMAIL}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        oa = data.get("best_oa_location") or {}
        pdf_url = oa.get("url_for_pdf")
        if pdf_url:
            return (pdf_url, pdf_url)
        # Sometimes url_for_landing_page has a direct PDF
        return None
    except Exception:
        return None


def _try_semantic_scholar(doi):
    """Try Semantic Scholar for an OA PDF URL. Returns (pdf_url, source_url) or None."""
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi, safe='')}?fields=openAccessPdf"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        oa = data.get("openAccessPdf") or {}
        pdf_url = oa.get("url")
        if pdf_url:
            return (pdf_url, pdf_url)
        return None
    except Exception:
        return None


def _try_doi_content_negotiation(doi):
    """Try DOI content negotiation for PDF. Returns (pdf_url, source_url) or None."""
    url = f"https://doi.org/{urllib.parse.quote(doi, safe='/:')}"
    req = urllib.request.Request(url, headers={"Accept": "application/pdf"}, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            ct = resp.headers.get("Content-Type", "")
            if "application/pdf" in ct:
                return (resp.url, url)
        return None
    except Exception:
        return None


def _find_pdf_source(doi, sources):
    """Try sources in order, return (pdf_url, source_url, source_name) or None."""
    source_funcs = {
        "unpaywall": (_try_unpaywall, 1),
        "semanticscholar": (_try_semantic_scholar, 1),
        "doi": (_try_doi_content_negotiation, 2),
    }
    for src in sources:
        if src not in source_funcs:
            continue
        func, delay = source_funcs[src]
        result = func(doi)
        if result:
            return (result[0], result[1], src)
        time.sleep(delay)
    return None


def _download_pdf(url, dest_path):
    """Download a PDF from url to dest_path. Returns True on success."""
    req = urllib.request.Request(url, headers={
        "User-Agent": f"Mozilla/5.0 (compatible; ZoteroCLI/1.0; mailto:{CROSSREF_EMAIL})",
        "Accept": "application/pdf,*/*",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(resp, f)
        # Verify it's actually a PDF (check magic bytes)
        with open(dest_path, "rb") as f:
            header = f.read(5)
        if header != b"%PDF-":
            os.unlink(dest_path)
            return False
        return True
    except Exception:
        if os.path.exists(dest_path):
            os.unlink(dest_path)
        return False


def _create_linked_url_attachment(api_key, prefix, parent_key, title, url):
    """Create a linked_url attachment as child of parent_key."""
    attachment = [{
        "itemType": "attachment",
        "parentItem": parent_key,
        "linkMode": "linked_url",
        "title": title,
        "url": url,
        "contentType": "application/pdf",
        "tags": [],
        "relations": {},
    }]
    body, _ = api_request(
        f"{prefix}/items", api_key, method="POST",
        data=attachment, content_type="application/json",
    )
    result = json.loads(body) if body.strip() else {}
    return bool(result.get("successful"))


def _upload_pdf_to_zotero(api_key, prefix, parent_key, filepath, filename):
    """Full Zotero S3 upload flow. Returns True on success."""
    # Step 1: Create child attachment item
    attachment = [{
        "itemType": "attachment",
        "parentItem": parent_key,
        "linkMode": "imported_file",
        "title": filename,
        "filename": filename,
        "contentType": "application/pdf",
        "tags": [],
        "relations": {},
    }]
    body, _ = api_request(
        f"{prefix}/items", api_key, method="POST",
        data=attachment, content_type="application/json",
    )
    result = json.loads(body) if body.strip() else {}
    success = result.get("successful", {})
    if not success:
        return False

    attach_key = list(success.values())[0]["key"]

    # Step 2: Get upload authorization
    with open(filepath, "rb") as f:
        file_bytes = f.read()
    file_size = len(file_bytes)
    file_md5 = hashlib.md5(file_bytes).hexdigest()
    file_mtime = int(os.path.getmtime(filepath) * 1000)

    auth_params = urllib.parse.urlencode({
        "md5": file_md5,
        "filename": filename,
        "filesize": str(file_size),
        "mtime": str(file_mtime),
    })

    auth_url = f"{API_BASE}{prefix}/items/{attach_key}/file"
    auth_headers = {
        "Zotero-API-Key": api_key,
        "Zotero-API-Version": "3",
        "Content-Type": "application/x-www-form-urlencoded",
        "If-None-Match": "*",
    }
    auth_req = urllib.request.Request(
        auth_url, data=auth_params.encode("utf-8"),
        headers=auth_headers, method="POST",
    )
    try:
        with urllib.request.urlopen(auth_req, timeout=30) as resp:
            auth_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"    ⚠  Upload auth failed: {e.code}", file=sys.stderr)
        return False

    if auth_data.get("exists"):
        # File already exists in storage
        return True

    upload_url = auth_data.get("url")
    prefix_bytes = auth_data.get("prefix", "").encode("utf-8")
    suffix_bytes = auth_data.get("suffix", "").encode("utf-8")
    content_type = auth_data.get("contentType", "application/x-www-form-urlencoded")
    upload_key = auth_data.get("uploadKey", "")

    # Step 3: Upload file to S3
    upload_body = prefix_bytes + file_bytes + suffix_bytes
    upload_req = urllib.request.Request(
        upload_url, data=upload_body,
        headers={"Content-Type": content_type},
        method="POST",
    )
    try:
        with urllib.request.urlopen(upload_req, timeout=120) as resp:
            pass
    except urllib.error.HTTPError as e:
        print(f"    ⚠  S3 upload failed: {e.code}", file=sys.stderr)
        return False

    # Step 4: Register upload
    reg_params = urllib.parse.urlencode({"upload": upload_key})
    reg_headers = {
        "Zotero-API-Key": api_key,
        "Zotero-API-Version": "3",
        "Content-Type": "application/x-www-form-urlencoded",
        "If-None-Match": "*",
    }
    reg_req = urllib.request.Request(
        auth_url, data=reg_params.encode("utf-8"),
        headers=reg_headers, method="POST",
    )
    try:
        with urllib.request.urlopen(reg_req, timeout=30) as resp:
            pass
        return True
    except urllib.error.HTTPError as e:
        print(f"    ⚠  Upload registration failed: {e.code}", file=sys.stderr)
        return False


def _item_has_pdf(api_key, prefix, item_key):
    """Check if an item already has a PDF attachment."""
    try:
        children, _ = api_get_json(f"{prefix}/items/{item_key}/children", api_key)
        if not isinstance(children, list):
            return False
        for c in children:
            cd = c.get("data", {})
            if cd.get("itemType") == "attachment":
                ct = cd.get("contentType", "")
                if "pdf" in ct.lower():
                    return True
                # Also check filename/title
                title = cd.get("title", "") + cd.get("filename", "")
                if title.lower().endswith(".pdf"):
                    return True
        return False
    except Exception:
        return False


def _make_pdf_filename(item_data, item_key):
    """Build AuthorYear_Key.pdf filename for local saving."""
    first_author = _first_author_last(item_data) or "Unknown"
    first_author = first_author.capitalize()
    year = _extract_year(item_data.get("date", "")) or "NoDate"
    # Clean author name for filesystem
    safe_author = re.sub(r"[^\w]", "", first_author)
    return f"{safe_author}{year}_{item_key}.pdf"


def _bulk_find_pdf_parents(api_key, prefix, collection_key=None):
    """Fetch all items and return set of parent keys that have PDF attachments.
    Much faster than checking children per-item."""
    if collection_key:
        all_items = paginate_all(f"{prefix}/collections/{collection_key}/items", api_key)
    else:
        all_items = paginate_all(f"{prefix}/items", api_key)

    pdf_parents = set()
    parents = {}

    for item in all_items:
        d = item["data"]
        itype = d.get("itemType", "")
        if itype == "attachment":
            ct = d.get("contentType", "")
            title = d.get("title", "") + d.get("filename", "")
            if "pdf" in ct.lower() or title.lower().endswith(".pdf"):
                parent_key = d.get("parentItem", "")
                if parent_key:
                    pdf_parents.add(parent_key)
        elif itype != "note":
            parents[d["key"]] = item

    return parents, pdf_parents


def cmd_fetch_pdfs(args):
    """Fetch open-access PDFs for items and attach to Zotero."""
    api_key, prefix = get_config()
    dry_run = args.dry_run
    upload_mode = args.upload
    download_dir = args.download_dir
    sources = [s.strip() for s in args.sources.split(",")] if args.sources else PDF_SOURCES

    # Validate sources
    for s in sources:
        if s not in PDF_SOURCES:
            print(f"Unknown source: {s}. Valid: {', '.join(PDF_SOURCES)}", file=sys.stderr)
            sys.exit(1)

    # Create download directory if needed
    if download_dir and not dry_run:
        os.makedirs(download_dir, exist_ok=True)

    # Fetch all items in one sweep (parents + attachments) — much faster than per-item checks
    print("Fetching library items (including attachments)...", file=sys.stderr)
    parents, pdf_parents = _bulk_find_pdf_parents(api_key, prefix, args.collection)

    # Filter: must have DOI, skip items that already have PDFs
    candidates = []
    skipped_no_doi = 0
    skipped_has_pdf = 0

    for key, item in parents.items():
        d = item["data"]
        doi = d.get("DOI", "").strip()
        if not doi:
            skipped_no_doi += 1
            continue
        if key in pdf_parents:
            skipped_has_pdf += 1
            continue
        candidates.append(item)
    if args.limit:
        candidates = candidates[:args.limit]

    print(f"Found {len(candidates)} items to process "
          f"(skipped: {skipped_no_doi} no DOI, {skipped_has_pdf} already have PDF)\n")

    if not candidates:
        print("Nothing to do.")
        return

    found = 0
    downloaded = 0
    failed = 0

    for i, item in enumerate(candidates, 1):
        d = item["data"]
        doi = d["DOI"].strip()
        key = d["key"]
        title = d.get("title", "untitled")

        print(f"[{i}/{len(candidates)}] {fmt_item_short(item)}")
        print(f"    DOI: {doi}")

        result = _find_pdf_source(doi, sources)

        if not result:
            print(f"    ❌ No open-access PDF found")
            failed += 1
            continue

        pdf_url, source_url, source_name = result
        found += 1
        print(f"    ✅ Found via {source_name}: {pdf_url[:80]}...")

        if dry_run:
            continue

        # Download PDF to temp file
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, "download.pdf")
        pdf_filename = _make_pdf_filename(d, key)

        try:
            pdf_downloaded = _download_pdf(pdf_url, tmp_path)

            if pdf_downloaded:
                file_size = os.path.getsize(tmp_path)
                print(f"    📥 Downloaded ({file_size:,} bytes)")

                # Save locally if requested
                if download_dir:
                    local_path = os.path.join(download_dir, pdf_filename)
                    shutil.copy2(tmp_path, local_path)
                    print(f"    💾 Saved: {local_path}")

                # Upload to Zotero storage if requested
                if upload_mode:
                    if _upload_pdf_to_zotero(api_key, prefix, key, tmp_path, pdf_filename):
                        print(f"    📎 Uploaded to Zotero storage")
                        downloaded += 1
                    else:
                        print(f"    ⚠  Upload to Zotero failed, creating linked URL instead")
                        if _create_linked_url_attachment(api_key, prefix, key, f"{title}.pdf", source_url):
                            print(f"    🔗 Linked URL attachment created")
                            downloaded += 1
                        else:
                            print(f"    ❌ Failed to create attachment")
                    continue
            else:
                print(f"    ⚠  Direct download blocked (anti-bot), creating linked URL")

            # Default: create linked URL attachment (works for both successful and failed downloads)
            if _create_linked_url_attachment(api_key, prefix, key, f"{title}.pdf", source_url):
                print(f"    🔗 Linked URL attachment created")
                downloaded += 1
            else:
                print(f"    ❌ Failed to create attachment")
        finally:
            # Cleanup temp
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # Summary
    print(f"\n{'='*50}")
    print(f"📊 fetch-pdfs Summary")
    print(f"{'='*50}")
    print(f"Processed:          {len(candidates)}")
    print(f"PDF found:          {found} ✅")
    if not dry_run:
        print(f"Attached:           {downloaded} 📎")
    print(f"Not found:          {failed} ❌")
    print(f"No DOI:             {skipped_no_doi} ⏭️")
    print(f"Already had PDF:    {skipped_has_pdf} ⏭️")
    if dry_run:
        print(f"\n💡 This was a dry run. Remove --dry-run to fetch and attach PDFs.")


def cmd_delete(args):
    """Move items to trash (default) or permanently delete them."""
    api_key, prefix = get_config()

    for key in args.keys:
        # Validate item key format
        if not validate_item_key(key):
            continue

        # Fetch item to show what we're deleting and get version
        try:
            item, headers = api_get_json(f"{prefix}/items/{key}", api_key)
        except SystemExit:
            print(f"❌ Item {key} not found", file=sys.stderr)
            continue

        version = headers.get("Last-Modified-Version", "0")
        title = item.get("data", {}).get("title", "untitled")

        if not args.yes:
            action = "permanently delete" if args.permanent else "trash"
            print(f"  {fmt_item_short(item)}")
            confirm = input(f"  {action.capitalize()} '{title}'? [y/N] ").strip().lower()
            if confirm != "y":
                print("  Skipped.")
                continue

        if args.permanent:
            # Permanent delete
            url = f"{API_BASE}{prefix}/items/{key}"
            req_headers = {
                "Zotero-API-Key": api_key,
                "Zotero-API-Version": "3",
                "If-Unmodified-Since-Version": str(version),
            }
            req = urllib.request.Request(url, headers=req_headers, method="DELETE")
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    pass
                print(f"🗑️  Permanently deleted: {title} [{key}]")
            except urllib.error.HTTPError as e:
                print(f"❌ Failed to delete {key}: {e.code} {e.reason}", file=sys.stderr)
        else:
            # Move to trash via PATCH (default — recoverable)
            patch_data = {"deleted": 1}
            url = f"{API_BASE}{prefix}/items/{key}"
            req_headers = {
                "Zotero-API-Key": api_key,
                "Zotero-API-Version": "3",
                "Content-Type": "application/json",
                "If-Unmodified-Since-Version": str(version),
            }
            body = json.dumps(patch_data).encode("utf-8")
            req = urllib.request.Request(url, data=body, headers=req_headers, method="PATCH")
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    pass
                print(f"🗑️  Trashed: {title} [{key}]")
            except urllib.error.HTTPError as e:
                print(f"❌ Failed to trash {key}: {e.code} {e.reason}", file=sys.stderr)


def cmd_update(args):
    """Update item metadata."""
    api_key, prefix = get_config()
    if not validate_item_key(args.key):
        sys.exit(1)

    # Fetch current item
    item, headers = api_get_json(f"{prefix}/items/{args.key}", api_key)
    version = headers.get("Last-Modified-Version", "0")
    d = item.get("data", {})

    changes = {}
    if args.title:
        changes["title"] = args.title
    if args.date:
        changes["date"] = args.date
    if args.doi is not None:
        changes["DOI"] = args.doi
    if args.url is not None:
        changes["url"] = args.url

    # Tag management
    current_tags = [t["tag"] for t in d.get("tags", [])]
    tags_changed = False

    if args.add_tags:
        for tag in args.add_tags.split(","):
            tag = tag.strip()
            if tag and tag not in current_tags:
                current_tags.append(tag)
                tags_changed = True

    if args.remove_tags:
        for tag in args.remove_tags.split(","):
            tag = tag.strip()
            if tag in current_tags:
                current_tags.remove(tag)
                tags_changed = True

    if tags_changed:
        changes["tags"] = [{"tag": t} for t in current_tags]

    if args.add_collection:
        current_collections = list(d.get("collections", []))
        if args.add_collection not in current_collections:
            current_collections.append(args.add_collection)
            changes["collections"] = current_collections

    if not changes:
        print("No changes specified.")
        return

    # Show diff
    print(f"Updating [{args.key}]:")
    for field, new_val in changes.items():
        old_val = d.get(field, "")
        if field == "tags":
            old_str = ", ".join(t["tag"] for t in d.get("tags", []))
            new_str = ", ".join(t["tag"] for t in new_val)
            print(f"  tags: {old_str} → {new_str}")
        elif field == "collections":
            print(f"  collections: {d.get('collections', [])} → {new_val}")
        else:
            print(f"  {field}: {old_val} → {new_val}")

    # PATCH
    url = f"{API_BASE}{prefix}/items/{args.key}"
    req_headers = {
        "Zotero-API-Key": api_key,
        "Zotero-API-Version": "3",
        "Content-Type": "application/json",
        "If-Unmodified-Since-Version": str(version),
    }
    body = json.dumps(changes).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=req_headers, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            pass
        print("✅ Updated successfully.")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        print(f"❌ Update failed: {e.code} {e.reason}", file=sys.stderr)
        if err_body:
            print(err_body[:500], file=sys.stderr)


def cmd_export(args):
    """Export items in standard bibliographic formats."""
    api_key, prefix = get_config()

    fmt = args.format
    if args.collection:
        path = f"{prefix}/collections/{args.collection}/items"
    else:
        path = f"{prefix}/items/top"

    # Zotero API supports format parameter directly
    params = {"format": fmt, "limit": "100"}
    all_output = []
    start = 0

    while True:
        params["start"] = str(start)
        body, headers = api_request(path, api_key, params=params)
        if body.strip():
            all_output.append(body)
        total = int(headers.get("Total-Results", "0"))
        start += 100
        if start >= total:
            break

    result = "\n".join(all_output)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Exported to {args.output} ({len(result)} bytes)")
    else:
        print(result)


def cmd_batch_add(args):
    """Add multiple items from a file of identifiers."""
    api_key, prefix = get_config()

    with open(args.file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    identifiers = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        identifiers.append(line)

    if not identifiers:
        print("No identifiers found in file.")
        return

    print(f"Processing {len(identifiers)} identifiers...\n")

    added = 0
    skipped = 0
    failed = 0

    for i, ident in enumerate(identifiers, 1):
        print(f"[{i}/{len(identifiers)}] {ident}")

        # Build a fake args object for cmd_add_identifier
        class FakeArgs:
            pass

        fake = FakeArgs()
        fake.identifier = ident
        fake.id_type = args.type
        fake.collection = args.collection
        fake.tags = args.tags
        fake.force = args.force

        try:
            result = cmd_add_identifier(fake)
            if result == "added":
                added += 1
            elif result == "duplicate":
                skipped += 1
            else:
                failed += 1
        except SystemExit:
            failed += 1

        time.sleep(1)  # Be polite to the API

    print(f"\n📊 Batch Summary")
    print(f"{'='*30}")
    print(f"Added:   {added} ✅")
    print(f"Skipped: {skipped} ⏭️  (duplicates)")
    print(f"Failed:  {failed} ❌")


def main():
    parser = argparse.ArgumentParser(
        description="Zotero CLI — interact with Zotero libraries via the Web API v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable text")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # items
    p = subparsers.add_parser("items", help="List library items")
    p.add_argument("--limit", type=int, default=25, help="Max items to return")
    p.add_argument("--sort", default="dateModified", help="Sort field")
    p.add_argument("--direction", default="desc", help="Sort direction (asc/desc)")
    p.add_argument("--collection", help="Filter by collection key")
    p.add_argument("--type", help="Filter by item type (e.g. journalArticle, book)")
    p.add_argument("--top", action="store_true", default=True, help="Top-level items only")

    # search
    p = subparsers.add_parser("search", help="Search library items")
    p.add_argument("query", help="Search query")
    p.add_argument("--limit", type=int, default=25, help="Max results")
    p.add_argument("--sort", default="relevance", help="Sort field")
    p.add_argument("--type", help="Filter by item type")

    # get
    p = subparsers.add_parser("get", help="Get full item details")
    p.add_argument("key", help="Item key")

    # collections
    subparsers.add_parser("collections", help="List collections")

    # tags
    subparsers.add_parser("tags", help="List tags")

    # children
    p = subparsers.add_parser("children", help="List child items")
    p.add_argument("key", help="Parent item key")

    # add-doi
    p = subparsers.add_parser("add-doi", help="Add item by DOI")
    p.add_argument("identifier", help="DOI (e.g. 10.1234/example)")
    p.add_argument("--collection", help="Add to collection key")
    p.add_argument("--tags", help="Comma-separated tags to add")
    p.add_argument("--force", action="store_true", help="Add even if duplicate detected")
    p.set_defaults(id_type="doi")

    # add-isbn
    p = subparsers.add_parser("add-isbn", help="Add item by ISBN")
    p.add_argument("identifier", help="ISBN")
    p.add_argument("--collection", help="Add to collection key")
    p.add_argument("--tags", help="Comma-separated tags to add")
    p.add_argument("--force", action="store_true", help="Add even if duplicate detected")
    p.set_defaults(id_type="isbn")

    # add-pmid
    p = subparsers.add_parser("add-pmid", help="Add item by PubMed ID")
    p.add_argument("identifier", help="PubMed ID")
    p.add_argument("--collection", help="Add to collection key")
    p.add_argument("--tags", help="Comma-separated tags to add")
    p.add_argument("--force", action="store_true", help="Add even if duplicate detected")
    p.set_defaults(id_type="pmid")

    # delete
    p = subparsers.add_parser("delete", help="Move items to trash (default) or permanently delete")
    p.add_argument("keys", nargs="+", help="Item key(s) to delete")
    p.add_argument("--yes", action="store_true", help="Skip confirmation")
    p.add_argument("--permanent", action="store_true", help="Permanently delete (default is recoverable trash)")
    p.add_argument("--trash", action="store_true", help="Move to trash (default, kept for backwards compat)")

    # update
    p = subparsers.add_parser("update", help="Update item metadata")
    p.add_argument("key", help="Item key to update")
    p.add_argument("--title", help="New title")
    p.add_argument("--date", help="New date")
    p.add_argument("--doi", help="Set DOI")
    p.add_argument("--url", help="Set URL")
    p.add_argument("--add-tags", help="Comma-separated tags to add")
    p.add_argument("--remove-tags", help="Comma-separated tags to remove")
    p.add_argument("--add-collection", help="Add to collection key")

    # export
    p = subparsers.add_parser("export", help="Export items in bibliographic format")
    p.add_argument("--format", default="bibtex", choices=["bibtex", "ris", "csljson"],
                    help="Export format (default: bibtex)")
    p.add_argument("--collection", help="Export only items from this collection")
    p.add_argument("--output", help="Write to file instead of stdout")

    # batch-add
    p = subparsers.add_parser("batch-add", help="Add multiple items from a file of identifiers")
    p.add_argument("file", help="File with one identifier per line")
    p.add_argument("--type", default="doi", choices=["doi", "isbn", "pmid"],
                    help="Identifier type (default: doi)")
    p.add_argument("--collection", help="Add to collection key")
    p.add_argument("--tags", help="Comma-separated tags to add")
    p.add_argument("--force", action="store_true", help="Skip duplicate detection")

    # check-pdfs
    p = subparsers.add_parser("check-pdfs", help="Report PDF attachment status")

    # crossref
    p = subparsers.add_parser("crossref", help="Cross-reference citations against library")
    p.add_argument("file", help="Text/markdown file with citations (Author, Year format)")

    # find-dois
    p = subparsers.add_parser("find-dois", help="Find and add missing DOIs via CrossRef")
    p.add_argument("--apply", action="store_true", help="Actually write DOIs (default is dry run)")
    p.add_argument("--limit", type=int, default=None, help="Max items to process")
    p.add_argument("--collection", help="Filter by collection key")

    # fetch-pdfs
    p = subparsers.add_parser("fetch-pdfs", help="Fetch open-access PDFs for items")
    p.add_argument("--dry-run", action="store_true", help="Show what would be fetched without downloading")
    p.add_argument("--limit", type=int, default=None, help="Max items to process")
    p.add_argument("--collection", help="Filter by collection key")
    p.add_argument("--download-dir", help="Save PDFs locally to this directory")
    p.add_argument("--upload", action="store_true", help="Upload to Zotero storage (S3) instead of linked URL")
    p.add_argument("--sources", default=",".join(PDF_SOURCES),
                    help=f"Comma-separated PDF sources to try (default: {','.join(PDF_SOURCES)})")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # JSON output mode — override formatters
    if args.json:
        _enable_json_mode()

    if args.command == "items":
        cmd_items(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "get":
        cmd_get(args)
    elif args.command == "collections":
        cmd_collections(args)
    elif args.command == "tags":
        cmd_tags(args)
    elif args.command == "children":
        cmd_children(args)
    elif args.command in ("add-doi", "add-isbn", "add-pmid"):
        result = cmd_add_identifier(args)
        if result == "failed":
            sys.exit(1)
    elif args.command == "delete":
        cmd_delete(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "batch-add":
        cmd_batch_add(args)
    elif args.command == "check-pdfs":
        cmd_check_pdfs(args)
    elif args.command == "crossref":
        cmd_crossref(args)
    elif args.command == "find-dois":
        cmd_find_dois(args)
    elif args.command == "fetch-pdfs":
        cmd_fetch_pdfs(args)


if __name__ == "__main__":
    main()
