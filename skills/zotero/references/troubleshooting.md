# Zotero Skill — Troubleshooting

## HTTP Errors

### 403 Forbidden
**Cause:** Invalid or expired API key, or insufficient write permissions on the library.

**Fix:**
- Check that `ZOTERO_API_KEY` is set correctly
- Regenerate the key at https://www.zotero.org/settings/keys/new
- Ensure the key has write permissions if using add/update/delete operations
- Verify you're using the right library (user vs. group)

### 429 Too Many Requests
**Cause:** Rate limit exceeded. Zotero is ratelimiting your requests.

**Fix:**
- Wait a few seconds and retry (the script includes delays between requests)
- Avoid concurrent requests (run one command at a time)
- If you're batch-adding many items, use `batch-add` instead of looping with `add-doi` — it's optimized with built-in delays

### 503 Service Unavailable
**Cause:** Zotero API or translation server is temporarily down.

**What happens:**
- For DOI lookups (`add-doi`): falls back to CrossRef (still works in most cases)
- For other commands: operation fails — wait a few minutes and retry

**Fix:**
- Check Zotero status at https://status.zotero.org
- Retry after 5–10 minutes
- If DOI lookup fails after 503, verify the DOI manually via CrossRef

## Environment Variable Issues

### Missing ZOTERO_API_KEY or ZOTERO_USER_ID
**Error:** Script exits with message linking to https://www.zotero.org/settings/keys/new

**Fix:**
```bash
export ZOTERO_API_KEY="YOUR_KEY"
export ZOTERO_USER_ID="YOUR_USER_ID"
```

### Using ZOTERO_GROUP_ID for a User Library (or vice versa)
**Symptom:** Empty results, permission errors, or "unknown item" errors.

**Fix:**
- If working with your personal library: use `ZOTERO_USER_ID` (numeric ID from settings)
- If working with a group library: use `ZOTERO_GROUP_ID` (numeric group ID, e.g., 123456)
- Check which library you're adding to: run `python3 zotero.py items --limit 1` to verify connectivity

### CROSSREF_EMAIL Not Set (Optional)
**Effect:** DOI lookup via CrossRef/Unpaywall may be slower or less reliable (anonymous requests are ratelimited more aggressively).

**Fix:**
```bash
export CROSSREF_EMAIL="your.email@example.com"
```

This is optional — the script has a fallback. Set it for better polite-pool behavior.

## DOI Lookup Failed

**Symptom:** `add-doi` fails or returns incomplete metadata.

**Cause:**
- Zotero translation server (503) → automatically falls back to CrossRef
- Invalid DOI format (must be `10.xxxx/...`)
- DOI doesn't exist or has no metadata in CrossRef

**Debug:**
- Verify the DOI is valid: paste it into https://www.crossref.org (e.g., `10.1093/jamia/ocaa037`)
- Try again a few minutes later (server may be recovering)
- Use `--force` to add the item with minimal metadata if you want to add it anyway

## "Duplicate Detected" Messages

**What it means:**
The script found what it thinks is the same item already in your library. The detection uses:
1. DOI match (strongest signal)
2. Title similarity (>85% string match) + exact year + first author last name

**Override:**
```bash
python3 zotero.py add-doi "10.xxxx/..." --force
```

`--force` skips duplicate detection and adds the item anyway. Use if you know it's a real duplicate (e.g., different editions of the same paper) or if the detection is wrong.

## Large Library Performance

**Problem:** `check-pdfs`, `fetch-pdfs`, and `find-dois` are slow on libraries with 500+ items.

**Why:**
- They fetch all items from the API (paginated, but still multiple requests)
- `fetch-pdfs` then attempts PDF lookup for each item
- `find-dois` queries CrossRef for each item missing a DOI

**Solutions:**
- Use `--collection COLLKEY` on `fetch-pdfs` and `find-dois` to scope to a single collection
- Use `--limit` to test on a subset first: `python3 zotero.py fetch-pdfs --limit 10 --dry-run`
- Be patient — rate limiting includes intentional delays to be polite to external services

For `check-pdfs`, there's currently no collection filter (P2 feature), so you'll see all items.

## No PDFs Found During fetch-pdfs

**Expected:** The script tries three sources: Unpaywall → Semantic Scholar → DOI content negotiation.

**Causes:**
- Paper is behind a paywall and no open-access copy exists in these sources
- DOI doesn't have metadata in these databases
- Article is too new or too old (some sources have coverage gaps)

**What you can do:**
- Use `--download-dir ./pdfs` to manually review what was downloaded
- Try a different source: `--sources semanticscholar` (just one source)
- Check https://unpaywall.org manually for the DOI
- Add PDF manually to Zotero (drag & drop or web clipper)

## Script Errors and Exit Codes

- **Exit 0:** Success
- **Exit 1:** API error, validation error, missing credentials, or file not found

For debugging, check stderr for detailed error messages. Use `--json` mode to get structured output where supported (items, search, get).

## Still Stuck?

- Double-check your API key and user ID
- Verify network connectivity (try `python3 -c "import urllib.request; urllib.request.urlopen('https://api.zotero.org')"`)
- Check if the Zotero API is up: https://status.zotero.org
- Try a simple command first: `python3 zotero.py items --limit 1`
- Run with stderr redirection to see full error details: `python3 zotero.py <cmd> 2>&1 | less`
