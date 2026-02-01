// Main exports
export { MonarchClient } from './client/MonarchClient'

// Types
export * from './types'

// Authentication
export { AuthenticationService, SessionStorage } from './client/auth'
export type { LoginOptions, MFAOptions } from './client/auth'

// GraphQL
export { GraphQLClient } from './client/graphql'
export type { GraphQLRequestOptions } from './client/graphql'

// Optimization utilities for MCP and other integrations
export { ResponseFormatter, type VerbosityLevel } from './client/ResponseFormatter'
export { getQueryForVerbosity } from './client/graphql/operations'

// Cache
export { MemoryCache, PersistentCache, MultiLevelCache } from './cache'

// API modules
export type { AccountsAPI } from './api/accounts'
export type { TransactionsAPI } from './api/transactions'
export type { BudgetsAPI } from './api/budgets'

// Utilities
export {
  MonarchError,
  MonarchAuthError,
  MonarchAPIError,
  MonarchRateLimitError,
  MonarchValidationError,
  MonarchNetworkError,
  MonarchGraphQLError,
  MonarchSessionExpiredError,
  MonarchMFARequiredError,
  MonarchConfigError,
  handleHTTPResponse,
  handleGraphQLErrors,
  isRetryableError,
  retryWithBackoff
} from './utils/errors'
export { logger, createLogger } from './utils/logger'
export { EncryptionService } from './utils/encryption'

// Default export
import { MonarchClient as Client } from './client/MonarchClient'
export default Client