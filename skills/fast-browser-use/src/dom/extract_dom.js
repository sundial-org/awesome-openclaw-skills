// ARIA Snapshot DOM Extraction
// Based on Playwright's ariaSnapshot.ts - generates ARIA-tree structure for AI consumption
JSON.stringify(
  (function () {
    "use strict";

    let currentIndex = 0;

    // Helper: normalize whitespace
    function normalizeWhiteSpace(text) {
      return text.replace(/\s+/g, " ").trim();
    }

    // Helper: check if element is visible for ARIA
    function isElementHiddenForAria(element) {
      const tagName = element.tagName;
      if (["STYLE", "SCRIPT", "NOSCRIPT", "TEMPLATE"].includes(tagName)) {
        return true;
      }

      const style = window.getComputedStyle(element);

      // Check display: contents
      if (style.display === "contents" && element.nodeName !== "SLOT") {
        let hasVisibleChild = false;
        for (let child of element.childNodes) {
          if (child.nodeType === 1 && !isElementHiddenForAria(child)) {
            hasVisibleChild = true;
            break;
          }
          if (
            child.nodeType === 3 &&
            child.textContent &&
            child.textContent.trim()
          ) {
            hasVisibleChild = true;
            break;
          }
        }
        if (!hasVisibleChild) return true;
      }

      // Check visibility
      if (style.visibility !== "visible") {
        return true;
      }

      // Check display: none and aria-hidden
      if (style.display === "none") {
        return true;
      }

      if (element.getAttribute("aria-hidden") === "true") {
        return true;
      }

      return false;
    }

    // Helper: check if element is visible (bounding box check)
    function isElementVisible(element) {
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    }

    // Helper: compute element box information
    function computeBox(element) {
      const style = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      const visible = rect.width > 0 && rect.height > 0;
      const inline = style.display === "inline";
      const cursor = style.cursor;

      return { visible, inline, cursor, rect };
    }

    // Helper: check if element receives pointer events
    function receivesPointerEvents(element) {
      const box = computeBox(element);
      if (!box.visible) return false;

      const style = window.getComputedStyle(element);
      return style.pointerEvents !== "none";
    }

    // Helper: get ARIA role for element
    function getAriaRole(element) {
      // Check explicit role
      const explicitRole = element.getAttribute("role");
      if (explicitRole) {
        const roles = explicitRole.split(" ").map((r) => r.trim());
        const validRole = roles[0]; // take first role
        if (validRole) return validRole;
      }

      // Implicit roles based on tag name
      const tagName = element.tagName;
      const implicitRoles = {
        BUTTON: "button",
        A: element.hasAttribute("href") ? "link" : null,
        INPUT: getInputRole(element),
        TEXTAREA: "textbox",
        SELECT:
          element.hasAttribute("multiple") || element.size > 1
            ? "listbox"
            : "combobox",
        H1: "heading",
        H2: "heading",
        H3: "heading",
        H4: "heading",
        H5: "heading",
        H6: "heading",
        IMG: element.getAttribute("alt") === "" ? "presentation" : "img",
        NAV: "navigation",
        MAIN: "main",
        ARTICLE: "article",
        SECTION:
          element.hasAttribute("aria-label") ||
          element.hasAttribute("aria-labelledby")
            ? "region"
            : null,
        HEADER: "banner",
        FOOTER: "contentinfo",
        ASIDE: "complementary",
        FORM: "form",
        TABLE: "table",
        UL: "list",
        OL: "list",
        LI: "listitem",
        P: "paragraph",
        DIALOG: "dialog",
        IFRAME: "iframe",
      };

      return implicitRoles[tagName] || "generic";
    }

    function getInputRole(input) {
      const type = (input.type || "text").toLowerCase();
      const roles = {
        button: "button",
        checkbox: "checkbox",
        radio: "radio",
        range: "slider",
        search: "searchbox",
        text: "textbox",
        email: "textbox",
        tel: "textbox",
        url: "textbox",
        number: "spinbutton",
      };
      return roles[type] || "textbox";
    }

    // Helper: get accessible name for element
    function getElementAccessibleName(element) {
      // Check aria-label
      const ariaLabel = element.getAttribute("aria-label");
      if (ariaLabel) return ariaLabel;

      // Check aria-labelledby
      const labelledBy = element.getAttribute("aria-labelledby");
      if (labelledBy) {
        const ids = labelledBy.split(/\s+/);
        const texts = ids
          .map((id) => {
            const el = document.getElementById(id);
            return el ? el.textContent : "";
          })
          .filter((t) => t);
        if (texts.length) return texts.join(" ");
      }

      // Check associated label (for inputs)
      if (
        element.tagName === "INPUT" ||
        element.tagName === "TEXTAREA" ||
        element.tagName === "SELECT"
      ) {
        const id = element.id;
        if (id) {
          const label = document.querySelector('label[for="' + id + '"]');
          if (label) return label.textContent || "";
        }
        // Check if wrapped in label
        const parentLabel = element.closest("label");
        if (parentLabel) {
          return parentLabel.textContent || "";
        }
      }

      // Check alt for images
      if (element.tagName === "IMG") {
        return element.getAttribute("alt") || "";
      }

      // Check title
      const title = element.getAttribute("title");
      if (title) return title;

      // Check placeholder for inputs
      if (element.tagName === "INPUT" || element.tagName === "TEXTAREA") {
        const placeholder = element.getAttribute("placeholder");
        if (placeholder) return placeholder;
      }

      // For links and buttons, use text content if no other name found
      if (element.tagName === "A" || element.tagName === "BUTTON") {
        const text = element.textContent || "";
        if (text.trim()) return text.trim();
      }

      return "";
    }

    // Helper: get ARIA checked state
    function getAriaChecked(element) {
      const checked = element.getAttribute("aria-checked");
      if (checked === "true") return true;
      if (checked === "false") return false;
      if (checked === "mixed") return "mixed";

      // Native checkbox/radio
      if (element.tagName === "INPUT") {
        if (element.type === "checkbox" || element.type === "radio") {
          return element.checked;
        }
      }

      return undefined;
    }

    // Helper: get ARIA disabled state
    function getAriaDisabled(element) {
      const disabled = element.getAttribute("aria-disabled");
      if (disabled === "true") return true;

      // Native disabled
      if (element.disabled !== undefined) {
        return element.disabled;
      }

      return undefined;
    }

    // Helper: get ARIA expanded state
    function getAriaExpanded(element) {
      const expanded = element.getAttribute("aria-expanded");
      if (expanded === "true") return true;
      if (expanded === "false") return false;
      return undefined;
    }

    // Helper: get ARIA level
    function getAriaLevel(element) {
      const level = element.getAttribute("aria-level");
      if (level) {
        const num = parseInt(level, 10);
        if (!isNaN(num)) return num;
      }

      // Heading level
      if (element.tagName.match(/^H[1-6]$/)) {
        return parseInt(element.tagName[1], 10);
      }

      return undefined;
    }

    // Helper: get ARIA pressed state
    function getAriaPressed(element) {
      const pressed = element.getAttribute("aria-pressed");
      if (pressed === "true") return true;
      if (pressed === "false") return false;
      if (pressed === "mixed") return "mixed";
      return undefined;
    }

    // Helper: get ARIA selected state
    function getAriaSelected(element) {
      const selected = element.getAttribute("aria-selected");
      if (selected === "true") return true;
      if (selected === "false") return false;
      return undefined;
    }

    // Helper: get CSS content (::before, ::after)
    function getCSSContent(element, pseudo) {
      try {
        const style = window.getComputedStyle(element, pseudo);
        const content = style.content;
        if (content && content !== "none" && content !== "normal") {
          // Simple extraction - remove quotes
          return content.replace(/^["']|["']$/g, "");
        }
      } catch (e) {
        // Ignore errors
      }
      return "";
    }

    // Compute ARIA index for element
    function computeAriaIndex(ariaNode) {
      // Only assign indices to visible, interactive ARIA roles
      if (!ariaNode.box.visible) {
        return;
      }

      // Check if this is an interactive role that should have an index
      const interactiveRoles = [
        "button",
        "link",
        "textbox",
        "searchbox",
        "checkbox",
        "radio",
        "combobox",
        "listbox",
        "option",
        "menuitem",
        "menuitemcheckbox",
        "menuitemradio",
        "tab",
        "tabpanel",
        "slider",
        "spinbutton",
        "switch",
        "img",
        "article",
        "region",
        "navigation",
        "main",
        "complementary",
        "banner",
        "contentinfo",
        "form",
        "search",
        "tree",
        "treeitem",
        "grid",
        "gridcell",
        "row",
        "columnheader",
        "rowheader",
        "heading",
        "dialog",
        "alertdialog",
        "alert",
        "status",
        "progressbar",
        "list",
        "listitem",
        "generic",
      ];

      // Only assign index to interactive roles or elements with pointer cursor
      const hasPointerCursor = ariaNode.box.cursor === "pointer";
      const isInteractiveRole = interactiveRoles.includes(ariaNode.role);

      if (!isInteractiveRole && !hasPointerCursor) {
        return;
      }

      // Assign sequential index
      ariaNode.index = currentIndex++;
    }

    // Convert element to AriaNode
    function toAriaNode(element) {
      const active = document.activeElement === element;

      // Handle iframe specially
      if (element.tagName === "IFRAME") {
        const ariaNode = {
          role: "iframe",
          name: "",
          children: [],
          props: {},
          element: element,
          box: computeBox(element),
          receivesPointerEvents: true,
          active: active,
        };
        computeAriaIndex(ariaNode);
        return ariaNode;
      }

      const role = getAriaRole(element);

      // Skip elements without role or with presentation/none
      if (!role || role === "presentation" || role === "none") {
        return null;
      }

      const name = normalizeWhiteSpace(getElementAccessibleName(element) || "");
      const box = computeBox(element);

      // Skip inline generic elements with just text
      if (
        role === "generic" &&
        box.inline &&
        element.childNodes.length === 1 &&
        element.childNodes[0].nodeType === 3
      ) {
        return null;
      }

      const result = {
        role: role,
        name: name,
        children: [],
        props: {},
        element: element,
        box: box,
        receivesPointerEvents: receivesPointerEvents(element),
        active: active,
      };

      computeAriaIndex(result);

      // Add ARIA properties based on role
      const checkedRoles = [
        "checkbox",
        "menuitemcheckbox",
        "menuitemradio",
        "radio",
        "switch",
      ];
      if (checkedRoles.includes(role)) {
        const checked = getAriaChecked(element);
        if (checked !== undefined) result.checked = checked;
      }

      const disabledRoles = ["button", "input", "select", "textarea"];
      if (disabledRoles.includes(role) || role.includes("menuitem")) {
        const disabled = getAriaDisabled(element);
        if (disabled !== undefined) result.disabled = disabled;
      }

      const expandedRoles = [
        "button",
        "combobox",
        "gridcell",
        "link",
        "menuitem",
        "row",
        "tab",
        "treeitem",
      ];
      if (expandedRoles.includes(role)) {
        const expanded = getAriaExpanded(element);
        if (expanded !== undefined) result.expanded = expanded;
      }

      const levelRoles = ["heading", "listitem", "row", "treeitem"];
      if (levelRoles.includes(role)) {
        const level = getAriaLevel(element);
        if (level !== undefined) result.level = level;
      }

      const pressedRoles = ["button"];
      if (pressedRoles.includes(role)) {
        const pressed = getAriaPressed(element);
        if (pressed !== undefined) result.pressed = pressed;
      }

      const selectedRoles = ["gridcell", "option", "row", "tab", "treeitem"];
      if (selectedRoles.includes(role)) {
        const selected = getAriaSelected(element);
        if (selected !== undefined) result.selected = selected;
      }

      // Special handling for input/textarea values
      if (element.tagName === "INPUT" || element.tagName === "TEXTAREA") {
        if (
          element.type !== "checkbox" &&
          element.type !== "radio" &&
          element.type !== "file"
        ) {
          result.children = [element.value || ""];
        }
      }

      return result;
    }

    // Main visitor function
    function visit(ariaNode, node, parentElementVisible, visited) {
      if (visited.has(node)) return;
      visited.add(node);

      // Handle text nodes
      if (node.nodeType === 3) {
        // TEXT_NODE
        if (!parentElementVisible) return;

        const text = node.nodeValue;
        // Skip text inside textbox
        if (ariaNode.role !== "textbox" && text) {
          ariaNode.children.push(text);
        }
        return;
      }

      // Only process element nodes
      if (node.nodeType !== 1) return; // ELEMENT_NODE

      const element = node;

      // Check visibility
      const isElementVisibleForAria = !isElementHiddenForAria(element);
      let visible = isElementVisibleForAria || isElementVisible(element);

      // Skip if not visible for ARIA
      if (!visible) return;

      // Handle aria-owns
      const ariaChildren = [];
      if (element.hasAttribute("aria-owns")) {
        const ids = element.getAttribute("aria-owns").split(/\s+/);
        for (const id of ids) {
          const ownedElement = document.getElementById(id);
          if (ownedElement) ariaChildren.push(ownedElement);
        }
      }

      // Convert to aria node
      const childAriaNode = toAriaNode(element);
      if (childAriaNode) {
        ariaNode.children.push(childAriaNode);
      }

      // Process element (add CSS content, children, etc.)
      processElement(
        childAriaNode || ariaNode,
        element,
        ariaChildren,
        visible,
        visited,
      );
    }

    function processElement(
      ariaNode,
      element,
      ariaChildren,
      parentElementVisible,
      visited,
    ) {
      const style = window.getComputedStyle(element);
      const display = style ? style.display : "inline";
      const treatAsBlock =
        display !== "inline" || element.nodeName === "BR" ? " " : "";

      if (treatAsBlock) {
        ariaNode.children.push(treatAsBlock);
      }

      // Add ::before content
      const beforeContent = getCSSContent(element, "::before");
      if (beforeContent) {
        ariaNode.children.push(beforeContent);
      }

      // Process shadow DOM slots
      if (element.nodeName === "SLOT") {
        const assignedNodes = element.assignedNodes();
        for (const child of assignedNodes) {
          visit(ariaNode, child, parentElementVisible, visited);
        }
      } else {
        // Process regular children
        for (let child = element.firstChild; child; child = child.nextSibling) {
          if (!child.assignedSlot) {
            visit(ariaNode, child, parentElementVisible, visited);
          }
        }

        // Process shadow root
        if (element.shadowRoot) {
          for (
            let child = element.shadowRoot.firstChild;
            child;
            child = child.nextSibling
          ) {
            visit(ariaNode, child, parentElementVisible, visited);
          }
        }
      }

      // Process aria-owns children
      for (const child of ariaChildren) {
        visit(ariaNode, child, parentElementVisible, visited);
      }

      // Add ::after content
      const afterContent = getCSSContent(element, "::after");
      if (afterContent) {
        ariaNode.children.push(afterContent);
      }

      if (treatAsBlock) {
        ariaNode.children.push(treatAsBlock);
      }

      // Remove redundant children
      if (
        ariaNode.children.length === 1 &&
        ariaNode.name === ariaNode.children[0]
      ) {
        ariaNode.children = [];
      }

      // Add special props
      if (ariaNode.role === "link" && element.hasAttribute("href")) {
        ariaNode.props.url = element.getAttribute("href");
      }

      if (ariaNode.role === "textbox" && element.hasAttribute("placeholder")) {
        const placeholder = element.getAttribute("placeholder");
        if (placeholder !== ariaNode.name) {
          ariaNode.props.placeholder = placeholder;
        }
      }
    }

    // Normalize string children
    function normalizeStringChildren(ariaNode) {
      const normalizedChildren = [];
      let buffer = [];

      function flushBuffer() {
        if (buffer.length === 0) return;
        const text = normalizeWhiteSpace(buffer.join(""));
        if (text) {
          normalizedChildren.push(text);
        }
        buffer = [];
      }

      for (const child of ariaNode.children || []) {
        if (typeof child === "string") {
          buffer.push(child);
        } else {
          flushBuffer();
          normalizeStringChildren(child);
          normalizedChildren.push(child);
        }
      }
      flushBuffer();

      ariaNode.children = normalizedChildren;

      // Remove if child equals name
      if (
        ariaNode.children.length === 1 &&
        ariaNode.children[0] === ariaNode.name
      ) {
        ariaNode.children = [];
      }
    }

    // Normalize generic roles (remove unnecessary generic wrappers)
    function normalizeGenericRoles(node) {
      function normalizeChildren(node) {
        const result = [];

        for (const child of node.children || []) {
          if (typeof child === "string") {
            result.push(child);
            continue;
          }

          const normalized = normalizeChildren(child);
          result.push(...normalized);
        }

        // Remove generic that encloses single element
        const removeSelf =
          node.role === "generic" &&
          !node.name &&
          result.length <= 1 &&
          result.every((c) => typeof c !== "string" && c.index !== undefined);

        if (removeSelf) {
          return result;
        }

        node.children = result;
        return [node];
      }

      normalizeChildren(node);
    }

    // Serialize ariaNode to plain object (remove Element references)
    function serializeAriaNode(ariaNode) {
      const result = {
        role: ariaNode.role,
        name: ariaNode.name,
        children: [],
        props: ariaNode.props,
      };

      // Include index if present
      if (ariaNode.index !== undefined) result.index = ariaNode.index;
      if (ariaNode.active) result.active = true;
      if (ariaNode.checked !== undefined) result.checked = ariaNode.checked;
      if (ariaNode.disabled !== undefined) result.disabled = ariaNode.disabled;
      if (ariaNode.expanded !== undefined) result.expanded = ariaNode.expanded;
      if (ariaNode.level !== undefined) result.level = ariaNode.level;
      if (ariaNode.pressed !== undefined) result.pressed = ariaNode.pressed;
      if (ariaNode.selected !== undefined) result.selected = ariaNode.selected;

      // Serialize box info
      result.box_info = {
        visible: ariaNode.box.visible,
        cursor: ariaNode.box.cursor,
        rect: ariaNode.box.rect,
      };

      // Serialize children
      for (const child of ariaNode.children) {
        if (typeof child === "string") {
          result.children.push(child);
        } else {
          result.children.push(serializeAriaNode(child));
        }
      }

      return result;
    }

    // Collect selectors and iframe indices
    function collectSelectorsAndIframes(ariaNode, selectors, iframeIndices) {
      if (ariaNode.index !== undefined && ariaNode.element) {
        // Store CSS selector for element at its index position
        const selector = buildSelector(ariaNode.element);
        // Ensure selectors array is large enough
        while (selectors.length <= ariaNode.index) {
          selectors.push("");
        }
        selectors[ariaNode.index] = selector;

        if (ariaNode.role === "iframe") {
          iframeIndices.push(ariaNode.index);
        }
      }

      for (const child of ariaNode.children) {
        if (typeof child !== "string") {
          collectSelectorsAndIframes(child, selectors, iframeIndices);
        }
      }
    }

    // Build CSS selector for element
    function buildSelector(element) {
      if (element.id) {
        return "#" + element.id;
      }

      const path = [];
      let current = element;

      while (current && current !== document.body) {
        let selector = current.tagName.toLowerCase();

        if (current.className && typeof current.className === "string") {
          const classes = current.className.trim().split(/\s+/);
          if (classes.length > 0 && classes[0]) {
            selector += "." + classes[0];
          }
        }

        // Add nth-child if needed for uniqueness
        const parent = current.parentElement;
        if (parent) {
          const siblings = Array.from(parent.children);
          const index = siblings.indexOf(current);
          if (
            siblings.filter((s) => s.tagName === current.tagName).length > 1
          ) {
            selector += ":nth-child(" + (index + 1) + ")";
          }
        }

        path.unshift(selector);
        current = current.parentElement;
      }

      return path.join(" > ");
    }

    // Main execution
    try {
      const rootElement = document.body || document.documentElement;
      const visited = new Set();

      // Reset index counter
      currentIndex = 0;

      // Create root fragment node
      const snapshot = {
        role: "fragment",
        name: "",
        children: [],
        props: {},
        element: rootElement,
        box: computeBox(rootElement),
        receivesPointerEvents: true,
      };

      // Visit the DOM tree
      visit(snapshot, rootElement, true, visited);

      // Normalize
      normalizeStringChildren(snapshot);
      normalizeGenericRoles(snapshot);

      // Collect selectors and iframe indices
      const selectors = [];
      const iframeIndices = [];
      collectSelectorsAndIframes(snapshot, selectors, iframeIndices);

      // Serialize and return
      const serialized = serializeAriaNode(snapshot);

      return {
        root: serialized,
        selectors: selectors,
        iframeIndices: iframeIndices,
      };
    } catch (error) {
      return {
        error: error.toString(),
        root: {
          role: "fragment",
          name: "",
          children: [],
          props: {},
          box_info: { visible: false },
        },
        selectors: [],
        iframeIndices: [],
      };
    }
  })(),
);
