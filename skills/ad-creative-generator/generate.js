#!/usr/bin/env node

/**
 * Ad Creative Generator - Main Script
 *
 * Interactive CLI for generating advertising creative prompts
 * Supports multiple export formats and category selection
 */

const readline = require('readline');
const fs = require('fs');
const path = require('path');
const {
  getAllCategories,
  getTemplatesByCategory,
  generateAllPrompts,
  generatePromptsForCategories,
  getTotalTemplateCount
} = require('./templates');

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Question wrapper for promises
function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      resolve(answer.trim());
    });
  });
}

// Clear screen
function clearScreen() {
  console.clear();
}

// Print header
function printHeader() {
  console.log(`\n${colors.cyan}${colors.bright}╔════════════════════════════════════════════════════════════╗${colors.reset}`);
  console.log(`${colors.cyan}${colors.bright}║          🎨 AD CREATIVE GENERATOR v1.0                  ║${colors.reset}`);
  console.log(`${colors.cyan}${colors.bright}║          Generate Compelling Ad Prompts                 ║${colors.reset}`);
  console.log(`${colors.cyan}${colors.bright}╚════════════════════════════════════════════════════════════╝${colors.reset}\n`);
}

// Print error message
function printError(message) {
  console.log(`\n${colors.red}✗ Error: ${message}${colors.reset}\n`);
}

// Print success message
function printSuccess(message) {
  console.log(`\n${colors.green}✓ ${message}${colors.reset}\n`);
}

// Print info message
function printInfo(message) {
  console.log(`${colors.blue}ℹ ${message}${colors.reset}`);
}

// Print warning message
function printWarning(message) {
  console.log(`${colors.yellow}⚠ ${message}${colors.reset}`);
}

// Validate product name
function validateProductName(name) {
  if (!name || name.length === 0) {
    throw new Error('Product name cannot be empty');
  }
  if (name.length > 100) {
    throw new Error('Product name too long (max 100 characters)');
  }
  return name;
}

// Display category menu
function displayCategoryMenu() {
  const categories = getAllCategories();
  console.log(`${colors.bright}Available Categories:${colors.reset}\n`);

  categories.forEach((cat, index) => {
    const styles = getTemplatesByCategory(cat);
    const styleNames = styles.map(s => s.name).join(', ');
    console.log(`  ${colors.cyan}${index + 1}.${colors.reset} ${colors.bright}${cat.charAt(0).toUpperCase() + cat.slice(1)}${colors.reset}`);
    console.log(`     ${colors.dim}(${styles.length} styles: ${styleNames})${colors.reset}`);
  });

  console.log(`\n  ${colors.green}a.${colors.reset} ${colors.bright}Select All Categories${colors.reset}`);
  console.log(`  ${colors.yellow}d.${colors.reset} ${colors.bright}Done Selecting${colors.reset}\n`);
}

// Get category selection from user
async function getCategorySelection() {
  const categories = getAllCategories();
  const selectedCategories = new Set();

  while (true) {
    clearScreen();
    printHeader();
    displayCategoryMenu();

    if (selectedCategories.size > 0) {
      console.log(`${colors.green}Selected Categories: ${Array.from(selectedCategories).map(c => c.charAt(0).toUpperCase() + c.slice(1)).join(', ')}${colors.reset}\n`);
    }

    const choice = await question('Select category (number, "a" for all, "d" for done): ').toLowerCase();

    if (choice === 'd') {
      if (selectedCategories.size === 0) {
        printError('Please select at least one category');
        await question('Press Enter to continue...');
        continue;
      }
      break;
    } else if (choice === 'a') {
      categories.forEach(cat => selectedCategories.add(cat));
      printSuccess(`All ${categories.length} categories selected!`);
      await question('Press Enter to continue...');
    } else {
      const num = parseInt(choice);
      if (num >= 1 && num <= categories.length) {
        const category = categories[num - 1];
        if (selectedCategories.has(category)) {
          selectedCategories.delete(category);
          printInfo(`Deselected: ${category}`);
        } else {
          selectedCategories.add(category);
          printSuccess(`Selected: ${category}`);
        }
        await question('Press Enter to continue...');
      } else {
        printError('Invalid selection. Please try again.');
        await question('Press Enter to continue...');
      }
    }
  }

  return Array.from(selectedCategories);
}

// Display export format menu
function displayExportMenu() {
  console.log(`${colors.bright}Export Format:${colors.reset}\n`);
  console.log(`  ${colors.cyan}1.${colors.reset} JSON (Structured data format)`);
  console.log(`  ${colors.cyan}2.${colors.reset} Text (Plain text format)`);
  console.log(`  ${colors.cyan}3.${colors.reset} Markdown (Formatted with structure)`);
  console.log(`  ${colors.cyan}4.${colors.reset} Display only (No export)\n`);
}

// Get export format from user
async function getExportFormat() {
  while (true) {
    displayExportMenu();
    const choice = await question('Select export format (1-4): ');

    switch (choice) {
      case '1':
        return 'json';
      case '2':
        return 'text';
      case '3':
        return 'markdown';
      case '4':
        return 'display';
      default:
        printError('Invalid selection. Please enter 1-4.');
        await question('Press Enter to continue...');
        clearScreen();
        printHeader();
    }
  }
}

// Generate output in JSON format
function generateJSON(product, prompts) {
  return JSON.stringify({
    product: product,
    generated_at: new Date().toISOString(),
    total_prompts: prompts.length,
    prompts: prompts.map(p => ({
      category: p.category,
      style: p.style,
      prompt: p.prompt
    }))
  }, null, 2);
}

// Generate output in text format
function generateText(product, prompts) {
  let output = `Ad Creative Prompts for: ${product}\n`;
  output += `${'='.repeat(60)}\n`;
  output += `Generated: ${new Date().toLocaleString()}\n`;
  output += `Total Prompts: ${prompts.length}\n\n`;

  prompts.forEach((p, index) => {
    output += `[${index + 1}] ${p.style} (${p.category})\n`;
    output += `${'-'.repeat(60)}\n`;
    output += `${p.prompt}\n\n`;
  });

  return output;
}

// Generate output in Markdown format
function generateMarkdown(product, prompts) {
  let output = `# Ad Creative Prompts for: ${product}\n\n`;
  output += `**Generated:** ${new Date().toLocaleString()}\n\n`;
  output += `**Total Prompts:** ${prompts.length}\n\n`;

  // Group by category
  const grouped = {};
  prompts.forEach(p => {
    if (!grouped[p.category]) {
      grouped[p.category] = [];
    }
    grouped[p.category].push(p);
  });

  // Output by category
  for (const [category, items] of Object.entries(grouped)) {
    output += `## ${category.charAt(0).toUpperCase() + category.slice(1)}\n\n`;

    items.forEach((item, index) => {
      output += `### ${index + 1}. ${item.style}\n\n`;
      output += `${item.prompt}\n\n`;
      output += `---\n\n`;
    });
  }

  return output;
}

// Display prompts to console
function displayPrompts(product, prompts) {
  console.log(`\n${colors.bright}${colors.cyan}Generated Prompts for: ${product}${colors.reset}\n`);
  console.log(`${colors.dim}${'='.repeat(70)}${colors.reset}\n`);

  // Group by category for display
  const grouped = {};
  prompts.forEach(p => {
    if (!grouped[p.category]) {
      grouped[p.category] = [];
    }
    grouped[p.category].push(p);
  });

  let count = 0;
  for (const [category, items] of Object.entries(grouped)) {
    console.log(`${colors.bright}${colors.magenta}${category.charAt(0).toUpperCase() + category.slice(1)}${colors.reset}`);
    console.log(`${colors.dim}${'-'.repeat(70)}${colors.reset}`);

    items.forEach((item) => {
      count++;
      console.log(`\n${colors.green}[${count}] ${item.style}${colors.reset}`);
      console.log(`${colors.dim}${item.prompt}${colors.reset}`);
    });

    console.log();
  }

  console.log(`${colors.dim}${'='.repeat(70)}${colors.reset}`);
  console.log(`${colors.bright}Total: ${count} prompts generated${colors.reset}\n`);
}

// Save output to file
function saveToFile(content, filename) {
  try {
    fs.writeFileSync(filename, content, 'utf8');
    printSuccess(`Exported to: ${filename}`);
    return true;
  } catch (error) {
    printError(`Failed to save file: ${error.message}`);
    return false;
  }
}

// Get output filename
async function getOutputFilename(format, product) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
  const safeProduct = product.replace(/[^a-z0-9]/gi, '-').toLowerCase();
  const defaultName = `ad-creative-${safeProduct}-${timestamp}.${format === 'markdown' ? 'md' : format}`;

  const filename = await question(`Enter output filename (or press Enter for "${defaultName}"): `);
  return filename || defaultName;
}

// Interactive mode
async function interactiveMode() {
  try {
    clearScreen();
    printHeader();

    // Get product name
    const product = await question('Enter product/brand name: ');
    validateProductName(product);

    // Get category selection
    const categories = await getCategorySelection();

    // Generate prompts
    printInfo('Generating creative prompts...');
    const prompts = generatePromptsForCategories(categories, product);
    printSuccess(`Generated ${prompts.length} creative prompts!`);

    await question('Press Enter to continue...');

    // Get export format
    clearScreen();
    printHeader();
    const format = await getExportFormat();

    if (format === 'display') {
      // Display only
      clearScreen();
      printHeader();
      displayPrompts(product, prompts);
    } else {
      // Export to file
      const filename = await getOutputFilename(format, product);

      let content;
      switch (format) {
        case 'json':
          content = generateJSON(product, prompts);
          break;
        case 'text':
          content = generateText(product, prompts);
          break;
        case 'markdown':
          content = generateMarkdown(product, prompts);
          break;
      }

      saveToFile(content, filename);

      // Also display to console
      console.log();
      displayPrompts(product, prompts);
    }

    printSuccess('Done!');
  } catch (error) {
    printError(error.message);
  } finally {
    rl.close();
  }
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    product: null,
    export: null,
    output: null,
    categories: [],
    all: false,
    help: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const nextArg = args[i + 1];

    if (arg === '--help' || arg === '-h') {
      options.help = true;
    } else if (arg === '--product' && nextArg) {
      options.product = nextArg;
      i++;
    } else if (arg === '--export' && nextArg) {
      options.export = nextArg;
      i++;
    } else if (arg === '--output' && nextArg) {
      options.output = nextArg;
      i++;
    } else if (arg === '--categories' && nextArg) {
      options.categories = nextArg.split(',').map(c => c.trim().toLowerCase());
      i++;
    } else if (arg === '--all') {
      options.all = true;
    }
  }

  return options;
}

// Display help
function displayHelp() {
  console.log(`
${colors.bright}Ad Creative Generator${colors.reset}
Generate creative advertising prompts for any product or brand.

${colors.bright}Usage:${colors.reset}
  node generate.js                    # Interactive mode
  node generate.js [options]          # Command line mode

${colors.bright}Options:${colors.reset}
  --help, -h              Show this help message
  --product <name>        Product or brand name
  --export <format>       Export format: json, text, markdown
  --output <file>         Output filename (optional)
  --categories <list>     Comma-separated categories
  --all                   Generate all categories

${colors.bright}Available Categories:${colors.reset}
  minimalist, productTransformation, culturalExotic, lifestyle,
  technology, luxury, ecoGreen, seasonal, emotional, playful

${colors.bright}Examples:${colors.reset}
  node generate.js --product "Luxury Perfume"
  node generate.js --product "Smart Watch" --export json --output ads.json
  node generate.js --product "Organic Tea" --categories minimalist,eco
  node generate.js --product "New App" --all --export markdown

${colors.bright}Information:${colors.reset}
  Total Templates: ${getTotalTemplateCount()}
  Categories: ${getAllCategories().length}
`);
}

// Command line mode
function commandLineMode(options) {
  try {
    validateProductName(options.product);

    let categories;
    if (options.all) {
      categories = getAllCategories();
    } else if (options.categories.length > 0) {
      categories = options.categories;
    } else {
      categories = getAllCategories();
    }

    printInfo('Generating creative prompts...');
    const prompts = generatePromptsForCategories(categories, options.product);
    printSuccess(`Generated ${prompts.length} prompts!`);

    if (!options.export || options.export === 'display') {
      displayPrompts(options.product, prompts);
    } else {
      const format = options.export;
      let content;
      switch (format) {
        case 'json':
          content = generateJSON(options.product, prompts);
          break;
        case 'text':
          content = generateText(options.product, prompts);
          break;
        case 'markdown':
          content = generateMarkdown(options.product, prompts);
          break;
        default:
          throw new Error(`Invalid export format: ${format}`);
      }

      const filename = options.output || `ad-creative-${options.product.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.${format === 'markdown' ? 'md' : format}`;
      saveToFile(content, filename);
    }

    printSuccess('Done!');
  } catch (error) {
    printError(error.message);
    process.exit(1);
  }
}

// Main entry point
function main() {
  const options = parseArgs();

  if (options.help) {
    displayHelp();
    rl.close();
    return;
  }

  if (options.product) {
    rl.close();
    commandLineMode(options);
  } else {
    interactiveMode();
  }
}

// Run
if (require.main === module) {
  main();
}

module.exports = {
  generateJSON,
  generateText,
  generateMarkdown,
  displayPrompts
};
