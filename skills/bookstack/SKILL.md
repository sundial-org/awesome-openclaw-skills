---
name: bookstack
description: "BookStack Wiki & Documentation API integration. Manage your knowledge base programmatically: create, read, update, and delete books, chapters, pages, and shelves. Full-text search across all content. Use when you need to: (1) Create or edit wiki pages and documentation, (2) Organize content in books and chapters, (3) Search your knowledge base, (4) Automate documentation workflows, (5) Sync content between systems. Supports both HTML and Markdown content."
---

# BookStack Skill

**BookStack** ist eine Open-Source Wiki- und Dokumentationsplattform. Mit diesem Skill kannst du deine gesamte Wissensdatenbank über die API verwalten – perfekt für Automatisierung und Integration.

## Was kann dieser Skill?

- 📚 **Bücher** erstellen, bearbeiten, löschen
- 📑 **Kapitel** innerhalb von Büchern verwalten
- 📄 **Seiten** mit HTML oder Markdown erstellen/bearbeiten
- 🔍 **Volltextsuche** über alle Inhalte
- 📁 **Regale** (Shelves) zum Organisieren von Büchern

## Quick Start

```bash
# Alle Bücher auflisten
python3 scripts/bookstack.py list_books

# Suche in der Wissensdatenbank
python3 scripts/bookstack.py search "Home Assistant"

# Seite abrufen
python3 scripts/bookstack.py get_page 123

# Neue Seite erstellen (Markdown)
python3 scripts/bookstack.py create_page --book-id 1 --name "Meine Seite" --markdown "# Titel\n\nInhalt hier..."
```

## Alle Befehle

### Books (Bücher)
```bash
python3 scripts/bookstack.py list_books                    # Alle Bücher
python3 scripts/bookstack.py get_book <id>                 # Buch-Details
python3 scripts/bookstack.py create_book "Name" ["Desc"]   # Neues Buch
python3 scripts/bookstack.py update_book <id> [--name] [--description]
python3 scripts/bookstack.py delete_book <id>
```

### Chapters (Kapitel)
```bash
python3 scripts/bookstack.py list_chapters                 # Alle Kapitel
python3 scripts/bookstack.py get_chapter <id>              # Kapitel-Details
python3 scripts/bookstack.py create_chapter --book-id <id> --name "Name"
python3 scripts/bookstack.py update_chapter <id> [--name] [--description]
python3 scripts/bookstack.py delete_chapter <id>
```

### Pages (Seiten)
```bash
python3 scripts/bookstack.py list_pages                    # Alle Seiten
python3 scripts/bookstack.py get_page <id>                 # Seiten-Preview
python3 scripts/bookstack.py get_page <id> --content       # Mit HTML-Content
python3 scripts/bookstack.py get_page <id> --markdown      # Als Markdown

# Seite erstellen (in Buch oder Kapitel)
python3 scripts/bookstack.py create_page --book-id <id> --name "Name" --markdown "# Content"
python3 scripts/bookstack.py create_page --chapter-id <id> --name "Name" --html "<p>HTML</p>"

# Seite bearbeiten
python3 scripts/bookstack.py update_page <id> [--name] [--content] [--markdown]
python3 scripts/bookstack.py delete_page <id>
```

### Search (Suche)
```bash
python3 scripts/bookstack.py search "query"                # Alles durchsuchen
python3 scripts/bookstack.py search "query" --type page    # Nur Seiten
python3 scripts/bookstack.py search "query" --type book    # Nur Bücher
```

### Shelves (Regale)
```bash
python3 scripts/bookstack.py list_shelves                  # Alle Regale
python3 scripts/bookstack.py get_shelf <id>                # Regal-Details
python3 scripts/bookstack.py create_shelf "Name" ["Desc"]  # Neues Regal
```

## Konfiguration

Setze die Umgebungsvariablen in `~/.clawdbot/clawdbot.json`:

```json
{
  "skills": {
    "entries": {
      "bookstack": {
        "env": {
          "BOOKSTACK_URL": "https://your-bookstack.example.com",
          "BOOKSTACK_TOKEN_ID": "dein-token-id",
          "BOOKSTACK_TOKEN_SECRET": "dein-token-secret"
        }
      }
    }
  }
}
```

### Token erstellen

1. In BookStack einloggen
2. **Profil bearbeiten** → **API Tokens**
3. **Create Token** klicken
4. Token ID und Secret kopieren

⚠️ Der User braucht die Rolle mit **"Access System API"** Permission!

## API Referenz

- **Base URL**: `{BOOKSTACK_URL}/api`
- **Auth Header**: `Authorization: Token {ID}:{SECRET}`
- **Offizielle Docs**: https://demo.bookstackapp.com/api/docs

---

**Author**: Seal 🦭 | **Version**: 1.0.1
