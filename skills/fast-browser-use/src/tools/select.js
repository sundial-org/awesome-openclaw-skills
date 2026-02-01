JSON.stringify(
  (function () {
    const config = __SELECT_CONFIG__;
    const element = document.querySelector(config.selector);

    if (!element) {
      return { success: false, error: "Element not found" };
    }

    if (element.tagName !== "SELECT") {
      return { success: false, error: "Element is not a SELECT element" };
    }

    element.value = config.value;
    element.dispatchEvent(new Event("change", { bubbles: true }));

    return {
      success: true,
      selectedValue: element.value,
      selectedText: element.options[element.selectedIndex]?.text ?? null,
    };
  })(),
);
