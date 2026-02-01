export function buildBriefingPacket(opts: {
  checklist: string[];
  memoryText: string;
  maxChars: number;
  taskHint: string;
}) {
  const header =
    `# Pre-Game Routine\n` +
    `Task hint: ${truncate(opts.taskHint, 240)}\n\n` +
    `## Checklist\n` +
    opts.checklist.map((x) => `- ${x}`).join("\n") +
    `\n\n## Retrieved Memory (bounded)\n`;
  const body = truncate(opts.memoryText, Math.max(0, opts.maxChars - header.length));
  return truncate(header + body, opts.maxChars);
}

function truncate(s: string, n: number) {
  if (!s) return "";
  if (s.length <= n) return s;
  return s.slice(0, Math.max(0, n - 20)) + "\n[truncated]\n";
}
