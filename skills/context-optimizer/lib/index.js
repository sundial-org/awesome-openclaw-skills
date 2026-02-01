/**
 * Context Pruner - Advanced context management optimized for DeepSeek's 64k context window
 * 
 * Features:
 * - DeepSeek-optimized token counting
 * - Multiple pruning strategies
 * - Semantic deduplication
 * - Adaptive compression based on context usage
 * - Real-time monitoring and health tracking
 * - Hierarchical memory system with context archive
 */

import { get_encoding } from 'tiktoken';
import { pipeline } from '@xenova/transformers';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Import chat logger from parent directory
import ContextOptimizerLogger from '../chat-logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DEFAULT_CONFIG = {
  // DeepSeek specific
  contextLimit: 64000,
  model: 'deepseek-chat',
  
  // Auto-compaction settings
  autoCompact: true,
  compactThreshold: 0.75,      // Start compacting at 75% usage
  aggressiveCompactThreshold: 0.9, // Aggressive compaction at 90%
  
  // Dynamic context settings
  dynamicContext: true,
  relevanceDecay: 0.95,        // Relevance decays 5% per time step
  minRelevanceScore: 0.3,      // Minimum relevance to keep
  queryAwareCompaction: true,  // Compact based on current query relevance
  
  // Compaction strategies
  strategies: ['semantic', 'temporal', 'extractive', 'adaptive'],
  preserveRecent: 10,          // Always keep last N messages
  preserveSystem: true,        // Always keep system messages
  preserveHighPriority: 8,     // Priority threshold for preservation
  
  // Semantic settings
  minSimilarity: 0.85,
  summarizer: null,
  
  // Tokenizer
  encoding: 'cl100k_base', // DeepSeek uses cl100k_base
  
  // Archive settings
  enableArchive: true,
  archivePath: './context-archive',
  archiveSearchLimit: 10,
  archiveMaxSize: 100 * 1024 * 1024, // 100MB
  archiveCompression: true,
  archiveIndexing: true,
  
  // Performance
  batchSize: 5,               // Messages to process in batch
  maxCompactionRatio: 0.5,    // Maximum 50% compaction in one pass
  
  // Chat logging
  logToChat: true,            // Log optimization events to chat
  chatLogLevel: 'brief',      // 'brief', 'detailed', or 'none'
  chatLogFormat: '🧠 {action}: {details}', // Format for chat messages
  chatLogger: null,           // Custom logger instance
};

/**
 * Context Archive - Hierarchical memory system for storing and retrieving pruned context
 * 
 * Like RAM vs Storage:
 * - Current context = RAM (limited, fast access)
 * - Archive = Storage (larger, slower access)
 * - Efficient search when something isn't in current context
 * - Extract only important parts to bring into RAM
 */
class ContextArchive {
  constructor(config) {
    this.config = config;
    this.archivePath = path.resolve(config.archivePath);
    this.indexPath = path.join(this.archivePath, 'index.json');
    this.embedder = null;
    this.index = {
      entries: [],
      totalSize: 0,
      lastUpdated: null,
      stats: {
        searches: 0,
        hits: 0,
        misses: 0,
        bytesStored: 0,
      }
    };
  }

  async initialize() {
    // Create archive directory if it doesn't exist
    await fs.mkdir(this.archivePath, { recursive: true });
    
    // Load existing index
    try {
      const indexData = await fs.readFile(this.indexPath, 'utf-8');
      this.index = JSON.parse(indexData);
    } catch (error) {
      // Create new index if doesn't exist
      await this.saveIndex();
    }
    
    // Initialize embedding model for semantic search
    if (this.config.archiveIndexing) {
      try {
        const { pipeline } = await import('@xenova/transformers');
        this.embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
      } catch (error) {
        console.warn('Failed to load embedding model for archive, semantic search disabled:', error.message);
        this.embedder = null;
      }
    }
    
    return this;
  }

  /**
   * Store pruned content in archive
   */
  async store(content, metadata = {}) {
    const entryId = `entry_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const entryPath = path.join(this.archivePath, `${entryId}.json`);
    
    const tokens = metadata.tokens || this.estimateTokens(content);
    const category = metadata.category || 'general';
    const priority = metadata.priority || 5;
    
    console.log(`[Archive] Storing entry: ${entryId}`);
    console.log(`[Archive] Content: "${content.substring(0, 80)}${content.length > 80 ? '...' : ''}"`);
    console.log(`[Archive] Metadata: ${tokens} tokens, category: ${category}, priority: ${priority}`);
    
    const entry = {
      id: entryId,
      content,
      metadata: {
        ...metadata,
        timestamp: Date.now(),
        tokens,
        priority,
        category,
      },
      embedding: null,
      keywords: this.extractKeywords(content),
    };
    
    // Generate embedding if available
    if (this.embedder && this.config.archiveIndexing) {
      try {
        console.log(`[Archive] Generating embedding for entry`);
        entry.embedding = await this.embed(content);
      } catch (error) {
        console.warn('[Archive] Failed to generate embedding for archive entry:', error.message);
      }
    }
    
    // Save entry to file
    await fs.writeFile(entryPath, JSON.stringify(entry, null, 2));
    
    // Update index
    this.index.entries.push({
      id: entryId,
      path: entryPath,
      size: Buffer.byteLength(JSON.stringify(entry)),
      metadata: entry.metadata,
      keywords: entry.keywords,
    });
    
    this.index.totalSize += this.index.entries[this.index.entries.length - 1].size;
    this.index.lastUpdated = Date.now();
    
    // Check if we need to clean up old entries
    await this.cleanupIfNeeded();
    
    // Save updated index
    await this.saveIndex();
    
    this.index.stats.bytesStored += Buffer.byteLength(JSON.stringify(entry));
    console.log(`[Archive] Entry stored successfully: ${entryId}`);
    return entryId;
  }

  /**
   * Search archive for relevant content
   */
  async search(query, options = {}) {
    const {
      limit = this.config.archiveSearchLimit,
      minScore = 0.3,
      categories = [],
      timeRange = null,
    } = options;

    this.index.stats.searches++;
    
    // Extract query keywords
    const queryKeywords = this.extractKeywords(query);
    let queryEmbedding = null;
    
    if (this.embedder) {
      try {
        queryEmbedding = await this.embed(query);
      } catch (error) {
        console.warn('Failed to generate query embedding:', error.message);
      }
    }
    
    const results = [];
    
    for (const entry of this.index.entries) {
      // Load entry data
      let entryData;
      try {
        const entryContent = await fs.readFile(entry.path, 'utf-8');
        entryData = JSON.parse(entryContent);
      } catch (error) {
        console.warn(`Failed to load archive entry ${entry.id}:`, error.message);
        continue;
      }
      
      // Apply filters
      if (categories.length > 0 && !categories.includes(entryData.metadata.category)) {
        continue;
      }
      
      if (timeRange) {
        const age = Date.now() - entryData.metadata.timestamp;
        if (age > timeRange) continue;
      }
      
      // Calculate score
      let score = 0;
      
      // Keyword matching
      const keywordMatches = queryKeywords.filter(kw => 
        entryData.keywords.some(ekw => ekw.toLowerCase().includes(kw.toLowerCase()) ||
                                      kw.toLowerCase().includes(ekw.toLowerCase()))
      ).length;
      
      score += (keywordMatches / Math.max(queryKeywords.length, 1)) * 0.4;
      
      // Semantic similarity if embeddings available
      if (queryEmbedding && entryData.embedding) {
        const similarity = this.cosineSimilarity(queryEmbedding, entryData.embedding);
        score += similarity * 0.6;
      }
      
      if (score >= minScore) {
        results.push({
          id: entryData.id,
          content: entryData.content,
          metadata: entryData.metadata,
          score,
          keywords: entryData.keywords,
        });
      }
    }
    
    // Sort by score (descending)
    results.sort((a, b) => b.score - a.score);
    
    // Limit results
    const limitedResults = results.slice(0, limit);
    
    if (limitedResults.length > 0) {
      this.index.stats.hits++;
    } else {
      this.index.stats.misses++;
    }
    
    return limitedResults;
  }

  /**
   * Extract relevant snippets from archive content
   */
  extractRelevantSnippets(content, query, maxTokens = 500) {
    const sentences = content.match(/[^.!?]+[.!?]+/g) || [content];
    const queryKeywords = this.extractKeywords(query);
    
    const scoredSentences = sentences.map((sentence, index) => {
      let score = 0;
      
      // Keyword matching
      const keywordMatches = queryKeywords.filter(kw => 
        sentence.toLowerCase().includes(kw.toLowerCase())
      ).length;
      
      score += (keywordMatches / Math.max(queryKeywords.length, 1)) * 0.7;
      
      // Position bonus (recent sentences are more relevant)
      score += (1 - index / sentences.length) * 0.3;
      
      return {
        sentence: sentence.trim(),
        score,
        tokens: this.estimateTokens(sentence),
      };
    });
    
    // Sort by score
    scoredSentences.sort((a, b) => b.score - a.score);
    
    // Collect sentences until token limit
    const snippets = [];
    let totalTokens = 0;
    
    for (const { sentence, tokens } of scoredSentences) {
      if (totalTokens + tokens <= maxTokens) {
        snippets.push(sentence);
        totalTokens += tokens;
      } else {
        break;
      }
    }
    
    return {
      snippets,
      totalTokens,
      coverage: snippets.length / sentences.length,
    };
  }

  /**
   * Retrieve and extract relevant information from archive
   */
  async retrieveRelevantInfo(query, options = {}) {
    const {
      maxContextTokens = 1000,
      minRelevance = 0.4,
    } = options;
    
    // Search archive
    const searchResults = await this.search(query, {
      limit: 5,
      minScore: minRelevance,
    });
    
    if (searchResults.length === 0) {
      return {
        found: false,
        snippets: [],
        totalTokens: 0,
        sources: [],
      };
    }
    
    // Extract relevant snippets from each result
    const allSnippets = [];
    const sources = [];
    let totalTokens = 0;
    
    for (const result of searchResults) {
      if (totalTokens >= maxContextTokens) break;
      
      const extraction = this.extractRelevantSnippets(
        result.content,
        query,
        maxContextTokens - totalTokens
      );
      
      if (extraction.snippets.length > 0) {
        allSnippets.push(...extraction.snippets);
        totalTokens += extraction.totalTokens;
        sources.push({
          id: result.id,
          score: result.score,
          metadata: result.metadata,
          snippetsCount: extraction.snippets.length,
          coverage: extraction.coverage,
        });
      }
    }
    
    return {
      found: true,
      snippets: allSnippets,
      totalTokens,
      sources,
      searchStats: {
        totalSearched: searchResults.length,
        totalHits: sources.length,
      },
    };
  }

  /**
   * Cleanup old entries if archive exceeds max size
   */
  async cleanupIfNeeded() {
    if (this.index.totalSize <= this.config.archiveMaxSize) {
      return;
    }
    
    console.log(`Archive size ${this.index.totalSize} exceeds limit ${this.config.archiveMaxSize}, cleaning up...`);
    
    // Sort entries by priority and age (lower priority and older first)
    this.index.entries.sort((a, b) => {
      const priorityDiff = (a.metadata.priority || 5) - (b.metadata.priority || 5);
      if (priorityDiff !== 0) return priorityDiff;
      return a.metadata.timestamp - b.metadata.timestamp;
    });
    
    let removedSize = 0;
    const toRemove = [];
    
    while (this.index.totalSize - removedSize > this.config.archiveMaxSize * 0.9 && this.index.entries.length > 0) {
      const entry = this.index.entries.shift();
      toRemove.push(entry);
      removedSize += entry.size;
    }
    
    // Remove files
    for (const entry of toRemove) {
      try {
        await fs.unlink(entry.path);
      } catch (error) {
        console.warn(`Failed to remove archive entry ${entry.id}:`, error.message);
      }
    }
    
    this.index.totalSize -= removedSize;
    await this.saveIndex();
    
    console.log(`Removed ${toRemove.length} entries, freed ${removedSize} bytes`);
  }

  /**
   * Get archive statistics
   */
  getStats() {
    return {
      ...this.index.stats,
      totalEntries: this.index.entries.length,
      totalSize: this.index.totalSize,
      maxSize: this.config.archiveMaxSize,
      usagePercentage: (this.index.totalSize / this.config.archiveMaxSize) * 100,
      lastUpdated: this.index.lastUpdated,
    };
  }

  /**
   * Clear entire archive
   */
  async clear() {
    // Remove all entry files
    for (const entry of this.index.entries) {
      try {
        await fs.unlink(entry.path);
      } catch (error) {
        // Ignore errors
      }
    }
    
    // Reset index
    this.index = {
      entries: [],
      totalSize: 0,
      lastUpdated: Date.now(),
      stats: {
        searches: 0,
        hits: 0,
        misses: 0,
        bytesStored: 0,
      }
    };
    
    await this.saveIndex();
  }

  // Helper methods
  async embed(text) {
    if (!this.embedder) return null;
    
    try {
      const result = await this.embedder(text, { pooling: 'mean', normalize: true });
      return Array.from(result.data);
    } catch (error) {
      console.warn('Embedding failed:', error.message);
      return null;
    }
  }

  cosineSimilarity(a, b) {
    if (!a || !b || a.length !== b.length) return 0;
    
    let dot = 0, normA = 0, normB = 0;
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  extractKeywords(text, maxKeywords = 10) {
    // Simple keyword extraction: remove common words, take most frequent
    const commonWords = new Set([
      'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
      'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
      'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
      'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
      'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
      'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
      'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see',
      'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
      'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
      'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
      'give', 'day', 'most', 'us'
    ]);
    
    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 3 && !commonWords.has(word));
    
    // Count frequency
    const freq = {};
    words.forEach(word => {
      freq[word] = (freq[word] || 0) + 1;
    });
    
    // Get top keywords
    return Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, maxKeywords)
      .map(([word]) => word);
  }

  estimateTokens(text) {
    // Simple estimation: 4 chars ≈ 1 token for English
    return Math.ceil((text || '').length / 4);
  }

  async saveIndex() {
    await fs.writeFile(this.indexPath, JSON.stringify(this.index, null, 2));
  }
}

export class ContextOptimizer {
  constructor(options = {}) {
    this.config = { ...DEFAULT_CONFIG, ...options };
    this.encoder = get_encoding(this.config.encoding);
    this.embedder = null;
    this.archive = null;
    this.messageHistory = [];
    this.tokenUsage = 0;
    this.relevanceScores = new Map(); // Track relevance of each message
    this.lastQuery = null;
    this.lastQueryTime = 0;
    
    // Initialize chat logger
    this.logger = this.config.chatLogger || new ContextOptimizerLogger({
      logToChat: this.config.logToChat,
      chatLogLevel: this.config.chatLogLevel,
      chatLogFormat: this.config.chatLogFormat,
    });
    
    this.stats = {
      totalCompacted: 0,
      totalTokensSaved: 0,
      archiveStores: 0,
      archiveRetrievals: 0,
      archiveAutoRetrievals: 0,
      compactions: 0,
      dynamicAdjustments: 0,
      relevanceUpdates: 0,
      chatLogs: 0,
    };
  }

  async initialize() {
    // Initialize embedding model for semantic deduplication
    try {
      this.embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
    } catch (error) {
      console.warn('Failed to load embedding model, semantic pruning disabled:', error.message);
      this.embedder = null;
    }
    
    // Initialize archive if enabled
    if (this.config.enableArchive) {
      this.archive = new ContextArchive(this.config);
      await this.archive.initialize();
    }
    
    return this;
  }

  // ---------------------------------------------------------------------------
  // Core Processing
  // ---------------------------------------------------------------------------

  /**
   * Process messages with automatic pruning based on context usage
   */
  async processMessages(messages) {
    if (!Array.isArray(messages)) {
      throw new Error('messages must be an array');
    }

    // Calculate current token usage
    const currentTokens = this.countTokensForMessages(messages);
    this.tokenUsage = currentTokens;
    
    // Check if pruning is needed
    const usageRatio = currentTokens / this.config.contextLimit;
    const status = this.getHealthStatus(usageRatio);
    
    let processedMessages = [...messages];
    
    // Apply pruning based on usage
    if (this.config.autoPrune) {
      if (status === 'EMERGENCY') {
        processedMessages = await this.emergencyPrune(processedMessages);
      } else if (status === 'PRUNE') {
        processedMessages = await this.prune(processedMessages, {
          targetTokens: this.config.contextLimit * 0.7, // Target 70% usage
          strategy: 'aggressive'
        });
      } else if (status === 'WARNING') {
        processedMessages = await this.prune(processedMessages, {
          targetTokens: this.config.contextLimit * 0.6, // Target 60% usage
          strategy: 'conservative'
        });
      }
    }
    
    // Update message history for temporal analysis
    this.updateMessageHistory(processedMessages);
    
    return processedMessages;
  }

  /**
   * Auto-compact messages based on current context usage
   */
  async autoCompact(messages, currentQuery = null) {
    const currentTokens = this.countTokensForMessages(messages);
    const usageRatio = currentTokens / this.config.contextLimit;
    
    // Check if compaction is needed
    if (usageRatio < this.config.compactThreshold) {
      return messages; // No compaction needed
    }
    
    // Update relevance scores based on current query
    if (currentQuery && this.config.queryAwareCompaction) {
      await this.updateRelevanceScores(messages, currentQuery);
      this.lastQuery = currentQuery;
      this.lastQueryTime = Date.now();
    }
    
    // Determine compaction intensity
    let compactionRatio;
    let strategy;
    
    if (usageRatio >= this.config.aggressiveCompactThreshold) {
      compactionRatio = 0.7; // Aggressive: target 30% of current size
      strategy = 'aggressive';
    } else {
      compactionRatio = 0.5; // Normal: target 50% of current size
      strategy = 'balanced';
    }
    
    const targetTokens = Math.min(
      currentTokens * compactionRatio,
      this.config.contextLimit * this.config.compactThreshold
    );
    
    console.log(`[Auto-Compact] Current: ${currentTokens} tokens, Target: ${targetTokens} tokens, Strategy: ${strategy}`);
    
    // Apply adaptive compaction
    const compacted = await this.adaptiveCompact(messages, targetTokens, strategy, currentQuery);
    
    // Log to chat
    const beforeCount = messages.length;
    const afterCount = compacted.length;
    const reduction = Math.round((1 - afterCount / beforeCount) * 100);
    const tokensSaved = currentTokens - this.countTokensForMessages(compacted);
    
    this.logger.logCompaction(beforeCount, afterCount, strategy);
    this.stats.chatLogs++;
    
    this.stats.compactions++;
    this.stats.totalCompacted += (beforeCount - afterCount);
    this.stats.totalTokensSaved += tokensSaved;
    
    return compacted;
  }

  /**
   * Adaptive compaction that chooses best strategy based on content
   */
  async adaptiveCompact(messages, targetTokens, strategy = 'balanced', currentQuery = null) {
    const currentTokens = this.countTokensForMessages(messages);
    const tokensToSave = currentTokens - targetTokens;
    
    if (tokensToSave <= 0) return messages;
    
    let compactedMessages = [...messages];
    const removedMessages = [];
    let tokensSaved = 0;
    
    // Analyze message characteristics to choose best strategy
    const analysis = this.analyzeMessages(messages);
    
    // Apply strategies based on analysis
    const strategies = this.selectStrategies(analysis, currentQuery);
    
    for (const strategyName of strategies) {
      if (tokensSaved >= tokensToSave) break;
      
      const remainingTokensToSave = tokensToSave - tokensSaved;
      
      switch (strategyName) {
        case 'semantic':
          const semanticResult = await this.applySemanticCompaction(compactedMessages, remainingTokensToSave, strategy, currentQuery);
          compactedMessages = semanticResult.compacted;
          removedMessages.push(...semanticResult.removed);
          tokensSaved += semanticResult.tokensSaved;
          break;
          
        case 'temporal':
          const temporalResult = this.applyTemporalCompaction(compactedMessages, remainingTokensToSave, strategy, currentQuery);
          compactedMessages = temporalResult.compacted;
          removedMessages.push(...temporalResult.removed);
          tokensSaved += temporalResult.tokensSaved;
          break;
          
        case 'extractive':
          const extractiveResult = await this.applyExtractiveCompaction(compactedMessages, remainingTokensToSave, strategy, currentQuery);
          compactedMessages = extractiveResult.compacted;
          removedMessages.push(...extractiveResult.removed);
          tokensSaved += extractiveResult.tokensSaved;
          break;
          
        case 'adaptive':
          const adaptiveResult = await this.applyAdaptiveCompaction(compactedMessages, remainingTokensToSave, strategy, currentQuery);
          compactedMessages = adaptiveResult.compacted;
          removedMessages.push(...adaptiveResult.removed);
          tokensSaved += adaptiveResult.tokensSaved;
          break;
      }
    }
    
    // Store removed messages in archive
    if (this.archive && removedMessages.length > 0) {
      await this.storeRemovedInArchive(removedMessages, strategy);
    }
    
    return compactedMessages;
  }

  /**
   * Process messages with auto-compaction
   */
  async processMessages(messages, currentQuery = null) {
    await this.initialize();
    
    const startTime = Date.now();
    const initialTokens = this.countTokensForMessages(messages);
    const initialCount = messages.length;
    
    console.log(`[Context-Optimizer] Starting processing: ${initialCount} messages, ${initialTokens} tokens`);
    if (currentQuery) {
      console.log(`[Context-Optimizer] Current query: "${currentQuery.substring(0, 50)}${currentQuery.length > 50 ? '...' : ''}"`);
    }
    
    // Update message history
    this.messageHistory.push({
      timestamp: Date.now(),
      count: messages.length,
      tokens: initialTokens,
    });
    
    // Keep only recent history
    if (this.messageHistory.length > 100) {
      this.messageHistory = this.messageHistory.slice(-100);
    }
    
    // Update token usage
    this.tokenUsage = initialTokens;
    
    // Apply auto-compaction if enabled
    if (this.config.autoCompact) {
      console.log(`[Context-Optimizer] Auto-compaction enabled, threshold: ${this.config.compactThreshold}`);
      messages = await this.autoCompact(messages, currentQuery);
      this.tokenUsage = this.countTokensForMessages(messages);
    }
    
    // Apply dynamic context adjustment if enabled
    if (this.config.dynamicContext) {
      console.log(`[Context-Optimizer] Dynamic context adjustment enabled`);
      messages = await this.adjustDynamicContext(messages, currentQuery);
      this.tokenUsage = this.countTokensForMessages(messages);
    }
    
    // Smart Archive Retrieval: Check if we should fetch relevant content from archive
    if (this.config.enableArchive && currentQuery) {
      console.log(`[Context-Optimizer] Smart archive retrieval enabled`);
      messages = await this.smartArchiveRetrieval(messages, currentQuery);
      this.tokenUsage = this.countTokensForMessages(messages);
    }
    
    const finalCount = messages.length;
    const finalTokens = this.tokenUsage;
    const tokensSaved = initialTokens - finalTokens;
    const timeTaken = Date.now() - startTime;
    
    console.log(`[Context-Optimizer] Processing complete: ${finalCount} messages, ${finalTokens} tokens (saved ${tokensSaved} tokens, ${timeTaken}ms)`);
    console.log(`[Context-Optimizer] Stats: ${this.stats.totalCompacted} compacted, ${this.stats.archiveRetrievals} archive retrievals`);
    
    return messages;
  }

  /**
   * Emergency pruning for critical situations
   */
  async emergencyPrune(messages) {
    console.warn('Applying emergency pruning - context near limit!');
    
    // Keep only essential messages
    const essential = messages.filter(msg => {
      // Always keep system messages
      if (this.config.preserveSystem && msg.role === 'system') return true;
      
      // Keep high priority messages
      if (msg.priority && msg.priority >= this.config.preserveHighPriority) return true;
      
      // Keep recent messages (last N)
      const recentIndex = messages.length - this.config.preserveRecent;
      const index = messages.indexOf(msg);
      return index >= recentIndex;
    });
    
    // If still too large, apply aggressive compression
    const tokens = this.countTokensForMessages(essential);
    if (tokens > this.config.contextLimit * 0.8) {
      return await this.applyExtractiveCompression(essential, tokens * 0.5, 'aggressive');
    }
    
    this.stats.totalPruned += (messages.length - essential.length);
    this.stats.prunes++;
    
    return essential;
  }

  // ---------------------------------------------------------------------------
  // Pruning Strategies
  // ---------------------------------------------------------------------------

  /**
   * Semantic compaction: merge similar messages instead of removing
   */
  async applySemanticCompaction(messages, targetTokensToSave, strategy = 'balanced', currentQuery = null) {
    if (!this.embedder || messages.length < 3) {
      return { compacted: messages, removed: [], tokensSaved: 0 };
    }
    
    const embeddings = await Promise.all(
      messages.map(async (msg, index) => ({
        index,
        embedding: await this.embed(msg.content),
        message: msg,
        relevance: this.relevanceScores.get(index) || 0.5,
      }))
    );
    
    // Find similar message pairs
    const similarPairs = [];
    for (let i = 0; i < embeddings.length; i++) {
      for (let j = i + 1; j < embeddings.length; j++) {
        const similarity = this.cosineSimilarity(
          embeddings[i].embedding,
          embeddings[j].embedding
        );
        
        if (similarity > this.config.minSimilarity) {
          // Calculate merge score based on similarity and relevance
          const mergeScore = similarity * 0.6 + 
                           (Math.max(embeddings[i].relevance, embeddings[j].relevance) * 0.4);
          
          similarPairs.push({
            i, j, similarity, mergeScore,
            tokensI: this.countTokens(embeddings[i].message.content),
            tokensJ: this.countTokens(embeddings[j].message.content),
            relevanceI: embeddings[i].relevance,
            relevanceJ: embeddings[j].relevance,
          });
        }
      }
    }
    
    // Sort by merge score (highest first)
    similarPairs.sort((a, b) => b.mergeScore - a.mergeScore);
    
    const mergedIndices = new Set();
    const compactedMessages = [];
    const removedMessages = [];
    let tokensSaved = 0;
    
    for (const pair of similarPairs) {
      if (tokensSaved >= targetTokensToSave) break;
      if (mergedIndices.has(pair.i) || mergedIndices.has(pair.j)) continue;
      
      // Merge the two messages
      const message1 = embeddings[pair.i].message;
      const message2 = embeddings[pair.j].message;
      
      // Create merged message
      const mergedContent = await this.mergeSimilarMessages(message1, message2, strategy);
      const mergedTokens = this.countTokens(mergedContent);
      const originalTokens = pair.tokensI + pair.tokensJ;
      const savedTokens = originalTokens - mergedTokens;
      
      if (savedTokens > 0) {
        // Add merged message
        compactedMessages.push({
          role: message1.role === message2.role ? message1.role : 'system',
          content: mergedContent,
          priority: Math.max(message1.priority || 5, message2.priority || 5),
          merged: true,
          originalCount: 2,
          mergedFrom: [pair.i, pair.j],
        });
        
        // Track removed original messages
        removedMessages.push({
          message: message1,
          reason: 'semantic_merge',
          similarity: pair.similarity,
          mergedInto: compactedMessages.length - 1,
        });
        
        removedMessages.push({
          message: message2,
          reason: 'semantic_merge',
          similarity: pair.similarity,
          mergedInto: compactedMessages.length - 1,
        });
        
        mergedIndices.add(pair.i);
        mergedIndices.add(pair.j);
        tokensSaved += savedTokens;
      }
    }
    
    // Add unmerged messages
    for (let i = 0; i < messages.length; i++) {
      if (!mergedIndices.has(i)) {
        compactedMessages.push(messages[i]);
      }
    }
    
    // Sort by original order (approximate)
    compactedMessages.sort((a, b) => {
      const aIndex = a.mergedFrom ? Math.min(...a.mergedFrom) : messages.findIndex(m => m === a);
      const bIndex = b.mergedFrom ? Math.min(...b.mergedFrom) : messages.findIndex(m => m === b);
      return aIndex - bIndex;
    });
    
    return { compacted: compactedMessages, removed: removedMessages, tokensSaved };
  }

  /**
   * Semantic pruning: remove semantically similar messages (original, kept for compatibility)
   */
  async applySemanticPruning(messages, targetTokensToRemove, strategy) {
    const result = await this.applySemanticPruningWithArchive(messages, targetTokensToRemove, strategy, false);
    return result.pruned;
  }

  /**
   * Temporal compaction: summarize older messages instead of removing
   */
  applyTemporalCompaction(messages, targetTokensToSave, strategy = 'balanced', currentQuery = null) {
    // Skip if we need to preserve recent messages
    const preserveCount = Math.min(this.config.preserveRecent, messages.length);
    const recentMessages = messages.slice(-preserveCount);
    const olderMessages = messages.slice(0, -preserveCount);
    
    if (olderMessages.length === 0) {
      return { compacted: messages, removed: [], tokensSaved: 0 };
    }
    
    // Group older messages by time windows
    const timeWindows = this.groupByTimeWindows(olderMessages);
    const compactedOlder = [];
    const removedMessages = [];
    let tokensSaved = 0;
    
    for (const window of timeWindows) {
      if (tokensSaved >= targetTokensToSave) {
        compactedOlder.push(...window.messages);
        continue;
      }
      
      const windowTokens = this.countTokensForMessages(window.messages);
      
      if (window.messages.length >= 3 && windowTokens > 300) {
        // Summarize this time window
        const summary = this.summarizeTimeWindow(window.messages, strategy);
        const summaryTokens = this.countTokens(summary);
        const savedTokens = windowTokens - summaryTokens;
        
        if (savedTokens > 0 && savedTokens <= targetTokensToSave - tokensSaved) {
          compactedOlder.push({
            role: 'system',
            content: `[Time window ${window.startTime.toLocaleTimeString()} - ${window.endTime.toLocaleTimeString()}]: ${summary}`,
            priority: 6,
            compressed: true,
            originalCount: window.messages.length,
            timeWindow: true,
          });
          
          // Track removed messages
          removedMessages.push(...window.messages.map((msg, index) => ({
            message: msg,
            reason: 'temporal_summary',
            timeWindow: window.label,
            summary: summary,
          })));
          
          tokensSaved += savedTokens;
        } else {
          compactedOlder.push(...window.messages);
        }
      } else {
        compactedOlder.push(...window.messages);
      }
    }
    
    return {
      compacted: [...compactedOlder, ...recentMessages],
      removed: removedMessages,
      tokensSaved,
    };
  }

  /**
   * Temporal pruning: remove older messages first (original, kept for compatibility)
   */
  applyTemporalPruning(messages, targetTokensToRemove, strategy) {
    const result = this.applyTemporalPruningWithArchive(messages, targetTokensToRemove, strategy, false);
    this.stats.totalTokensSaved += (this.countTokensForMessages(messages) - this.countTokensForMessages(result.pruned));
    this.stats.totalPruned += (messages.length - result.pruned.length);
    return result.pruned;
  }

  /**
   * Extractive compaction: extract key information from verbose messages
   */
  async applyExtractiveCompaction(messages, targetTokensToSave, strategy = 'balanced', currentQuery = null) {
    // Identify verbose messages that can be compacted
    const verboseMessages = messages.filter((msg, index) => {
      const tokens = this.countTokens(msg.content);
      const relevance = this.relevanceScores.get(index) || 0.5;
      
      // Messages that are long but not highly relevant to current query
      return tokens > 100 && relevance < 0.7 && msg.priority < 8;
    });
    
    if (verboseMessages.length === 0) {
      return { compacted: messages, removed: [], tokensSaved: 0 };
    }
    
    // Sort by length (longest first) and low relevance
    verboseMessages.sort((a, b) => {
      const aTokens = this.countTokens(a.content);
      const bTokens = this.countTokens(b.content);
      const aIndex = messages.indexOf(a);
      const bIndex = messages.indexOf(b);
      const aRelevance = this.relevanceScores.get(aIndex) || 0.5;
      const bRelevance = this.relevanceScores.get(bIndex) || 0.5;
      
      // Prioritize long, low-relevance messages
      return (bTokens * (1 - bRelevance)) - (aTokens * (1 - aRelevance));
    });
    
    const compactedMessages = [...messages];
    const removedMessages = [];
    let tokensSaved = 0;
    
    for (const verboseMsg of verboseMessages) {
      if (tokensSaved >= targetTokensToSave) break;
      
      const originalIndex = messages.indexOf(verboseMsg);
      if (originalIndex === -1) continue;
      
      const originalTokens = this.countTokens(verboseMsg.content);
      
      // Extract key information
      const extracted = this.extractKeyInformation(verboseMsg.content, currentQuery, strategy);
      const extractedTokens = this.countTokens(extracted);
      const savedTokens = originalTokens - extractedTokens;
      
      if (savedTokens > 0 && savedTokens <= targetTokensToSave - tokensSaved) {
        // Replace verbose message with extracted version
        compactedMessages[originalIndex] = {
          ...verboseMsg,
          content: `[Extracted key points]: ${extracted}`,
          extracted: true,
          originalLength: originalTokens,
        };
        
        removedMessages.push({
          message: verboseMsg,
          reason: 'extractive_compaction',
          extraction: extracted,
          savedTokens,
        });
        
        tokensSaved += savedTokens;
      }
    }
    
    return { compacted: compactedMessages, removed: removedMessages, tokensSaved };
  }

  /**
   * Extractive compression: summarize groups of messages (original, kept for compatibility)
   */
  async applyExtractiveCompression(messages, targetTokensToRemove, strategy) {
    const result = await this.applyExtractiveCompressionWithArchive(messages, targetTokensToRemove, strategy, false);
    this.stats.totalTokensSaved += (this.countTokensForMessages(messages) - this.countTokensForMessages(result.pruned));
    return result.pruned;
  }

  // ---------------------------------------------------------------------------
  // Helper Methods
  // ---------------------------------------------------------------------------

  groupMessagesForCompression(messages) {
    const groups = [];
    let currentGroup = { role: null, messages: [], startIndex: 0 };
    
    for (let i = 0; i < messages.length; i++) {
      const msg = messages[i];
      
      // Start new group if:
      // 1. Role changes
      // 2. Group is getting too large (> 10 messages)
      // 3. Large gap in timestamps (if available)
      if (currentGroup.role !== msg.role || 
          currentGroup.messages.length >= 10 ||
          (msg.timestamp && currentGroup.messages.length > 0 && 
           msg.timestamp - currentGroup.messages[currentGroup.messages.length - 1].timestamp > 300000)) { // 5 minutes
        
        if (currentGroup.messages.length > 0) {
          groups.push({ ...currentGroup });
        }
        
        currentGroup = {
          role: msg.role,
          messages: [msg],
          startIndex: i,
        };
      } else {
        currentGroup.messages.push(msg);
      }
    }
    
    // Add the last group
    if (currentGroup.messages.length > 0) {
      groups.push(currentGroup);
    }
    
    return groups;
  }

  async summarizeGroup(messages, strategy) {
    if (this.config.summarizer) {
      try {
        const combined = messages.map(m => `[${m.role}]: ${m.content}`).join('\n\n');
        return await this.config.summarizer(combined);
      } catch (error) {
        console.warn('Summarizer failed:', error.message);
      }
    }
    
    // Fallback extractive summarization
    return this.extractiveSummarize(messages, strategy);
  }

  /**
   * Adaptive compaction: choose best approach based on message characteristics
   */
  async applyAdaptiveCompaction(messages, targetTokensToSave, strategy = 'balanced', currentQuery = null) {
    // Analyze message characteristics
    const analysis = this.analyzeMessages(messages);
    
    let compactedMessages = [...messages];
    const removedMessages = [];
    let tokensSaved = 0;
    
    // Always try at least one technique based on analysis
    let triedAny = false;
    
    // Try semantic compaction if there's any duplication
    if (analysis.duplicateScore > 0.1 || messages.length > 5) {
      triedAny = true;
      const semanticResult = await this.applySemanticCompaction(
        compactedMessages, 
        targetTokensToSave - tokensSaved, 
        strategy, 
        currentQuery
      );
      compactedMessages = semanticResult.compacted;
      removedMessages.push(...semanticResult.removed);
      tokensSaved += semanticResult.tokensSaved;
    }
    
    // Try extractive compaction if messages are verbose or we haven't saved enough
    if (tokensSaved < targetTokensToSave && (analysis.verboseScore > 0.2 || analysis.avgTokens > 50)) {
      triedAny = true;
      const extractiveResult = await this.applyExtractiveCompaction(
        compactedMessages,
        targetTokensToSave - tokensSaved,
        strategy,
        currentQuery
      );
      compactedMessages = extractiveResult.compacted;
      removedMessages.push(...extractiveResult.removed);
      tokensSaved += extractiveResult.tokensSaved;
    }
    
    // Try temporal compaction as last resort if we have timestamps
    if (tokensSaved < targetTokensToSave && analysis.temporalSpread > 0.1) {
      triedAny = true;
      const temporalResult = this.applyTemporalCompaction(
        compactedMessages,
        targetTokensToSave - tokensSaved,
        strategy,
        currentQuery
      );
      compactedMessages = temporalResult.compacted;
      removedMessages.push(...temporalResult.removed);
      tokensSaved += temporalResult.tokensSaved;
    }
    
    // If nothing worked and we still need to save tokens, use aggressive extractive on longest messages
    if (tokensSaved < targetTokensToSave && !triedAny && messages.length > 3) {
      // Find the longest messages
      const messagesWithTokens = messages.map((msg, index) => ({
        msg,
        index,
        tokens: this.countTokens(msg.content),
      }));
      
      messagesWithTokens.sort((a, b) => b.tokens - a.tokens);
      
      // Try to compact the longest messages
      for (const { msg, index, tokens } of messagesWithTokens) {
        if (tokensSaved >= targetTokensToSave) break;
        if (tokens < 30) continue; // Skip very short messages
        
        const extracted = this.extractKeyInformation(msg.content, currentQuery, 'aggressive');
        const extractedTokens = this.countTokens(extracted);
        const savedTokens = tokens - extractedTokens;
        
        if (savedTokens > 0) {
          compactedMessages[index] = {
            ...msg,
            content: `[Compressed]: ${extracted}`,
            extracted: true,
            originalLength: tokens,
          };
          
          removedMessages.push({
            message: msg,
            reason: 'adaptive_fallback',
            extraction: extracted,
            savedTokens,
          });
          
          tokensSaved += savedTokens;
        }
      }
    }
    
    return { compacted: compactedMessages, removed: removedMessages, tokensSaved };
  }

  /**
   * Dynamic context adjustment based on relevance
   */
  async adjustDynamicContext(messages, currentQuery = null) {
    if (messages.length === 0) return messages;
    
    // Update relevance scores
    if (currentQuery) {
      await this.updateRelevanceScores(messages, currentQuery);
    }
    
    // Apply relevance decay over time
    this.applyRelevanceDecay();
    
    // Filter messages below minimum relevance
    const relevantMessages = messages.filter((_, index) => {
      const relevance = this.relevanceScores.get(index) || 0.5;
      return relevance >= this.config.minRelevanceScore;
    });
    
    if (relevantMessages.length < messages.length) {
      const filtered = messages.length - relevantMessages.length;
      const total = messages.length;
      
      // Calculate average relevance of filtered messages
      let avgRelevance = 0;
      let filteredCount = 0;
      for (let i = 0; i < messages.length; i++) {
        if (!relevantMessages.includes(messages[i])) {
          const relevance = this.relevanceScores.get(i) || 0.5;
          avgRelevance += relevance;
          filteredCount++;
        }
      }
      avgRelevance = filteredCount > 0 ? avgRelevance / filteredCount : 0;
      
      // Log to chat
      this.logger.logDynamicContext(filtered, total, avgRelevance);
      this.stats.chatLogs++;
      
      this.stats.dynamicAdjustments++;
      console.log(`[Dynamic Context] Filtered ${filtered} low-relevance messages`);
    }
    
    return relevantMessages;
  }

  /**
   * Update relevance scores based on current query
   */
  async updateRelevanceScores(messages, currentQuery) {
    if (!this.embedder || !currentQuery) return;
    
    try {
      const queryEmbedding = await this.embed(currentQuery);
      
      for (let i = 0; i < messages.length; i++) {
        const msg = messages[i];
        const msgEmbedding = await this.embed(msg.content);
        const similarity = this.cosineSimilarity(queryEmbedding, msgEmbedding);
        
        // Combine similarity with message priority
        const priorityFactor = (msg.priority || 5) / 10;
        const relevance = (similarity * 0.7) + (priorityFactor * 0.3);
        
        this.relevanceScores.set(i, relevance);
      }
      
      this.stats.relevanceUpdates++;
    } catch (error) {
      console.warn('Failed to update relevance scores:', error.message);
    }
  }

  /**
   * Apply relevance decay over time
   */
  applyRelevanceDecay() {
    const now = Date.now();
    const timeSinceLastQuery = now - this.lastQueryTime;
    
    if (timeSinceLastQuery > 5 * 60 * 1000) { // 5 minutes
      for (const [index, relevance] of this.relevanceScores.entries()) {
        const decayed = relevance * Math.pow(this.config.relevanceDecay, timeSinceLastQuery / (60 * 1000));
        this.relevanceScores.set(index, decayed);
      }
    }
  }

  /**
   * Smart Archive Retrieval: Automatically fetch relevant content from archive
   * when current query suggests missing context
   */
  async smartArchiveRetrieval(messages, currentQuery) {
    if (!this.config.enableArchive || !this.archive || !currentQuery) {
      return messages;
    }
    
    // Check if we have space for archive content
    const currentTokens = this.countTokensForMessages(messages);
    const availableTokens = this.config.contextLimit - currentTokens;
    
    // Only retrieve if we have reasonable space (at least 10% of context limit)
    if (availableTokens < this.config.contextLimit * 0.1) {
      return messages;
    }
    
    // Calculate query complexity to decide if archive search is needed
    const queryTokens = this.countTokens(currentQuery);
    const queryComplexity = queryTokens > 20; // Longer queries are more likely to need context
    
    // Check if current messages already contain relevant information
    let hasRelevantContext = false;
    if (this.embedder) {
      try {
        const queryEmbedding = await this.embed(currentQuery);
        for (const msg of messages) {
          const msgEmbedding = await this.embed(msg.content);
          const similarity = this.cosineSimilarity(queryEmbedding, msgEmbedding);
            if (similarity > 0.8) {
            hasRelevantContext = true;
            break;
          }
        }
      } catch (error) {
        console.warn('Failed to check context relevance:', error.message);
      }
    }
    
    // If query is complex AND we don't have highly relevant context, search archive
    if (queryComplexity && !hasRelevantContext) {
      
      const archiveResult = await this.retrieveFromArchive(currentQuery, {
        maxContextTokens: Math.min(availableTokens * 0.5, 2000), // Use up to half available space
        minRelevance: 0.6, // High relevance threshold
        limit: 5, // Limit to top 5 snippets
      });
      
      if (archiveResult.found && archiveResult.snippets.length > 0) {
        // Deduplicate snippets (simple content-based deduplication)
        const uniqueSnippets = [];
        const seenContents = new Set();
        
        for (const snippet of archiveResult.snippets) {
          const normalized = snippet.trim().toLowerCase().substring(0, 100);
          if (!seenContents.has(normalized)) {
            seenContents.add(normalized);
            uniqueSnippets.push(snippet);
          }
        }
        
        // Limit to top 3 unique snippets
        const topSnippets = uniqueSnippets.slice(0, 3);
        
        if (topSnippets.length > 0) {
          console.log(`[Smart Archive] Retrieved ${topSnippets.length} relevant snippets (${archiveResult.totalTokens} tokens)`);
          
          // Log to chat
          const avgSimilarity = archiveResult.relevanceScores ? 
            archiveResult.relevanceScores.reduce((a, b) => a + b, 0) / archiveResult.relevanceScores.length : 0.5;
          this.logger.logArchiveSearch(currentQuery, topSnippets.length, avgSimilarity);
          this.stats.chatLogs++;
          
          // Add archive snippets as system messages at the beginning
          const archiveMessages = topSnippets.map((snippet, index) => ({
            role: 'system',
            content: `[Archived Context]: ${snippet}`,
            priority: 7, // High priority for retrieved context
            fromArchive: true,
            archiveRelevance: archiveResult.relevanceScores?.[index] || 0.5,
          }));
          
          // Combine archive messages with current messages
          const combinedMessages = [...archiveMessages, ...messages];
          const combinedTokens = this.countTokensForMessages(combinedMessages);
          
          // If combined exceeds limit, compact again
          if (combinedTokens > this.config.contextLimit * 0.9) {
            console.log(`[Smart Archive] Combined context (${combinedTokens} tokens) exceeds 90% limit, re-compacting...`);
            const compacted = await this.autoCompact(combinedMessages, currentQuery);
            return compacted;
          }
          
          this.stats.archiveAutoRetrievals++;
          return combinedMessages;
        }
      }
    }
    
    return messages;
  }

  /**
   * Analyze message characteristics
   */
  analyzeMessages(messages) {
    if (messages.length === 0) {
      return {
        duplicateScore: 0,
        verboseScore: 0,
        temporalSpread: 0,
        prioritySpread: 0,
      };
    }
    
    // Calculate duplicate score (based on message lengths and similarities)
    const avgLength = messages.reduce((sum, msg) => sum + msg.content.length, 0) / messages.length;
    const lengthVariance = messages.reduce((sum, msg) => {
      const diff = msg.content.length - avgLength;
      return sum + (diff * diff);
    }, 0) / messages.length;
    
    // Calculate verbose score (percentage of long messages)
    const longMessages = messages.filter(msg => this.countTokens(msg.content) > 150).length;
    const verboseScore = longMessages / messages.length;
    
    // Calculate temporal spread (if timestamps available)
    let temporalSpread = 0;
    if (messages[0].timestamp && messages[messages.length - 1].timestamp) {
      const timeSpan = messages[messages.length - 1].timestamp - messages[0].timestamp;
      temporalSpread = Math.min(timeSpan / (60 * 60 * 1000), 1); // Normalize to 0-1 over 1 hour
    }
    
    // Calculate priority spread
    const priorities = messages.map(msg => msg.priority || 5);
    const minPriority = Math.min(...priorities);
    const maxPriority = Math.max(...priorities);
    const prioritySpread = (maxPriority - minPriority) / 10; // Normalize to 0-1
    
    return {
      duplicateScore: Math.min(lengthVariance / (avgLength * avgLength), 1),
      verboseScore,
      temporalSpread,
      prioritySpread,
      avgTokens: messages.reduce((sum, msg) => sum + this.countTokens(msg.content), 0) / messages.length,
    };
  }

  /**
   * Select strategies based on message analysis
   */
  selectStrategies(analysis, currentQuery = null) {
    const strategies = [];
    
    // Always try semantic if we have enough messages
    if (analysis.duplicateScore > 0.1 || analysis.avgTokens > 30) {
      strategies.push('semantic');
    }
    
    // Try extractive if messages are verbose
    if (analysis.verboseScore > 0.2 || analysis.avgTokens > 50) {
      strategies.push('extractive');
    }
    
    // Try temporal if we have time data
    if (analysis.temporalSpread > 0.2) {
      strategies.push('temporal');
    }
    
    // Always include adaptive as fallback
    strategies.push('adaptive');
    
    return strategies;
  }

  /**
   * Store removed messages in archive
   */
  async storeRemovedInArchive(removedMessages, strategy) {
    if (!this.archive || removedMessages.length === 0) return;
    
    for (const removed of removedMessages) {
      const { message, reason, ...context } = removed;
      
      // Prepare metadata for archive
      const metadata = {
        role: message.role,
        priority: message.priority || 5,
        tokens: this.countTokens(message.content),
        compactedAt: Date.now(),
        compactionReason: reason,
        compactionStrategy: strategy,
        compactionContext: context,
        category: this.determineCategory(message.content),
      };
      
      // Store in archive
      try {
        await this.archive.store(message.content, metadata);
        this.stats.archiveStores++;
      } catch (error) {
        console.warn('Failed to store message in archive:', error.message);
      }
    }
  }

  /**
   * Retrieve relevant information from archive when not in current context
   */
  async retrieveFromArchive(query, options = {}) {
    if (!this.archive) {
      return {
        found: false,
        snippets: [],
        totalTokens: 0,
        sources: [],
        error: 'Archive not enabled',
      };
    }
    
    const result = await this.archive.retrieveRelevantInfo(query, options);
    
    if (result.found) {
      this.stats.archiveRetrievals++;
    }
    
    return result;
  }

  /**
   * Merge similar messages
   */
  async mergeSimilarMessages(message1, message2, strategy) {
    // Simple merging: combine key points
    const content1 = message1.content;
    const content2 = message2.content;
    
    if (strategy === 'aggressive') {
      // Take the longer/more detailed message
      return content1.length > content2.length ? content1 : content2;
    } else {
      // Combine key points from both
      const sentences1 = content1.match(/[^.!?]+[.!?]+/g) || [content1];
      const sentences2 = content2.match(/[^.!?]+[.!?]+/g) || [content2];
      
      // Take unique sentences (simple deduplication)
      const uniqueSentences = new Set([...sentences1, ...sentences2]);
      return Array.from(uniqueSentences).slice(0, 5).join(' ');
    }
  }

  /**
   * Group messages by time windows
   */
  groupByTimeWindows(messages) {
    if (messages.length === 0) return [];
    
    const windows = [];
    const windowSize = 5 * 60 * 1000; // 5 minutes
    
    let currentWindow = {
      messages: [],
      startTime: new Date(messages[0].timestamp || Date.now()),
      endTime: new Date(messages[0].timestamp || Date.now()),
      label: '',
    };
    
    for (const msg of messages) {
      const msgTime = new Date(msg.timestamp || Date.now());
      
      if (msgTime - currentWindow.startTime > windowSize) {
        // Close current window
        currentWindow.label = `${currentWindow.startTime.toLocaleTimeString()} - ${currentWindow.endTime.toLocaleTimeString()}`;
        windows.push(currentWindow);
        
        // Start new window
        currentWindow = {
          messages: [msg],
          startTime: msgTime,
          endTime: msgTime,
          label: '',
        };
      } else {
        currentWindow.messages.push(msg);
        currentWindow.endTime = msgTime;
      }
    }
    
    // Add last window
    if (currentWindow.messages.length > 0) {
      currentWindow.label = `${currentWindow.startTime.toLocaleTimeString()} - ${currentWindow.endTime.toLocaleTimeString()}`;
      windows.push(currentWindow);
    }
    
    return windows;
  }

  /**
   * Summarize a time window
   */
  summarizeTimeWindow(messages, strategy) {
    const allContent = messages.map(m => m.content).join(' ');
    return this.extractiveSummarize([{ content: allContent }], strategy);
  }

  /**
   * Extract key information from verbose content
   */
  extractKeyInformation(content, currentQuery = null, strategy = 'balanced') {
    const sentences = content.match(/[^.!?]+[.!?]+/g) || [content];
    
    // Score sentences based on query relevance and importance markers
    const scoredSentences = sentences.map((sentence, index) => {
      let score = 0;
      
      // Length bonus (medium-length sentences are often most informative)
      const lengthBonus = Math.min(sentence.length / 100, 1) * 0.3;
      
      // Position bonus (first and last sentences are often important)
      const positionBonus = (index === 0 || index === sentences.length - 1) ? 0.2 : 0;
      
      // Importance markers
      const hasImportantMarker = /(important|key|critical|essential|must|should)/i.test(sentence);
      const markerBonus = hasImportantMarker ? 0.3 : 0;
      
      // Query relevance (if query provided)
      let queryBonus = 0;
      if (currentQuery) {
        const queryWords = currentQuery.toLowerCase().split(/\s+/);
        const matchingWords = queryWords.filter(word => 
          sentence.toLowerCase().includes(word)
        ).length;
        queryBonus = (matchingWords / Math.max(queryWords.length, 1)) * 0.2;
      }
      
      score = lengthBonus + positionBonus + markerBonus + queryBonus;
      
      return { sentence: sentence.trim(), score };
    });
    
    // Sort by score
    scoredSentences.sort((a, b) => b.score - a.score);
    
    // Select top sentences based on strategy
    let topCount;
    switch (strategy) {
      case 'aggressive': topCount = 2; break;
      case 'conservative': topCount = 4; break;
      default: topCount = 3; break;
    }
    
    const topSentences = scoredSentences
      .slice(0, Math.min(topCount, scoredSentences.length))
      .filter(s => s.score > 0.2); // Only include sentences with meaningful score
    
    return topSentences.map(s => s.sentence).join(' ');
  }

  /**
   * Determine category for archive entry
   */
  determineCategory(content) {
    const contentLower = content.toLowerCase();
    
    if (contentLower.includes('code') || contentLower.includes('function') || contentLower.includes('import')) {
      return 'code';
    } else if (contentLower.includes('error') || contentLower.includes('failed') || contentLower.includes('issue')) {
      return 'error';
    } else if (contentLower.includes('todo') || contentLower.includes('task') || contentLower.includes('remind')) {
      return 'todo';
    } else if (contentLower.includes('question') || contentLower.includes('ask') || contentLower.includes('what') || contentLower.includes('how')) {
      return 'question';
    } else if (contentLower.includes('prefer') || contentLower.includes('like') || contentLower.includes('want')) {
      return 'preference';
    } else if (contentLower.includes('decision') || contentLower.includes('choose') || contentLower.includes('select')) {
      return 'decision';
    } else {
      return 'general';
    }
  }

  extractiveSummarize(messages, strategy) {
    // Simple extractive summarization: take key sentences
    const allContent = messages.map(m => m.content).join(' ');
    const sentences = allContent.match(/[^.!?]+[.!?]+/g) || [allContent];
    
    // Score sentences (simple heuristic: length and position)
    const scoredSentences = sentences.map((sentence, index) => ({
      sentence,
      score: sentence.length / 100 + (1 - index / sentences.length) * 0.5,
    }));
    
    // Sort by score and take top 3-5
    scoredSentences.sort((a, b) => b.score - a.score);
    const topCount = strategy === 'aggressive' ? 2 : strategy === 'conservative' ? 5 : 3;
    const topSentences = scoredSentences.slice(0, Math.min(topCount, scoredSentences.length));
    
    return topSentences.map(s => s.sentence.trim()).join(' ');
  }

  async embed(text) {
    if (!this.embedder) return null;
    
    try {
      const result = await this.embedder(text, { pooling: 'mean', normalize: true });
      return Array.from(result.data);
    } catch (error) {
      console.warn('Embedding failed:', error.message);
      return null;
    }
  }

  cosineSimilarity(a, b) {
    if (!a || !b || a.length !== b.length) return 0;
    
    let dot = 0, normA = 0, normB = 0;
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  countTokens(text) {
    return this.encoder.encode(text).length;
  }

  countTokensForMessages(messages) {
    return messages.reduce((total, msg) => total + this.countTokens(msg.content || ''), 0);
  }

  getHealthStatus(usageRatio) {
    if (usageRatio >= this.config.aggressiveCompactThreshold) return 'AGGRESSIVE_COMPACT';
    if (usageRatio >= this.config.compactThreshold) return 'COMPACT';
    return 'HEALTHY';
  }

  updateMessageHistory(messages) {
    // Keep track of recent message patterns for better pruning decisions
    this.messageHistory.push({
      timestamp: Date.now(),
      count: messages.length,
      tokens: this.countTokensForMessages(messages),
      compressed: messages.some(m => m.compressed),
    });
    
    // Keep only last 100 entries
    if (this.messageHistory.length > 100) {
      this.messageHistory = this.messageHistory.slice(-100);
    }
  }

  // ---------------------------------------------------------------------------
  // Status and Monitoring
  // ---------------------------------------------------------------------------

  getStatus() {
    const usageRatio = this.tokenUsage / this.config.contextLimit;
    const health = this.getHealthStatus(usageRatio);
    
    const status = {
      health,
      tokens: {
        used: this.tokenUsage,
        limit: this.config.contextLimit,
        remaining: this.config.contextLimit - this.tokenUsage,
        percentage: Math.round(usageRatio * 100),
      },
      messages: this.messageHistory.length > 0 ? this.messageHistory[this.messageHistory.length - 1].count : 0,
      relevanceScores: this.relevanceScores.size,
      stats: { ...this.stats },
      config: {
        strategies: this.config.strategies,
        autoCompact: this.config.autoCompact,
        dynamicContext: this.config.dynamicContext,
        thresholds: {
          compact: this.config.compactThreshold,
          aggressiveCompact: this.config.aggressiveCompactThreshold,
        },
      },
    };
    
    // Add relevance distribution if available
    if (this.relevanceScores.size > 0) {
      const scores = Array.from(this.relevanceScores.values());
      status.relevanceStats = {
        avg: scores.reduce((a, b) => a + b, 0) / scores.length,
        min: Math.min(...scores),
        max: Math.max(...scores),
        lowRelevance: scores.filter(s => s < this.config.minRelevanceScore).length,
      };
    }
    
    // Add archive stats if enabled
    if (this.archive) {
      status.archive = {
        enabled: true,
        stats: this.archive.getStats(),
      };
    } else {
      status.archive = {
        enabled: false,
      };
    }
    
    return status;
  }

  getStats() {
    return { ...this.stats };
  }

  resetStats() {
    this.stats = {
      totalCompacted: 0,
      totalTokensSaved: 0,
      archiveStores: 0,
      archiveRetrievals: 0,
      archiveAutoRetrievals: 0,
      compactions: 0,
      dynamicAdjustments: 0,
      relevanceUpdates: 0,
    };
  }

  // ---------------------------------------------------------------------------
  // Cleanup
  // ---------------------------------------------------------------------------

  destroy() {
    try {
      this.encoder.free();
    } catch (error) {
      // Ignore
    }
    this.embedder = null;
    
    // Clean up archive if exists
    if (this.archive) {
      // Archive cleanup happens automatically
    }
  }
}

// Factory function
export function createContextPruner(options = {}) {
  return new ContextOptimizer(options);
}

// Alias for the new name
export function createContextOptimizer(options = {}) {
  return new ContextOptimizer(options);
}

// Singleton instance
let _instance = null;

export function getContextPruner(options = {}) {
  if (!_instance) {
    _instance = new ContextOptimizer(options);
  }
  return _instance;
}

// Auto-compaction functions
export async function autoCompactMessages(pruner, messages, currentQuery = null) {
  return await pruner.autoCompact(messages, currentQuery);
}

export async function adaptiveCompactMessages(pruner, messages, targetTokens, strategy = 'balanced', currentQuery = null) {
  return await pruner.adaptiveCompact(messages, targetTokens, strategy, currentQuery);
}

export async function adjustDynamicContext(pruner, messages, currentQuery = null) {
  return await pruner.adjustDynamicContext(messages, currentQuery);
}

// Archive-specific functions
export function getArchiveStats(pruner) {
  return pruner.archive ? pruner.archive.getStats() : null;
}

export async function searchArchive(pruner, query, options = {}) {
  if (!pruner.archive) {
    throw new Error('Archive not enabled');
  }
  return await pruner.archive.search(query, options);
}

export async function retrieveFromArchive(pruner, query, options = {}) {
  if (!pruner.archive) {
    throw new Error('Archive not enabled');
  }
  return await pruner.retrieveFromArchive(query, options);
}

export default ContextOptimizer;