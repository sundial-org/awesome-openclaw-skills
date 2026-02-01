//==============================================================================
// AUTO-GENERATED - DO NOT EDIT
//==============================================================================
// Source: src/core/templates/scripts/utils.js
// To edit: Modify source file, then run: src/scripts/sync-skills.sh
//==============================================================================

/**
 * Browser Utilities for Preview Skills
 */

/**
 * UTF-8 safe base64 decode
 * Handles Unicode characters properly
 * @param {string} str - Base64 encoded string
 * @returns {string} Decoded UTF-8 string
 */
// eslint-disable-next-line no-unused-vars
function base64DecodeUnicode(str) {
  return decodeURIComponent(
    atob(str)
      .split('')
      .map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      })
      .join('')
  );
}

/**
 * Get element by ID safely
 * @param {string} id - Element ID
 * @returns {HTMLElement|null} Element or null if not found
 */
function getElement(id) {
  return document.getElementById(id);
}

/**
 * Set element content
 * @param {string} id - Element ID
 * @param {string} content - HTML content to set
 * @deprecated WARNING: This function uses innerHTML and should ONLY be used
 * with trusted/sanitized content. For untrusted content, use textContent
 * or sanitize with DOMPurify first. Consider using setTextContent() instead.
 */
// eslint-disable-next-line no-unused-vars
function setContent(id, content) {
  const element = getElement(id);
  if (element) {
    element.innerHTML = content;
  }
}

/**
 * Set element text content safely (XSS-safe)
 * @param {string} id - Element ID
 * @param {string} text - Plain text content to set
 */
// eslint-disable-next-line no-unused-vars
function setTextContent(id, text) {
  const element = getElement(id);
  if (element) {
    element.textContent = text;
  }
}
