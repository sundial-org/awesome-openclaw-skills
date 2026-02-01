// Core MonarchMoney TypeScript Types and Interfaces

export interface MonarchConfig {
  // Authentication
  email?: string
  password?: string
  sessionToken?: string
  
  // API Settings
  baseURL?: string
  timeout?: number
  retries?: number
  retryDelay?: number
  
  // Caching
  cache?: CacheConfig
  enablePersistentCache?: boolean
  cacheEncryptionKey?: string
  
  // Logging
  logLevel?: 'debug' | 'info' | 'warn' | 'error'
  logger?: Logger
  
  // Rate Limiting
  rateLimit?: {
    requestsPerMinute: number
    burstLimit: number
  }
}

export interface CacheConfig {
  // In-memory cache settings
  memoryTTL: {
    accounts: number      // 5 minutes (rarely change)
    categories: number    // 30 minutes (static data)
    transactions: number  // 2 minutes (frequently updated)
    budgets: number      // 10 minutes
  }
  
  // Persistent cache settings
  persistentTTL: {
    session: number      // 24 hours
    userProfile: number  // 1 hour
  }
  
  // Cache invalidation
  autoInvalidate: boolean  // Smart invalidation on writes
  maxMemorySize: number   // Max in-memory cache size (MB)
}

export interface Logger {
  debug(message: string, ...args: unknown[]): void
  info(message: string, ...args: unknown[]): void
  warn(message: string, ...args: unknown[]): void
  error(message: string, ...args: unknown[]): void
}

// Account Types
export interface Account {
  id: string
  displayName: string
  syncDisabled: boolean
  deactivatedAt?: string
  isHidden: boolean
  isAsset: boolean
  includeInNetWorth: boolean
  currentBalance: number
  availableBalance?: number
  dataProvider: string
  dataProviderAccountId?: string
  institutionName: string
  mask?: string
  createdAt: string
  updatedAt: string
  importedFromMint: boolean
  accountTypeId: number
  accountSubtypeId: number
  type: {
    id: number
    name: string
    display: string
  }
  subtype: {
    id: number
    name: string
    display: string
  }
  credential?: {
    id: string
    institutionId: string
    institutionName: string
  }
}

export interface AccountBalance {
  accountId: string
  date: string
  balance: number
}

// Transaction Types
export interface Transaction {
  id: string
  amount: number
  date: string
  merchantName: string
  categoryId?: string
  category?: TransactionCategory
  accountId: string
  account: Account
  notes?: string
  isRecurring: boolean
  needsReview: boolean
  reviewedAt?: string
  createdAt: string
  updatedAt: string
  importedFromMint: boolean
  plaidTransactionId?: string
  dataProvider: string
  dataProviderTransactionId?: string
  hasTags: boolean
  tags?: TransactionTag[]
  isHidden: boolean
  hiddenAt?: string
  isSplit: boolean
  splits?: TransactionSplit[]
  originalDescription?: string
  isCashIn: boolean
  isCashOut: boolean
}

export interface TransactionCategory {
  id: string
  name: string
  displayName?: string
  shortName?: string
  icon?: string
  color?: string
  order: number
  isDefault?: boolean
  isDisabled?: boolean
  isSystemCategory?: boolean
  groupId?: string
  group?: CategoryGroup
  parentCategoryId?: string
  parentCategory?: TransactionCategory
  childCategories?: TransactionCategory[]
  createdAt?: string
  updatedAt?: string
}

export interface TransactionCategoryGroup {
  id: string
  name: string
  type: string
}

export interface TransactionTag {
  id: string
  name: string
  color?: string
  order?: number
  isDefault?: boolean
  createdAt?: string
  updatedAt?: string
}

export interface TransactionSplit {
  id: string
  amount: number
  categoryId?: string
  category?: TransactionCategory
  notes?: string
}

export interface TransactionRule {
  id: string
  conditions: TransactionRuleCondition[]
  actions: TransactionRuleAction[]
  applyToExistingTransactions: boolean
  createdAt: string
  updatedAt: string
}

export interface TransactionRuleCondition {
  field: string
  operation: string
  value: string | number | string[]
}

export interface TransactionRuleAction {
  field: string
  value: string | number | string[]
}

// Budget Types
export interface Budget {
  id: string
  startDate: string
  endDate: string
  categories: BudgetCategory[]
}

export interface BudgetCategory {
  id: string
  name: string
  budgetAmount: number
  spentAmount: number
  remainingAmount: number
  percentSpent: number
  isFlexible: boolean
  flexibleAmounts?: BudgetFlexMonthlyAmounts[]
}

export interface BudgetFlexMonthlyAmounts {
  month: string
  amount: number
}

// Goal Types
export interface Goal {
  id: string
  name: string
  targetAmount: number
  currentAmount: number
  targetDate?: string
  createdAt: string
  updatedAt: string
  completedAt?: string
}

// Investment Types
export interface Holding {
  id: string
  accountId: string
  securityId: string
  security: Security
  quantity: number
  price: number
  value: number
  costBasis?: number
  unrealizedGainLoss?: number
  percentOfPortfolio: number
}

export interface Security {
  id: string
  symbol: string
  name: string
  type: string
  price: number
  priceDate: string
}

// Cashflow Types
export interface CashflowSummary {
  income: number
  expenses: number
  netCashflow: number
  period: string
  categories: CategoryCashflow[]
}

export interface CategoryCashflow {
  categoryId: string
  categoryName: string
  amount: number
  transactionCount: number
}

export interface MonthlyCashflow {
  month: string
  income: number
  expenses: number
  netCashflow: number
}

// Recurring Transaction Types
export interface RecurringTransaction {
  id: string
  merchantName: string
  amount: number
  categoryId?: string
  category?: TransactionCategory
  frequency: string
  nextDate: string
  isActive: boolean
}

// User Profile Types
export interface UserProfile {
  id: string
  email: string
  firstName?: string
  lastName?: string
  timezone: string
  subscriptionType: string
  isMfaEnabled: boolean
  createdAt: string
}

// Bill Types
export interface Bill {
  id: string
  merchantName: string
  amount?: number
  dueDate: string
  categoryId?: string
  category?: TransactionCategory
  isPaid: boolean
}

// Institution Types
export interface Institution {
  id: string
  name: string
  logo?: string
  url?: string
}

// Merchant Types
export interface Merchant {
  id: string
  name: string
  transactionCount: number
  logoUrl?: string
}

// Session Types
export interface SessionInfo {
  isValid: boolean
  createdAt?: string
  lastValidated?: string
  isStale: boolean
  expiresAt?: string
  token?: string
  userId?: string
  email?: string
  deviceUuid?: string
}

// API Method Parameter Types
export interface TransactionListOptions {
  limit?: number
  offset?: number
  startDate?: string
  endDate?: string
  search?: string
  categoryIds?: string[]
  accountIds?: string[]
  tagIds?: string[]
  hasAttachments?: boolean
  hasNotes?: boolean
  hiddenFromReports?: boolean
  isSplit?: boolean
  isRecurring?: boolean
  importedFromMint?: boolean
  syncedFromInstitution?: boolean
  isCredit?: boolean
  absAmountRange?: [number, number]
}

export interface CreateTransactionInput {
  date: string
  accountId: string
  amount: number
  /** Preferred field name (matches Monarch API) */
  merchantName?: string
  /** Deprecated: use merchantName */
  merchant?: string
  categoryId?: string
  notes?: string
  /** Maps to shouldUpdateBalance in the API (default: true) */
  updateBalance?: boolean
  /** Optional owner user id (null = default owner) */
  ownerUserId?: string | null
}

export interface UpdateTransactionInput {
  amount?: number
  date?: string
  /** Preferred field name (matches Monarch API) */
  merchantName?: string
  /** Deprecated: use merchantName */
  merchant?: string
  categoryId?: string
  notes?: string
  hideFromReports?: boolean
  isHidden?: boolean
  tagIds?: string[]
}

export interface CreateAccountInput {
  name: string
  typeName: string
  subtypeName: string
  balance: number
  includeInNetWorth?: boolean
  isAsset?: boolean
}

export interface UpdateAccountInput {
  displayName?: string
  isHidden?: boolean
  includeInNetWorth?: boolean
  currentBalance?: number
}

export interface CreateCategoryInput {
  name: string
  displayName?: string
  shortName?: string
  icon?: string
  color?: string
  groupId?: string
  parentCategoryId?: string
  order?: number
}

export interface UpdateCategoryInput {
  name?: string
  displayName?: string
  shortName?: string
  icon?: string
  color?: string
  groupId?: string
  parentCategoryId?: string
  order?: number
  isDisabled?: boolean
}

export interface CreateTagInput {
  name: string
  color?: string
  order?: number
}

export interface BulkDeleteResult {
  deletedCount: number
  failedCount: number
  errors?: Array<{
    id: string
    message: string
  }>
}

export interface CreateGoalInput {
  name: string
  targetAmount: number
  targetDate?: string
}

export interface UpdateGoalInput {
  name?: string
  targetAmount?: number
  targetDate?: string
  currentAmount?: number
}

export interface CreateHoldingInput {
  accountId: string
  securityId?: string
  ticker?: string
  quantity: number
}

export interface UpdateHoldingInput {
  quantity: number
}

// MCP Types
export interface MCPTool {
  name: string
  description: string
  inputSchema: Record<string, unknown>
}

export interface MCPResource {
  uri: string
  name: string
  description?: string
  mimeType?: string
}

export interface MCPResourceSchema {
  name: string
  description: string
  uriTemplate: string
}

// Error Types
export interface MonarchErrorDetails {
  code?: string
  statusCode?: number
  response?: unknown
  retryAfter?: number
}

// GraphQL Types
export interface GraphQLResponse<T = unknown> {
  data?: T
  errors?: GraphQLError[]
}

export interface GraphQLError {
  message: string
  locations?: Array<{
    line: number
    column: number
  }>
  path?: (string | number)[]
  extensions?: Record<string, unknown>
}

// Utility Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type Nullable<T> = T | null

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

// Additional Transaction API Types
export interface TransactionDetails extends Transaction {
  merchant?: {
    name: string
    id?: string
  }
  isHide?: boolean
  importIdentifier?: string
}

export interface TransactionSummary {
  totalIncome: number
  totalExpenses: number
  netTotal: number
  transactionCount: number
  categorySummary?: {
    categoryId: string
    categoryName: string
    totalAmount: number
    transactionCount: number
  }[]
  monthlyTrend?: {
    month: string
    income: number
    expenses: number
    net: number
  }[]
}

export interface RuleCondition {
  field: string
  operator: string
  value: any
}

export interface RuleAction {
  type: string
  value: any
}

export interface CategoryGroup {
  id: string
  name: string
  displayName?: string
  type?: string
  color?: string
  icon?: string
  order?: number
  isDefault?: boolean
  categories?: TransactionCategory[]
  createdAt?: string
  updatedAt?: string
}

export interface BulkUpdateResult {
  affectedCount: number
  successful: boolean
  errors?: any[]
}

export interface PaginatedTransactions {
  transactions: Transaction[]
  totalCount: number
  hasMore: boolean
  limit: number
  offset: number
}

// Budget API Types
export interface BudgetItem {
  id: string
  amount: number
  categoryId?: string
  categoryGroupId?: string
  timeframe: string
  startDate: string
  endDate?: string
}

export interface CashFlowData {
  totalIncome: number
  totalExpenses: number
  netCashFlow: number
  periods: {
    period: string
    income: number
    expenses: number
    netCashFlow: number
  }[]
  categories: {
    categoryId: string
    categoryName: string
    totalAmount: number
    transactionCount: number
  }[]
}

export interface CashFlowSummary {
  totalIncome: number
  totalExpenses: number
  netCashFlow: number
  averageMonthlyIncome: number
  averageMonthlyExpenses: number
  averageMonthlyNetCashFlow: number
  periodCount: number
}

export interface BillsData {
  totalAmount: number
  totalCount: number
  overdueBills: number
  upcomingBills: number
  bills: {
    id: string
    merchant: { name: string }
    amount: number
    dueDate: string
    isPaid: boolean
    isOverdue: boolean
    category?: { id: string; name: string }
    account?: { id: string; displayName: string }
    recurringRule?: {
      frequency: string
      nextDate: string
    }
  }[]
}

// Export all types
export * from './generated'