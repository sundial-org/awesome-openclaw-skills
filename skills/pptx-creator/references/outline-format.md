# Outline Format Reference

## Basic Structure

```markdown
# Presentation Title
subtitle: Optional Subtitle
author: Your Name

## First Slide Title
- Bullet point one
- Bullet point two
- Bullet point three

## Second Slide Title
- More content here
- And here
```

## Special Directives

### Images
```markdown
## Slide with Image
- ![alt text](/path/to/image.png)
- ![hero](generate: description for AI image generation)
```

### Charts
```markdown
## Chart Slide
- chart: bar
- data: /path/to/data.csv
- Optional bullet describing the chart
```

Chart types: `bar`, `column`, `line`, `pie`, `doughnut`, `area`, `scatter`

### Tables
```markdown
## Table Slide  
- table: my_table
- data: /path/to/data.csv
- columns: name, value, category
```

### Layouts
```markdown
## Custom Layout Slide
- layout: two_column
- Left column content
- Right column content
```

Layouts: `title_and_content`, `two_column`, `image_and_text`, `chart`, `table`, `section`, `blank`

### Speaker Notes
```markdown
## Slide Title
- Bullet points
> These are speaker notes that won't appear on the slide
> They help the presenter remember key points
```

## Complete Example

```markdown
# Q4 2026 Review
subtitle: Performance & Outlook
author: Your Name

## Agenda
- Q4 Performance Highlights
- Regional Breakdown
- Key Wins
- 2027 Outlook

## Q4 Highlights
- Revenue: $4.2M (+18% YoY)
- New customers: 47
- Retention rate: 94%
> Emphasize the retention improvement from Q3

## Regional Performance
- chart: bar
- data: regional_sales_q4.csv
- Northeast led growth at 24%
- West recovering after Q3 dip

## Key Wins
- ![logo](generate: abstract celebration, confetti, corporate style)
- Major enterprise deal closed
- Strategic partnership signed
- Product launch successful

## 2027 Outlook
- layout: two_column
- **Goals**: $18M revenue, 200 new customers
- **Investments**: Team expansion, Platform upgrades
- **Risks**: Market conditions, Competition

## Next Steps
- Finalize 2027 targets
- Kick-off planning meeting
- Q1 pipeline review
> Schedule follow-ups with regional leads
```
