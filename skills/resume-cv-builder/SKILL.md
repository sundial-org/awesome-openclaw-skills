---
name: resume-cv-builder
description: Create professional resumes and CVs. Generate ATS-friendly formats, optimize bullet points, tailor for specific jobs, and export to multiple formats (Markdown, HTML, LaTeX, PDF).
homepage: https://github.com/your-username/resume-builder-skill
metadata: {"clawdbot":{"emoji":"📄","requires":{"bins":["pandoc"],"env":[]}}}
---

# Resume/CV Builder Skill

Create professional, ATS-optimized resumes and CVs directly from Clawdbot.

## Quick Start

Ask me to:
- "Create a resume for a software engineer position"
- "Optimize my resume for ATS"
- "Convert my resume to PDF"
- "Tailor my resume for this job description: [paste JD]"

## Resume Structure

### Standard Sections (Recommended Order)

```markdown
# FULL NAME
Contact Info | LinkedIn | GitHub | Portfolio

## PROFESSIONAL SUMMARY
2-3 sentences highlighting key qualifications

## SKILLS
Technical Skills | Soft Skills | Tools | Languages

## EXPERIENCE
Company — Title (Date - Date)
• Achievement-focused bullet points

## EDUCATION
Degree, Major — University (Year)

## PROJECTS (Optional)
## CERTIFICATIONS (Optional)
## PUBLICATIONS (Optional)
```

## Writing Guidelines

### Professional Summary Formula

```
[Title] with [X years] of experience in [domain]. 
Proven track record of [key achievement]. 
Skilled in [top 3 skills]. Seeking to [goal] at [company type].
```

**Example:**
```
Senior Software Engineer with 7 years of experience in full-stack development. 
Proven track record of reducing system latency by 40% and leading teams of 5+ developers. 
Skilled in Python, React, and AWS. Seeking to drive technical innovation at a growth-stage startup.
```

### Bullet Point Formula (CAR Method)

```
[Action Verb] + [Task/Project] + [Result with Metrics]
```

**Strong Action Verbs by Category:**

| Leadership | Technical | Growth | Efficiency |
|------------|-----------|--------|------------|
| Led | Developed | Increased | Reduced |
| Directed | Engineered | Grew | Streamlined |
| Managed | Architected | Expanded | Automated |
| Mentored | Implemented | Generated | Optimized |
| Coordinated | Designed | Boosted | Consolidated |

**Examples:**
```
❌ Weak: "Responsible for managing a team"
✅ Strong: "Led cross-functional team of 8 engineers, delivering 3 major features ahead of schedule"

❌ Weak: "Worked on improving website performance"
✅ Strong: "Optimized database queries reducing page load time by 65%, improving user retention by 23%"

❌ Weak: "Helped with customer support"
✅ Strong: "Resolved 500+ customer tickets monthly with 98% satisfaction rate, reducing escalations by 40%"
```

### Quantify Everything

| Instead of... | Write... |
|---------------|----------|
| Managed a team | Managed team of 12 engineers across 3 time zones |
| Increased sales | Increased sales by $2.3M (34% YoY growth) |
| Improved efficiency | Reduced processing time from 4 hours to 15 minutes |
| Handled budget | Managed $500K annual budget with 100% compliance |
| Many users | Platform serving 50K+ daily active users |

## ATS Optimization

### Do's ✅
- Use standard section headings (Experience, Education, Skills)
- Include keywords from job description
- Use common job titles
- Spell out acronyms first: "Search Engine Optimization (SEO)"
- Use standard fonts (Arial, Calibri, Times New Roman)
- Save as .docx or .pdf (text-based, not image)

### Don'ts ❌
- No tables, columns, or text boxes
- No headers/footers (ATS may not read them)
- No images, logos, or graphics
- No creative section names ("My Journey" → "Experience")
- No special characters or icons
- Avoid PDF if created from image/scan

### Keyword Optimization

```bash
# Extract keywords from job description
echo "JOB_DESCRIPTION" | tr '[:upper:]' '[:lower:]' | \
  grep -oE '\b[a-z]{3,}\b' | sort | uniq -c | sort -rn | head -20
```

## Templates

### Software Engineer

```markdown
# JANE DOE
San Francisco, CA | jane@email.com | linkedin.com/in/janedoe | github.com/janedoe

## PROFESSIONAL SUMMARY
Full-stack Software Engineer with 5+ years building scalable web applications. 
Expert in React, Node.js, and AWS with a track record of improving system performance by 40%+. 
Passionate about clean code and mentoring junior developers.

## TECHNICAL SKILLS
**Languages:** Python, JavaScript/TypeScript, Go, SQL
**Frontend:** React, Next.js, Redux, Tailwind CSS
**Backend:** Node.js, FastAPI, PostgreSQL, Redis
**Cloud/DevOps:** AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD
**Tools:** Git, Jira, Figma, DataDog

## EXPERIENCE

**Senior Software Engineer** | TechCorp Inc. | Jan 2022 – Present
• Architected microservices migration reducing deployment time by 70% and enabling independent scaling
• Led team of 5 engineers delivering real-time notification system serving 2M+ users
• Implemented automated testing pipeline increasing code coverage from 45% to 92%
• Mentored 3 junior developers through structured onboarding program

**Software Engineer** | StartupXYZ | Jun 2019 – Dec 2021
• Built React dashboard processing $5M+ monthly transactions with 99.9% uptime
• Optimized PostgreSQL queries reducing API response time by 60%
• Developed CI/CD pipeline cutting release cycles from 2 weeks to 2 days

## EDUCATION
**B.S. Computer Science** | University of California, Berkeley | 2019
GPA: 3.7 | Relevant Coursework: Distributed Systems, Machine Learning, Algorithms

## PROJECTS
**Open Source Contribution** | github.com/project
• Contributed authentication module to popular framework (500+ GitHub stars)
```

### Product Manager

```markdown
# ALEX SMITH
New York, NY | alex@email.com | linkedin.com/in/alexsmith

## PROFESSIONAL SUMMARY
Product Manager with 6 years driving B2B SaaS products from concept to scale. 
Led products generating $15M+ ARR with proven expertise in user research, data analysis, and cross-functional leadership. 
MBA from Wharton.

## SKILLS
**Product:** Roadmap Planning, User Research, A/B Testing, PRDs, OKRs
**Analytics:** SQL, Amplitude, Mixpanel, Tableau, Excel
**Tools:** Jira, Figma, Miro, Notion, Productboard
**Methods:** Agile/Scrum, Design Thinking, Jobs-to-be-Done

## EXPERIENCE

**Senior Product Manager** | SaaS Company | Mar 2021 – Present
• Own product roadmap for enterprise platform ($8M ARR, 200+ customers)
• Launched AI-powered feature increasing user engagement by 45% and reducing churn by 20%
• Conducted 100+ customer interviews identifying $3M expansion opportunity
• Collaborated with engineering (12 devs), design, and sales to deliver quarterly releases

**Product Manager** | Tech Startup | Jan 2019 – Feb 2021
• Grew mobile app from 10K to 150K MAU through data-driven feature prioritization
• Reduced onboarding drop-off by 35% via user research and UX improvements
• Defined and tracked KPIs resulting in 25% improvement in activation rate

## EDUCATION
**MBA** | The Wharton School | 2018
**B.A. Economics** | NYU | 2014
```

### Marketing Manager

```markdown
# SARAH JOHNSON
Los Angeles, CA | sarah@email.com | linkedin.com/in/sarahjohnson

## PROFESSIONAL SUMMARY
Digital Marketing Manager with 5+ years driving growth for DTC and B2B brands. 
Managed $2M+ annual ad spend with 4x ROAS. Expert in paid acquisition, SEO, and marketing automation.

## SKILLS
**Channels:** Google Ads, Meta Ads, LinkedIn, TikTok, SEO/SEM
**Tools:** HubSpot, Marketo, Google Analytics, SEMrush, Klaviyo
**Skills:** Marketing Automation, Content Strategy, CRO, Email Marketing
**Analytics:** SQL, Looker, Excel, Attribution Modeling

## EXPERIENCE

**Marketing Manager** | E-commerce Brand | Jun 2021 – Present
• Manage $150K/month paid media budget achieving 4.2x ROAS (vs. 2.5x benchmark)
• Grew organic traffic by 180% YoY through SEO content strategy (50+ articles)
• Built email automation flows generating $500K incremental revenue
• Led rebrand project increasing brand awareness by 60% (measured via surveys)

**Digital Marketing Specialist** | Agency | Aug 2019 – May 2021
• Managed campaigns for 8 clients with combined $1M annual spend
• Achieved average 35% reduction in CAC across client portfolio
• Created reporting dashboards saving team 10 hours/week

## EDUCATION
**B.S. Marketing** | USC Marshall | 2019

## CERTIFICATIONS
Google Ads Certified | HubSpot Inbound Marketing | Meta Blueprint
```

## Export Commands

### Markdown to HTML
```bash
pandoc resume.md -o resume.html --standalone --css=style.css
```

### Markdown to PDF
```bash
pandoc resume.md -o resume.pdf --pdf-engine=xelatex
```

### Markdown to DOCX
```bash
pandoc resume.md -o resume.docx
```

### With Custom Styling
```bash
# Create styled HTML
pandoc resume.md -o resume.html --standalone \
  --metadata title="Resume" \
  --css="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css"
```

## Tailoring for Specific Jobs

### Step-by-Step Process

1. **Extract Keywords** from job description
2. **Match Skills** — ensure your skills section mirrors JD requirements
3. **Reorder Bullets** — most relevant experience first
4. **Mirror Language** — use same terminology as JD
5. **Customize Summary** — mention company name and specific role

### Example Tailoring

**Job Description says:**
> "Looking for experience with React, TypeScript, and AWS. Must have led teams."

**Your bullet BEFORE:**
```
• Developed web applications using various technologies
```

**Your bullet AFTER:**
```
• Led team of 4 engineers building React/TypeScript applications deployed on AWS, serving 50K users
```

## Common Mistakes to Avoid

| Mistake | Fix |
|---------|-----|
| Including "References available upon request" | Remove — it's assumed |
| Using personal pronouns (I, me, my) | Start bullets with action verbs |
| Listing job duties instead of achievements | Focus on results and impact |
| Including outdated skills (jQuery, Flash) | Keep skills current and relevant |
| Making it longer than 2 pages | 1 page for <10 years exp, 2 max |
| Using generic objective statement | Replace with targeted summary |
| Inconsistent formatting | Use same date format, bullet style |
| Typos and grammar errors | Proofread multiple times |

## Quick Checklist

```
□ Contact info is current and professional
□ Email is professional (not coolboy99@...)
□ Summary is tailored to target role
□ All bullets start with action verbs
□ Achievements include metrics/numbers
□ Skills match job description keywords
□ Education includes relevant details only
□ No typos or grammatical errors
□ Consistent formatting throughout
□ Saved in ATS-friendly format
□ File named professionally (FirstName_LastName_Resume.pdf)
```

## Resources

- [Harvard Resume Guide](https://careerservices.fas.harvard.edu/resources/resume-guide/)
- [Google XYZ Formula](https://www.inc.com/bill-murphy-jr/google-recruiters-say-these-5-resume-tips-including-x-y-z-formula-will-improve-your-odds-of-getting-hired-at-google.html)
- [ATS Resume Test](https://www.jobscan.co/)
