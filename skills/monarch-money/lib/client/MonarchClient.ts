import { AuthenticationService, LoginOptions, MFAOptions } from './auth'
import { DirectAuthenticationService, DirectLoginOptions } from './auth/DirectAuthenticationService'
import { GraphQLClient } from './graphql'
import { MultiLevelCache } from '../cache'
import { AccountsAPIImpl } from '../api/accounts'
import { TransactionsAPIImpl } from '../api/transactions'
import { BudgetsAPIImpl } from '../api/budgets'
import { CategoriesAPIImpl } from '../api/categories'
import { CashflowAPIImpl } from '../api/cashflow'
import { RecurringAPIImpl } from '../api/recurring'
import { InstitutionsAPIImpl } from '../api/institutions'
import { InsightsAPIImpl } from '../api/insights'
import { 
  getEnvironmentVariable,
  logger,
  deepMerge
} from '../utils'
import { MonarchConfig, /* CacheConfig, */ SessionInfo } from '../types'

// Default configuration
const DEFAULT_CONFIG: Required<MonarchConfig> = {
  email: '',
  password: '',
  sessionToken: '',
  baseURL: 'https://api.monarchmoney.com',
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
  cache: {
    memoryTTL: {
      accounts: 300000,     // 5 minutes
      categories: 1800000,  // 30 minutes
      transactions: 120000, // 2 minutes
      budgets: 600000,      // 10 minutes
    },
    persistentTTL: {
      session: 86400000,    // 24 hours
      userProfile: 3600000, // 1 hour
    },
    autoInvalidate: true,
    maxMemorySize: 100,     // MB
  },
  enablePersistentCache: true,
  cacheEncryptionKey: '',
  logLevel: 'info',
  logger: logger,
  rateLimit: {
    requestsPerMinute: 60,
    burstLimit: 10,
  },
}

export class MonarchClient {
  private config: Required<MonarchConfig>
  private auth: AuthenticationService
  private directAuth: DirectAuthenticationService
  private graphql: GraphQLClient
  private cache?: MultiLevelCache

  // API modules
  public accounts: AccountsAPIImpl
  public transactions: TransactionsAPIImpl
  public budgets: BudgetsAPIImpl
  public categories: CategoriesAPIImpl
  public cashflow: CashflowAPIImpl
  public recurring: RecurringAPIImpl
  public institutions: InstitutionsAPIImpl
  public insights: InsightsAPIImpl

  constructor(config: MonarchConfig = {}) {
    // Merge with defaults and environment variables
    this.config = this.buildConfig(config)
    
    // Initialize cache if enabled
    if (this.config.enablePersistentCache) {
      this.cache = new MultiLevelCache(this.config.cache, this.config.cacheEncryptionKey)
    }

    // Initialize authentication service
    this.auth = new AuthenticationService(
      this.config.baseURL,
      undefined
    )

    // Initialize direct authentication service with shared session storage
    // We need to access the private sessionStorage, so we'll use a workaround
    this.directAuth = new DirectAuthenticationService(
      this.config.baseURL,
      (this.auth as any).sessionStorage  // Access private property for shared storage
    )

    // Initialize GraphQL client
    this.graphql = new GraphQLClient(
      this.config.baseURL,
      this.auth,
      this.cache,
      this.config.timeout
    )

    // Initialize API modules
    this.accounts = new AccountsAPIImpl(this.graphql)
    this.transactions = new TransactionsAPIImpl(this.graphql)
    this.budgets = new BudgetsAPIImpl(this.graphql)
    this.categories = new CategoriesAPIImpl(this.graphql)
    this.cashflow = new CashflowAPIImpl(this.graphql)
    this.recurring = new RecurringAPIImpl(this.graphql)
    this.institutions = new InstitutionsAPIImpl(this.graphql)
    this.insights = new InsightsAPIImpl(this.graphql)

    logger.info('MonarchClient initialized', {
      baseURL: this.config.baseURL,
      cacheEnabled: !!this.cache,
      timeout: this.config.timeout
    })
  }

  private buildConfig(userConfig: MonarchConfig): Required<MonarchConfig> {
    // Start with defaults
    let config = { ...DEFAULT_CONFIG }

    // Merge environment variables
    const envConfig: MonarchConfig = {
      email: getEnvironmentVariable('MONARCH_EMAIL'),
      password: getEnvironmentVariable('MONARCH_PASSWORD'),
      sessionToken: getEnvironmentVariable('MONARCH_SESSION_TOKEN'),
      baseURL: getEnvironmentVariable('MONARCH_BASE_URL'),
      cacheEncryptionKey: getEnvironmentVariable('MONARCH_CACHE_ENCRYPTION_KEY'),
      logLevel: getEnvironmentVariable('MONARCH_LOG_LEVEL') as 'debug' | 'info' | 'warn' | 'error',
    }

    // Remove undefined values from env config
    const cleanedEnvConfig = Object.fromEntries(
      Object.entries(envConfig).filter(([_, value]) => value !== undefined)
    )

    // Merge configs: defaults -> env -> user
    config = deepMerge(config, cleanedEnvConfig)
    config = deepMerge(config, userConfig)

    return config as Required<MonarchConfig>
  }

  // Authentication methods
  async login(options?: LoginOptions): Promise<void> {
    const loginOptions: LoginOptions = {
      email: options?.email || this.config.email,
      password: options?.password || this.config.password,
      useSavedSession: options?.useSavedSession ?? true,
      saveSession: options?.saveSession ?? true,
      mfaSecretKey: options?.mfaSecretKey,
    }

    await this.auth.login(loginOptions)
  }

  async interactiveLogin(options?: Omit<LoginOptions, 'email' | 'password'>): Promise<void> {
    await this.auth.interactiveLogin(options)
  }

  async multiFactorAuthenticate(options: MFAOptions): Promise<void> {
    await this.auth.multiFactorAuthenticate(options)
  }

  /**
   * Direct login using the proven working authentication approach
   * This bypasses the complex retry logic and directly replicates the working raw authentication
   */
  async directLogin(options: DirectLoginOptions): Promise<void> {
    await this.directAuth.login(options)
  }

  // Session management
  async validateSession(): Promise<boolean> {
    return await this.auth.validateSession()
  }

  isSessionStale(): boolean {
    return this.auth.isSessionStale()
  }

  async ensureValidSession(): Promise<void> {
    // Check if direct auth has a valid session first
    const directSession = this.directAuth.getSessionInfo()
    if (directSession.isValid) {
      return // Direct auth session is valid
    }
    
    // Fall back to regular auth
    return await this.auth.ensureValidSession()
  }

  getSessionInfo(): SessionInfo {
    // Try direct auth first, then fall back to main auth
    const directSession = this.directAuth.getSessionInfo()
    if (directSession.isValid) {
      return directSession
    }
    return this.auth.getSessionInfo()
  }

  saveSession(): void {
    this.auth.saveSession()
  }

  loadSession(): boolean {
    return this.auth.loadSession()
  }

  deleteSession(): void {
    this.auth.deleteSession()
    this.directAuth.deleteSession()
  }

  // GraphQL methods
  async gqlCall<T = unknown>(
    _operation: string,
    query: string,
    variables?: Record<string, unknown>
  ): Promise<T> {
    return await this.graphql.query<T>(query, variables)
  }

  async gqlMutation<T = unknown>(
    _operation: string,
    mutation: string,
    variables?: Record<string, unknown>
  ): Promise<T> {
    return await this.graphql.mutation<T>(mutation, variables)
  }

  // GraphQL client access (for advanced usage like schema discovery)
  getGraphQLClient(): GraphQLClient {
    return this.graphql
  }

  // Cache management
  clearCache(): void {
    this.cache?.clear()
    this.graphql.clearCache()
  }

  getCacheStats(): ReturnType<MultiLevelCache['getStats']> | null {
    return this.cache?.getStats() || null
  }

  async preloadCache(operations: Array<{
    operation: string
    params?: Record<string, unknown>
    factory: () => Promise<unknown>
  }>): Promise<void> {
    if (this.cache) {
      await this.cache.preloadCache(operations)
    }
  }

  // Utility methods
  getVersion(): { version: string; sessionInfo: SessionInfo } {
    return {
      version: '1.0.0',
      sessionInfo: this.getSessionInfo()
    }
  }

  setTimeout(timeoutMs: number): void {
    this.config.timeout = timeoutMs
    // Note: We'd need to recreate the GraphQL client to apply the new timeout
    logger.info(`Timeout updated to ${timeoutMs}ms`)
  }

  setToken(token: string): void {
    this.config.sessionToken = token
    // Note: This would need to be passed to the auth service
    logger.info('Token updated')
  }

  // Cleanup
  async close(): Promise<void> {
    this.cache?.close()
    logger.info('MonarchClient closed')
  }

  // Legacy method aliases for backward compatibility
  async get_accounts(includeHidden?: boolean): Promise<ReturnType<AccountsAPIImpl['getAll']>> {
    return this.accounts.getAll({ includeHidden })
  }

  async get_me(): Promise<unknown> {
    const GET_ME_QUERY = `
      query Common_GetMe {
        me {
          id
          birthday
          email
          isSuperuser
          name
          timezone
          hasPassword
          hasMfaOn
          externalAuthProviderNames
          pendingEmailUpdateVerification {
            email
            __typename
          }
          profilePicture {
            id
            cloudinaryPublicId
            thumbnailUrl
            __typename
          }
          profilePictureUrl
          activeSupportAccountAccessGrant {
            id
            createdAt
            expiresAt
            __typename
          }
          profile {
            id
            hasSeenCategoriesManagementTour
            dismissedTransactionsListUpdatesTourAt
            viewedMarkAsReviewedUpdatesCalloutAt
            hasDismissedWhatsNewAt
            __typename
          }
          __typename
        }
      }
    `

    return await this.graphql.query<{
      me: {
        id: string
        birthday?: string
        email: string
        isSuperuser?: boolean
        name?: string
        timezone: string
        hasPassword?: boolean
        hasMfaOn?: boolean
        externalAuthProviderNames?: string[]
        pendingEmailUpdateVerification?: {
          email: string
          __typename: string
        }
        profilePicture?: {
          id: string
          cloudinaryPublicId: string
          thumbnailUrl: string
          __typename: string
        }
        profilePictureUrl?: string
        activeSupportAccountAccessGrant?: {
          id: string
          createdAt: string
          expiresAt: string
          __typename: string
        }
        profile?: {
          id: string
          hasSeenCategoriesManagementTour?: boolean
          dismissedTransactionsListUpdatesTourAt?: string
          viewedMarkAsReviewedUpdatesCalloutAt?: string
          hasDismissedWhatsNewAt?: string
          __typename: string
        }
        __typename: string
      }
    }>(GET_ME_QUERY).then(response => response.me)
  }

  // Environment detection
  static isNode(): boolean {
    return typeof process !== 'undefined' && process.versions?.node !== undefined
  }

  static isBrowser(): boolean {
    return typeof globalThis !== 'undefined' && 
           typeof (globalThis as any).window !== 'undefined' && 
           typeof (globalThis as any).window.document !== 'undefined'
  }

  // Static factory methods
  static create(config?: MonarchConfig): MonarchClient {
    return new MonarchClient(config)
  }

  static async createAndLogin(config: MonarchConfig & { 
    email: string
    password: string 
  }): Promise<MonarchClient> {
    const client = new MonarchClient(config)
    await client.login({
      email: config.email,
      password: config.password
    })
    return client
  }
}