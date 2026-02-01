export function compressToolResult(result: any, maxChars: number) {
  const s = typeof result === "string" ? result : safeJson(result);
  if (s.length <= maxChars) return result;
  const head = s.slice(0, Math.floor(maxChars * 0.6));
  const tail = s.slice(-Math.floor(maxChars * 0.3));
  const out = `${head}\n[tool output truncated]\n${tail}`;
  return typeof result === "string" ? out : { truncated: true, preview: out };
}

function safeJson(x: any) {
  try {
    return JSON.stringify(x, null, 2);
  } catch {
    return String(x);
  }
}
