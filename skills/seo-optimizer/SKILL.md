---
name: seo-optimizer
description: This skill should be used when analyzing HTML/CSS websites for SEO optimization, fixing SEO issues, generating SEO reports, or implementing SEO best practices. Use when the user requests SEO audits, optimization, meta tag improvements, schema markup implementation, sitemap generation, or general search engine optimization tasks.
---

# SEO Optimizer

## Overview

This skill provides comprehensive SEO optimization capabilities for HTML/CSS websites. It analyzes websites for SEO issues, implements best practices, and generates optimization reports covering all critical SEO aspects including meta tags, heading structure, image optimization, schema markup, mobile optimization, and technical SEO.

## When to Use This Skill

Use this skill when the user requests:
- "Analyze my website for SEO issues"
- "Optimize this page for SEO"
- "Generate an SEO audit report"
- "Fix SEO problems on my website"
- "Add proper meta tags to my pages"
- "Implement schema markup"
- "Generate a sitemap"
- "Improve my site's search engine rankings"
- Any task related to search engine optimization for HTML/CSS websites

## Workflow

### 1. Initial SEO Analysis

Start with comprehensive analysis using the SEO analyzer script:

```bash
python scripts/seo_analyzer.py <directory_or_file>
```

This script analyzes HTML files and generates a detailed report covering:
- Title tags (length, presence, uniqueness)
- Meta descriptions (length, presence)
- Heading structure (H1-H6 hierarchy)
- Image alt attributes
- Open Graph tags
- Twitter Card tags
- Schema.org markup
- HTML lang attribute
- Viewport and charset meta tags
- Canonical URLs
- Content length

**Output Options**:
- Default: Human-readable text report with issues, warnings, and good practices
- `--json`: Machine-readable JSON format for programmatic processing

**Example Usage**:
```bash
# Analyze single file
python scripts/seo_analyzer.py index.html

# Analyze entire directory
python scripts/seo_analyzer.py ./public

# Get JSON output
python scripts/seo_analyzer.py ./public --json
```

### 2. Review Analysis Results

The analyzer categorizes findings into three levels:

**Critical Issues (🔴)** - Fix immediately:
- Missing title tags
- Missing meta descriptions
- Missing H1 headings
- Images without alt attributes
- Missing HTML lang attribute

**Warnings (⚠️)** - Fix soon for optimal SEO:
- Suboptimal title/description lengths
- Multiple H1 tags
- Missing Open Graph or Twitter Card tags
- Missing viewport meta tag
- Missing schema markup
- Heading hierarchy issues

**Good Practices (✅)** - Already optimized:
- Properly formatted elements
- Correct lengths
- Present required tags

### 3. Prioritize and Fix Issues

Address issues in priority order:

#### Priority 1: Critical Issues

**Missing or Poor Title Tags**:
```html
<!-- Add unique, descriptive title to <head> -->
<title>Primary Keyword - Secondary Keyword | Brand Name</title>
```
- Keep 50-60 characters
- Include target keywords at the beginning
- Make unique for each page

**Missing Meta Descriptions**:
```html
<!-- Add compelling description to <head> -->
<meta name="description" content="Clear, concise description that includes target keywords and encourages clicks. 150-160 characters.">
```

**Missing H1 or Multiple H1s**:
- Ensure exactly ONE H1 per page
- H1 should describe the main topic
- Should match or relate to title tag

**Images Without Alt Text**:
```html
<!-- Add descriptive alt text to all images -->
<img src="image.jpg" alt="Descriptive text explaining image content">
```

**Missing HTML Lang Attribute**:
```html
<!-- Add to opening <html> tag -->
<html lang="en">
```

#### Priority 2: Important Optimizations

**Viewport Meta Tag** (critical for mobile SEO):
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

**Charset Declaration**:
```html
<meta charset="UTF-8">
```

**Open Graph Tags** (for social media sharing):
```html
<meta property="og:title" content="Your Page Title">
<meta property="og:description" content="Your page description">
<meta property="og:image" content="https://example.com/image.jpg">
<meta property="og:url" content="https://example.com/page-url">
<meta property="og:type" content="website">
```

**Twitter Card Tags**:
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Your Page Title">
<meta name="twitter:description" content="Your page description">
<meta name="twitter:image" content="https://example.com/image.jpg">
```

**Canonical URL**:
```html
<link rel="canonical" href="https://example.com/preferred-url">
```

#### Priority 3: Advanced Optimization

**Schema Markup** - Refer to `references/schema_markup_guide.md` for detailed implementation. Common types:
- Organization (homepage)
- Article/BlogPosting (blog posts)
- LocalBusiness (local businesses)
- Breadcrumb (navigation)
- FAQ (FAQ pages)
- Product (e-commerce)

Example implementation:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "datePublished": "2024-01-15",
  "image": "https://example.com/image.jpg"
}
</script>
```

### 4. Generate or Update Sitemap

After fixing issues, generate an XML sitemap:

```bash
python scripts/generate_sitemap.py <directory> <base_url> [output_file]
```

**Example**:
```bash
# Generate sitemap for website
python scripts/generate_sitemap.py ./public https://example.com

# Specify output location
python scripts/generate_sitemap.py ./public https://example.com ./public/sitemap.xml
```

The script:
- Automatically finds all HTML files
- Generates proper URLs
- Includes lastmod dates
- Estimates priority and changefreq values
- Creates properly formatted XML sitemap

**After generation**:
1. Upload sitemap.xml to website root
2. Add reference to robots.txt
3. Submit to Google Search Console and Bing Webmaster Tools

### 5. Update robots.txt

Use the template from `assets/robots.txt` and customize:

```
User-agent: *
Allow: /

# Block sensitive directories
Disallow: /admin/
Disallow: /private/

# Reference your sitemap
Sitemap: https://yourdomain.com/sitemap.xml
```

Place robots.txt in website root directory.

### 6. Verify and Test

After implementing fixes:

**Local Testing**:
1. Run the SEO analyzer again to verify fixes
2. Check that all critical issues are resolved
3. Ensure no new issues were introduced

**Online Testing**:
1. Deploy changes to production
2. Test with Google Rich Results Test: https://search.google.com/test/rich-results
3. Validate schema markup: https://validator.schema.org/
4. Check mobile-friendliness: https://search.google.com/test/mobile-friendly
5. Monitor in Google Search Console

### 7. Ongoing Optimization

**Regular maintenance**:
- Update sitemap when adding new pages
- Keep meta descriptions fresh and compelling
- Ensure new images have alt text
- Add schema markup to new content types
- Monitor Search Console for issues
- Update content regularly

## Common Optimization Patterns

### Pattern 1: New Website Setup

For a brand new HTML/CSS website:

1. Run initial analysis: `python scripts/seo_analyzer.py ./public`
2. Add essential meta tags to all pages (title, description, viewport)
3. Ensure proper heading structure (one H1 per page)
4. Add alt text to all images
5. Implement organization schema on homepage
6. Generate sitemap: `python scripts/generate_sitemap.py ./public https://yourdomain.com`
7. Create robots.txt from template
8. Deploy and submit sitemap to search engines

### Pattern 2: Existing Website Audit

For an existing website needing optimization:

1. Run comprehensive analysis: `python scripts/seo_analyzer.py ./public`
2. Identify and prioritize issues (critical first)
3. Fix critical issues across all pages
4. Add missing Open Graph and Twitter Card tags
5. Implement schema markup for appropriate pages
6. Regenerate sitemap with updates
7. Verify fixes with analyzer
8. Deploy and monitor

### Pattern 3: Single Page Optimization

For optimizing a specific page:

1. Analyze specific file: `python scripts/seo_analyzer.py page.html`
2. Fix identified issues
3. Optimize title and meta description for target keywords
4. Ensure proper heading hierarchy
5. Add appropriate schema markup for page type
6. Verify with analyzer
7. Update sitemap if new page

### Pattern 4: Blog Post Optimization

For blog posts and articles:

1. Ensure unique title (50-60 chars) with target keyword
2. Write compelling meta description (150-160 chars)
3. Use single H1 for article title
4. Implement proper H2/H3 hierarchy for sections
5. Add alt text to all images
6. Implement Article or BlogPosting schema (see `references/schema_markup_guide.md`)
7. Add Open Graph and Twitter Card tags for social sharing
8. Include author information
9. Add breadcrumb schema for navigation

## Reference Materials

### Detailed Guides

**`references/seo_checklist.md`**:
Comprehensive checklist covering all SEO aspects:
- Title tags and meta descriptions guidelines
- Heading structure best practices
- Image optimization techniques
- URL structure recommendations
- Internal linking strategies
- Page speed optimization
- Mobile optimization requirements
- Semantic HTML usage
- Complete technical SEO checklist

Reference this for detailed specifications on any SEO element.

**`references/schema_markup_guide.md`**:
Complete guide for implementing schema.org structured data:
- JSON-LD implementation (recommended format)
- 10+ common schema types with examples
- Organization, LocalBusiness, Article, BlogPosting, FAQ, Product, etc.
- Required properties for each type
- Best practices and common mistakes
- Validation tools and resources

Reference this when implementing schema markup for any content type.

### Scripts

**`scripts/seo_analyzer.py`**:
Python script for automated SEO analysis. Analyzes HTML files for common issues and generates detailed reports. Can output text or JSON format. Deterministic and reliable for repeated analysis.

**`scripts/generate_sitemap.py`**:
Python script for generating XML sitemaps. Automatically crawls directories, estimates priorities and change frequencies, and generates properly formatted sitemaps ready for submission to search engines.

### Assets

**`assets/robots.txt`**:
Template robots.txt file with common configurations and comments. Customize for specific needs and place in website root directory.

## Key Principles

1. **User-First**: Optimize for users first, search engines second. Good user experience leads to better SEO.

2. **Unique Content**: Every page should have unique title, description, and H1. Duplicate content hurts SEO.

3. **Mobile-First**: Google uses mobile-first indexing. Always include viewport meta tag and ensure mobile responsiveness.

4. **Accessibility = SEO**: Accessible websites (alt text, semantic HTML, proper headings) rank better.

5. **Quality Over Quantity**: Substantial, valuable content ranks better than thin content. Aim for comprehensive pages.

6. **Technical Foundation**: Fix critical technical issues (missing tags, broken structure) before advanced optimization.

7. **Structured Data**: Schema markup helps search engines understand content and can lead to rich results.

8. **Regular Updates**: SEO is ongoing. Keep content fresh, monitor analytics, and adapt to algorithm changes.

9. **Natural Language**: Write for humans using natural language. Avoid keyword stuffing.

10. **Validation**: Always validate changes with testing tools before deploying to production.

## Tips for Maximum Impact

- **Start with critical issues**: Fix missing title tags and meta descriptions first - these have the biggest impact
- **Be consistent**: Apply optimizations across all pages, not just homepage
- **Use semantic HTML**: Use proper HTML5 semantic tags (`<header>`, `<nav>`, `<main>`, `<article>`, `<aside>`, `<footer>`)
- **Optimize images**: Compress images, use descriptive filenames, always include alt text
- **Internal linking**: Link to related pages with descriptive anchor text
- **Page speed matters**: Fast-loading pages rank better
- **Test on mobile**: Majority of searches are mobile - ensure excellent mobile experience
- **Monitor Search Console**: Use Google Search Console to track performance and identify issues
- **Update regularly**: Fresh content signals active, valuable websites

## Quick Reference Commands

```bash
# Analyze single file
python scripts/seo_analyzer.py index.html

# Analyze entire website
python scripts/seo_analyzer.py ./public

# Generate sitemap
python scripts/generate_sitemap.py ./public https://example.com

# Get JSON analysis output
python scripts/seo_analyzer.py ./public --json
```
