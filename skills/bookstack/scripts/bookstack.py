#!/usr/bin/env python3
"""
BookStack API Integration for Clawdbot
Full CRUD for books, chapters, pages, shelves + search
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

# Configuration from environment
BASE_URL = os.getenv('BOOKSTACK_URL', '').rstrip('/')
TOKEN_ID = os.getenv('BOOKSTACK_TOKEN_ID', '')
TOKEN_SECRET = os.getenv('BOOKSTACK_TOKEN_SECRET', '')

def api_call(method, endpoint, data=None, params=None):
    """Make API call to BookStack"""
    if not BASE_URL or not TOKEN_ID or not TOKEN_SECRET:
        print("❌ Error: BOOKSTACK_URL, BOOKSTACK_TOKEN_ID, and BOOKSTACK_TOKEN_SECRET required!")
        print("   Set them in environment or ~/.clawdbot/clawdbot.json")
        sys.exit(1)
    
    url = f"{BASE_URL}/api/{endpoint}"
    
    if params:
        url += '?' + urllib.parse.urlencode(params)
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Token {TOKEN_ID}:{TOKEN_SECRET}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            method=method
        )
        
        if data:
            data = {k: v for k, v in data.items() if v is not None}
            req.data = json.dumps(data).encode()
        
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 204:
                return None
            return json.loads(response.read().decode())
    
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode())
            print(f"❌ HTTP {e.code}: {error_data.get('error', {}).get('message', 'Unknown error')}")
        except:
            print(f"❌ HTTP {e.code}: {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Connection error: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

# ============ BOOKS ============

def list_books(args):
    """List all books"""
    params = {'count': args.count} if args.count else {}
    result = api_call("GET", "books", params=params)
    
    if not result.get('data'):
        print("📚 No books found")
        return
    
    print(f"📚 {result.get('total', len(result['data']))} Books:\n")
    for book in result['data']:
        desc = book.get('description', '')[:50] + '...' if book.get('description') else ''
        print(f"  [{book['id']}] {book['name']}")
        if desc:
            print(f"       {desc}")

def get_book(args):
    """Get book details"""
    result = api_call("GET", f"books/{args.id}")
    print(f"📚 Book: {result['name']}")
    print(f"   ID: {result['id']}")
    print(f"   Slug: {result['slug']}")
    if result.get('description'):
        print(f"   Description: {result['description']}")
    print(f"   Created: {result['created_at']}")
    print(f"   Updated: {result['updated_at']}")
    if result.get('contents'):
        print(f"\n   Contents ({len(result['contents'])} items):")
        for item in result['contents'][:10]:
            icon = '📑' if item['type'] == 'chapter' else '📄'
            print(f"     {icon} [{item['id']}] {item['name']}")

def create_book(args):
    """Create a new book"""
    data = {
        "name": args.name,
        "description": args.description
    }
    result = api_call("POST", "books", data)
    print(f"✅ Book created: {result['name']} (ID: {result['id']})")

def update_book(args):
    """Update a book"""
    data = {}
    if args.name:
        data['name'] = args.name
    if args.description:
        data['description'] = args.description
    
    if not data:
        print("❌ Nothing to update. Use --name or --description")
        sys.exit(1)
    
    result = api_call("PUT", f"books/{args.id}", data)
    print(f"✅ Book updated: {result['name']}")

def delete_book(args):
    """Delete a book"""
    api_call("DELETE", f"books/{args.id}")
    print(f"✅ Book {args.id} deleted")

# ============ CHAPTERS ============

def list_chapters(args):
    """List all chapters"""
    params = {'count': args.count} if args.count else {}
    result = api_call("GET", "chapters", params=params)
    
    if not result.get('data'):
        print("📑 No chapters found")
        return
    
    print(f"📑 {result.get('total', len(result['data']))} Chapters:\n")
    for ch in result['data']:
        print(f"  [{ch['id']}] {ch['name']} (Book: {ch.get('book_id', '?')})")

def get_chapter(args):
    """Get chapter details"""
    result = api_call("GET", f"chapters/{args.id}")
    print(f"📑 Chapter: {result['name']}")
    print(f"   ID: {result['id']}")
    print(f"   Book ID: {result['book_id']}")
    if result.get('description'):
        print(f"   Description: {result['description']}")
    if result.get('pages'):
        print(f"\n   Pages ({len(result['pages'])}):")
        for page in result['pages'][:10]:
            print(f"     📄 [{page['id']}] {page['name']}")

def create_chapter(args):
    """Create a new chapter"""
    data = {
        "book_id": args.book_id,
        "name": args.name,
        "description": args.description
    }
    result = api_call("POST", "chapters", data)
    print(f"✅ Chapter created: {result['name']} (ID: {result['id']})")

def update_chapter(args):
    """Update a chapter"""
    data = {}
    if args.name:
        data['name'] = args.name
    if args.description:
        data['description'] = args.description
    if args.book_id:
        data['book_id'] = args.book_id
    
    if not data:
        print("❌ Nothing to update")
        sys.exit(1)
    
    result = api_call("PUT", f"chapters/{args.id}", data)
    print(f"✅ Chapter updated: {result['name']}")

def delete_chapter(args):
    """Delete a chapter"""
    api_call("DELETE", f"chapters/{args.id}")
    print(f"✅ Chapter {args.id} deleted")

# ============ PAGES ============

def list_pages(args):
    """List all pages"""
    params = {'count': args.count} if args.count else {}
    result = api_call("GET", "pages", params=params)
    
    if not result.get('data'):
        print("📄 No pages found")
        return
    
    print(f"📄 {result.get('total', len(result['data']))} Pages:\n")
    for page in result['data']:
        location = f"Chapter {page['chapter_id']}" if page.get('chapter_id') else f"Book {page['book_id']}"
        print(f"  [{page['id']}] {page['name']} ({location})")

def get_page(args):
    """Get page with full content"""
    result = api_call("GET", f"pages/{args.id}")
    print(f"📄 Page: {result['name']}")
    print(f"   ID: {result['id']}")
    print(f"   Book ID: {result['book_id']}")
    if result.get('chapter_id'):
        print(f"   Chapter ID: {result['chapter_id']}")
    print(f"   Editor: {result.get('editor', 'unknown')}")
    print(f"   Created: {result['created_at']}")
    print(f"   Updated: {result['updated_at']}")
    
    if args.content:
        print(f"\n--- Content (HTML) ---")
        print(result.get('html', ''))
    elif args.markdown:
        print(f"\n--- Content (Markdown) ---")
        print(result.get('markdown', result.get('html', '')))
    else:
        # Show preview
        html = result.get('html', '')
        if html:
            # Strip HTML tags for preview
            import re
            text = re.sub('<[^<]+?>', '', html)
            text = ' '.join(text.split())[:200]
            print(f"\n   Preview: {text}...")

def create_page(args):
    """Create a new page"""
    data = {
        "name": args.name,
    }
    
    if args.book_id:
        data['book_id'] = args.book_id
    if args.chapter_id:
        data['chapter_id'] = args.chapter_id
    
    if not args.book_id and not args.chapter_id:
        print("❌ Either --book-id or --chapter-id required")
        sys.exit(1)
    
    if args.html:
        data['html'] = args.html
    elif args.markdown:
        data['markdown'] = args.markdown
    elif args.content:
        # Auto-detect: if starts with # or no HTML tags, treat as markdown
        if args.content.startswith('#') or '<' not in args.content:
            data['markdown'] = args.content
        else:
            data['html'] = args.content
    
    result = api_call("POST", "pages", data)
    print(f"✅ Page created: {result['name']} (ID: {result['id']})")

def update_page(args):
    """Update a page"""
    data = {}
    if args.name:
        data['name'] = args.name
    if args.html:
        data['html'] = args.html
    if args.markdown:
        data['markdown'] = args.markdown
    if args.content:
        if args.content.startswith('#') or '<' not in args.content:
            data['markdown'] = args.content
        else:
            data['html'] = args.content
    if args.book_id:
        data['book_id'] = args.book_id
    if args.chapter_id:
        data['chapter_id'] = args.chapter_id
    
    if not data:
        print("❌ Nothing to update")
        sys.exit(1)
    
    result = api_call("PUT", f"pages/{args.id}", data)
    print(f"✅ Page updated: {result['name']}")

def delete_page(args):
    """Delete a page"""
    api_call("DELETE", f"pages/{args.id}")
    print(f"✅ Page {args.id} deleted")

# ============ SHELVES ============

def list_shelves(args):
    """List all shelves"""
    params = {'count': args.count} if args.count else {}
    result = api_call("GET", "shelves", params=params)
    
    if not result.get('data'):
        print("📁 No shelves found")
        return
    
    print(f"📁 {result.get('total', len(result['data']))} Shelves:\n")
    for shelf in result['data']:
        print(f"  [{shelf['id']}] {shelf['name']}")

def get_shelf(args):
    """Get shelf details"""
    result = api_call("GET", f"shelves/{args.id}")
    print(f"📁 Shelf: {result['name']}")
    print(f"   ID: {result['id']}")
    if result.get('description'):
        print(f"   Description: {result['description']}")
    if result.get('books'):
        print(f"\n   Books ({len(result['books'])}):")
        for book in result['books'][:10]:
            print(f"     📚 [{book['id']}] {book['name']}")

def create_shelf(args):
    """Create a new shelf"""
    data = {
        "name": args.name,
        "description": args.description
    }
    result = api_call("POST", "shelves", data)
    print(f"✅ Shelf created: {result['name']} (ID: {result['id']})")

# ============ SEARCH ============

def search(args):
    """Search content"""
    params = {
        'query': args.query,
        'count': args.count or 20
    }
    if args.type:
        params['query'] = f"{{{args.type}}} {args.query}"
    
    result = api_call("GET", "search", params=params)
    
    if not result.get('data'):
        print(f"🔍 No results for: {args.query}")
        return
    
    print(f"🔍 {result.get('total', len(result['data']))} Results for '{args.query}':\n")
    for item in result['data']:
        icon = {'page': '📄', 'chapter': '📑', 'book': '📚', 'bookshelf': '📁'}.get(item['type'], '📎')
        print(f"  {icon} [{item['type']}:{item['id']}] {item['name']}")
        if item.get('preview_html'):
            import re
            preview = re.sub('<[^<]+?>', '', item['preview_html'].get('content', ''))
            preview = ' '.join(preview.split())[:80]
            if preview:
                print(f"       {preview}...")

# ============ MAIN ============

def main():
    parser = argparse.ArgumentParser(description='BookStack API CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Books
    p = subparsers.add_parser('list_books', help='List all books')
    p.add_argument('--count', type=int, help='Max results')
    p.set_defaults(func=list_books)
    
    p = subparsers.add_parser('get_book', help='Get book details')
    p.add_argument('id', type=int)
    p.set_defaults(func=get_book)
    
    p = subparsers.add_parser('create_book', help='Create a book')
    p.add_argument('name')
    p.add_argument('description', nargs='?')
    p.set_defaults(func=create_book)
    
    p = subparsers.add_parser('update_book', help='Update a book')
    p.add_argument('id', type=int)
    p.add_argument('--name')
    p.add_argument('--description')
    p.set_defaults(func=update_book)
    
    p = subparsers.add_parser('delete_book', help='Delete a book')
    p.add_argument('id', type=int)
    p.set_defaults(func=delete_book)
    
    # Chapters
    p = subparsers.add_parser('list_chapters', help='List all chapters')
    p.add_argument('--count', type=int)
    p.set_defaults(func=list_chapters)
    
    p = subparsers.add_parser('get_chapter', help='Get chapter details')
    p.add_argument('id', type=int)
    p.set_defaults(func=get_chapter)
    
    p = subparsers.add_parser('create_chapter', help='Create a chapter')
    p.add_argument('--book-id', type=int, required=True)
    p.add_argument('--name', required=True)
    p.add_argument('--description')
    p.set_defaults(func=create_chapter)
    
    p = subparsers.add_parser('update_chapter', help='Update a chapter')
    p.add_argument('id', type=int)
    p.add_argument('--name')
    p.add_argument('--description')
    p.add_argument('--book-id', type=int)
    p.set_defaults(func=update_chapter)
    
    p = subparsers.add_parser('delete_chapter', help='Delete a chapter')
    p.add_argument('id', type=int)
    p.set_defaults(func=delete_chapter)
    
    # Pages
    p = subparsers.add_parser('list_pages', help='List all pages')
    p.add_argument('--count', type=int)
    p.set_defaults(func=list_pages)
    
    p = subparsers.add_parser('get_page', help='Get page with content')
    p.add_argument('id', type=int)
    p.add_argument('--content', action='store_true', help='Show full HTML')
    p.add_argument('--markdown', action='store_true', help='Show as markdown')
    p.set_defaults(func=get_page)
    
    p = subparsers.add_parser('create_page', help='Create a page')
    p.add_argument('--name', required=True)
    p.add_argument('--book-id', type=int)
    p.add_argument('--chapter-id', type=int)
    p.add_argument('--content', help='Content (auto-detect HTML/MD)')
    p.add_argument('--html', help='HTML content')
    p.add_argument('--markdown', help='Markdown content')
    p.set_defaults(func=create_page)
    
    p = subparsers.add_parser('update_page', help='Update a page')
    p.add_argument('id', type=int)
    p.add_argument('--name')
    p.add_argument('--content')
    p.add_argument('--html')
    p.add_argument('--markdown')
    p.add_argument('--book-id', type=int)
    p.add_argument('--chapter-id', type=int)
    p.set_defaults(func=update_page)
    
    p = subparsers.add_parser('delete_page', help='Delete a page')
    p.add_argument('id', type=int)
    p.set_defaults(func=delete_page)
    
    # Shelves
    p = subparsers.add_parser('list_shelves', help='List all shelves')
    p.add_argument('--count', type=int)
    p.set_defaults(func=list_shelves)
    
    p = subparsers.add_parser('get_shelf', help='Get shelf details')
    p.add_argument('id', type=int)
    p.set_defaults(func=get_shelf)
    
    p = subparsers.add_parser('create_shelf', help='Create a shelf')
    p.add_argument('name')
    p.add_argument('description', nargs='?')
    p.set_defaults(func=create_shelf)
    
    # Search
    p = subparsers.add_parser('search', help='Search content')
    p.add_argument('query')
    p.add_argument('--type', choices=['page', 'chapter', 'book', 'shelf'])
    p.add_argument('--count', type=int)
    p.set_defaults(func=search)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == '__main__':
    main()
