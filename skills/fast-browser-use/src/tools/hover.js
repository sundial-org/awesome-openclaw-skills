JSON.stringify(
  (function () {
    const selector = __SELECTOR__;
    const element = document.querySelector(selector);
    if (!element) {
      return { success: false, error: "Element not found" };
    }

    element.scrollIntoView({
      behavior: "auto",
      block: "center",
      inline: "center",
    });

    const rect = element.getBoundingClientRect();
    const event = new MouseEvent("mouseover", {
      view: window,
      bubbles: true,
      cancelable: true,
      clientX: rect.left + rect.width / 2,
      clientY: rect.top + rect.height / 2,
    });

    element.dispatchEvent(event);

    return {
      success: true,
      tagName: element.tagName,
      id: element.id,
      className: element.className,
    };
  })(),
);
