/**
 * OpenClaw memory plugin shim for keep.
 * 
 * Wraps the Python keep library via subprocess calls.
 * For production, consider a long-running Python service with HTTP/gRPC.
 */

import { Type } from "@sinclair/typebox";
import { spawn } from "child_process";

interface PluginApi {
  config: PluginConfig;
  logger: { info: (msg: string) => void; error: (msg: string) => void };
  registerTool: (tool: Tool, opts?: { optional?: boolean }) => void;
  registerCli: (fn: (ctx: CliContext) => void, opts: { commands: string[] }) => void;
  registerService: (svc: Service) => void;
}

interface PluginConfig {
  plugins?: {
    entries?: {
      "memory-keep"?: {
        config?: KeepConfig;
      };
    };
  };
  agents?: {
    defaults?: {
      workspace?: string;
    };
  };
}

interface KeepConfig {
  pythonPath?: string;
  halfLifeDays?: number;
  indexingMode?: "document" | "chunked" | "hybrid" | "bm25_only";
  embeddingProvider?: "sentence-transformers" | "openai" | "mlx";
  embeddingModel?: string;
  hybridSearch?: {
    enabled?: boolean;
    vectorWeight?: number;
    textWeight?: number;
  };
  cache?: {
    enabled?: boolean;
    maxEntries?: number;
  };
}

interface Tool {
  name: string;
  description: string;
  parameters: unknown;
  execute: (id: string, params: Record<string, unknown>) => Promise<ToolResult>;
}

interface ToolResult {
  content: Array<{ type: "text"; text: string }>;
}

interface CliContext {
  program: {
    command: (name: string) => {
      description: (desc: string) => CliContext["program"];
      option: (flags: string, desc: string) => CliContext["program"];
      action: (fn: (...args: unknown[]) => void | Promise<void>) => void;
    };
  };
}

interface Service {
  id: string;
  start: () => void | Promise<void>;
  stop: () => void | Promise<void>;
}

// Helper to call Python CLI
async function callKeep(
  config: KeepConfig,
  args: string[],
  workspace?: string
): Promise<string> {
  const python = config.pythonPath || "python3";
  const fullArgs = ["-m", "keep", ...args];
  
  // Add config flags
  if (config.halfLifeDays) {
    fullArgs.push("--decay-half-life", String(config.halfLifeDays));
  }
  if (config.indexingMode) {
    fullArgs.push("--mode", config.indexingMode);
  }
  if (config.embeddingProvider) {
    fullArgs.push("--embedding-provider", config.embeddingProvider);
  }
  
  return new Promise((resolve, reject) => {
    const proc = spawn(python, fullArgs, {
      cwd: workspace,
      env: { ...process.env },
    });
    
    let stdout = "";
    let stderr = "";
    
    proc.stdout.on("data", (data) => { stdout += data; });
    proc.stderr.on("data", (data) => { stderr += data; });
    
    proc.on("close", (code) => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(new Error(`keep exited with code ${code}: ${stderr}`));
      }
    });
  });
}

// Plugin entry point
export default function register(api: PluginApi) {
  const pluginConfig = api.config.plugins?.entries?.["memory-keep"]?.config ?? {};
  const workspace = api.config.agents?.defaults?.workspace ?? "~/.openclaw/workspace";
  
  // ─────────────────────────────────────────────────────────────
  // Tool: memory_search
  // ─────────────────────────────────────────────────────────────
  api.registerTool({
    name: "memory_search",
    description: 
      "Semantically search memory for relevant notes. " +
      "Returns snippets with file paths and line ranges. " +
      "Use this to recall context, facts, or past decisions.",
    parameters: Type.Object({
      query: Type.String({ description: "Natural language search query" }),
      limit: Type.Optional(Type.Number({ 
        description: "Maximum results to return",
        default: 5 
      })),
    }),
    async execute(_id, params) {
      const query = params.query as string;
      const limit = (params.limit as number) || 5;
      
      try {
        const output = await callKeep(
          pluginConfig,
          ["find", query, "--limit", String(limit), "--json"],
          workspace
        );
        
        const results = JSON.parse(output);
        
        // Format as OpenClaw expects
        const formatted = results.map((r: {
          source: string;
          start_line?: number;
          end_line?: number;
          score: number;
          snippet: string;
        }) => ({
          file: r.source,
          lineRange: r.start_line && r.end_line 
            ? [r.start_line, r.end_line] 
            : undefined,
          score: r.score,
          snippet: r.snippet?.slice(0, 700),  // OpenClaw caps at ~700 chars
        }));
        
        return {
          content: [{
            type: "text",
            text: JSON.stringify(formatted, null, 2),
          }],
        };
      } catch (err) {
        return {
          content: [{
            type: "text",
            text: `Memory search failed: ${err}`,
          }],
        };
      }
    },
  });

  // ─────────────────────────────────────────────────────────────
  // Tool: memory_get
  // ─────────────────────────────────────────────────────────────
  api.registerTool({
    name: "memory_get",
    description:
      "Read content from a memory file by path. " +
      "Use after memory_search to read full context.",
    parameters: Type.Object({
      path: Type.String({ description: "File path (workspace-relative)" }),
      startLine: Type.Optional(Type.Number({ description: "Starting line (1-based)" })),
      lines: Type.Optional(Type.Number({ description: "Number of lines to read" })),
    }),
    async execute(_id, params) {
      const path = params.path as string;
      const startLine = params.startLine as number | undefined;
      const lines = params.lines as number | undefined;
      
      try {
        const args = ["get", path];
        if (startLine) args.push("--start-line", String(startLine));
        if (lines) args.push("--lines", String(lines));
        args.push("--json");
        
        const output = await callKeep(pluginConfig, args, workspace);
        const result = JSON.parse(output);
        
        return {
          content: [{
            type: "text",
            text: result.content,
          }],
        };
      } catch (err) {
        return {
          content: [{
            type: "text",
            text: `Memory get failed: ${err}`,
          }],
        };
      }
    },
  });

  // ─────────────────────────────────────────────────────────────
  // CLI: openclaw memory ...
  // ─────────────────────────────────────────────────────────────
  api.registerCli(({ program }) => {
    const memory = program
      .command("memory")
      .description("Manage associative memory index");
    
    memory
      .command("status")
      .description("Show memory index status")
      .option("--deep", "Run diagnostics")
      .option("--index", "Reindex if dirty")
      .option("--agent <id>", "Scope to agent")
      .action(async (opts) => {
        try {
          const args = ["status"];
          if (opts.deep) args.push("--deep");
          if (opts.index) args.push("--reindex");
          
          const output = await callKeep(pluginConfig, args, workspace);
          console.log(output);
        } catch (err) {
          console.error(err);
          process.exit(1);
        }
      });
    
    memory
      .command("index")
      .description("Rebuild memory index")
      .option("--verbose", "Show details")
      .option("--agent <id>", "Scope to agent")
      .action(async (opts) => {
        try {
          const args = ["index"];
          if (opts.verbose) args.push("--verbose");
          
          const output = await callKeep(pluginConfig, args, workspace);
          console.log(output);
        } catch (err) {
          console.error(err);
          process.exit(1);
        }
      });
    
    memory
      .command("search <query>")
      .description("Search memory")
      .option("--limit <n>", "Max results", "5")
      .option("--agent <id>", "Scope to agent")
      .action(async (query, opts) => {
        try {
          const args = ["find", query, "--limit", opts.limit];
          const output = await callKeep(pluginConfig, args, workspace);
          console.log(output);
        } catch (err) {
          console.error(err);
          process.exit(1);
        }
      });
  }, { commands: ["memory"] });

  // ─────────────────────────────────────────────────────────────
  // Background service (optional watcher)
  // ─────────────────────────────────────────────────────────────
  api.registerService({
    id: "memory-keep-watcher",
    start: () => {
      api.logger.info("keep: watcher started (stub)");
      // TODO: watch workspace for .md changes, trigger reindex
    },
    stop: () => {
      api.logger.info("keep: watcher stopped");
    },
  });
  
  api.logger.info("memory-keep plugin loaded");
}
