//==============================================================================
// AUTO-GENERATED - DO NOT EDIT
//==============================================================================
// Source: src/core/templates/scripts/common-ui.js
// To edit: Modify source file, then run: src/scripts/sync-skills.sh
//==============================================================================

/* eslint-disable no-unused-vars */
// Functions in this file are used by other scripts and HTML onclick handlers

const GITHUB_REPO = 'https://github.com/veelenga/preview-skills';

function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
}

function createHeader(title, stats, toolbarItems = []) {
  const themeToggle = `
        <div class="theme-toggle-wrapper">
            <span class="theme-label">Theme</span>
            <div class="theme-toggle" onclick="toggleTheme()" title="Toggle theme"></div>
        </div>
    `;

  const statsHtml = stats ? `<span class="preview-header-stats">${stats}</span>` : '';
  const toolbarHtml =
    toolbarItems.length > 0 ? `<div class="preview-toolbar">${toolbarItems.join('')}</div>` : '';

  return `
        <div class="preview-header">
            <div class="preview-header-info">
                <strong class="preview-header-title">${title}</strong>
                ${statsHtml}
            </div>
            ${toolbarHtml}
            ${themeToggle}
        </div>
    `;
}

initTheme();

function createSearchBox(onInput, onClear) {
  return `
        <div class="search-box">
            <span class="search-icon">🔍</span>
            <input type="text" class="search-input" placeholder="Search... (Ctrl+F)" oninput="${onInput}">
            <button class="search-clear" onclick="${onClear}">×</button>
        </div>
    `;
}

function createButton(label, onclick, icon = '') {
  const iconHtml = icon ? icon + ' ' : '';
  return `<button class="action-btn" onclick="${onclick}">${iconHtml}${label}</button>`;
}

function createFooter() {
  const year = new Date().getFullYear();
  return `
        <div class="preview-footer">
            <div class="footer-links">
                <a href="${GITHUB_REPO}" target="_blank" class="footer-link">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
                    </svg>
                    Source
                </a>
                <a href="${GITHUB_REPO}/blob/main/LICENSE" target="_blank" class="footer-link">
                    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"/>
                    </svg>
                    MIT License
                </a>
            </div>
            <div class="footer-copyright">
                ${year} Preview Skill. Built with <span style="color: #ef4444;">❤</span> by <a href="https://github.com/veelenga" target="_blank" class="footer-author">veelenga</a>
            </div>
        </div>
    `;
}

function showStatus(message) {
  const existing = document.querySelector('.status-message');
  if (existing) existing.remove();

  const statusDiv = document.createElement('div');
  statusDiv.className = 'status-message';
  statusDiv.textContent = message;
  document.body.appendChild(statusDiv);

  setTimeout(() => {
    statusDiv.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => statusDiv.remove(), 300);
  }, 2000);
}

function initSearchShortcut(inputSelector) {
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
      e.preventDefault();
      document.querySelector(inputSelector).focus();
    }
  });
}

function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
  navigator.clipboard.writeText(text).then(() => {
    showStatus(successMessage);
  });
}
