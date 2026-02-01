/* eslint-disable no-unused-vars */

const SCROLL_PADDING = 20;
const INITIAL_SCROLL_DELAY_MS = 100;
const HEADER_SELECTOR =
  '#markdown-content h1, #markdown-content h2, #markdown-content h3, #markdown-content h4, #markdown-content h5, #markdown-content h6';

const container = document.getElementById('content');
const markdownContent = base64DecodeUnicode('MARKDOWN_CONTENT');

if (typeof mermaid !== 'undefined') {
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'strict',
  });
}

const renderer = new marked.Renderer();

renderer.heading = function (text, level, raw) {
  const id = raw
    .toLowerCase()
    .replace(/<[^>]*>/g, '')
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
  return `<h${level} id="${id}">${text}</h${level}>`;
};

marked.setOptions({
  breaks: true,
  gfm: true,
  renderer: renderer,
});

const rawHtml = marked.parse(markdownContent);
const renderedHtml = DOMPurify.sanitize(rawHtml, {
  ALLOWED_TAGS: [
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'p',
    'a',
    'ul',
    'ol',
    'li',
    'blockquote',
    'code',
    'pre',
    'strong',
    'em',
    'del',
    'br',
    'hr',
    'table',
    'thead',
    'tbody',
    'tr',
    'th',
    'td',
    'img',
    'div',
    'span',
    'input',
    'label',
    'details',
    'summary',
  ],
  ALLOWED_ATTR: [
    'href',
    'src',
    'alt',
    'title',
    'class',
    'id',
    'type',
    'checked',
    'disabled',
    'open',
  ],
  ALLOW_DATA_ATTR: false,
  ALLOW_UNKNOWN_PROTOCOLS: false,
  SAFE_FOR_JQUERY: true,
});

const lines = markdownContent.split('\n').length;
const words = markdownContent.split(/\s+/).filter((w) => w.length > 0).length;
const chars = markdownContent.length;
const stats = `${lines} lines • ${words} words • ${chars} chars`;

const toolbarItems = [
  createButton('Copy Markdown', 'copyMarkdown()', '📋'),
  createButton('Copy HTML', 'copyHTML()', '📄'),
];

container.innerHTML =
  createHeader('Markdown Preview', stats, toolbarItems) +
  '<div class="preview-body"><div id="markdown-content"></div></div>' +
  createFooter();

document.getElementById('markdown-content').innerHTML = renderedHtml;

if (typeof mermaid !== 'undefined') {
  renderMermaidDiagrams();
}

addHeaderAnchors();
setupAnchorScrolling();
handleInitialHash();

function copyMarkdown() {
  copyToClipboard(markdownContent, 'Markdown copied to clipboard!');
}

function copyHTML() {
  copyToClipboard(renderedHtml, 'HTML copied to clipboard!');
}

function renderMermaidDiagrams() {
  const codeBlocks = document.querySelectorAll('code.language-mermaid');
  let diagramIndex = 0;

  codeBlocks.forEach((codeBlock) => {
    const pre = codeBlock.parentElement;
    const diagramCode = codeBlock.textContent;
    const diagramId = `mermaid-diagram-${diagramIndex++}`;

    const diagramContainer = document.createElement('div');
    diagramContainer.className = 'mermaid-container';
    diagramContainer.style.textAlign = 'center';
    diagramContainer.style.margin = '20px 0';

    const diagramDiv = document.createElement('div');
    diagramDiv.id = diagramId;
    diagramDiv.className = 'mermaid';
    diagramDiv.textContent = diagramCode;

    diagramContainer.appendChild(diagramDiv);
    pre.parentNode.replaceChild(diagramContainer, pre);
  });

  if (diagramIndex > 0) {
    mermaid.run({ querySelector: '.mermaid' });
  }
}

function addHeaderAnchors() {
  const headers = document.querySelectorAll(HEADER_SELECTOR);

  headers.forEach((header) => {
    if (!header.id) return;

    const anchor = document.createElement('a');
    anchor.className = 'header-anchor';
    anchor.href = `#${header.id}`;
    anchor.setAttribute('aria-label', `Link to ${header.textContent}`);
    anchor.textContent = '#';

    header.insertBefore(anchor, header.firstChild);
  });
}

function setupAnchorScrolling() {
  const previewBody = document.querySelector('.preview-body');
  if (!previewBody) return;

  function handleAnchorClick(e) {
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;

    const targetId = link.getAttribute('href').slice(1);
    const targetElement = document.getElementById(targetId);
    if (!targetElement) return;

    e.preventDefault();
    history.pushState(null, '', `#${targetId}`);
    scrollToElement(targetElement, previewBody);
  }

  document.addEventListener('click', handleAnchorClick);

  window.addEventListener('unload', function cleanup() {
    document.removeEventListener('click', handleAnchorClick);
    window.removeEventListener('unload', cleanup);
  });
}

function handleInitialHash() {
  const previewBody = document.querySelector('.preview-body');
  if (!window.location.hash || !previewBody) return;

  const targetId = window.location.hash.slice(1);
  const targetElement = document.getElementById(targetId);
  if (!targetElement) return;

  setTimeout(() => scrollToElement(targetElement, previewBody), INITIAL_SCROLL_DELAY_MS);
}

function scrollToElement(element, container) {
  const containerRect = container.getBoundingClientRect();
  const elementRect = element.getBoundingClientRect();
  const scrollTop = container.scrollTop + (elementRect.top - containerRect.top) - SCROLL_PADDING;

  container.scrollTo({ top: scrollTop, behavior: 'smooth' });
}
