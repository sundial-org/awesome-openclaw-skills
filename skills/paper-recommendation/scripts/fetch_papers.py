#!/usr/bin/env python3
"""
 Jarvis Research Skill - Script 1: Paper Fetching

 Fetches latest papers from arXiv and optionally downloads PDFs.

 Usage:
   python3 fetch_papers.py [--limit N] [--download] [--json]

 Output:
   Paper list in JSON format (to stdout)
   PDF files saved to ~/jarvis-research/papers/
"""

import json
import subprocess
import re
import argparse
from datetime import datetime
from pathlib import Path

# Configuration
PAPERS_DIR = Path.home() / "jarvis-research/papers"
CATEGORIES = ['cs.AI', 'cs.LG', 'cs.MA']
KEYWORDS = [
    'agent', 'multi-agent', 'llm', 'large language model',
    'reasoning', 'planning', 'autonomous', 'chain-of-thought', 'CoT',
    'reasoning models', 'foundation models', 'alignment', 'safety',
    'in-context learning', 'few-shot', 'prompt engineering',
    'self-evolution', 'self-improving', '反思', 'reflection',
    'tool use', 'function calling', 'RAG', 'retrieval-augmented',
    'memory', 'long context', 'context length', 'prompt caching'
]


def fetch_papers(limit=15, min_score=3):
    """Fetch latest papers from arXiv."""
    papers = []
    
    for category in CATEGORIES:
        url = f'https://export.arxiv.org/api/query?search_query=cat:{category}&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending'
        
        result = subprocess.run(['curl', '-sL', url], capture_output=True, text=True, timeout=30)
        data = result.stdout
        entries = re.findall(r'<entry>(.*?)</entry>', data, re.DOTALL)
        
        for entry in entries:
            id_match = re.search(r'<id>(.*?)</id>', entry)
            if id_match:
                paper_id = id_match.group(1).split('/abs/')[-1].split('v')[0]
            else:
                continue
            
            title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            title = title.group(1).replace('\n', ' ').strip() if title else "No title"
            
            summary = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            summary = summary.group(1).replace('\n', ' ').strip() if summary else ""
            
            authors = re.findall(r'<name>(.*?)</name>', entry)[:3]
            published = re.search(r'<published>(\d{4}-\d{2}-\d{2})</published>', entry)
            published = published.group(1) if published else datetime.now().strftime('%Y-%m-%d')
            
            text = (title + ' ' + summary).lower()
            score = sum(1 for kw in KEYWORDS if kw in text)
            
            if score >= min_score:
                papers.append({
                    'id': paper_id,
                    'title': title,
                    'summary': summary,
                    'authors': authors,
                    'published': published,
                    'url': f'https://arxiv.org/abs/{paper_id}',
                    'pdf_url': f'https://arxiv.org/pdf/{paper_id}.pdf',
                    'category': category,
                    'relevance_score': score
                })
    
    papers.sort(key=lambda x: (-x['relevance_score'], x['published']))
    seen = set()
    unique = []
    for p in papers:
        if p['id'] not in seen:
            seen.add(p['id'])
            unique.append(p)
    
    return unique[:limit]


def download_papers(papers, output_dir):
    """Download PDF papers."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded = []
    for p in papers:
        pdf_path = output_dir / f"{p['id']}.pdf"
        if pdf_path.exists():
            downloaded.append(str(pdf_path))
            continue
        
        try:
            subprocess.run(['curl', '-sL', p['pdf_url'], '-o', str(pdf_path)], timeout=60)
            if pdf_path.exists() and pdf_path.stat().st_size > 1000:
                downloaded.append(str(pdf_path))
        except:
            pass
    
    return downloaded


def main():
    parser = argparse.ArgumentParser(description='Fetch latest AI research papers from arXiv')
    parser.add_argument('--limit', type=int, default=15, help='Max papers to fetch')
    parser.add_argument('--download', action='store_true', help='Download PDF files')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    # Fetch papers
    papers = fetch_papers(limit=args.limit)
    
    result = {
        'papers': papers,
        'total': len(papers),
        'fetched_at': datetime.utcnow().isoformat() + 'Z',
        'papers_dir': str(PAPERS_DIR),
        'pdfs_downloaded': []
    }
    
    # Download PDFs if requested
    if args.download:
        pdfs = download_papers(papers, PAPERS_DIR)
        result['pdfs_downloaded'] = pdfs
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Fetched {len(papers)} papers")
        if result.get('pdfs_downloaded'):
            print(f"Downloaded {len(result['pdfs_downloaded'])} PDFs to {PAPERS_DIR}")
    
    return result


if __name__ == '__main__':
    main()
