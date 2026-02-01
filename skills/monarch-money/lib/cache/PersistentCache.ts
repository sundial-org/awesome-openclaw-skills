import * as path from 'path'
import * as fs from 'fs'
import * as os from 'os'
import { EncryptionService } from '../utils/encryption'
import { logger } from '../utils'
import { MonarchConfigError } from '../utils/errors'

interface CacheRecord {
  key: string
  value: string // JSON string
  expires_at: number
  created_at: number
}

interface CacheIndex {
  [key: string]: CacheRecord
}

export class PersistentCache {
  private cacheIndex: CacheIndex = {}
  private encryptionKey: string
  private cacheDir: string
  private cacheFile: string
  private saveScheduled = false

  constructor(encryptionKey?: string, cacheDir?: string) {
    this.encryptionKey = encryptionKey || this.generateOrGetKey()
    this.cacheDir = cacheDir || path.join(os.homedir(), '.mm')
    this.cacheFile = path.join(this.cacheDir, 'cache.json')
    this.initializeCache()
  }

  private generateOrGetKey(): string {
    const keyFile = path.join(os.homedir(), '.mm', 'cache.key')
    
    try {
      if (fs.existsSync(keyFile)) {
        return fs.readFileSync(keyFile, 'utf8').trim()
      }
    } catch (error) {
      logger.warn('Failed to read existing cache key, generating new one')
    }

    // Generate new key
    const newKey = EncryptionService.generateKey()
    
    try {
      fs.mkdirSync(path.dirname(keyFile), { recursive: true })
      fs.writeFileSync(keyFile, newKey, { mode: 0o600 })
      logger.info('Generated new cache encryption key')
    } catch (error) {
      logger.warn('Failed to save cache key to file')
    }

    return newKey
  }

  private initializeCache(): void {
    try {
      fs.mkdirSync(this.cacheDir, { recursive: true })

      if (fs.existsSync(this.cacheFile)) {
        try {
          const data = fs.readFileSync(this.cacheFile, 'utf8')
          const decryptedData = EncryptionService.decrypt(data, this.encryptionKey)
          this.cacheIndex = JSON.parse(decryptedData)
        } catch (error) {
          logger.warn('Failed to load existing cache, starting fresh')
          this.cacheIndex = {}
        }
      }

      logger.debug('Persistent cache initialized')
    } catch (error) {
      throw new MonarchConfigError(
        `Failed to initialize persistent cache: ${error instanceof Error ? error.message : 'Unknown error'}`
      )
    }
  }

  private scheduleSave(): void {
    if (this.saveScheduled) return
    
    this.saveScheduled = true
    setTimeout(() => {
      try {
        const data = JSON.stringify(this.cacheIndex)
        const encryptedData = EncryptionService.encrypt(data, this.encryptionKey)
        fs.writeFileSync(this.cacheFile, encryptedData, { mode: 0o600 })
      } catch (error) {
        logger.error('Failed to save cache to file', error)
      }
      this.saveScheduled = false
    }, 1000) // Debounce saves by 1 second
  }

  set<T>(key: string, value: T, ttlMs: number = 3600000): void {
    const now = Date.now()
    const record: CacheRecord = {
      key,
      value: EncryptionService.encrypt(JSON.stringify(value), this.encryptionKey),
      expires_at: now + ttlMs,
      created_at: now
    }

    this.cacheIndex[key] = record
    this.scheduleSave()
    logger.debug(`Persistent cache SET: ${key}`)
  }

  get<T>(key: string): T | undefined {
    const record = this.cacheIndex[key]
    if (!record) {
      return undefined
    }

    const now = Date.now()
    if (now > record.expires_at) {
      delete this.cacheIndex[key]
      this.scheduleSave()
      return undefined
    }

    try {
      const decryptedValue = EncryptionService.decrypt(record.value, this.encryptionKey)
      return JSON.parse(decryptedValue) as T
    } catch (error) {
      logger.error(`Failed to decrypt cache entry: ${key}`, error)
      delete this.cacheIndex[key]
      this.scheduleSave()
      return undefined
    }
  }

  has(key: string): boolean {
    const record = this.cacheIndex[key]
    if (!record) return false

    const now = Date.now()
    if (now > record.expires_at) {
      delete this.cacheIndex[key]
      this.scheduleSave()
      return false
    }

    return true
  }

  delete(key: string): boolean {
    const existed = key in this.cacheIndex
    delete this.cacheIndex[key]
    
    if (existed) {
      this.scheduleSave()
      logger.debug(`Persistent cache DELETE: ${key}`)
    }
    
    return existed
  }

  clear(): void {
    const count = Object.keys(this.cacheIndex).length
    this.cacheIndex = {}
    this.scheduleSave()
    logger.debug(`Persistent cache CLEAR: Removed ${count} entries`)
  }

  size(): number {
    const now = Date.now()
    let validCount = 0

    for (const [key, record] of Object.entries(this.cacheIndex)) {
      if (now > record.expires_at) {
        delete this.cacheIndex[key]
      } else {
        validCount++
      }
    }

    if (Object.keys(this.cacheIndex).length !== validCount) {
      this.scheduleSave()
    }

    return validCount
  }

  keys(): string[] {
    const now = Date.now()
    const validKeys: string[] = []

    for (const [key, record] of Object.entries(this.cacheIndex)) {
      if (now > record.expires_at) {
        delete this.cacheIndex[key]
      } else {
        validKeys.push(key)
      }
    }

    return validKeys
  }

  cleanup(): number {
    const now = Date.now()
    let cleaned = 0

    for (const [key, record] of Object.entries(this.cacheIndex)) {
      if (now > record.expires_at) {
        delete this.cacheIndex[key]
        cleaned++
      }
    }

    if (cleaned > 0) {
      this.scheduleSave()
      logger.debug(`Persistent cache CLEANUP: Removed ${cleaned} expired entries`)
    }

    return cleaned
  }

  getStats(): {
    size: number
    totalEntries: number
    expiredEntries: number
  } {
    const now = Date.now()
    let validCount = 0
    let expiredCount = 0

    for (const record of Object.values(this.cacheIndex)) {
      if (now > record.expires_at) {
        expiredCount++
      } else {
        validCount++
      }
    }

    return {
      size: validCount,
      totalEntries: validCount + expiredCount,
      expiredEntries: expiredCount
    }
  }

  invalidatePattern(pattern: string | RegExp): number {
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern
    let invalidated = 0

    for (const key of Object.keys(this.cacheIndex)) {
      if (regex.test(key)) {
        delete this.cacheIndex[key]
        invalidated++
      }
    }

    if (invalidated > 0) {
      this.scheduleSave()
      logger.debug(`Persistent cache INVALIDATE_PATTERN: Removed ${invalidated} entries`)
    }

    return invalidated
  }

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

  close(): void {
    // Force save any pending changes
    if (this.saveScheduled) {
      try {
        const data = JSON.stringify(this.cacheIndex)
        const encryptedData = EncryptionService.encrypt(data, this.encryptionKey)
        fs.writeFileSync(this.cacheFile, encryptedData, { mode: 0o600 })
      } catch (error) {
        logger.error('Failed to save cache on close', error)
      }
    }
    logger.debug('Persistent cache closed')
  }
}