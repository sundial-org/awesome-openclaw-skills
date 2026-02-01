---
name: swiss-phone-directory
description: "Swiss phone directory lookup via search.ch API. Search for businesses, people, or reverse-lookup phone numbers. Use when: (1) finding contact details for Swiss companies or people, (2) looking up addresses by name or phone number, (3) reverse phone number lookup, (4) finding business categories. Requires SEARCHCH_API_KEY."
---

# Swiss Phone Directory Skill

Search the Swiss phone directory (search.ch) for businesses, people, and phone numbers.

## Quick Start

```bash
# Search for a business
python3 scripts/searchch.py search "Migros" --location "Zürich"

# Search for a person
python3 scripts/searchch.py search "Müller Hans" --type person

# Reverse phone number lookup
python3 scripts/searchch.py search "+41442345678"

# Business-only search
python3 scripts/searchch.py search "Restaurant" --location "Bern" --type business --limit 5
```

## Commands

### search
Search for businesses, people, or phone numbers.

```bash
python3 scripts/searchch.py search <query> [options]

Options:
  --location, -l    City, ZIP, street, or canton (e.g., "Zürich", "8000", "ZH")
  --type, -t        Filter: "business", "person", or "all" (default: all)
  --limit, -n       Max results (default: 10, max: 200)
  --lang            Output language: de, fr, it, en (default: de)
```

### Examples

```bash
# Find restaurants in Rapperswil
python3 scripts/searchch.py search "Restaurant" -l "Rupperswil" -t business -n 5

# Find a person by name
python3 scripts/searchch.py search "Meier Peter" -l "Zürich" -t person

# Reverse lookup a phone number
python3 scripts/searchch.py search "044 123 45 67"

# Search with canton abbreviation
python3 scripts/searchch.py search "Bäckerei" -l "SG"
```

## Output Format

Results include (when available):
- **Name** - Business or person name
- **Type** - Organisation or Person
- **Address** - Street, ZIP, city, canton
- **Phone** - Phone number(s)
- **Fax** - Fax number
- **Email** - Email address
- **Website** - Website URL
- **Categories** - Business categories

## Configuration

See [references/configuration.md](references/configuration.md) for setup.

Required: `SEARCHCH_API_KEY` environment variable.

## API Reference

- Base URL: `https://search.ch/tel/api/`
- Rate limits: Depend on API key tier
- Full docs: https://search.ch/tel/api/help.en.html
