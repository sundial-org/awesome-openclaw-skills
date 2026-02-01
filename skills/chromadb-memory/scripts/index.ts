/**
 * ChromaDB Memory Plugin for OpenClaw
 *
 * Provides:
 * 1. chromadb_search tool - manual semantic search over ChromaDB
 * 2. Auto-recall - injects relevant memories before each agent turn
 *
 * Uses local Ollama (nomic-embed-text) for embeddings. No cloud APIs.
 */

// Use plain JSON Schema instead of typebox (not available in workspace context)
type OpenClawPluginApi = any;

// ============================================================================
// Config
// ============================================================================

interface ChromaDBConfig {
  chromaUrl: string;
  collectionId: string;
  ollamaUrl: string;
  embeddingModel: string;
  autoRecall: boolean;
  autoRecallResults: number;
  minScore: number;
}

function parseConfig(raw: unknown): ChromaDBConfig {
  const cfg = (raw ?? {}) as Record<string, unknown>;
  return {
    chromaUrl: (cfg.chromaUrl as string) || "http://localhost:8100",
    collectionId: cfg.collectionId as string,
    ollamaUrl: (cfg.ollamaUrl as string) || "http://localhost:11434",
    embeddingModel: (cfg.embeddingModel as string) || "nomic-embed-text",
    autoRecall: cfg.autoRecall !== false,
    autoRecallResults: (cfg.autoRecallResults as number) || 3,
    minScore: (cfg.minScore as number) || 0.5,
  };
}

// ============================================================================
// Ollama Embeddings
// ============================================================================

async function getEmbedding(
  ollamaUrl: string,
  model: string,
  text: string,
): Promise<number[]> {
  const resp = await fetch(`${ollamaUrl}/api/embeddings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, prompt: text }),
  });

  if (!resp.ok) {
    throw new Error(`Ollama embedding failed: ${resp.status} ${resp.statusText}`);
  }

  const data = (await resp.json()) as { embedding: number[] };
  return data.embedding;
}

// ============================================================================
// ChromaDB Client
// ============================================================================

interface ChromaResult {
  source: string;
  text: string;
  distance: number;
  score: number;
  metadata: Record<string, string>;
}

const CHROMA_BASE = "/api/v2/tenants/default_tenant/databases/default_database/collections";

async function queryChromaDB(
  chromaUrl: string,
  collectionId: string,
  embedding: number[],
  nResults: number,
): Promise<ChromaResult[]> {
  const url = `${chromaUrl}${CHROMA_BASE}/${collectionId}/query`;

  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query_embeddings: [embedding],
      n_results: nResults,
      include: ["documents", "metadatas", "distances"],
    }),
  });

  if (!resp.ok) {
    throw new Error(`ChromaDB query failed: ${resp.status} ${resp.statusText}`);
  }

  const data = (await resp.json()) as {
    ids: string[][];
    documents: string[][];
    metadatas: Record<string, string>[][];
    distances: number[][];
  };

  if (!data.ids?.[0]?.length) return [];

  return data.ids[0].map((id, i) => ({
    source: data.metadatas[0][i]?.source || "unknown",
    text: data.documents[0][i] || "",
    distance: data.distances[0][i],
    // Convert cosine distance to similarity score (0-1)
    score: 1 - data.distances[0][i],
    metadata: data.metadatas[0][i] || {},
  }));
}

// ============================================================================
// Plugin
// ============================================================================

export default function register(api: OpenClawPluginApi) {
  const cfg = parseConfig(api.pluginConfig);

  if (!cfg.collectionId) {
    api.logger.warn("chromadb-memory: No collectionId configured, plugin disabled");
    return;
  }

  api.logger.info(
    `chromadb-memory: registered (chroma: ${cfg.chromaUrl}, ollama: ${cfg.ollamaUrl}, model: ${cfg.embeddingModel})`,
  );

  // ========================================================================
  // Tool: chromadb_search
  // ========================================================================

  api.registerTool({
    name: "chromadb_search",
    description:
      "Search the ChromaDB long-term memory archive. Contains indexed memory files, session transcripts, and homelab documentation. Use when you need deep historical context or can't find something in memory_search.",
    parameters: {
      type: "object",
      properties: {
        query: { type: "string", description: "Semantic search query" },
        limit: { type: "number", description: "Max results (default: 5)" },
      },
      required: ["query"],
    },
    async execute(_toolCallId, params) {
      const { query, limit = 5 } = params as {
        query: string;
        limit?: number;
      };

      try {
        const embedding = await getEmbedding(
          cfg.ollamaUrl,
          cfg.embeddingModel,
          query,
        );
        const results = await queryChromaDB(
          cfg.chromaUrl,
          cfg.collectionId,
          embedding,
          limit,
        );

        if (results.length === 0) {
          return {
            content: [
              { type: "text", text: "No relevant results found in ChromaDB." },
            ],
          };
        }

        const filtered = results.filter((r) => r.score >= cfg.minScore);

        if (filtered.length === 0) {
          return {
            content: [
              {
                type: "text",
                text: `Found ${results.length} results but none above similarity threshold (${cfg.minScore}). Best match: ${results[0].score.toFixed(3)} from ${results[0].source}`,
              },
            ],
          };
        }

        const text = filtered
          .map(
            (r, i) =>
              `### Result ${i + 1} — ${r.source} (${(r.score * 100).toFixed(0)}% match)\n${r.text.slice(0, 500)}${r.text.length > 500 ? "..." : ""}`,
          )
          .join("\n\n");

        return {
          content: [
            {
              type: "text",
              text: `Found ${filtered.length} results from ChromaDB:\n\n${text}`,
            },
          ],
        };
      } catch (err) {
        return {
          content: [
            {
              type: "text",
              text: `ChromaDB search error: ${String(err)}`,
            },
          ],
          isError: true,
        };
      }
    },
  });

  // ========================================================================
  // Auto-recall: inject relevant memories before each agent turn
  // ========================================================================

  if (cfg.autoRecall) {
    api.on("before_agent_start", async (event: { prompt?: string }) => {
      if (!event.prompt || event.prompt.length < 10) return;

      try {
        const embedding = await getEmbedding(
          cfg.ollamaUrl,
          cfg.embeddingModel,
          event.prompt,
        );
        const results = await queryChromaDB(
          cfg.chromaUrl,
          cfg.collectionId,
          embedding,
          cfg.autoRecallResults,
        );

        // Filter by minimum similarity
        const relevant = results.filter((r) => r.score >= cfg.minScore);
        if (relevant.length === 0) return;

        const memoryContext = relevant
          .map(
            (r) =>
              `- [${r.source}] ${r.text.slice(0, 300)}${r.text.length > 300 ? "..." : ""}`,
          )
          .join("\n");

        api.logger.info(
          `chromadb-memory: auto-recall injecting ${relevant.length} memories (best: ${relevant[0].score.toFixed(3)} from ${relevant[0].source})`,
        );

        return {
          prependContext: `<chromadb-memories>\nRelevant context from long-term memory (ChromaDB):\n${memoryContext}\n</chromadb-memories>`,
        };
      } catch (err) {
        api.logger.warn(`chromadb-memory: auto-recall failed: ${String(err)}`);
      }
    });
  }

  // ========================================================================
  // Service
  // ========================================================================

  api.registerService({
    id: "chromadb-memory",
    start: () => {
      api.logger.info(
        `chromadb-memory: service started (auto-recall: ${cfg.autoRecall}, collection: ${cfg.collectionId})`,
      );
    },
    stop: () => {
      api.logger.info("chromadb-memory: stopped");
    },
  });
}
