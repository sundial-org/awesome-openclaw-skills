import { logger } from '../utils'

interface CacheEntry<T> {
  data: T
  expiresAt: number
  createdAt: number
}

export class MemoryCache {
  private cache = new Map<string, CacheEntry<unknown>>()
  private maxSize: number
  private defaultTTL: number

  constructor(maxSize: number = 100, defaultTTL: number = 300000) { // 5 minutes default
    this.maxSize = maxSize
    this.defaultTTL = defaultTTL
  }

  set<T>(key: string, value: T, ttlMs?: number): void {
    const ttl = ttlMs || this.defaultTTL
    const now = Date.now()
    
    // If cache is full, remove oldest entry
    if (this.cache.size >= this.maxSize) {
      this.evictOldest()
    }

    const entry: CacheEntry<T> = {
      data: value,
      expiresAt: now + ttl,
      createdAt: now
    }

    this.cache.set(key, entry)
    logger.debug(`Cache SET: ${key} (TTL: ${ttl}ms)`)
  }

  get<T>(key: string): T | undefined {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined
    
    if (!entry) {
      logger.debug(`Cache MISS: ${key}`)
      return undefined
    }

    const now = Date.now()
    if (now > entry.expiresAt) {
      this.cache.delete(key)
      logger.debug(`Cache EXPIRED: ${key}`)
      return undefined
    }

    logger.debug(`Cache HIT: ${key}`)
    return entry.data
  }

  has(key: string): boolean {
    const entry = this.cache.get(key)
    if (!entry) {
      return false
    }

    const now = Date.now()
    if (now > entry.expiresAt) {
      this.cache.delete(key)
      return false
    }

    return true
  }

  delete(key: string): boolean {
    const deleted = this.cache.delete(key)
    if (deleted) {
      logger.debug(`Cache DELETE: ${key}`)
    }
    return deleted
  }

  clear(): void {
    const size = this.cache.size
    this.cache.clear()
    logger.debug(`Cache CLEAR: Removed ${size} entries`)
  }

  size(): number {
    return this.cache.size
  }

  keys(): string[] {
    return Array.from(this.cache.keys())
  }

  private evictOldest(): void {
    let oldestKey: string | undefined
    let oldestTime = Date.now()

    for (const [key, entry] of this.cache.entries()) {
      if (entry.createdAt < oldestTime) {
        oldestTime = entry.createdAt
        oldestKey = key
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey)
      logger.debug(`Cache EVICT: ${oldestKey}`)
    }
  }

  // Clean up expired entries
  cleanup(): number {
    const now = Date.now()
    let cleaned = 0

    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        this.cache.delete(key)
        cleaned++
      }
    }

    if (cleaned > 0) {
      logger.debug(`Cache CLEANUP: Removed ${cleaned} expired entries`)
    }

    return cleaned
  }

  // Get cache statistics
  getStats(): {
    size: number
    maxSize: number
    hitRate?: number
    memoryUsage?: number
  } {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      // Note: Hit rate tracking would require additional counters
      // Memory usage is estimated (not precise in Node.js)
    }
  }

  // Invalidate entries matching a pattern
  invalidatePattern(pattern: string | RegExp): number {
    let invalidated = 0
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern

    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key)
        invalidated++
      }
    }

    if (invalidated > 0) {
      logger.debug(`Cache INVALIDATE_PATTERN: Removed ${invalidated} entries matching ${pattern}`)
    }

    return invalidated
  }

  // Get or set pattern - if key doesn't exist, call factory function
  async getOrSet<T>(
    key: string, 
    factory: () => Promise<T>, 
    ttlMs?: number
  ): Promise<T> {
    const existing = this.get<T>(key)
    if (existing !== undefined) {
      return existing
    }

    const value = await factory()
    this.set(key, value, ttlMs)
    return value
  }
}