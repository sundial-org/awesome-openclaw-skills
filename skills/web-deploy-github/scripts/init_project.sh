#!/bin/bash
# Initialize a new web project for GitHub Pages deployment

set -e

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: bash init_project.sh <project-name>"
    exit 1
fi

echo "🚀 Initializing project: $PROJECT_NAME"

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Create basic structure
mkdir -p .github/workflows

# Create index.html
cat > index.html <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <title>My Site</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <main>
        <section class="hero">
            <h1>Welcome</h1>
            <p>This is a starter template</p>
        </section>
    </main>
    <script src="script.js"></script>
</body>
</html>
EOF

# Create styles.css
cat > styles.css <<'EOF'
:root {
    --primary: #007bff;
    --text: #333;
    --bg: #fff;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    color: var(--text);
    background: var(--bg);
    line-height: 1.6;
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.hero {
    text-align: center;
    padding: 4rem 2rem;
}

h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

@media (max-width: 768px) {
    h1 {
        font-size: 2rem;
    }
}
EOF

# Create script.js
cat > script.js <<'EOF'
// Add your JavaScript here
console.log('Site loaded');
EOF

# Create README.md
cat > README.md <<EOF
# $PROJECT_NAME

Live site: Coming soon

## Development

Open \`index.html\` in your browser to preview locally.

## Deployment

Automatically deployed to GitHub Pages on push to main branch.
EOF

# Create GitHub Actions workflow
cat > .github/workflows/deploy.yml <<'EOF'
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
        
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
          
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
EOF

echo "✅ Project structure created in $PROJECT_NAME/"
echo ""
echo "Next steps:"
echo "  1. Edit index.html, styles.css, and script.js"
echo "  2. Run: bash deploy_github_pages.sh $PROJECT_NAME <github-username>"
