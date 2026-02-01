// Enhanced JavaScript code to convert HTML to markdown using Mozilla Readability
// Based on UI-TARS implementation
// Returns JSON string with title, HTML content, and metadata

(function () {
  try {
    // Load Readability constructor from the injected script
    // The script should be injected as READABILITY_SCRIPT constant
    if (typeof READABILITY_SCRIPT === "undefined") {
      throw new Error(
        "READABILITY_SCRIPT not defined. Readability.js must be injected first.",
      );
    }

    // Always re-evaluate Readability to ensure fresh instance
    // This prevents issues with state pollution between multiple calls
    // Use Function constructor instead of eval to create a clean scope
    var ReadabilityConstructor;
    var __readabilityModule = { exports: {} };

    // Create an isolated function scope for Readability
    var loadReadability = new Function(
      "module",
      "exports",
      READABILITY_SCRIPT + "; return module.exports;",
    );
    ReadabilityConstructor = loadReadability(
      __readabilityModule,
      __readabilityModule.exports,
    );

    if (!ReadabilityConstructor) {
      throw new Error("Failed to load Readability constructor");
    }

    // Clone the document to avoid DOM flickering (visual artifacts)
    // This prevents the page from changing appearance during extraction
    // Use deep clone with true parameter to ensure all children are cloned
    var documentClone = document.cloneNode(true);

    // Clean up unwanted elements from the clone
    // These elements don't contribute to the main content and can interfere with extraction
    var elementsToRemove = [
      "script", // JavaScript code
      "noscript", // Fallback content
      "style", // CSS styles
      "link", // External resources
      "svg", // Vector graphics
      "img", // Images (handled separately by Readability)
      "video", // Videos
      "iframe", // Embedded frames
      "canvas", // Canvas elements
      ".reflist", // Reference lists (Wikipedia-style)
    ];

    documentClone
      .querySelectorAll(elementsToRemove.join(","))
      .forEach(function (el) {
        el.remove();
      });

    // Use Mozilla Readability algorithm to extract main content
    // This filters out navigation, ads, sidebars, etc.
    var reader = new ReadabilityConstructor(documentClone);
    var article = reader.parse();

    if (!article) {
      // Readability failed to extract content, fall back to basic extraction
      // This can happen on pages with insufficient content or unusual structure
      var fallbackContent = document.body ? document.body.innerHTML : "";
      var fallbackText = document.body ? document.body.textContent : "";

      return JSON.stringify({
        title: document.title || "",
        content: fallbackContent,
        textContent: fallbackText,
        url: window.location.href,
        excerpt: "",
        byline: "",
        siteName: "",
        length: fallbackText.length,
        lang: document.documentElement.lang || "",
        dir: document.documentElement.dir || "",
        publishedTime: "",
        readabilityFailed: true,
        error: "Readability.parse() returned null - using fallback extraction",
      });
    }

    // Return structured data as JSON string
    // The HTML content will be converted to Markdown on the Rust side
    return JSON.stringify({
      title: article.title || document.title || "",
      content: article.content || "", // Main HTML content
      textContent: article.textContent || "", // Plain text version
      url: window.location.href,
      excerpt: article.excerpt || "",
      byline: article.byline || "",
      siteName: article.siteName || "",
      length: article.length || 0,
      lang: article.lang || document.documentElement.lang || "",
      dir: article.dir || document.documentElement.dir || "",
      publishedTime: article.publishedTime || "",
      readabilityFailed: false,
    });
  } catch (error) {
    // If anything goes wrong, return error information
    return JSON.stringify({
      title: document.title || "",
      content: "",
      textContent: "",
      url: window.location.href,
      error: error.message + " (stack: " + (error.stack || "no stack") + ")",
      readabilityFailed: true,
    });
  }
})();
