import os
import sys
import argparse
import json
from linkedin_api import Linkedin
from requests.cookies import RequestsCookieJar

# Styling
BOLD = "\033[1m"
RESET = "\033[0m"
BLUE = "\033[94m"
GREEN = "\033[92m"

def get_api():
    li_at = os.environ.get("LINKEDIN_LI_AT")
    jsessionid = os.environ.get("LINKEDIN_JSESSIONID")
    if not li_at or not jsessionid:
        print("Error: LINKEDIN_LI_AT and LINKEDIN_JSESSIONID environment variables not set.")
        sys.exit(1)
    
    jar = RequestsCookieJar()
    jar.set("li_at", li_at, domain=".www.linkedin.com")
    jar.set("JSESSIONID", jsessionid, domain=".www.linkedin.com")
    
    return Linkedin("", "", cookies=jar)

def whoami(api):
    profile = api.get_user_profile()
    name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()
    headline = profile.get('headline', profile.get('miniProfile', {}).get('occupation', 'No headline'))
    location = profile.get('locationName', 'Unknown')
    print(f"{BOLD}{name}{RESET}")
    print(f"{BLUE}{headline}{RESET}")
    print(f"📍 {location}")

def search(api, query):
    results = api.search_people(keywords=query, limit=10)
    print(f"Search results for '{BOLD}{query}{RESET}':")
    for res in results:
        name = res.get('name', 'Unknown')
        job = res.get('jobtitle', 'No headline')
        urn = res.get('urn_id', 'No URN')
        print(f"- {BOLD}{name}{RESET} ({urn})")
        print(f"  {job}")

def view_profile(api, public_id):
    profile = api.get_profile(public_id)
    name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
    headline = profile.get('headline', 'No headline')
    summary = profile.get('summary', 'No summary provided.')
    
    print(f"{BOLD}{name}{RESET}")
    print(f"{BLUE}{headline}{RESET}")
    print("-" * 20)
    print(summary)
    
    print(f"\n{BOLD}Experience:{RESET}")
    for exp in profile.get('experience', [])[:3]:
        company = exp.get('companyName', 'Unknown')
        title = exp.get('title', 'Unknown')
        print(f"• {BOLD}{title}{RESET} at {company}")

def check_messages(api):
    conversations = api.get_conversations()
    print(f"{BOLD}Recent Conversations:{RESET}")
    for conv in conversations.get('elements', [])[:5]:
        participants = ", ".join([p.get('firstName', 'Unknown') for p in conv.get('participants', [])])
        events = conv.get('events', [{}])
        snippet = "No preview"
        if events:
             content = events[0].get('eventContent', {})
             msg_event = content.get('com.linkedin.voyager.messaging.event.MessageEvent', {})
             snippet = msg_event.get('body', 'No preview')
        
        print(f"• {BOLD}{participants}{RESET}")
        print(f"  {snippet[:100]}...")

def feed(api, count=10):
    posts = api.get_feed_posts(limit=count)
    print(f"{BOLD}LinkedIn Feed (Top {count}):{RESET}")
    for post in posts:
        author = post.get('author_name', 'Unknown')
        time = post.get('old', 'Recently').strip()
        content = post.get('content', 'No content').replace('\n', ' ')
        print(f"• {BOLD}{author}{RESET} ({time}): {content[:200]}...")

def main():
    parser = argparse.ArgumentParser(description="lk - LinkedIn CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("whoami", help="Display current user profile")
    
    search_parser = subparsers.add_parser("search", help="Search for people")
    search_parser.add_argument("query", help="Search keywords")
    
    profile_parser = subparsers.add_parser("profile", help="View profile details")
    profile_parser.add_argument("public_id", help="Public ID or URN")
    
    subparsers.add_parser("messages", help="Check recent messages")
    
    feed_parser = subparsers.add_parser("feed", help="Summarize your timeline")
    feed_parser.add_argument("-n", "--count", type=int, default=10, help="Number of posts to fetch")
    
    subparsers.add_parser("check", help="Quick status check")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    api = get_api()

    try:
        if args.command == "whoami":
            whoami(api)
        elif args.command == "search":
            search(api, args.query)
        elif args.command == "profile":
            view_profile(api, args.public_id)
        elif args.command == "messages":
            check_messages(api)
        elif args.command == "feed":
            feed(api, args.count)
        elif args.command == "check":
            whoami(api)
            print("-" * 10)
            check_messages(api)
    except Exception as e:
        print(f"{BOLD}LinkedIn Error:{RESET} {e}")

if __name__ == "__main__":
    main()
