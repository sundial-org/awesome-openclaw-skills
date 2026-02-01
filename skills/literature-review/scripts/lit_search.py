#!/usr/bin/env python3
import sys
import json
import requests
import argparse
import os
import time
import xml.etree.ElementTree as ET

S2_BASE_URL = "https://api.semanticscholar.org/graph/v1"
OA_BASE_URL = "https://api.openalex.org"
CR_BASE_URL = "https://api.crossref.org/works"
PM_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Timeout for all requests (seconds)
REQUEST_TIMEOUT = 30

# Env vars - NO hardcoded emails
S2_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
OA_API_KEY = os.getenv("OPENALEX_API_KEY")
USER_EMAIL = os.getenv("USER_EMAIL", os.getenv("CLAWDBOT_EMAIL", "anonymous@example.org"))

def get_s2_headers():
    headers = {}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY
    return headers

def get_oa_params(params):
    if OA_API_KEY:
        params["api_key"] = OA_API_KEY
    return params

def get_headers():
    return {"User-Agent": f"Clawdbot/1.0 (mailto:{USER_EMAIL})"}

def safe_get_year(item, *keys):
    """Safely extract year from nested dict structures, handling None/missing fields."""
    for key in keys:
        try:
            val = item.get(key)
            if val is None:
                continue
            if isinstance(val, int):
                return val
            if isinstance(val, str):
                # Try to extract year from string like "2023" or "2023-01-15"
                year_str = val.split("-")[0].split(" ")[0]
                if year_str.isdigit() and len(year_str) == 4:
                    return int(year_str)
            if isinstance(val, dict):
                # Handle Crossref date-parts format
                date_parts = val.get("date-parts")
                if date_parts and isinstance(date_parts, list) and len(date_parts) > 0:
                    first_part = date_parts[0]
                    if isinstance(first_part, list) and len(first_part) > 0 and first_part[0]:
                        return first_part[0]
        except (TypeError, KeyError, IndexError, AttributeError):
            continue
    return None

def search_s2(query, limit=10):
    fields = "title,year,abstract,authors,citationCount,venue,externalIds"
    url = f"{S2_BASE_URL}/paper/search"
    params = {"query": query, "limit": limit, "fields": fields}
    try:
        response = requests.get(url, params=params, headers=get_s2_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}: {response.text[:200]}", "data": []}
        data = response.json()
        # Normalize output to include doi field for deduplication
        results = []
        for paper in data.get("data", []):
            ext_ids = paper.get("externalIds") or {}
            results.append({
                "id": paper.get("paperId"),
                "doi": ext_ids.get("DOI"),
                "title": paper.get("title"),
                "year": paper.get("year"),
                "abstract": paper.get("abstract"),
                "authors": [a.get("name") for a in (paper.get("authors") or [])],
                "citationCount": paper.get("citationCount"),
                "venue": paper.get("venue"),
                "source": "semantic_scholar"
            })
        return {"total": data.get("total"), "data": results}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out", "data": []}
    except Exception as e:
        return {"error": str(e), "data": []}

def search_oa(query, limit=10):
    url = f"{OA_BASE_URL}/works"
    params = {
        "search": query,
        "per_page": limit,
        "select": "id,doi,title,display_name,publication_year,cited_by_count,authorships,abstract_inverted_index,primary_location"
    }
    try:
        response = requests.get(url, params=get_oa_params(params), headers=get_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}: {response.text[:200]}", "data": []}
        data = response.json()
        results = []
        for work in data.get("results", []):
            abstract = ""
            index = work.get("abstract_inverted_index")
            if index:
                words = {}
                for word, positions in index.items():
                    for pos in positions: words[pos] = word
                abstract = " ".join([words[p] for p in sorted(words.keys())])
            
            # Safe venue extraction
            venue = None
            primary_loc = work.get("primary_location")
            if primary_loc and isinstance(primary_loc, dict):
                source = primary_loc.get("source")
                if source and isinstance(source, dict):
                    venue = source.get("display_name")
            
            results.append({
                "id": work.get("id"),
                "doi": work.get("doi"),
                "title": work.get("title") or work.get("display_name"),
                "year": work.get("publication_year"),
                "citationCount": work.get("cited_by_count"),
                "authors": [a.get("author", {}).get("display_name") for a in work.get("authorships", [])],
                "abstract": abstract,
                "venue": venue,
                "source": "openalex"
            })
        return {"total": data.get("meta", {}).get("count"), "data": results}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out", "data": []}
    except Exception as e:
        return {"error": str(e), "data": []}

def search_cr(query, limit=10):
    params = {"query": query, "rows": limit}
    try:
        response = requests.get(CR_BASE_URL, params=params, headers=get_headers(), timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}: {response.text[:200]}", "data": []}
        data = response.json()
        items = data.get("message", {}).get("items", [])
        results = []
        for item in items:
            # Safe year extraction using helper
            year = safe_get_year(item, "published-print", "published-online", "created")
            
            results.append({
                "id": item.get("DOI"),
                "doi": item.get("DOI"),
                "title": " ".join(item.get("title", [])) if item.get("title") else None,
                "year": year,
                "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get("author", [])],
                "venue": " ".join(item.get("container-title", [])) if item.get("container-title") else None,
                "source": "crossref"
            })
        return {"total": data.get("message", {}).get("total-results"), "data": results}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out", "data": []}
    except Exception as e:
        return {"error": str(e), "data": []}

def search_pm(query, limit=10):
    """Search PubMed using esearch + efetch for full abstracts and DOIs."""
    try:
        # Step 1: esearch to get PMIDs
        search_url = f"{PM_BASE_URL}/esearch.fcgi"
        search_params = {"db": "pubmed", "term": query, "retmax": limit, "retmode": "json"}
        search_res = requests.get(search_url, params=search_params, timeout=REQUEST_TIMEOUT)
        if search_res.status_code != 200:
            return {"error": f"esearch HTTP {search_res.status_code}", "data": []}
        ids = search_res.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return {"total": 0, "data": []}
        
        # Step 2: efetch to get full records with abstracts
        fetch_url = f"{PM_BASE_URL}/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml",
            "rettype": "abstract"
        }
        fetch_res = requests.get(fetch_url, params=fetch_params, timeout=REQUEST_TIMEOUT)
        if fetch_res.status_code != 200:
            return {"error": f"efetch HTTP {fetch_res.status_code}", "data": []}
        
        # Parse XML
        results = []
        root = ET.fromstring(fetch_res.content)
        
        for article in root.findall(".//PubmedArticle"):
            pmid = None
            pmid_elem = article.find(".//PMID")
            if pmid_elem is not None:
                pmid = pmid_elem.text
            
            # Title
            title = None
            title_elem = article.find(".//ArticleTitle")
            if title_elem is not None:
                title = "".join(title_elem.itertext())
            
            # Abstract - combine all AbstractText elements
            abstract_parts = []
            for abs_elem in article.findall(".//AbstractText"):
                label = abs_elem.get("Label", "")
                text = "".join(abs_elem.itertext())
                if label:
                    abstract_parts.append(f"{label}: {text}")
                else:
                    abstract_parts.append(text)
            abstract = " ".join(abstract_parts) if abstract_parts else None
            
            # Year
            year = None
            pub_date = article.find(".//PubDate/Year")
            if pub_date is not None and pub_date.text:
                try:
                    year = int(pub_date.text)
                except ValueError:
                    pass
            if not year:
                # Try MedlineDate
                medline_date = article.find(".//PubDate/MedlineDate")
                if medline_date is not None and medline_date.text:
                    parts = medline_date.text.split()
                    if parts and parts[0].isdigit():
                        year = int(parts[0])
            
            # Authors
            authors = []
            for author in article.findall(".//Author"):
                last = author.find("LastName")
                first = author.find("ForeName")
                if last is not None:
                    name = last.text or ""
                    if first is not None and first.text:
                        name = f"{first.text} {name}"
                    authors.append(name.strip())
            
            # Journal
            venue = None
            journal = article.find(".//Journal/Title")
            if journal is not None:
                venue = journal.text
            
            # DOI
            doi = None
            for aid in article.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text
                    break
            # Also check ELocationID
            if not doi:
                for eloc in article.findall(".//ELocationID"):
                    if eloc.get("EIdType") == "doi":
                        doi = eloc.text
                        break
            
            results.append({
                "id": pmid,
                "pmid": pmid,
                "doi": doi,
                "title": title,
                "year": year,
                "authors": authors,
                "abstract": abstract,
                "venue": venue,
                "source": "pubmed"
            })
        
        return {"total": len(results), "data": results}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out", "data": []}
    except ET.ParseError as e:
        return {"error": f"XML parse error: {e}", "data": []}
    except Exception as e:
        return {"error": str(e), "data": []}

def deduplicate_by_doi(all_results):
    """Deduplicate results by DOI, keeping the first occurrence (with most metadata)."""
    seen_dois = set()
    unique = []
    no_doi = []
    
    for result in all_results:
        doi = result.get("doi")
        if doi:
            # Normalize DOI (lowercase, strip https://doi.org/ prefix)
            doi_normalized = doi.lower().replace("https://doi.org/", "").replace("http://doi.org/", "")
            if doi_normalized not in seen_dois:
                seen_dois.add(doi_normalized)
                unique.append(result)
        else:
            # Keep results without DOI (can't dedupe)
            no_doi.append(result)
    
    return unique + no_doi

def main():
    parser = argparse.ArgumentParser(description="Multi-Source Academic Search Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Search
    search_parser = subparsers.add_parser("search", help="Search for papers")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results per source")
    search_parser.add_argument("--source", choices=["s2", "oa", "cr", "pm", "both", "all"], default="oa", 
                               help="Source: s2 (Semantic Scholar), oa (OpenAlex), cr (Crossref), pm (PubMed)")
    search_parser.add_argument("--dedupe", action="store_true", help="Deduplicate results by DOI (auto-enabled for multi-source)")

    # Details (S2)
    details_parser = subparsers.add_parser("details", help="Get paper details (S2)")
    details_parser.add_argument("id", help="Paper ID (DOI, S2ID)")

    args = parser.parse_known_args()[0]

    if args.command == "search":
        output = {}
        if args.source in ["s2", "both", "all"]: output["semantic_scholar"] = search_s2(args.query, args.limit)
        if args.source in ["oa", "both", "all"]: output["openalex"] = search_oa(args.query, args.limit)
        if args.source in ["cr", "all"]: output["crossref"] = search_cr(args.query, args.limit)
        if args.source in ["pm", "all"]: output["pubmed"] = search_pm(args.query, args.limit)
        
        # Flatten if only one source
        if len(output) == 1:
            print(json.dumps(list(output.values())[0], indent=2, ensure_ascii=False))
        else:
            # Multi-source: deduplicate by default (or if --dedupe)
            if args.dedupe or args.source in ["both", "all"]:
                all_data = []
                for src_name, src_result in output.items():
                    all_data.extend(src_result.get("data", []))
                deduped = deduplicate_by_doi(all_data)
                combined = {
                    "total_before_dedupe": sum(len(r.get("data", [])) for r in output.values()),
                    "total_after_dedupe": len(deduped),
                    "data": deduped
                }
                print(json.dumps(combined, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(output, indent=2, ensure_ascii=False))

    elif args.command == "details":
        try:
            url = f"{S2_BASE_URL}/paper/{args.id}"
            params = {"fields": "title,year,abstract,authors,citationCount,venue,externalIds,tldr,referenceCount"}
            response = requests.get(url, params=params, headers=get_s2_headers(), timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                print(json.dumps({"error": f"HTTP {response.status_code}: {response.text[:500]}"}, indent=2))
                sys.exit(1)
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except requests.exceptions.Timeout:
            print(json.dumps({"error": "Request timed out"}))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
