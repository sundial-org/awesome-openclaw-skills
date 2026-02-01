# Design Patterns and Best Practices

## Design Philosophy

### Thomek's Design Principles
1. **Autonomous Generation** - Complete, production-ready code without placeholders
2. **Modern Aesthetics** - Clean, contemporary design patterns
3. **Performance First** - Fast loading, optimized assets
4. **Mobile Priority** - Responsive from the ground up
5. **User Experience** - Intuitive navigation, clear CTAs

## Color Schemes

### Professional Palettes
```css
/* Modern Blue */
--primary: #0066FF;
--secondary: #00A3FF;
--accent: #FF6B6B;
--text: #1A1A1A;
--bg: #FFFFFF;

/* Dark Theme */
--primary: #00D9FF;
--secondary: #0066FF;
--accent: #FF4D94;
--text: #FFFFFF;
--bg: #0A0A0A;

/* Minimal Monochrome */
--primary: #000000;
--secondary: #666666;
--accent: #FF0000;
--text: #333333;
--bg: #F5F5F5;
```

### Gradient Patterns
```css
/* Modern gradient backgrounds */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
```

## Typography

### Font Stacks
```css
/* System fonts (fastest) */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
             Oxygen, Ubuntu, Cantarell, sans-serif;

/* Modern sans-serif */
font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;

/* Elegant serif */
font-family: 'Playfair Display', Georgia, serif;

/* Monospace for code */
font-family: 'Fira Code', 'Consolas', monospace;
```

### Scale and Hierarchy
```css
/* Type scale (1.25 ratio) */
--fs-xs: 0.64rem;    /* 10px */
--fs-sm: 0.8rem;     /* 13px */
--fs-base: 1rem;     /* 16px */
--fs-md: 1.25rem;    /* 20px */
--fs-lg: 1.563rem;   /* 25px */
--fs-xl: 1.953rem;   /* 31px */
--fs-2xl: 2.441rem;  /* 39px */
--fs-3xl: 3.052rem;  /* 49px */
```

## Layout Patterns

### Hero Section
```html
<section class="hero">
    <div class="hero-content">
        <h1 class="hero-title">Bold Statement</h1>
        <p class="hero-subtitle">Supporting text that explains value proposition</p>
        <div class="hero-cta">
            <a href="#action" class="btn btn-primary">Primary Action</a>
            <a href="#learn" class="btn btn-secondary">Learn More</a>
        </div>
    </div>
</section>
```

```css
.hero {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
}

.hero-title {
    font-size: var(--fs-3xl);
    font-weight: 700;
    margin-bottom: 1rem;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: var(--fs-lg);
    opacity: 0.8;
    margin-bottom: 2rem;
}
```

### Grid Layouts
```css
/* Auto-fit responsive grid */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

/* 3-column layout */
.three-col {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
}

@media (max-width: 768px) {
    .three-col {
        grid-template-columns: 1fr;
    }
}
```

### Card Components
```html
<div class="card">
    <div class="card-image">
        <img src="..." alt="...">
    </div>
    <div class="card-content">
        <h3 class="card-title">Title</h3>
        <p class="card-description">Description</p>
        <a href="#" class="card-link">Learn more →</a>
    </div>
</div>
```

```css
.card {
    background: var(--bg);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}
```

## Component Patterns

### Navigation Bar
```html
<nav class="navbar">
    <div class="nav-container">
        <a href="#" class="nav-logo">Logo</a>
        <button class="menu-toggle" aria-label="Toggle menu">
            <span></span>
            <span></span>
            <span></span>
        </button>
        <ul class="nav-menu">
            <li><a href="#about">About</a></li>
            <li><a href="#work">Work</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </div>
</nav>
```

```css
.navbar {
    position: fixed;
    top: 0;
    width: 100%;
    background: var(--bg);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    z-index: 1000;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
}

.nav-menu {
    display: flex;
    gap: 2rem;
    list-style: none;
}

@media (max-width: 768px) {
    .nav-menu {
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        width: 100%;
        background: var(--bg);
        transform: translateX(-100%);
        transition: transform 0.3s;
    }
    
    .nav-menu.active {
        transform: translateX(0);
    }
}
```

### Buttons
```css
.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s;
    cursor: pointer;
    border: none;
}

.btn-primary {
    background: var(--primary);
    color: white;
}

.btn-primary:hover {
    background: var(--secondary);
    transform: scale(1.05);
}

.btn-secondary {
    background: transparent;
    color: var(--primary);
    border: 2px solid var(--primary);
}

.btn-secondary:hover {
    background: var(--primary);
    color: white;
}
```

### Contact Forms
```html
<form class="contact-form">
    <div class="form-group">
        <label for="name">Name</label>
        <input type="text" id="name" name="name" required>
    </div>
    <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" required>
    </div>
    <div class="form-group">
        <label for="message">Message</label>
        <textarea id="message" name="message" rows="5" required></textarea>
    </div>
    <button type="submit" class="btn btn-primary">Send Message</button>
</form>
```

```css
.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: var(--primary);
}
```

## Animation Patterns

### Entrance Animations
```css
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-in {
    animation: fadeInUp 0.6s ease-out;
}

/* Stagger children */
.stagger-children > * {
    animation: fadeInUp 0.6s ease-out;
}

.stagger-children > *:nth-child(1) { animation-delay: 0.1s; }
.stagger-children > *:nth-child(2) { animation-delay: 0.2s; }
.stagger-children > *:nth-child(3) { animation-delay: 0.3s; }
```

### Hover Effects
```css
/* Scale on hover */
.hover-scale {
    transition: transform 0.3s;
}
.hover-scale:hover {
    transform: scale(1.05);
}

/* Lift effect */
.hover-lift {
    transition: transform 0.3s, box-shadow 0.3s;
}
.hover-lift:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.15);
}

/* Glow effect */
.hover-glow {
    transition: box-shadow 0.3s;
}
.hover-glow:hover {
    box-shadow: 0 0 20px var(--primary);
}
```

## Accessibility

### Required Practices
```html
<!-- Semantic HTML -->
<header>, <nav>, <main>, <section>, <article>, <aside>, <footer>

<!-- Alt text for images -->
<img src="..." alt="Descriptive text">

<!-- ARIA labels -->
<button aria-label="Close menu">×</button>

<!-- Skip to content -->
<a href="#main" class="skip-link">Skip to content</a>

<!-- Focus indicators -->
:focus {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
}
```

## Performance Optimizations

### Critical CSS
```html
<style>
/* Inline critical above-the-fold styles */
.hero { min-height: 100vh; display: flex; }
/* ... */
</style>
<link rel="stylesheet" href="styles.css">
```

### Lazy Loading
```html
<img src="..." alt="..." loading="lazy">
```

### Preload Critical Assets
```html
<link rel="preload" href="hero-image.webp" as="image">
```

## Modern CSS Features

### CSS Grid Areas
```css
.layout {
    display: grid;
    grid-template-areas:
        "header header"
        "sidebar main"
        "footer footer";
    grid-template-columns: 250px 1fr;
    gap: 2rem;
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; }
.footer { grid-area: footer; }
```

### Custom Properties with Fallbacks
```css
:root {
    --spacing: 2rem;
    --radius: 8px;
}

.card {
    padding: var(--spacing);
    border-radius: var(--radius);
}
```

### Container Queries (Modern browsers)
```css
@container (min-width: 400px) {
    .card {
        grid-template-columns: 1fr 1fr;
    }
}
```
