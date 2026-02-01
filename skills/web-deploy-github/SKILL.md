---
name: web-deploy-github
description: Create and deploy single-page static websites to GitHub Pages with autonomous workflow. Use when building portfolio sites, CV pages, landing pages, or any static web project that needs GitHub Pages deployment. Handles complete workflow from project initialization to live deployment with GitHub Actions automation.
---

# Web Deploy GitHub Pages

## Overview

This skill enables autonomous creation and deployment of static websites to GitHub Pages. It follows a complete workflow from project structure initialization through automatic deployment via GitHub Actions, optimized for single-page applications, portfolios, and landing pages.

## Core Workflow

### 1. Project Initialization

Create the project structure:

```bash
bash scripts/init_project.sh <project-name>
```

This creates:
```
project-name/
├── index.html
├── styles.css
├── script.js
├── README.md
└── .github/
    └── workflows/
        └── deploy.yml
```

### 2. Development

Build the website following these principles:
- **Single-page first**: Optimize for one-page layouts unless multiple pages explicitly required
- **Autonomous generation**: Generate complete, production-ready code without placeholders
- **Modern design**: Use modern CSS (flexbox, grid), responsive design, clean aesthetics
- **No dependencies**: Pure HTML/CSS/JS when possible, CDN links if frameworks needed

Use templates from `assets/templates/` as starting points:
- `base-html/` - Minimal HTML5 boilerplate
- `portfolio/` - Portfolio/CV template with sections
- `landing/` - Landing page with hero and CTA

### 3. GitHub Repository Setup

```bash
bash scripts/deploy_github_pages.sh <project-name> <github-username>
```

This script:
1. Initializes git repository
2. Creates GitHub repository via GitHub CLI
3. Configures GitHub Pages settings
4. Pushes initial commit
5. Triggers first deployment

### 4. Deployment

GitHub Actions automatically deploys on push to main branch. The workflow:
- Checks out code
- Deploys to `gh-pages` branch
- Makes site live at `https://<username>.github.io/<project-name>/`

## Architecture Guidelines

### HTML Structure
- Semantic HTML5 elements
- Meta tags for SEO and social sharing
- Responsive viewport configuration
- Favicon and icons

### CSS Design
- Mobile-first responsive design
- CSS variables for theming
- Flexbox/Grid for layouts
- Smooth transitions and animations
- Dark mode support when appropriate

### JavaScript
- Vanilla JS preferred
- Progressive enhancement
- Event delegation
- No console errors

### Performance
- Optimized images
- Minified assets for production
- Lazy loading where appropriate
- Fast initial load time

## Quick Examples

### Example 1: Portfolio CV Site
**User request:** "Crée-moi un site portfolio CV"

**Action:**
1. Run `init_project.sh portfolio-cv`
2. Use `assets/templates/portfolio/` as base
3. Generate complete HTML with sections: Hero, About, Skills, Projects, Contact
4. Deploy with `deploy_github_pages.sh portfolio-cv username`

### Example 2: Landing Page
**User request:** "Fais-moi une landing page pour mon app"

**Action:**
1. Run `init_project.sh app-landing`
2. Use `assets/templates/landing/` as base
3. Generate with Hero, Features, Pricing, CTA
4. Deploy with `deploy_github_pages.sh app-landing username`

## Troubleshooting

### GitHub Pages Not Deploying
- Check repository Settings → Pages → Source is set to `gh-pages` branch
- Verify GitHub Actions workflow ran successfully
- Check DNS propagation (can take 5-10 minutes)

### Permission Errors
- Ensure `gh` CLI is authenticated: `gh auth status`
- Check repository permissions on GitHub

### Build Failures
- Review Actions logs in repository
- Verify `.github/workflows/deploy.yml` syntax
- Check file paths and references

## Resources

### scripts/
- `init_project.sh` - Initialize project structure
- `deploy_github_pages.sh` - Deploy to GitHub Pages

### references/
- `workflow.md` - Detailed workflow documentation
- `design-patterns.md` - Design best practices

### assets/
- `templates/base-html/` - Minimal HTML5 boilerplate
- `templates/portfolio/` - Portfolio/CV template
- `templates/landing/` - Landing page template
- `.github/workflows/deploy.yml` - GitHub Actions workflow template
