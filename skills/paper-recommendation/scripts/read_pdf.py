#!/usr/bin/env python3
"""
 Jarvis Research Skill - Script 3: PDF Reader

 Reads PDF files and extracts text for analysis.

 Usage:
   python3 read_pdf.py <pdf-path> [--pages N] [--json]

 Output:
   Plain text extracted from PDF
   Or JSON with structured content
"""

import json
import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def extract_text(pdf_path, max_pages=None):
    """Extract text from PDF using pdftotext."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        return {"error": f"File not found: {pdf_path}"}
    
    cmd = ['pdftotext', str(pdf_path), '-']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            return {"error": f"pdftotext failed: {result.stderr}"}
        
        text = result.stdout
        
        if max_pages:
            # Rough page estimation (assuming ~3000 chars per page)
            chars_per_page = 3000
            text = text[:max_pages * chars_per_page]
        
        return {
            "success": True,
            "pdf_path": str(pdf_path),
            "text_length": len(text),
            "text": text,
            "extracted_at": datetime.utcnow().isoformat() + 'Z'
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "PDF extraction timed out"}
    except Exception as e:
        return {"error": str(e)}


def extract_sections(text):
    """Extract key sections from paper text."""
    sections = {}
    
    # Common section headers
    section_patterns = [
        ('abstract', r'Abstract[:\s]*([\s\S]*?)(?:\n\n|\n1\.|Introduction)'),
        ('introduction', r'Introduction[:\s]*([\s\S]*?)(?:\n\n|\n2\.|\nRelated)'),
        ('methodology', r'Methodology[:\s]*([\s\S]*?)(?:\n\n|\n3\.|\nExperiments|Results|Conclusion)'),
        ('experiments', r'Experiments?[:\s]*([\s\S]*?)(?:\n\n|\n4\.|\nResults|Discussion|Conclusion)'),
        ('results', r'Results?[:\s]*([\s\S]*?)(?:\n\n|\n5\.|\nDiscussion|Conclusion)'),
        ('conclusion', r'Conclusion[s]?[:\s]*([\s\S]*?)(?:\n\n|\nReferences|\n\n\n)'),
    ]
    
    for section_name, pattern in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            sections[section_name] = match.group(1).strip()
    
    return sections


def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--pages', type=int, default=None, help='Max pages to extract')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--sections', action='store_true', help='Extract sections')
    
    args = parser.parse_args()
    
    result = extract_text(args.pdf_path, args.pages)
    
    if result.get('success') and args.sections:
        result['sections'] = extract_sections(result['text'])
        # Limit section text
        for key in result['sections']:
            result['sections'][key] = result['sections'][key][:5000]
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get('success'):
            print(f"✅ Extracted {result['text_length']} characters from {result['pdf_path']}")
            if result.get('sections'):
                print(f"\n📑 Sections found: {', '.join(result['sections'].keys())}")
            print("\n" + "=" * 60)
            print(result['text'][:2000])
            print("=" * 60)
        else:
            print(f"❌ Error: {result.get('error')}")
    
    return result


if __name__ == '__main__':
    main()
