---
name: apple-contacts
description: Look up contacts from macOS Contacts.app. Use when resolving phone numbers to names, finding contact info, or searching the address book.
metadata: {"clawdbot":{"emoji":"👤","os":["darwin"]}}
---

# Apple Contacts

Query Contacts.app via AppleScript.

## Quick Lookups

```bash
# By phone (name only)
osascript -e 'tell application "Contacts" to get name of every person whose value of phones contains "+1XXXXXXXXXX"'

# By name
osascript -e 'tell application "Contacts" to get name of every person whose name contains "John"'

# List all
osascript -e 'tell application "Contacts" to get name of every person'
```

## Full Contact Info

⚠️ Don't use `first person whose` — buggy. Use this pattern:

```bash
# By phone
osascript -e 'tell application "Contacts"
  set matches to every person whose value of phones contains "+1XXXXXXXXXX"
  if length of matches > 0 then
    set p to item 1 of matches
    return {name of p, value of phones of p, value of emails of p}
  end if
end tell'

# By name
osascript -e 'tell application "Contacts"
  set matches to every person whose name contains "John"
  if length of matches > 0 then
    set p to item 1 of matches
    return {name of p, value of phones of p, value of emails of p}
  end if
end tell'
```

## Phone Lookup

⚠️ **Exact string match required** — must match stored format exactly.

| Stored | Search | Works? |
|--------|--------|--------|
| `+1XXXXXXXXXX` | `+1XXXXXXXXXX` | ✅ |
| `+1XXXXXXXXXX` | `XXXXXXXXXX` | ❌ |

Try with `+1` prefix first. If fails, search by name instead.

## Name Search

- Case-insensitive
- Partial match with `contains`
- Exact match: use `is` instead of `contains`

## Output

Returns comma-separated: `name, phone1, [phone2...], email1, [email2...]`

No match = empty output (not an error).
