import fs from "node:fs/promises";
import nodePath from "node:path";

export async function loadMemoryFiles(files: string[]) {
  const parts: string[] = [];
  for (const f of files) {
    try {
      const txt = await fs.readFile(f, "utf8");
      parts.push(`## ${f}\n${txt}\n`);
    } catch {
      // Missing files are fine. Keep routine resilient.
    }
  }
  return parts.join("\n");
}

export async function appendAfterAction(opts: {
  filePath: string;
  sessionId: string;
  runId: string;
  maxBullets: number;
  finalAnswer: string;
  toolCalls: Array<{ name: string; ok?: boolean }>;
}) {
  const toolLine = (opts.toolCalls || [])
    .slice(0, 12)
    .map((t) => `- ${t.name}${t.ok === false ? " (failed)" : ""}`)
    .join("\n");

  const bullets = deriveBullets(opts.finalAnswer, opts.maxBullets)
    .map((b) => `- ${b}`)
    .join("\n");

  const entry =
    `\n## After Action Review\n` +
    `session: ${opts.sessionId}\n` +
    `run: ${opts.runId}\n\n` +
    `### What happened\n${bullets}\n\n` +
    `### Tools used\n${toolLine || "- none"}\n`;

  await fs.mkdir(nodePath.dirname(opts.filePath), { recursive: true });
  await fs.appendFile(opts.filePath, entry, "utf8");
}

function deriveBullets(finalAnswer: string, maxBullets: number) {
  const lines = (finalAnswer || "")
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
  const bullets: string[] = [];
  for (const l of lines) {
    if (bullets.length >= maxBullets) break;
    if (l.length < 8) continue;
    bullets.push(l.slice(0, 180));
  }
  if (bullets.length === 0) bullets.push("Completed run. No durable notes extracted.");
  return bullets;
}
