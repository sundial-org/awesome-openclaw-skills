import path from "node:path";
import { buildBriefingPacket } from "./briefing";
import { loadMemoryFiles, appendAfterAction } from "./memory";
import { compressToolResult } from "./compress";

export default function register(api: any) {
  const cfg = api.config?.plugins?.entries?.["memory-pipeline"] ?? {};
  if (cfg.enabled === false) return;

  const briefingCfg = cfg.briefing ?? {};
  const toolsCfg = cfg.tools ?? {};
  const afterActionCfg = cfg.afterAction ?? {};

  // 1) Purposeful Thinking: build a briefing packet before each run.
  api.hooks.on("before_agent_start", async (ctx: any) => {
    const workspaceRoot = ctx.workspaceRoot ?? api.config?.agents?.defaults?.workspace;
    const files = (briefingCfg.memoryFiles ?? []).map((p: string) =>
      path.isAbsolute(p) ? p : path.join(workspaceRoot, p)
    );
    const memoryText = await loadMemoryFiles(files);
    const packet = buildBriefingPacket({
      checklist: briefingCfg.checklist ?? [],
      memoryText,
      maxChars: briefingCfg.maxChars ?? 6000,
      taskHint: ctx.input?.message ?? "",
    });
    ctx.systemPromptAppend?.(`\n${packet}\n`);
    ctx.systemPromptParts?.push(packet);
    return ctx;
  });

  // 2) Reactive Execution: enforce discipline right before tool calls.
  api.hooks.on("before_tool_call", async (ctx: any) => {
    const deny: string[] = toolsCfg.deny ?? [];
    const toolName = ctx.tool?.name;
    if (toolName && deny.includes(toolName)) {
      throw new Error(`Tool denied by performance-routine policy: ${toolName}`);
    }
    return ctx;
  });

  // 3) Prevent tool bloat: compress tool results before persisting.
  api.hooks.on("tool_result_persist", async (ctx: any) => {
    const limit = toolsCfg.maxToolResultChars ?? 12000;
    ctx.toolResult = compressToolResult(ctx.toolResult, limit);
    return ctx;
  });

  // 4) After Action Review: write durable notes at the end of the run.
  api.hooks.on("agent_end", async (ctx: any) => {
    const workspaceRoot = ctx.workspaceRoot ?? api.config?.agents?.defaults?.workspace;
    const outFile = path.isAbsolute(afterActionCfg.writeMemoryFile)
      ? afterActionCfg.writeMemoryFile
      : path.join(workspaceRoot, afterActionCfg.writeMemoryFile ?? "memory/AFTER_ACTION.md");
    const maxBullets = afterActionCfg.maxBullets ?? 8;
    await appendAfterAction({
      filePath: outFile,
      sessionId: ctx.sessionId,
      runId: ctx.runId,
      maxBullets,
      finalAnswer: ctx.finalAnswerText ?? "",
      toolCalls: ctx.toolCalls ?? [],
    });
    return ctx;
  });
}
