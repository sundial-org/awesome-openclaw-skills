(async function () {
  const config = __SCROLL_CONFIG__;
  const beforeScrollY = window.scrollY;
  const scrollAmount =
    typeof config.amount === "number" ? config.amount : window.innerHeight;

  window.scrollBy(0, scrollAmount);

  await new Promise((resolve) => setTimeout(resolve, 100));

  const actualScroll = window.scrollY - beforeScrollY;
  const scrollHeight = Math.max(
    document.documentElement.scrollHeight,
    document.body.scrollHeight,
  );
  const scrollTop = window.scrollY;
  const clientHeight =
    window.innerHeight || document.documentElement.clientHeight;
  const isAtBottom = Math.abs(scrollHeight - scrollTop - clientHeight) <= 1;

  return JSON.stringify({ actualScroll, isAtBottom });
})();
