# Schema Markup Guide

Complete guide for implementing schema.org structured data on HTML websites.

## What is Schema Markup?

Schema markup (structured data) is code that helps search engines understand your content better and display rich results in search. It uses vocabulary from schema.org to provide context about your page content.

## Why Use Schema Markup?

1. **Rich Results**: Enhanced search listings with images, ratings, prices, etc.
2. **Better CTR**: Rich results stand out and get more clicks
3. **Voice Search**: Helps voice assistants understand and use your content
4. **Knowledge Graph**: Can appear in Google's Knowledge Graph
5. **Competitive Advantage**: Many sites don't use schema markup

## Implementation Formats

Schema markup can be implemented in three formats. **JSON-LD is recommended** by Google.

### 1. JSON-LD (Recommended)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Your Article Title"
}
</script>
```

### 2. Microdata
```html
<div itemscope itemtype="https://schema.org/Article">
  <h1 itemprop="headline">Your Article Title</h1>
</div>
```

### 3. RDFa
```html
<div vocab="https://schema.org/" typeof="Article">
  <h1 property="headline">Your Article Title</h1>
</div>
```

## Common Schema Types for HTML Websites

### 1. Organization Schema

Use on your homepage or about page to define your organization.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Your Company Name",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "description": "Brief description of your organization",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-555-555-5555",
    "contactType": "Customer Service",
    "areaServed": "US",
    "availableLanguage": "English"
  },
  "sameAs": [
    "https://facebook.com/yourcompany",
    "https://twitter.com/yourcompany",
    "https://linkedin.com/company/yourcompany"
  ]
}
</script>
```

### 2. LocalBusiness Schema

For businesses with physical locations.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Your Business Name",
  "image": "https://example.com/business-photo.jpg",
  "@id": "https://example.com",
  "url": "https://example.com",
  "telephone": "+1-555-555-5555",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "City Name",
    "addressRegion": "State",
    "postalCode": "12345",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 40.7589,
    "longitude": -73.9851
  },
  "openingHoursSpecification": {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": [
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday"
    ],
    "opens": "09:00",
    "closes": "17:00"
  }
}
</script>
```

### 3. Article Schema

For blog posts, news articles, and editorial content.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title - Keep Under 110 Characters",
  "image": [
    "https://example.com/article-image.jpg"
  ],
  "datePublished": "2024-01-15T08:00:00+00:00",
  "dateModified": "2024-01-15T09:00:00+00:00",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "url": "https://example.com/author/author-name"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Publisher Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png",
      "width": 600,
      "height": 60
    }
  },
  "description": "A brief description of the article content",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/article-url"
  }
}
</script>
```

**Note**: For Article schema, images must be at least 1200px wide, and logo must be 600px wide by 60px tall.

### 4. BlogPosting Schema

Similar to Article but specifically for blog posts.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Blog Post Title",
  "image": "https://example.com/blog-image.jpg",
  "datePublished": "2024-01-15T08:00:00+00:00",
  "dateModified": "2024-01-15T09:00:00+00:00",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Blog Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "description": "Brief description of the blog post",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/blog/post-url"
  }
}
</script>
```

### 5. Breadcrumb Schema

For breadcrumb navigation - helps show site hierarchy in search results.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Blog",
      "item": "https://example.com/blog"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Article Title",
      "item": "https://example.com/blog/article"
    }
  ]
}
</script>
```

### 6. FAQ Schema

For pages with frequently asked questions - can show in FAQ rich results.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is schema markup?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Schema markup is structured data that helps search engines understand your content better. It can lead to rich results in search."
      }
    },
    {
      "@type": "Question",
      "name": "Why should I use schema markup?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Schema markup can help your pages appear with rich results in search, which can improve click-through rates and visibility."
      }
    }
  ]
}
</script>
```

### 7. WebSite Schema

For your homepage - enables sitelinks search box in Google.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Your Website Name",
  "url": "https://example.com",
  "description": "Brief description of your website",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://example.com/search?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
</script>
```

### 8. Product Schema

For product pages - can show price, availability, and ratings in search.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "image": "https://example.com/product-image.jpg",
  "description": "Product description",
  "brand": {
    "@type": "Brand",
    "name": "Brand Name"
  },
  "sku": "SKU123",
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product",
    "priceCurrency": "USD",
    "price": "29.99",
    "priceValidUntil": "2024-12-31",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "89"
  }
}
</script>
```

### 9. Review Schema

For review pages or product reviews.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Review",
  "itemReviewed": {
    "@type": "Product",
    "name": "Product Name",
    "image": "https://example.com/product.jpg"
  },
  "author": {
    "@type": "Person",
    "name": "Reviewer Name"
  },
  "reviewRating": {
    "@type": "Rating",
    "ratingValue": "4",
    "bestRating": "5",
    "worstRating": "1"
  },
  "reviewBody": "This is the review text content.",
  "datePublished": "2024-01-15"
}
</script>
```

### 10. Person Schema

For author pages or about pages.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "John Doe",
  "url": "https://example.com/about",
  "image": "https://example.com/john-doe.jpg",
  "jobTitle": "CEO",
  "worksFor": {
    "@type": "Organization",
    "name": "Company Name"
  },
  "sameAs": [
    "https://twitter.com/johndoe",
    "https://linkedin.com/in/johndoe"
  ],
  "email": "john@example.com"
}
</script>
```

## Best Practices

### 1. Use JSON-LD Format
- Easiest to implement and maintain
- Recommended by Google
- Doesn't interfere with existing HTML

### 2. Be Accurate and Complete
- Only markup content that's visible on the page
- Don't add false or misleading information
- Include all required properties for each type

### 3. Validate Your Markup
Use these tools to test:
- Google's Rich Results Test: https://search.google.com/test/rich-results
- Schema.org Validator: https://validator.schema.org/
- Google Search Console

### 4. Multiple Schemas on One Page
You can include multiple schemas:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "name": "Company Name",
      "url": "https://example.com"
    },
    {
      "@type": "Article",
      "headline": "Article Title",
      "author": {
        "@type": "Person",
        "name": "Author Name"
      }
    }
  ]
}
</script>
```

### 5. Common Required Properties

Different schema types require different properties. Here are the most common:

**Article/BlogPosting**:
- headline (required)
- image (required)
- datePublished (required)
- author (required)
- publisher (required)

**Organization**:
- name (required)
- url (required)

**LocalBusiness**:
- name (required)
- address (required)

**Product**:
- name (required)
- image (required)
- offers (required)

## Implementation Checklist

1. ✅ Identify appropriate schema types for your pages
2. ✅ Add schema markup to HTML (preferably JSON-LD in `<head>`)
3. ✅ Include all required properties
4. ✅ Validate using Google's Rich Results Test
5. ✅ Test on Search Console after deploying
6. ✅ Monitor performance in Search Console > Enhancements

## Common Mistakes to Avoid

1. ❌ Marking up content not visible to users
2. ❌ Using wrong schema type for content
3. ❌ Missing required properties
4. ❌ Invalid date formats (use ISO 8601: YYYY-MM-DD)
5. ❌ Invalid URLs (must be absolute, not relative)
6. ❌ Incorrect image dimensions for Article schema
7. ❌ Fake or misleading ratings/reviews

## Resources

- Schema.org Documentation: https://schema.org/
- Google Search Central: https://developers.google.com/search/docs/appearance/structured-data
- Rich Results Test: https://search.google.com/test/rich-results
- Schema Markup Generator Tools: Various online tools available
