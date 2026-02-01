#!/usr/bin/env python3
"""
Tabstack API wrapper for structured data extraction
Requires: TABSTACK_API_KEY environment variable or api_key parameter

API Documentation: https://docs.tabstack.ai/api/tabs-api
Endpoints:
- /extract/json - Extract structured data with JSON schema
- /extract/markdown - Extract clean markdown content
- /generate/json - Generate JSON from queries (research)
- /automate - Browser automation
- /research - Research capabilities
"""

import os
import json
import sys
import requests
from typing import Dict, Any, Optional, Union

TABSTACK_BASE_URL = "https://api.tabstack.ai/v1"

def extract_json(url: str, schema: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract structured data from a URL using Tabstack JSON extraction
    
    Args:
        url: URL to extract data from
        schema: JSON schema defining the structure to extract
        api_key: Tabstack API key (defaults to TABSTACK_API_KEY env var)
    
    Returns:
        Extracted data matching the schema
    
    Example schema for job listing:
    {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "company": {"type": "string"},
            "location": {"type": "string"},
            "description": {"type": "string"},
            "salary": {"type": "string"},
            "apply_url": {"type": "string"}
        }
    }
    """
    api_key = api_key or os.environ.get("TABSTACK_API_KEY")
    if not api_key:
        raise ValueError("Tabstack API key required. Set TABSTACK_API_KEY environment variable.")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url,
        "schema": schema
    }
    
    response = requests.post(f"{TABSTACK_BASE_URL}/extract/json", 
                           headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

def extract_markdown(url: str, api_key: Optional[str] = None) -> str:
    """
    Extract readable markdown content from a URL
    
    Args:
        url: URL to extract content from
        api_key: Tabstack API key (defaults to TABSTACK_API_KEY env var)
    
    Returns:
        Markdown content
    """
    api_key = api_key or os.environ.get("TABSTACK_API_KEY")
    if not api_key:
        raise ValueError("Tabstack API key required. Set TABSTACK_API_KEY environment variable.")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url
    }
    
    response = requests.post(f"{TABSTACK_BASE_URL}/extract/markdown", 
                           headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.text

def test_connection(api_key: Optional[str] = None) -> bool:
    """
    Test Tabstack API connection with a simple request
    
    Args:
        api_key: Tabstack API key (defaults to TABSTACK_API_KEY env var)
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        api_key = api_key or os.environ.get("TABSTACK_API_KEY")
        if not api_key:
            return False
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Try a simple request to check authentication
        response = requests.get(f"{TABSTACK_BASE_URL}/", headers=headers, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python3 tabstack_api.py <command> [args]")
        print("Commands:")
        print("  test                 - Test API connection")
        print("  markdown <url>       - Extract markdown from URL")
        print("  json <url> <schema>  - Extract JSON using schema file")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "test":
        if test_connection():
            print("✅ Tabstack API connection successful")
        else:
            print("❌ Tabstack API connection failed")
            print("Set TABSTACK_API_KEY environment variable")
    
    elif command == "markdown":
        if len(sys.argv) < 3:
            print("Usage: python3 tabstack_api.py markdown <url>")
            sys.exit(1)
        url = sys.argv[2]
        result = extract_markdown(url)
        print(result)
    
    elif command == "json":
        if len(sys.argv) < 4:
            print("Usage: python3 tabstack_api.py json <url> <schema_file.json>")
            sys.exit(1)
        url = sys.argv[2]
        schema_file = sys.argv[3]
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        result = extract_json(url, schema)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)