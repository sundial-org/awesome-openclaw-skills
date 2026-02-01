import { MemoryCache } from './MemoryCache'
import { PersistentCache } from './PersistentCache'
import { CacheConfig } from '../types'
import { logger } from '../utils'

export { MemoryCache } from './MemoryCache'
export { PersistentCache } from './PersistentCache'

export interface CacheInterface<T = unknown> {
  set(key: string, value: T, ttlMs?: number): void | Promise<void>
  get<U extends T>(key: string): U | undefined | Promise<U | undefined>
  has(key: string): boolean | Promise<boolean>
  delete(key: string): boolean | Promise<boolean>
  clear(): void | Promise<void>
  size(): number | Promise<number>
  keys(): string[] | Promise<string[]>
  cleanup(): number | Promise<number>
  invalidatePattern(pattern: string | RegExp): number | Promise<number>
  getOrSet<U extends T>(
    key: string,
    factory: () => Promise<U>,
    ttlMs?: number
  ): Promise<U>
}

export class MultiLevelCache implements CacheInterface {
  private memoryCache: MemoryCache
  private persistentCache?: PersistentCache
  private config: CacheConfig

  constructor(config: CacheConfig, encryptionKey?: string) {
    this.config = config
    
    // Initialize memory cache
    this.memoryCache = new MemoryCache(
      Math.floor(config.maxMemorySize * 0.7), // Use 70% of max size for entries count estimate
      Math.min(...Object.values(config.memoryTTL)) // Use shortest TTL as default
    )

    // Initialize persistent cache if enabled
    if (config.autoInvalidate) {
      this.persistentCache = new PersistentCache(encryptionKey)
    }

    // Start cleanup interval
    this.startCleanupInterval()
  }

  private startCleanupInterval(): void {
    const interval = Math.min(...Object.values(this.config.memoryTTL)) / 2
    
    setInterval(() => {
      this.memoryCache.cleanup()
      this.persistentCache?.cleanup()
    }, interval)
  }

  private getCacheKey(operation: string, params?: Record<string, unknown>): string {
    if (!params) return operation
    
    const sortedParams = Object.keys(params)
      .sort()
      .reduce((sorted, key) => {
        sorted[key] = params[key]
        return sorted
      }, {} as Record<string, unknown>)
    
    return `${operation}:${JSON.stringify(sortedParams)}`
  }

  private getTTL(operation: string): number {
    // Map operation types to TTL configuration
    if (operation.includes('account')) {
      return this.config.memoryTTL.accounts
    }
    if (operation.includes('category')) {
      return this.config.memoryTTL.categories
    }
    if (operation.includes('transaction')) {
      return this.config.memoryTTL.transactions
    }
    if (operation.includes('budget')) {
      return this.config.memoryTTL.budgets
    }
    
    return this.config.memoryTTL.transactions // Default to shortest TTL
  }

  set<T>(key: string, value: T, ttlMs?: number): void {
    const ttl = ttlMs || this.getTTL(key)
    
    // Store in memory cache
    this.memoryCache.set(key, value, ttl)
    
    // Store in persistent cache with longer TTL
    if (this.persistentCache) {
      const persistentTTL = ttl * 2 // Persistent cache lives longer
      this.persistentCache.set(key, value, persistentTTL)
    }
  }

  get<T>(key: string): T | undefined {
    // Try memory cache first
    let value = this.memoryCache.get<T>(key)
    if (value !== undefined) {
      logger.debug(`Multi-level cache HIT (memory): ${key}`)
      return value
    }

    // Try persistent cache
    if (this.persistentCache) {
      value = this.persistentCache.get<T>(key)
      if (value !== undefined) {
        // Promote to memory cache
        const ttl = this.getTTL(key)
        this.memoryCache.set(key, value, ttl)
        logger.debug(`Multi-level cache HIT (persistent): ${key}`)
        return value
      }
    }

    logger.debug(`Multi-level cache MISS: ${key}`)
    return undefined
  }

  has(key: string): boolean {
    return this.memoryCache.has(key) || (this.persistentCache?.has(key) ?? false)
  }

  delete(key: string): boolean {
    const memoryDeleted = this.memoryCache.delete(key)
    const persistentDeleted = this.persistentCache?.delete(key) ?? false
    
    return memoryDeleted || persistentDeleted
  }

  clear(): void {
    this.memoryCache.clear()
    this.persistentCache?.clear()
  }

  size(): number {
    return this.memoryCache.size() + (this.persistentCache?.size() ?? 0)
  }

  keys(): string[] {
    const memoryKeys = this.memoryCache.keys()
    const persistentKeys = this.persistentCache?.keys() ?? []
    
    // Return unique keys
    return [...new Set([...memoryKeys, ...persistentKeys])]
  }

  cleanup(): number {
    const memoryCleaned = this.memoryCache.cleanup()
    const persistentCleaned = this.persistentCache?.cleanup() ?? 0
    
    return memoryCleaned + persistentCleaned
  }

  invalidatePattern(pattern: string | RegExp): number {
    const memoryInvalidated = this.memoryCache.invalidatePattern(pattern)
    const persistentInvalidated = this.persistentCache?.invalidatePattern(pattern) ?? 0
    
    return memoryInvalidated + persistentInvalidated
  }

  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    ttlMs?: number
  ): Promise<T> {
    // Check memory cache first
    const existing = this.get<T>(key)
    if (existing !== undefined) {
      return existing
    }

    // Call factory and cache result
    const value = await factory()
    this.set(key, value, ttlMs)
    return value
  }

  // Cache operations by operation type
  cacheOperation<T>(
    operation: string,
    params: Record<string, unknown> | undefined,
    factory: () => Promise<T>
  ): Promise<T> {
    const key = this.getCacheKey(operation, params)
    const ttl = this.getTTL(operation)
    
    return this.getOrSet(key, factory, ttl)
  }

  // Invalidate cache for specific operations
  invalidateOperation(operation: string, params?: Record<string, unknown>): void {
    if (params) {
      const key = this.getCacheKey(operation, params)
      this.delete(key)
    } else {
      // Invalidate all keys starting with operation
      this.invalidatePattern(`^${operation}`)
    }
  }

  // Smart invalidation based on data changes
  invalidateRelated(operation: string, data?: Record<string, unknown>): void {
    const patterns: string[] = []
    
    if (operation.includes('transaction') && data?.accountId) {
      patterns.push(`get_transactions.*accountIds.*${data.accountId}`)
      patterns.push(`get_account_.*${data.accountId}`)
      patterns.push('get_cashflow')
    }
    
    if (operation.includes('account')) {
      patterns.push('get_accounts')
      patterns.push('get_net_worth')
    }
    
    if (operation.includes('budget')) {
      patterns.push('get_budgets')
      patterns.push('get_cashflow')
    }

    for (const pattern of patterns) {
      this.invalidatePattern(pattern)
    }
  }

  // Get comprehensive cache statistics
  getStats(): {
    memory: ReturnType<MemoryCache['getStats']>
    persistent?: ReturnType<PersistentCache['getStats']>
    total: {
      size: number
      hitRate?: number
    }
  } {
    const memoryStats = this.memoryCache.getStats()
    const persistentStats = this.persistentCache?.getStats()
    
    return {
      memory: memoryStats,
      persistent: persistentStats,
      total: {
        size: memoryStats.size + (persistentStats?.size ?? 0),
      }
    }
  }

  // Preload common data into cache
  async preloadCache(operations: Array<{ operation: string; params?: Record<string, unknown>; factory: () => Promise<unknown> }>): Promise<void> {
    logger.info(`Preloading cache with ${operations.length} operations`)
    
    const promises = operations.map(async ({ operation, params, factory }) => {
      try {
        await this.cacheOperation(operation, params, factory)
      } catch (error) {
        logger.warn(`Failed to preload cache for ${operation}`, error)
      }
    })
    
    await Promise.allSettled(promises)
    logger.info('Cache preloading completed')
  }

  close(): void {
    this.persistentCache?.close()
  }
}