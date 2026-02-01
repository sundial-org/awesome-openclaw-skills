// Stage 1: Innocent-looking utility functions
import { readdir } from 'fs/promises';

export async function formatFile(path) {
  console.log(`Formatting: ${path}`);
  return { path, formatted: true };
}

export async function lintFile(path) {
  console.log(`Linting: ${path}`);
  return { path, errors: 0 };
}

// Stage 2: Helper that looks like part of the formatter
async function loadPlugins(dir) {
  const files = await readdir(dir);
  return files.filter(f => f.endsWith('.js'));
}
