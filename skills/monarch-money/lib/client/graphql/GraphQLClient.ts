import fetch from 'node-fetch'
import { 
  logger, 
  MonarchGraphQLError, 
  MonarchAPIError,
  handleHTTPResponse, 
  retryWithBackoff 
} from '../../utils'
import { GraphQLResponse, GraphQLError } from '../../types'
import { AuthenticationService } from '../auth'
import { MultiLevelCache } from '../../cache'

export interface GraphQLRequestOptions {
  cache?: boolean
  cacheTTL?: number
  timeout?: number
  retries?: number
}

export class GraphQLClient {
  private baseUrl: string
  private auth: AuthenticationService
  private cache?: MultiLevelCache
  private timeout: number
  private lastRequestTime = 0
  private readonly minRequestInterval = 250 // 250ms for more human-like behavior
  private readonly burstLimit = 5 // Max requests in burst
  private requestTimes: number[] = []
  
  // Enhanced performance features
  private requestDeduplication = new Map<string, Promise<unknown>>()
  private requestQueue: Array<{ resolve: Function; reject: Function; execute: Function }> = []
  private isProcessingQueue = false
  private readonly maxConcurrentRequests = 3
  private activeRequestCount = 0

  constructor(
    baseUrl: string,
    auth: AuthenticationService,
    cache?: MultiLevelCache,
    timeout: number = 30000
  ) {
    this.baseUrl = `${baseUrl}/graphql`
    this.auth = auth
    this.cache = cache
    this.timeout = timeout
  }

  async query<T = unknown>(
    query: string,
    variables?: Record<string, unknown>,
    options: GraphQLRequestOptions = {}
  ): Promise<T> {
    const {
      cache = true,
      cacheTTL,
      timeout = this.timeout,
      retries = 3
    } = options

    // Generate cache key
    const cacheKey = cache && this.cache ? 
      this.generateCacheKey('query', query, variables) : null

    // Try cache first
    if (cacheKey && this.cache) {
      const cached = this.cache.get<T>(cacheKey)
      if (cached !== undefined) {
        logger.debug(`GraphQL cache HIT: ${cacheKey}`)
        return cached
      }
    }

    // Request deduplication - check if identical request is in progress
    const deduplicationKey = this.generateCacheKey('query', query, variables)
    if (this.requestDeduplication.has(deduplicationKey)) {
      logger.debug(`Request deduplication HIT: ${deduplicationKey}`)
      return this.requestDeduplication.get(deduplicationKey) as Promise<T>
    }

    // Create and store deduplication promise
    const requestPromise = this.executeWithQueue<T>(async () => {
      return retryWithBackoff(async () => {
        return this.executeQuery<T>(query, variables, timeout)
      }, retries)
    })

    this.requestDeduplication.set(deduplicationKey, requestPromise)

    try {
      const result = await requestPromise

      // Cache result
      if (cacheKey && this.cache && result) {
        this.cache.set(cacheKey, result, cacheTTL)
        logger.debug(`GraphQL cache SET: ${cacheKey}`)
      }

      return result
    } finally {
      // Clean up deduplication entry
      this.requestDeduplication.delete(deduplicationKey)
    }
  }

  async mutation<T = unknown>(
    mutation: string,
    variables?: Record<string, unknown>,
    options: GraphQLRequestOptions = {}
  ): Promise<T> {
    const { timeout = this.timeout, retries = 3 } = options

    // Execute mutation with queue management
    const result = await this.executeWithQueue<T>(async () => {
      return retryWithBackoff(async () => {
        return this.executeQuery<T>(mutation, variables, timeout)
      }, retries)
    })

    // Invalidate related cache entries for mutations
    if (this.cache) {
      this.invalidateMutationCache(mutation, variables)
    }

    return result
  }

  private async rateLimit(): Promise<void> {
    const now = Date.now()
    
    // Clean old request times (older than 1 minute)
    this.requestTimes = this.requestTimes.filter(time => now - time < 60000)
    
    // Check burst limit - if we've made too many requests recently, wait longer
    if (this.requestTimes.length >= this.burstLimit) {
      const oldestRecentRequest = Math.min(...this.requestTimes)
      const waitTime = 60000 - (now - oldestRecentRequest) + 100 // Wait until burst window resets
      if (waitTime > 0) {
        logger.debug(`Rate limit burst protection: waiting ${waitTime}ms`)
        await new Promise(resolve => setTimeout(resolve, waitTime))
      }
    }
    
    // Standard rate limiting
    const timeSinceLastRequest = now - this.lastRequestTime
    if (timeSinceLastRequest < this.minRequestInterval) {
      const sleepTime = this.minRequestInterval - timeSinceLastRequest
      logger.debug(`Rate limit: waiting ${sleepTime}ms`)
      await new Promise(resolve => setTimeout(resolve, sleepTime))
    }
    
    // Add some randomness to make it more human-like (±50ms)
    const jitter = Math.random() * 100 - 50
    if (jitter > 0) {
      await new Promise(resolve => setTimeout(resolve, jitter))
    }
    
    this.lastRequestTime = Date.now()
    this.requestTimes.push(this.lastRequestTime)
  }

  private async executeQuery<T>(
    query: string,
    variables?: Record<string, unknown>,
    _timeout?: number
  ): Promise<T> {
    // Add rate limiting BEFORE the request like Python library
    await this.rateLimit()
    
    // Ensure we have a valid session
    await this.auth.ensureValidSession()
    
    const token = this.auth.getToken()
    const deviceUuid = this.auth.getDeviceUuid()
    
    if (!token) {
      throw new MonarchAPIError('No authentication token available')
    }

    const requestBody = {
      query: query.trim(),
      variables: variables || {},
      operationName: null // The web UI sends null for operationName when not specified
    }

    const requestHeaders = {
      'Content-Type': 'application/json',
      'Authorization': `Token ${token}`,
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
      'Accept': 'application/json',
      'Client-Platform': 'web', // Fixed: match Python case exactly
      'Origin': 'https://app.monarchmoney.com',
      'device-uuid': deviceUuid || this.auth.getDeviceUuid() || 'unknown',
      'x-cio-client-platform': 'web',
      'x-cio-site-id': '2598be4aa410159198b2',
      'x-gist-user-anonymous': 'false'
    }

    // Debug: Log GraphQL request details
    const safeHeaders = { ...requestHeaders }
    if (safeHeaders.Authorization) {
      safeHeaders.Authorization = 'Token ***'
    }
    logger.debug('GraphQL Request Details:', {
      url: this.baseUrl,
      headers: safeHeaders,
      body: requestBody
    })

    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: requestHeaders,
      body: JSON.stringify(requestBody)
    })

    // Debug: Log response details
    logger.debug(`GraphQL Response: ${response.status} ${response.statusText}`)

    // Get response text first to log it, then handle errors
    const responseText = await response.text()
    logger.debug('GraphQL Response Body:', responseText)

    if (response.status >= 400) {
      handleHTTPResponse(response)
    }

    let data: GraphQLResponse<T>
    try {
      data = JSON.parse(responseText) as GraphQLResponse<T>
    } catch (parseError) {
      logger.error('Failed to parse GraphQL response as JSON:', parseError)
      throw new MonarchAPIError(`Invalid JSON response: ${responseText}`)
    }

    if (data.errors && data.errors.length > 0) {
      this.handleGraphQLErrors(data.errors)
    }

    if (!data.data) {
      throw new MonarchGraphQLError('No data returned from GraphQL query')
    }

    return data.data
  }

  private handleGraphQLErrors(errors: GraphQLError[]): never {
    const firstError = errors[0]
    const message = firstError.message || 'GraphQL error occurred'

    // Check for authentication errors
    if (message.toLowerCase().includes('unauthorized') || 
        message.toLowerCase().includes('authentication') ||
        message.toLowerCase().includes('token')) {
      // Clear session and throw auth error
      this.auth.deleteSession()
      throw new MonarchAPIError('Authentication failed - session expired', 401)
    }

    // Log all errors for debugging
    logger.error('GraphQL errors:', errors)

    throw new MonarchGraphQLError(message, errors)
  }

  private generateCacheKey(
    type: 'query' | 'mutation',
    operation: string,
    variables?: Record<string, unknown>
  ): string {
    const operationName = this.extractOperationName(operation) || type
    
    if (!variables || Object.keys(variables).length === 0) {
      return operationName
    }

    // Sort variables for consistent caching
    const sortedVars = Object.keys(variables)
      .sort()
      .reduce((sorted, key) => {
        sorted[key] = variables[key]
        return sorted
      }, {} as Record<string, unknown>)

    return `${operationName}:${JSON.stringify(sortedVars)}`
  }

  private extractOperationName(operation: string): string | null {
    // Extract operation name from GraphQL query/mutation
    const match = operation.match(/(?:query|mutation)\s+(\w+)/)
    return match ? match[1] : null
  }

  private invalidateMutationCache(mutation: string, variables?: Record<string, unknown>): void {
    if (!this.cache) return

    const operationName = this.extractOperationName(mutation)
    if (!operationName) return

    // Invalidation patterns based on mutation type
    const invalidationPatterns: string[] = []

    if (operationName.toLowerCase().includes('transaction')) {
      invalidationPatterns.push(
        '^GetTransactions',
        '^GetTransactionsSummary',
        '^GetCashflow'
      )

      // If account-specific, invalidate account-related cache
      if (variables?.accountId) {
        invalidationPatterns.push(`GetAccount.*${variables.accountId}`)
      }
    }

    if (operationName.toLowerCase().includes('account')) {
      invalidationPatterns.push(
        '^GetAccounts',
        '^GetNetWorth',
        '^GetAccountHistory'
      )
    }

    if (operationName.toLowerCase().includes('budget')) {
      invalidationPatterns.push(
        '^GetBudgets',
        '^GetCashflow'
      )
    }

    if (operationName.toLowerCase().includes('category')) {
      invalidationPatterns.push(
        '^GetTransactionCategories',
        '^GetCategoryGroups'
      )
    }

    // Execute invalidations
    for (const pattern of invalidationPatterns) {
      const invalidated = this.cache.invalidatePattern(new RegExp(pattern))
      if (invalidated > 0) {
        logger.debug(`Invalidated ${invalidated} cache entries matching ${pattern}`)
      }
    }
  }

  // Batch multiple queries
  async batchQuery<T = unknown>(
    queries: Array<{
      query: string
      variables?: Record<string, unknown>
      operationName?: string
    }>,
    options: GraphQLRequestOptions = {}
  ): Promise<T[]> {
    const { timeout: _timeout = this.timeout, retries: _retries = 3 } = options

    // Execute queries in parallel
    const promises = queries.map(({ query, variables, operationName: _operationName }) => 
      this.query<T>(query, variables, { ...options, cache: false })
    )

    const results = await Promise.allSettled(promises)

    // Check for failures
    const failures = results
      .map((result, index) => ({ result, index }))
      .filter(({ result }) => result.status === 'rejected')

    if (failures.length > 0) {
      logger.warn(`${failures.length} out of ${queries.length} batch queries failed`)
      
      // If more than half failed, throw the first error
      if (failures.length > queries.length / 2) {
        const firstFailure = failures[0]
        if (firstFailure.result.status === 'rejected') {
          throw (firstFailure.result as PromiseRejectedResult).reason
        }
      }
    }

    // Return successful results (with undefined for failures)
    return results.map(result => 
      result.status === 'fulfilled' ? result.value : undefined
    ) as T[]
  }

  // Execute raw GraphQL with minimal processing
  async raw<T = unknown>(
    query: string,
    variables?: Record<string, unknown>
  ): Promise<GraphQLResponse<T>> {
    // Add rate limiting BEFORE the request like Python library
    await this.rateLimit()
    
    await this.auth.ensureValidSession()
    
    const token = this.auth.getToken()
    const deviceUuid = this.auth.getDeviceUuid()
    
    if (!token) {
      throw new MonarchAPIError('No authentication token available')
    }

    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Client-Platform': 'web', // Fixed: match Python case exactly
        'Origin': 'https://app.monarchmoney.com',
        'device-uuid': deviceUuid || this.auth.getDeviceUuid() || 'unknown',
        'x-cio-client-platform': 'web',
        'x-cio-site-id': '2598be4aa410159198b2',
        'x-gist-user-anonymous': 'false'
      },
      body: JSON.stringify({
        query: query.trim(),
        variables: variables || {}
      })
    })

    handleHTTPResponse(response)

    return await response.json() as GraphQLResponse<T>
  }

  // Clear all cached GraphQL responses
  clearCache(): void {
    this.cache?.clear()
    logger.debug('GraphQL cache cleared')
  }

  // Execute request with concurrency control and queue management
  private async executeWithQueue<T>(execute: () => Promise<T>): Promise<T> {
    // If under concurrency limit, execute immediately
    if (this.activeRequestCount < this.maxConcurrentRequests) {
      this.activeRequestCount++
      try {
        const result = await execute()
        return result
      } finally {
        this.activeRequestCount--
        // Process queued requests
        this.processQueue()
      }
    }

    // Otherwise queue the request
    return new Promise<T>((resolve, reject) => {
      this.requestQueue.push({
        resolve,
        reject,
        execute: async () => {
          try {
            const result = await execute()
            resolve(result)
          } catch (error) {
            reject(error)
          }
        }
      })
    })
  }

  private processQueue(): void {
    if (this.isProcessingQueue || this.requestQueue.length === 0) {
      return
    }

    this.isProcessingQueue = true

    // Process requests while under concurrency limit
    while (this.requestQueue.length > 0 && this.activeRequestCount < this.maxConcurrentRequests) {
      const request = this.requestQueue.shift()
      if (request) {
        this.activeRequestCount++
        
        // Execute request asynchronously
        request.execute().finally(() => {
          this.activeRequestCount--
          // Continue processing queue
          setImmediate(() => this.processQueue())
        })
      }
    }

    this.isProcessingQueue = false
  }

  // Advanced analytics for performance monitoring
  getPerformanceStats(): {
    cacheStats: ReturnType<MultiLevelCache['getStats']> | null
    requestStats: {
      activeRequests: number
      queuedRequests: number
      deduplicatedRequests: number
      averageRequestInterval: number
      burstProtectionEngagements: number
    }
  } {
    // Calculate average request interval from recent requests
    const recentRequests = this.requestTimes.slice(-10)
    let averageInterval = 0
    if (recentRequests.length > 1) {
      const intervals = []
      for (let i = 1; i < recentRequests.length; i++) {
        intervals.push(recentRequests[i] - recentRequests[i - 1])
      }
      averageInterval = intervals.reduce((sum, interval) => sum + interval, 0) / intervals.length
    }

    return {
      cacheStats: this.cache?.getStats() || null,
      requestStats: {
        activeRequests: this.activeRequestCount,
        queuedRequests: this.requestQueue.length,
        deduplicatedRequests: this.requestDeduplication.size,
        averageRequestInterval: Math.round(averageInterval),
        burstProtectionEngagements: 0 // Could add counter for this
      }
    }
  }

  // Get cache statistics (backward compatibility)
  getCacheStats(): ReturnType<MultiLevelCache['getStats']> | null {
    return this.cache?.getStats() || null
  }

  // Preload common queries for better performance
  async preloadCommonQueries(): Promise<void> {
    const commonQueries = [
      { query: 'query GetMe { me { id email displayName } }' },
      { query: 'query GetCategories { categories { id name icon } }' },
      { query: 'query GetAccounts { accounts { id displayName displayType } }' }
    ]

    logger.debug('Preloading common queries for better performance...')
    
    const preloadPromises = commonQueries.map(({ query }) => 
      this.query(query, {}, { cache: true, cacheTTL: 300000 }) // 5 min cache
        .catch(error => {
          logger.debug(`Preload failed for query: ${error.message}`)
          return null
        })
    )

    await Promise.allSettled(preloadPromises)
    logger.debug('Common queries preloaded')
  }
}