---
name: servicenow-docs
description: Search and retrieve ServiceNow documentation, release notes, and developer docs (APIs, references, guides). Uses docs.servicenow.com via Zoomin and developer.servicenow.com APIs for developer topics.
metadata:
  clawdbot:
    emoji: "📘"
    read_when:
      - Answering questions about ServiceNow features, APIs, or scripting
      - Looking up release notes or patch information
      - Finding documentation for GlideRecord, GlideAjax, workflows, etc.
      - Researching ServiceNow platform capabilities
---

# ServiceNow Documentation Skill

Search and retrieve documentation from docs.servicenow.com and developer.servicenow.com. This skill provides access to ServiceNow's release notes, platform documentation, and developer-focused API references and guides.

## When to Use

Use this skill when the user asks about:
- ServiceNow API documentation (GlideRecord, GlideAjax, GlideQuery, etc.)
- Release notes, patches, or new features
- Platform configuration or administration
- Scripting patterns or best practices
- Accessibility, UI, or user preferences
- Any ServiceNow product or feature documentation
- Developer topics like openFrameAPI, ScriptLoader, spContextManager, or mobile APIs

## Tools

### servicenow_search
Search the ServiceNow documentation database.

**Args:**
- `query` (string, required) - Search terms (e.g., "GlideRecord", "accessibility preferences", "patch notes")
- `limit` (number, default: 10) - Maximum results to return
- `version` (string, optional) - Filter by version (e.g., "Washington DC", "Zurich", "Yokohama")

**Example:**
```json
{"query": "GlideAjax client script", "limit": 5}
```

### servicenow_get_article
Fetch the full content of a documentation article.

**Args:**
- `url` (string, required) - The article URL (automatically converted from Zoomin to docs.servicenow.com)

**Example:**
```json
{"url": "https://docs.servicenow.com/bundle/zurich-release-notes/page/release-notes/quality/zurich-patch-5.html"}
```

### servicenow_list_versions
List available ServiceNow documentation versions/releases.

**Args:** None required

### servicenow_latest_release
Get release notes for the latest ServiceNow version (automatically detects most recent).

**Args:** None required

### servicenow_dev_suggest
Get autocomplete suggestions from ServiceNow Developer Documentation.

**Args:**
- `term` (string, required) - Partial search term (e.g., "Gli", "openFrame", "spCon")

**Example:**
```json
{"term": "openFrame"}
```

### servicenow_dev_search
Search ServiceNow Developer Documentation (APIs, guides, references). Returns URLs to API reference pages.

**Args:**
- `query` (string, required) - Search terms (e.g., "openFrameAPI", "spContextManager")
- `limit` (number, default: 10) - Maximum results to return

**Example:**
```json
{"query": "ScriptLoader", "limit": 5}
```

### servicenow_dev_guide
Fetch a ServiceNow Developer Guide by path. Works for PDI guides, developer program docs, etc.

**Args:**
- `path` (string, required) - Guide path (e.g., "developer-program/getting-instance-assistance", "pdi-guide/requesting-an-instance")
- `release` (string, default: "zurich") - Release version

**Example:**
```json
{"path": "developer-program/getting-instance-assistance"}
```

## URL Handling

- **Search API:** Uses Zoomin API (servicenow-be-prod.servicenow.com) for searching
- **User-facing URLs:** Automatically converted to docs.servicenow.com for readability
- **Article content:** Fetched via the Zoomin API endpoint with proper headers
- **Developer Docs Search:** developer.servicenow.com GraphQL + databroker search APIs
- **Developer Docs Content:** fetched directly from developer.servicenow.com pages

## Example Usage

User: "What are the accessibility preferences in ServiceNow?"
→ Use servicenow_search to find accessibility documentation
→ Use servicenow_get_article to fetch the full content
→ Summarize the preferences for the user

User: "Tell me about the latest ServiceNow patch"
→ Use servicenow_latest_release to get the most recent release notes
→ Fetch and summarize the patch details

User: "How do I use openFrameAPI?"
→ Use servicenow_dev_suggest or servicenow_dev_search to find the best developer docs topic
→ Returns URLs to API reference pages (requires browser access for full content)

User: "Show me the PDI guide for getting an instance"
→ Use servicenow_dev_guide with path "pdi-guide/requesting-an-instance"
→ Returns full guide content

## APIs Used

- **Zoomin Search API:** `https://servicenow-be-prod.servicenow.com/search`
- **Content Source:** docs.servicenow.com (accessed via Zoomin API)
- **Developer Search API:** `https://developer.servicenow.com/api/now/uxf/databroker/exec`
- **Developer Suggest API:** `https://developer.servicenow.com/api/now/graphql`
- **Developer Guides API:** `https://developer.servicenow.com/api/snc/v1/guides` (public, no auth needed)

## Limitations

- **API Reference Content:** The developer.servicenow.com API reference pages require browser access. `servicenow_dev_search` returns URLs but cannot fetch the full API documentation content.
- **Guide Content:** Guides are fully available via `servicenow_dev_guide` without authentication.
