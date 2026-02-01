#!/usr/bin/env python3
"""
TechNews Orchestrator - Main entry point for the technews skill
"""

import json
import sys
from pathlib import Path

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent

# Import our modules
sys.path.insert(0, str(SCRIPT_DIR))

from techmeme_scraper import fetch_techmeme, load_cache, save_cache
from article_fetcher import fetch_multiple, summarize_content
from social_reactions import analyze_reactions


def format_output(stories: List[Dict]) -> str:
    """Format stories for display."""
    output = []
    output.append("📰 **Tech News Briefing**")
    output.append("")
    
    for i, story in enumerate(stories, 1):
        output.append(f"**{i}. {story['title']}**")
        # Use markdown inline link for Telegram
        output.append(f"🔗 [{story['url']}]({story['url']})")
        
        if story.get("summary"):
            output.append(f"📝 {story['summary'][:200]}...")
        
        # Show reactions if available
        if story.get("reactions"):
            reactions = story["reactions"]
            
            if reactions.get("hacker_news"):
                hn = reactions["hacker_news"]
                hn_url = hn.get("hn_url", "")
                points = hn.get("points", 0)
                comments = hn.get("comment_count", 0)
                output.append(f"💬 [HN: {points}pts, {comments} comments]({hn_url})")
            
            if reactions.get("spicy_quotes"):
                output.append(f"🔥 \"{reactions['spicy_quotes'][0][:100]}...\"")
        
        output.append("")
    
    return "\n".join(output)


def run_technews(num_stories: int = 10) -> str:
    """Main technews workflow."""
    try:
        # Step 1: Fetch from TechMeme
        print("Fetching TechMeme stories...")
        stories = fetch_techmeme(num_stories)
        
        if not stories:
            return "❌ Could not fetch stories from TechMeme"
        
        # Step 2: Fetch article content
        print(f"Fetching {len(stories)} articles...")
        urls = [s["url"] for s in stories]
        articles = fetch_multiple(urls)
        
        # Step 3: Merge content into stories
        for story, article in zip(stories, articles):
            if article.get("success"):
                story["content"] = article.get("content", "")
                story["summary"] = article.get("summary", "")
        
        # Step 4: Analyze reactions
        print("Analyzing social reactions...")
        analyzed = analyze_reactions(stories)
        
        # Step 5: Format output
        return format_output(analyzed)
        
    except requests.exceptions.RequestException as e:
        return f"❌ Network error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def main():
    """CLI entry point."""
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    result = run_technews(num_stories=num)
    print(result)


if __name__ == "__main__":
    main()
