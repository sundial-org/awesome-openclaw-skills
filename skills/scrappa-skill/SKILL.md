---
name: Scrappa MCP
description: Access Scrappa's MCP server for Google, YouTube, Amazon, LinkedIn, Trustpilot, flights, hotels, and more via Model Context Protocol
---

# Scrappa MCP Skill

Access 80+ tools for searching Google, YouTube, Amazon, LinkedIn, Trustpilot, business reviews, flights, hotels, real estate, and more via the Scrappa Model Context Protocol (MCP) server.

## Setup

### 1. Get Your Scrappa API Key

Sign up for a free account at [scrappa.co](https://scrappa.co/dashboard/register) and get your API key from the dashboard.

### 2. Configure in Clawdbot

Add Scrappa to your mcporter configuration:

```bash
mcporter config add scrappa --url "https://scrappa.co/mcp" --headers "X-API-KEY=YOUR_API_KEY"
```

Or manually edit `~/clawd/config/mcporter.json`:

```json
{
  "mcpServers": {
    "scrappa": {
      "baseUrl": "https://scrappa.co/mcp",
      "headers": {
        "X-API-KEY": "your_api_key_here"
      }
    }
  }
}
```

### 3. Restart Clawdbot

```bash
clawdbot gateway restart
```

## All Available Tools (80+)

### Google Search & Translation

| Tool | Description |
|------|-------------|
| `search` | Scrape Google search results with advanced filters |
| `google-search-light` | Lightweight Google web search |
| `google-search-autocomplete` | Google search suggestions |
| `google-translate-api` | Translate text between languages |
| `google-images` | Search Google Images |
| `google-videos` | Search Google Videos |
| `google-news` | Search Google News articles |
| `google-jobs` | Search jobs indexed on Google |
| `brave-search` | Privacy-focused Brave web search |

### YouTube

| Tool | Description |
|------|-------------|
| `youtube-external-search` | Search videos |
| `youtube-external-video` | Get full video details |
| `youtube-external-info` | Basic video metadata |
| `youtube-external-channel` | Channel profile and stats |
| `youtube-external-comments` | Fetch video comments |
| `youtube-external-related` | Get related videos |
| `youtube-external-chapters` | Extract video chapters |
| `youtube-external-trending` | Trending videos by category |
| `youtube-external-suggestions` | Search autocomplete suggestions |
| `youtube-external-channel-videos` | Channel uploads |
| `youtube-external-channel-playlists` | Channel playlists |
| `youtube-external-channel-community` | Channel community posts |
| `youtube-external-playlist` | Get playlist videos |
| `youtube-external-health` | Check API status |
| `youtube-external-proxies` | YouTube Proxies API |
| `youtube-external-locales` | YouTube Locales API |

### Amazon

| Tool | Description |
|------|-------------|
| `amazon-search` | Search products across 22 marketplaces |
| `amazon-product` | Get detailed product by ASIN |

### LinkedIn

| Tool | Description |
|------|-------------|
| `linkedin-profile` | Get LinkedIn profile data |
| `linkedin-company` | Get company page data |
| `linkedin-post` | Get post details |
| `linkedin-search` | Search LinkedIn profiles |

### Trustpilot

| Tool | Description |
|------|-------------|
| `trustpilot-categories` | List business categories |
| `trustpilot-businesses` | Search businesses |
| `trustpilot-countries` | List supported countries |
| `trustpilot-company-search` | Search for a company |
| `trustpilot-company-details` | Get company profile |
| `trustpilot-company-reviews` | Fetch company reviews |

### Kununu (German Reviews)

| Tool | Description |
|------|-------------|
| `kununu-search` | Search companies on Kununu |
| `kununu-reviews` | Fetch company reviews |
| `kununu-profiles` | Get company profile data |
| `kununu-industries` | List available industries |
| `kununu-company-details` | Full company details |

### TrustedShops (European Reviews)

| Tool | Description |
|------|-------------|
| `trustedshops-markets` | Get all available markets |
| `trustedshops-search` | Search for shops |
| `trustedshops-reviews` | Get reviews for a shop |
| `trustedshops-shop` | Get detailed shop profile |

### Google Maps & Places

| Tool | Description |
|------|-------------|
| `simple-search` | Quick search for places by query |
| `advanced-search` | Search with filters and pagination |
| `autocomplete` | Get place suggestions as you type |
| `google-reviews` | Fetch Google place reviews |
| `google-single-review` | Get single review details |
| `google-business-details` | Full business info from Maps |
| `google-maps-photos` | Download photos from a place |
| `google-maps-directions` | Get directions between locations |

### Google Flights

| Tool | Description |
|------|-------------|
| `google-flights-one-way` | Search one-way flights |
| `google-flights-round-trip` | Search round-trip flights |
| `google-flights-date-range` | Find cheapest dates to fly |
| `google-flights-airlines` | Get supported airlines (free) |
| `google-flights-airports` | Get supported airports (free) |
| `google-flights-booking-details` | Get flight booking information |

### Google Hotels

| Tool | Description |
|------|-------------|
| `google-hotels-search` | Search hotels by location |
| `google-hotels-autocomplete` | Location autocomplete for hotels |

### ImmobilienScout24 (German Real Estate)

| Tool | Description |
|------|-------------|
| `immobilienscout24-search` | Search property listings |
| `immobilienscout24-property` | Get property details |
| `immobilienscout24-locations` | Location autocomplete |
| `immobilienscout24-price-insights` | Average price per m² |

### Vinted (Marketplace)

| Tool | Description |
|------|-------------|
| `vinted-search` | Search items on Vinted |
| `vinted-filters` | Get available filters |
| `vinted-suggestions` | Search autocomplete |
| `vinted-item-details` | Get item information |
| `vinted-item-shipping` | Get shipping details |
| `vinted-similar-items` | Get similar items |
| `vinted-user-profile` | Get user profile |
| `vinted-user-items` | Get items listed by user |
| `vinted-categories` | Get all catalog categories |

### Indeed (Jobs)

| Tool | Description |
|------|-------------|
| `indeed-jobs` | Search for jobs on Indeed |

## Example Usage

### Google Search
```
Search for "best coffee shops in New York"
```

### YouTube
```
Get details for video: dQw4w9WgXcQ
Search for "latest AI news 2024"
```

### Translation
```
Translate "Hello world" from English to Spanish
Translate "Good morning" from English to German
```

### Amazon
```
Search for "wireless headphones" on Amazon US
Get product details for B09V3KXJPB
```

### LinkedIn
```
Get profile: https://www.linkedin.com/in/someone
Search for "software engineer" in San Francisco
```

### Trustpilot
```
Search for company "bestbuy"
Get reviews for amazon.com
```

### Google Maps
```
Search for "coffee shops" near "Times Square"
Get directions from "Central Park" to "Brooklyn Bridge"
```

### Flights
```
Search one-way flights from JFK to LHR on 2025-03-15
Find cheapest dates to fly from NYC to Paris in April
```

### Hotels
```
Search hotels in Paris for check-in 2025-04-01, check-out 2025-04-05
```

### Real Estate (Germany)
```
Search apartments for rent in Berlin, max €1500
Get property details for listing ID 123456
```

### Vinted
```
Search for "Nike shoes" on Vinted France
Get item details for item ID 12345
```

## Notes

- API key required from [scrappa.co](https://scrappa.co)
- Rate limits apply based on your Scrappa plan
- Some tools require specific marketplace/country parameters
- Google search results may have caching delays
- Flight/hotel searches support various filters and sorting options

## Links

- [Scrappa Dashboard](https://scrappa.co/dashboard)
- [Scrappa Documentation](https://scrappa.co/docs)
- [MCP Integration Guide](https://scrappa.co/docs/mcp-integration)
- [GitHub Repo](https://github.com/Scrappa-co/scrappa-skill)
