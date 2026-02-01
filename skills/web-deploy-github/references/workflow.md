# Complete Workflow Documentation

## Full Development Cycle

### Phase 1: Planning
1. Understand user requirements
2. Choose appropriate template (base/portfolio/landing)
3. Define site structure and sections

### Phase 2: Project Setup
```bash
cd /root/creations
bash /root/clawd/web-deploy-github/scripts/init_project.sh project-name
```

### Phase 3: Development
1. **Generate complete code** - No placeholders, full implementation
2. **Test locally** - Open index.html in browser
3. **Verify responsiveness** - Check mobile/tablet/desktop views
4. **Validate HTML** - Ensure semantic markup
5. **Optimize performance** - Check load times

### Phase 4: Deployment
```bash
cd project-name
bash /root/clawd/web-deploy-github/scripts/deploy_github_pages.sh project-name username
```

### Phase 5: Verification
1. Wait 1-2 minutes for deployment
2. Visit `https://username.github.io/project-name/`
3. Test all functionality
4. Verify mobile responsiveness

## Autonomous Generation Principles

### Code Completeness
- Generate **complete, production-ready code**
- No TODO comments or placeholder text
- All sections fully implemented
- Real content, not "Lorem ipsum"

### Quality Standards
- Valid HTML5
- Modern CSS (no outdated practices)
- Accessible (ARIA labels, semantic HTML)
- Fast loading (< 2s initial load)
- Mobile-first responsive

### Design Principles
- Clean, modern aesthetics
- Clear visual hierarchy
- Consistent spacing and typography
- Professional color schemes
- Smooth interactions

## Common Patterns

### Single-Page Site Structure
```html
<nav>    <!-- Navigation -->
<header> <!-- Hero/Introduction -->
<main>
  <section id="about">     <!-- About -->
  <section id="features">  <!-- Features/Skills -->
  <section id="work">      <!-- Projects/Portfolio -->
  <section id="contact">   <!-- Contact Form/Info -->
</main>
<footer> <!-- Footer -->
```

### Responsive Breakpoints
```css
/* Mobile first */
/* Default styles for mobile */

/* Tablet */
@media (min-width: 768px) { }

/* Desktop */
@media (min-width: 1024px) { }

/* Large screens */
@media (min-width: 1440px) { }
```

### JavaScript Patterns
```javascript
// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href'))
            .scrollIntoView({ behavior: 'smooth' });
    });
});

// Mobile menu toggle
const menuBtn = document.querySelector('.menu-btn');
const nav = document.querySelector('nav');
menuBtn?.addEventListener('click', () => {
    nav.classList.toggle('active');
});
```

## Git Workflow

### Initial Commit
```bash
git init
git add .
git commit -m "Initial commit: Complete site implementation"
```

### Subsequent Updates
```bash
git add .
git commit -m "Update: [specific changes]"
git push origin main
```

### GitHub Actions Auto-Deploy
- Triggers on push to main
- Builds and deploys to gh-pages branch
- Live site updates automatically

## Troubleshooting Guide

### Deployment Issues

**Problem:** Pages not updating
**Solution:**
```bash
# Force trigger workflow
git commit --allow-empty -m "Trigger deployment"
git push origin main
```

**Problem:** 404 error on GitHub Pages
**Solution:**
- Check repository Settings → Pages
- Ensure source is set to "GitHub Actions"
- Verify deployment workflow ran successfully

**Problem:** CSS/JS not loading
**Solution:**
- Use relative paths: `./styles.css` not `/styles.css`
- Check browser console for errors
- Verify file names match exactly (case-sensitive)

### Development Issues

**Problem:** Layout broken on mobile
**Solution:**
- Add viewport meta tag
- Test with browser DevTools device emulation
- Use mobile-first CSS approach

**Problem:** Images not displaying
**Solution:**
- Verify image paths are relative
- Check image file extensions match
- Ensure images are committed to git

## Performance Optimization

### Images
- Use WebP format when possible
- Provide width/height attributes
- Use `loading="lazy"` for below-fold images
- Optimize with tools like TinyPNG

### CSS
- Minimize unused styles
- Use CSS variables for themes
- Avoid deep nesting
- Use efficient selectors

### JavaScript
- Load scripts with `defer` attribute
- Minimize DOM manipulation
- Use event delegation
- Avoid memory leaks

### Fonts
- Use system fonts when possible
- Preload critical fonts
- Use `font-display: swap`
- Subset custom fonts
