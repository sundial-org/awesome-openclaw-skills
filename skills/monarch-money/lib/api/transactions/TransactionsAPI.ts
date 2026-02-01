import { GraphQLClient } from '../../client/graphql'
import {
  Transaction,
  TransactionDetails,
  TransactionSummary,
  TransactionRule,
  TransactionTag,
  TransactionCategory,
  CategoryGroup,
  Merchant,
  RecurringTransaction,
  BulkUpdateResult,
  PaginatedTransactions
} from '../../types'
import {
  validateTransactionId,
  validateDateRange,
  logger
} from '../../utils'

export interface TransactionsAPI {
  // Core CRUD operations
  getTransactions(options?: GetTransactionsOptions): Promise<PaginatedTransactions>
  getTransactionDetails(transactionId: string): Promise<TransactionDetails>
  createTransaction(data: CreateTransactionInput): Promise<Transaction>
  updateTransaction(transactionId: string, data: UpdateTransactionInput): Promise<Transaction>
  deleteTransaction(transactionId: string): Promise<boolean>

  // Summary and aggregation
  getTransactionsSummary(): Promise<TransactionSummary>
  getTransactionsSummaryCard(): Promise<any>

  // Transaction splits
  getTransactionSplits(transactionId: string): Promise<any>
  updateTransactionSplits(transactionId: string, splits: TransactionSplit[]): Promise<Transaction>

  // Bulk operations
  bulkUpdateNotes(updates: NoteUpdate[]): Promise<BulkNoteUpdateResult>

  // Transaction rules
  getTransactionRules(): Promise<TransactionRule[]>
  createTransactionRule(data: CreateTransactionRuleInput): Promise<TransactionRule>
  updateTransactionRule(ruleId: string, data: UpdateTransactionRuleInput): Promise<TransactionRule>
  deleteTransactionRule(ruleId: string): Promise<boolean>
  deleteAllTransactionRules(): Promise<boolean>
  previewTransactionRule(conditions: RuleCondition[], actions: RuleAction[]): Promise<any>

  // Categories
  getTransactionCategories(): Promise<TransactionCategory[]>
  createTransactionCategory(data: CreateTransactionCategoryInput): Promise<TransactionCategory>
  updateTransactionCategory(categoryId: string, data: UpdateTransactionCategoryInput): Promise<TransactionCategory>
  deleteTransactionCategory(categoryId: string): Promise<boolean>
  getTransactionCategoryGroups(): Promise<CategoryGroup[]>
  getCategoryDetails(categoryId: string): Promise<any>

  // Tags
  getTransactionTags(): Promise<TransactionTag[]>
  createTransactionTag(data: CreateTransactionTagInput): Promise<TransactionTag>
  setTransactionTags(transactionId: string, tagIds: string[]): Promise<Transaction>

  // Merchants
  getMerchants(options?: GetMerchantsOptions): Promise<Merchant[]>
  getMerchantDetails(merchantId: string): Promise<any>
  getEditMerchant(merchantId: string): Promise<any>

  // Recurring transactions
  getRecurringTransactions(options?: GetRecurringTransactionsOptions): Promise<RecurringTransaction[]>
  getRecurringStreams(options?: GetRecurringStreamsOptions): Promise<any[]>
  getAggregatedRecurringItems(options: GetAggregatedRecurringItemsOptions): Promise<any>
  getAllRecurringTransactionItems(options?: GetAllRecurringTransactionItemsOptions): Promise<any[]>
  reviewRecurringStream(streamId: string, reviewStatus: string): Promise<any>
  markStreamAsNotRecurring(streamId: string): Promise<boolean>
  getRecurringMerchantSearchStatus(): Promise<any>

  // Bulk operations
  bulkUpdateTransactions(data: BulkUpdateTransactionsInput): Promise<BulkUpdateResult>
  bulkHideTransactions(transactionIds: string[], filters?: any): Promise<BulkUpdateResult>
  bulkUnhideTransactions(transactionIds: string[], filters?: any): Promise<BulkUpdateResult>
  getHiddenTransactions(options?: GetHiddenTransactionsOptions): Promise<PaginatedTransactions>
}

// Input/Options interfaces
export interface GetTransactionsOptions {
  limit?: number
  offset?: number
  startDate?: string
  endDate?: string
  categoryIds?: string[]
  accountIds?: string[]
  tagIds?: string[]
  merchantIds?: string[]
  search?: string
  isCredit?: boolean
  absAmountRange?: [number?, number?]
}

export interface CreateTransactionInput {
  accountId: string
  /** Preferred field name (matches Monarch API) */
  merchantName?: string
  /** Deprecated: use merchantName */
  merchant?: string
  amount: number
  date: string
  categoryId?: string
  notes?: string
  /** Maps to shouldUpdateBalance in the API (default: true) */
  updateBalance?: boolean
  /** Optional owner user id (null = default owner) */
  ownerUserId?: string | null
}

export interface UpdateTransactionInput {
  /** Preferred field name (matches Monarch API) */
  merchantName?: string
  /** Deprecated: use merchantName */
  merchant?: string
  amount?: number
  date?: string
  categoryId?: string
  notes?: string
  hideFromReports?: boolean
  isHidden?: boolean
  tagIds?: string[]
}

/**
 * Transaction split configuration
 * Used when splitting transactions into multiple categories
 */
export interface TransactionSplit {
  merchantName: string
  amount: number
  categoryId: string
  notes?: string
  hideFromReports?: boolean
}

/**
 * Note update for bulk operations
 */
export interface NoteUpdate {
  transactionId: string
  notes: string
}

/**
 * Result from bulk note updates
 */
export interface BulkNoteUpdateResult {
  successful: number
  failed: number
  errors: Array<{ transactionId: string; error: string }>
}

export interface CreateTransactionRuleInput {
  name: string
  conditions: RuleCondition[]
  actions: RuleAction[]
  priority?: number
}

export interface UpdateTransactionRuleInput {
  name?: string
  conditions?: RuleCondition[]
  actions?: RuleAction[]
  priority?: number
  isEnabled?: boolean
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

export interface CreateTransactionCategoryInput {
  name: string
  groupId: string
  icon?: string
  color?: string
}

export interface UpdateTransactionCategoryInput {
  name?: string
  icon?: string
  color?: string
}

export interface CreateTransactionTagInput {
  name: string
  color: string
}

export interface GetMerchantsOptions {
  search?: string
  limit?: number
}

export interface GetRecurringTransactionsOptions {
  startDate?: string
  endDate?: string
}

export interface GetRecurringStreamsOptions {
  includeLiabilities?: boolean
  includePending?: boolean
  filters?: any
}

export interface GetAggregatedRecurringItemsOptions {
  startDate: string
  endDate: string
  groupBy?: string
  filters?: any
}

export interface GetAllRecurringTransactionItemsOptions {
  filters?: any
  includeLiabilities?: boolean
}

export interface BulkUpdateTransactionsInput {
  transactionIds: string[]
  updates: Record<string, any>
  excludedTransactionIds?: string[]
  allSelected?: boolean
  filters?: any
}

export interface GetHiddenTransactionsOptions {
  limit?: number
  offset?: number
  orderBy?: string
}

export class TransactionsAPIImpl implements TransactionsAPI {
  constructor(private graphql: GraphQLClient) {}

  async getTransactions(options: GetTransactionsOptions = {}): Promise<PaginatedTransactions> {
    const {
      limit = 100,
      offset = 0,
      startDate,
      endDate,
      categoryIds,
      accountIds,
      tagIds,
      merchantIds,
      search,
      isCredit,
      absAmountRange
    } = options

    if (startDate && endDate) {
      validateDateRange(startDate, endDate)
    }

    // Build filters object for web app compatibility
    const filters: any = {
      transactionVisibility: 'non_hidden_transactions_only'
    }

    if (startDate) filters.startDate = startDate
    if (endDate) filters.endDate = endDate
    if (categoryIds && categoryIds.length > 0) filters.categoryIds = categoryIds
    if (accountIds && accountIds.length > 0) filters.accountIds = accountIds
    if (tagIds && tagIds.length > 0) filters.tagIds = tagIds
    if (merchantIds && merchantIds.length > 0) filters.merchantIds = merchantIds
    if (search) filters.search = search
    if (isCredit !== undefined) filters.isCredit = isCredit
    if (absAmountRange) {
      if (absAmountRange[0] !== undefined) filters.minAmount = absAmountRange[0]
      if (absAmountRange[1] !== undefined) filters.maxAmount = absAmountRange[1]
    }

    const variables = {
      limit,
      offset,
      filters,
      orderBy: 'date'
    }

    logger.debug('Getting transactions with options:', variables)

    // Minified query for reduced payload size
    const query = `query Web_GetTransactionsList($offset:Int,$limit:Int,$filters:TransactionFilterInput,$orderBy:TransactionOrdering){allTransactions(filters:$filters){totalCount totalSelectableCount results(offset:$offset,limit:$limit,orderBy:$orderBy){id amount pending date hideFromReports hiddenByAccount plaidName notes isRecurring reviewStatus needsReview isSplitTransaction dataProviderDescription attachments{id}goal{id name}category{id name icon group{id type}}merchant{name id transactionsCount logoUrl recurringTransactionStream{frequency isActive}}tags{id name color order}account{id displayName icon logoUrl}}}transactionRules{id}}`

    const data = await this.graphql.query<{
      allTransactions: {
        totalCount: number
        totalSelectableCount: number
        results: Transaction[]
      }
      transactionRules: Array<{ id: string }>
    }>(query, variables)

    logger.debug(`Retrieved ${data.allTransactions.results.length} transactions using web app schema`)

    return {
      transactions: data.allTransactions.results,
      totalCount: data.allTransactions.totalCount,
      hasMore: offset + limit < data.allTransactions.totalCount,
      limit,
      offset
    }
  }

  async getTransactionDetails(transactionId: string): Promise<TransactionDetails> {
    validateTransactionId(transactionId)

    const query = `
      query GetTransactionDrawer($transactionId: String!) {
        getTransaction(id: $transactionId) {
          id
          amount
          date
          merchant {
            name
          }
          category {
            id
            name
            icon
            color
          }
          account {
            id
            displayName
            type {
              name
            }
            institution {
              name
              plaidInstitutionId
            }
          }
          tags {
            id
            name
            color
          }
          splits {
            id
            amount
            category {
              id
              name
            }
          }
          isRecurring
          reviewStatus
          notes
          originalDescription
          needsReview
          dataProvider
          dataProviderDescription
          isHide
          importIdentifier
          plaidTransactionId
        }
      }
    `

    const data = await this.graphql.query<{
      getTransaction: TransactionDetails
    }>(query, { transactionId })

    return data.getTransaction
  }

  async createTransaction(data: CreateTransactionInput): Promise<Transaction> {
    const {
      accountId,
      merchantName,
      merchant,
      amount,
      date,
      categoryId,
      notes,
      updateBalance,
      ownerUserId
    } = data

    const resolvedMerchant = merchantName ?? merchant
    if (!resolvedMerchant) {
      throw new Error('merchantName is required to create a transaction')
    }

    const mutation = `
      mutation Common_CreateTransactionMutation($input: CreateTransactionMutationInput!) {
        createTransaction(input: $input) {
          transaction {
            id
            amount
            date
            notes
            merchant {
              id
              name
            }
            category {
              id
              name
              icon
              color
            }
            account {
              id
              displayName
            }
          }
          errors {
            message
            code
            fieldErrors {
              field
              messages
            }
          }
        }
      }
    `

    const input: Record<string, any> = {
      date,
      shouldUpdateBalance: updateBalance ?? true,
      amount,
      merchantName: resolvedMerchant,
      accountId,
      ownerUserId: ownerUserId ?? null,
    }

    if (categoryId) input.categoryId = categoryId
    if (notes !== undefined) input.notes = notes

    const result = await this.graphql.mutation<{
      createTransaction: {
        transaction: Transaction
        errors?: any
      }
    }>(mutation, { input })

    const errors = result.createTransaction?.errors
    if (errors) {
      const errorList = Array.isArray(errors) ? errors : [errors]
      if (errorList.length > 0) {
        const first = errorList[0]
        const message = first?.message || first?.fieldErrors?.[0]?.messages?.join(', ')
        throw new Error(`Transaction creation failed: ${message || 'Unknown error'}`)
      }
    }

    logger.info('Transaction created successfully:', result.createTransaction.transaction.id)
    return result.createTransaction.transaction
  }

  async updateTransaction(transactionId: string, data: UpdateTransactionInput): Promise<Transaction> {
    validateTransactionId(transactionId)

    const updates: Record<string, any> = {}
    const resolvedMerchant = data.merchantName ?? data.merchant

    if (resolvedMerchant) updates.merchantName = resolvedMerchant
    if (data.amount !== undefined) updates.amount = data.amount
    if (data.date) updates.date = data.date
    if (data.categoryId) updates.categoryId = data.categoryId
    if (data.notes !== undefined) updates.notes = data.notes

    const hide = data.hideFromReports ?? data.isHidden
    if (hide !== undefined) updates.hide = hide

    if (data.tagIds && data.tagIds.length > 0) updates.tagIds = data.tagIds

    if (Object.keys(updates).length === 0) {
      // Nothing to update, return current details
      return (await this.getTransactionDetails(transactionId)) as unknown as Transaction
    }

    const mutation = `mutation Common_BulkUpdateTransactionsMutation($selectedTransactionIds:[ID!]$excludedTransactionIds:[ID!]$allSelected:Boolean!$expectedAffectedTransactionCount:Int!$updates:TransactionUpdateParams!$filters:TransactionFilterInput){bulkUpdateTransactions(selectedTransactionIds:$selectedTransactionIds excludedTransactionIds:$excludedTransactionIds updates:$updates allSelected:$allSelected expectedAffectedTransactionCount:$expectedAffectedTransactionCount filters:$filters){success affectedCount errors{message}}}`

    const result = await this.graphql.mutation<{
      bulkUpdateTransactions: {
        success: boolean
        affectedCount: number
        errors?: Array<{ message: string }>
      }
    }>(mutation, {
      selectedTransactionIds: [transactionId],
      excludedTransactionIds: [],
      allSelected: false,
      expectedAffectedTransactionCount: 1,
      updates,
      filters: { transactionVisibility: 'non_hidden_transactions_only' },
    })

    if (!result.bulkUpdateTransactions?.success) {
      const message = result.bulkUpdateTransactions?.errors?.[0]?.message || 'Unknown error'
      throw new Error(`Transaction update failed: ${message}`)
    }

    logger.info('Transaction updated successfully:', transactionId)
    return (await this.getTransactionDetails(transactionId)) as unknown as Transaction
  }

  async deleteTransaction(transactionId: string): Promise<boolean> {
    validateTransactionId(transactionId)

    const mutation = `mutation Common_BulkDeleteTransactionsMutation($selectedTransactionIds:[ID!]$excludedTransactionIds:[ID!]$allSelected:Boolean!$expectedAffectedTransactionCount:Int!$filters:TransactionFilterInput){bulkDeleteTransactions(input:{selectedTransactionIds:$selectedTransactionIds excludedTransactionIds:$excludedTransactionIds isAllSelected:$allSelected expectedAffectedTransactionCount:$expectedAffectedTransactionCount filters:$filters}){success affectedCount errors{message}}}`

    const result = await this.graphql.mutation<{
      bulkDeleteTransactions: {
        success: boolean
        affectedCount: number
        errors?: Array<{ message: string }>
      }
    }>(mutation, {
      selectedTransactionIds: [transactionId],
      excludedTransactionIds: [],
      allSelected: false,
      expectedAffectedTransactionCount: 1,
      filters: { transactionVisibility: 'non_hidden_transactions_only' },
    })

    if (!result.bulkDeleteTransactions?.success) {
      const message = result.bulkDeleteTransactions?.errors?.[0]?.message || 'Unknown error'
      logger.warn(`Transaction delete failed: ${message}`)
      return false
    }

    logger.info('Transaction deleted successfully:', transactionId)
    return true
  }

  async getTransactionsSummary(): Promise<TransactionSummary> {
    const query = `
      query GetTransactionsPage {
        transactionsSummary {
          totalIncome
          totalExpenses
          netTotal
          transactionCount
          categorySummary {
            categoryId
            categoryName
            totalAmount
            transactionCount
          }
          monthlyTrend {
            month
            income
            expenses
            net
          }
        }
      }
    `

    const data = await this.graphql.query<{
      transactionsSummary: TransactionSummary
    }>(query)

    return data.transactionsSummary
  }

  async getTransactionsSummaryCard(): Promise<any> {
    const query = `
      query GetTransactionsSummaryCard {
        transactionsSummaryCard {
          totalTransactions
          totalAmount
          averageTransaction
          topCategories {
            categoryId
            categoryName
            amount
            count
          }
          recentTransactions {
            id
            merchant {
              name
            }
            amount
            date
          }
        }
      }
    `

    const data = await this.graphql.query<{
      transactionsSummaryCard: any
    }>(query)

    return data.transactionsSummaryCard
  }

  async getTransactionSplits(transactionId: string): Promise<any> {
    validateTransactionId(transactionId)

    const query = `
      query TransactionSplitQuery($transactionId: String!) {
        getTransaction(id: $transactionId) {
          splits {
            id
            amount
            category {
              id
              name
              icon
              color
            }
          }
        }
      }
    `

    const data = await this.graphql.query<{
      getTransaction: {
        splits: any[]
      }
    }>(query, { transactionId })

    return data.getTransaction.splits
  }

  async updateTransactionSplits(transactionId: string, splits: TransactionSplit[]): Promise<Transaction> {
    validateTransactionId(transactionId)

    // Split transaction using browser mutation
    const splitMutation = `mutation Common_SplitTransactionMutation($input:UpdateTransactionSplitMutationInput!){updateTransactionSplit(input:$input){errors{message code}transaction{id amount hasSplitTransactions splitTransactions{id amount notes merchant{name}category{id name}}}}}`

    const splitData = splits.map(split => ({
      merchantName: split.merchantName,
      hideFromReports: split.hideFromReports || false,
      amount: split.amount,
      categoryId: split.categoryId,
      ownerUserId: null,
    }))

    const splitResult = await this.graphql.mutation<{
      updateTransactionSplit: {
        errors?: Array<{ message: string; code: string }>
        transaction: Transaction & {
          splitTransactions: Array<{
            id: string
            amount: number
            notes?: string
            merchant: { name: string }
            category: { id: string; name: string }
          }>
        }
      }
    }>(splitMutation, {
      input: { transactionId, splitData },
    })

    if (splitResult.updateTransactionSplit.errors) {
      throw new Error(
        `Split failed: ${JSON.stringify(splitResult.updateTransactionSplit.errors)}`
      )
    }

    const transaction = splitResult.updateTransactionSplit.transaction

    // Update notes in parallel for splits that have notes
    if (transaction.splitTransactions && splits.some(s => s.notes)) {
      const bulkUpdateMutation = `mutation Common_BulkUpdateTransactionsMutation($selectedTransactionIds:[ID!]$excludedTransactionIds:[ID!]$allSelected:Boolean!$expectedAffectedTransactionCount:Int!$updates:TransactionUpdateParams!$filters:TransactionFilterInput){bulkUpdateTransactions(selectedTransactionIds:$selectedTransactionIds excludedTransactionIds:$excludedTransactionIds updates:$updates allSelected:$allSelected expectedAffectedTransactionCount:$expectedAffectedTransactionCount filters:$filters){success affectedCount errors{message}}}`

      // Build array of note update promises
      const noteUpdatePromises = splits
        .map((split, i) => {
          if (!split.notes || !transaction.splitTransactions[i]) {
            return null
          }

          const splitId = transaction.splitTransactions[i].id

          // Return promise for parallel execution
          return this.graphql.mutation<{
            bulkUpdateTransactions: {
              success: boolean
              affectedCount: number
              errors?: Array<{ message: string }>
            }
          }>(bulkUpdateMutation, {
            selectedTransactionIds: [splitId],
            excludedTransactionIds: [],
            allSelected: false,
            expectedAffectedTransactionCount: 1,
            updates: { notes: split.notes },
            filters: { transactionVisibility: 'non_hidden_transactions_only' },
          }).then(result => {
            if (!result.bulkUpdateTransactions.success) {
              logger.warn(`Failed to add notes to split ${i + 1}`)
            }
            return result
          })
        })
        .filter(Boolean) // Remove nulls

      // Execute all note updates in parallel
      await Promise.all(noteUpdatePromises)

      logger.info(
        `Split transaction completed with ${noteUpdatePromises.length} note updates (parallel)`
      )
    }

    return transaction
  }


  /**
   * Bulk update notes in parallel
   *
   * Updates multiple transaction notes simultaneously.
   *
   * @param updates - Array of transaction ID + notes pairs
   * @returns Result with success/failure counts
   */
  async bulkUpdateNotes(updates: NoteUpdate[]): Promise<BulkNoteUpdateResult> {
    const bulkUpdateMutation = `mutation Common_BulkUpdateTransactionsMutation($selectedTransactionIds:[ID!]$excludedTransactionIds:[ID!]$allSelected:Boolean!$expectedAffectedTransactionCount:Int!$updates:TransactionUpdateParams!$filters:TransactionFilterInput){bulkUpdateTransactions(selectedTransactionIds:$selectedTransactionIds excludedTransactionIds:$excludedTransactionIds updates:$updates allSelected:$allSelected expectedAffectedTransactionCount:$expectedAffectedTransactionCount filters:$filters){success affectedCount errors{message}}}`

    const promises = updates.map(({ transactionId, notes }) =>
      this.graphql.mutation<{
        bulkUpdateTransactions: {
          success: boolean
          affectedCount: number
          errors?: Array<{ message: string }>
        }
      }>(bulkUpdateMutation, {
        selectedTransactionIds: [transactionId],
        excludedTransactionIds: [],
        allSelected: false,
        expectedAffectedTransactionCount: 1,
        updates: { notes },
        filters: { transactionVisibility: 'non_hidden_transactions_only' },
      })
        .then(result => ({
          transactionId,
          success: result.bulkUpdateTransactions.success,
          error: result.bulkUpdateTransactions.errors?.[0]?.message,
        }))
        .catch(error => ({
          transactionId,
          success: false,
          error: error.message,
        }))
    )

    const results = await Promise.all(promises)

    const successful = results.filter(r => r.success).length
    const failed = results.filter(r => !r.success).length
    const errors = results
      .filter(r => !r.success)
      .map(r => ({ transactionId: r.transactionId, error: r.error || 'Unknown error' }))

    logger.info(`Bulk note update completed: ${successful} successful, ${failed} failed`)

    return { successful, failed, errors }
  }

  async getTransactionRules(): Promise<TransactionRule[]> {
    const query = `
      query GetTransactionRules {
        transactionRules {
          id
          name
          isEnabled
          priority
          conditions {
            field
            operator
            value
          }
          actions {
            type
            value
          }
          createdAt
          updatedAt
        }
      }
    `

    const data = await this.graphql.query<{
      transactionRules: TransactionRule[]
    }>(query)

    return data.transactionRules
  }

  async createTransactionRule(data: CreateTransactionRuleInput): Promise<TransactionRule> {
    const { name, conditions, actions, priority } = data

    const mutation = `
      mutation CreateTransactionRule(
        $name: String!
        $conditions: [RuleConditionInput!]!
        $actions: [RuleActionInput!]!
        $priority: Int
      ) {
        createTransactionRule(
          name: $name
          conditions: $conditions
          actions: $actions
          priority: $priority
        ) {
          transactionRule {
            id
            name
            isEnabled
            priority
            conditions {
              field
              operator
              value
            }
            actions {
              type
              value
            }
            createdAt
          }
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      createTransactionRule: {
        transactionRule: TransactionRule
        errors: any[]
      }
    }>(mutation, { name, conditions, actions, priority })

    if (result.createTransactionRule.errors?.length > 0) {
      throw new Error(`Transaction rule creation failed: ${result.createTransactionRule.errors[0].messages.join(', ')}`)
    }

    logger.info('Transaction rule created successfully:', result.createTransactionRule.transactionRule.id)
    return result.createTransactionRule.transactionRule
  }

  async updateTransactionRule(ruleId: string, data: UpdateTransactionRuleInput): Promise<TransactionRule> {
    const mutation = `
      mutation UpdateTransactionRule(
        $ruleId: String!
        $name: String
        $conditions: [RuleConditionInput!]
        $actions: [RuleActionInput!]
        $priority: Int
        $isEnabled: Boolean
      ) {
        updateTransactionRule(
          ruleId: $ruleId
          name: $name
          conditions: $conditions
          actions: $actions
          priority: $priority
          isEnabled: $isEnabled
        ) {
          transactionRule {
            id
            name
            isEnabled
            priority
            conditions {
              field
              operator
              value
            }
            actions {
              type
              value
            }
            updatedAt
          }
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      updateTransactionRule: {
        transactionRule: TransactionRule
        errors: any[]
      }
    }>(mutation, { ruleId, ...data })

    if (result.updateTransactionRule.errors?.length > 0) {
      throw new Error(`Transaction rule update failed: ${result.updateTransactionRule.errors[0].messages.join(', ')}`)
    }

    logger.info('Transaction rule updated successfully:', ruleId)
    return result.updateTransactionRule.transactionRule
  }

  async deleteTransactionRule(ruleId: string): Promise<boolean> {
    const mutation = `
      mutation DeleteTransactionRule($ruleId: String!) {
        deleteTransactionRule(ruleId: $ruleId) {
          deleted
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      deleteTransactionRule: {
        deleted: boolean
        errors: any[]
      }
    }>(mutation, { ruleId })

    if (result.deleteTransactionRule.errors?.length > 0) {
      throw new Error(`Transaction rule deletion failed: ${result.deleteTransactionRule.errors[0].messages.join(', ')}`)
    }

    logger.info('Transaction rule deleted successfully:', ruleId)
    return result.deleteTransactionRule.deleted
  }

  async deleteAllTransactionRules(): Promise<boolean> {
    const mutation = `
      mutation DeleteAllTransactionRules {
        deleteAllTransactionRules {
          deletedCount
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      deleteAllTransactionRules: {
        deletedCount: number
        errors: any[]
      }
    }>(mutation)

    if (result.deleteAllTransactionRules.errors?.length > 0) {
      throw new Error(`Delete all transaction rules failed: ${result.deleteAllTransactionRules.errors[0].messages.join(', ')}`)
    }

    logger.info('All transaction rules deleted successfully:', result.deleteAllTransactionRules.deletedCount)
    return result.deleteAllTransactionRules.deletedCount > 0
  }

  async previewTransactionRule(conditions: RuleCondition[], actions: RuleAction[]): Promise<any> {
    const mutation = `
      mutation PreviewTransactionRule(
        $conditions: [RuleConditionInput!]!
        $actions: [RuleActionInput!]!
      ) {
        previewTransactionRule(conditions: $conditions, actions: $actions) {
          affectedTransactions {
            id
            merchant {
              name
            }
            amount
            date
            category {
              id
              name
            }
          }
          previewChanges {
            field
            currentValue
            newValue
          }
        }
      }
    `

    const data = await this.graphql.mutation<{
      previewTransactionRule: any
    }>(mutation, { conditions, actions })

    return data.previewTransactionRule
  }

  async getTransactionCategories(): Promise<TransactionCategory[]> {
    const query = `
      query GetCategories {
        categories {
          id
          name
          icon
          color
          group {
            id
            name
            type
          }
          systemCategory
          isHidden
        }
      }
    `

    const data = await this.graphql.query<{
      categories: TransactionCategory[]
    }>(query)

    return data.categories
  }

  async createTransactionCategory(data: CreateTransactionCategoryInput): Promise<TransactionCategory> {
    const { name, groupId, icon, color } = data

    const mutation = `
      mutation CreateCategory(
        $name: String!
        $groupId: String!
        $icon: String
        $color: String
      ) {
        createCategory(
          name: $name
          groupId: $groupId
          icon: $icon
          color: $color
        ) {
          category {
            id
            name
            icon
            color
            group {
              id
              name
              type
            }
          }
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      createCategory: {
        category: TransactionCategory
        errors: any[]
      }
    }>(mutation, { name, groupId, icon, color })

    if (result.createCategory.errors?.length > 0) {
      throw new Error(`Category creation failed: ${result.createCategory.errors[0].messages.join(', ')}`)
    }

    logger.info('Category created successfully:', result.createCategory.category.id)
    return result.createCategory.category
  }

  async updateTransactionCategory(categoryId: string, data: UpdateTransactionCategoryInput): Promise<TransactionCategory> {
    const mutation = `
      mutation UpdateCategory(
        $categoryId: String!
        $name: String
        $icon: String
        $color: String
      ) {
        updateCategory(
          categoryId: $categoryId
          name: $name
          icon: $icon
          color: $color
        ) {
          category {
            id
            name
            icon
            color
            group {
              id
              name
              type
            }
          }
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      updateCategory: {
        category: TransactionCategory
        errors: any[]
      }
    }>(mutation, { categoryId, ...data })

    if (result.updateCategory.errors?.length > 0) {
      throw new Error(`Category update failed: ${result.updateCategory.errors[0].messages.join(', ')}`)
    }

    logger.info('Category updated successfully:', categoryId)
    return result.updateCategory.category
  }

  async deleteTransactionCategory(categoryId: string): Promise<boolean> {
    const mutation = `
      mutation DeleteCategory($categoryId: String!) {
        deleteCategory(categoryId: $categoryId) {
          deleted
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      deleteCategory: {
        deleted: boolean
        errors: any[]
      }
    }>(mutation, { categoryId })

    if (result.deleteCategory.errors?.length > 0) {
      throw new Error(`Category deletion failed: ${result.deleteCategory.errors[0].messages.join(', ')}`)
    }

    logger.info('Category deleted successfully:', categoryId)
    return result.deleteCategory.deleted
  }

  async getTransactionCategoryGroups(): Promise<CategoryGroup[]> {
    const query = `
      query GetCategoryGroups {
        categoryGroups {
          id
          name
          type
          categories {
            id
            name
            icon
            color
          }
        }
      }
    `

    const data = await this.graphql.query<{
      categoryGroups: CategoryGroup[]
    }>(query)

    return data.categoryGroups
  }

  async getCategoryDetails(categoryId: string): Promise<any> {
    const query = `
      query GetCategoryDetails($categoryId: String!) {
        getCategoryDetails(categoryId: $categoryId) {
          id
          name
          icon
          color
          group {
            id
            name
            type
          }
          transactionCount
          totalAmount
          averageAmount
          monthlyBreakdown {
            month
            amount
            count
          }
          recentTransactions {
            id
            merchant {
              name
            }
            amount
            date
          }
        }
      }
    `

    const data = await this.graphql.query<{
      getCategoryDetails: any
    }>(query, { categoryId })

    return data.getCategoryDetails
  }

  async getTransactionTags(): Promise<TransactionTag[]> {
    const query = `
      query GetTransactionTags {
        transactionTags {
          id
          name
          color
          transactionCount
        }
      }
    `

    const data = await this.graphql.query<{
      transactionTags: TransactionTag[]
    }>(query)

    return data.transactionTags
  }

  async createTransactionTag(data: CreateTransactionTagInput): Promise<TransactionTag> {
    const { name, color } = data

    const mutation = `
      mutation CreateTransactionTag($name: String!, $color: String!) {
        createTransactionTag(name: $name, color: $color) {
          tag {
            id
            name
            color
            transactionCount
          }
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      createTransactionTag: {
        tag: TransactionTag
        errors: any[]
      }
    }>(mutation, { name, color })

    if (result.createTransactionTag.errors?.length > 0) {
      throw new Error(`Tag creation failed: ${result.createTransactionTag.errors[0].messages.join(', ')}`)
    }

    logger.info('Transaction tag created successfully:', result.createTransactionTag.tag.id)
    return result.createTransactionTag.tag
  }

  async setTransactionTags(transactionId: string, tagIds: string[]): Promise<Transaction> {
    validateTransactionId(transactionId)

    const mutation = `
      mutation SetTransactionTags($transactionId: String!, $tagIds: [String!]!) {
        setTransactionTags(transactionId: $transactionId, tagIds: $tagIds) {
          transaction {
            id
            tags {
              id
              name
              color
            }
          }
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      setTransactionTags: {
        transaction: Transaction
        errors: any[]
      }
    }>(mutation, { transactionId, tagIds })

    if (result.setTransactionTags.errors?.length > 0) {
      throw new Error(`Set transaction tags failed: ${result.setTransactionTags.errors[0].messages.join(', ')}`)
    }

    logger.info('Transaction tags updated successfully:', transactionId)
    return result.setTransactionTags.transaction
  }

  async getMerchants(options: GetMerchantsOptions = {}): Promise<Merchant[]> {
    const { search, limit = 100 } = options

    const query = `
      query GetMerchants($search: String, $limit: Int) {
        merchants(search: $search, limit: $limit) {
          id
          name
          transactionCount
          totalAmount
          logoUrl
        }
      }
    `

    const data = await this.graphql.query<{
      merchants: Merchant[]
    }>(query, { search, limit })

    return data.merchants
  }

  async getMerchantDetails(merchantId: string): Promise<any> {
    const query = `
      query GetMerchantDetails($merchantId: String!) {
        getMerchantDetails(merchantId: $merchantId) {
          id
          name
          transactionCount
          totalAmount
          logoUrl
          categoryBreakdown {
            categoryId
            categoryName
            amount
            count
          }
          recentTransactions {
            id
            amount
            date
            account {
              displayName
            }
          }
        }
      }
    `

    const data = await this.graphql.query<{
      getMerchantDetails: any
    }>(query, { merchantId })

    return data.getMerchantDetails
  }

  async getEditMerchant(merchantId: string): Promise<any> {
    const query = `
      query GetEditMerchant($merchantId: String!) {
        getEditMerchant(merchantId: $merchantId) {
          id
          name
          logoUrl
          suggestedCategories {
            id
            name
            confidence
          }
          recurringTransactionSettings {
            isRecurring
            frequency
            nextDate
          }
        }
      }
    `

    const data = await this.graphql.query<{
      getEditMerchant: any
    }>(query, { merchantId })

    return data.getEditMerchant
  }

  async getRecurringTransactions(options: GetRecurringTransactionsOptions = {}): Promise<RecurringTransaction[]> {
    const { startDate, endDate } = options

    const query = `
      query GetRecurringTransactions($startDate: String, $endDate: String) {
        recurringTransactions(startDate: $startDate, endDate: $endDate) {
          id
          merchant {
            name
          }
          amount
          frequency
          nextDate
          category {
            id
            name
          }
          account {
            id
            displayName
          }
          isActive
          reviewStatus
        }
      }
    `

    const data = await this.graphql.query<{
      recurringTransactions: RecurringTransaction[]
    }>(query, { startDate, endDate })

    return data.recurringTransactions
  }

  async getRecurringStreams(options: GetRecurringStreamsOptions = {}): Promise<any[]> {
    const {
      includeLiabilities = true,
      includePending = true,
      filters
    } = options

    const query = `
      query GetRecurringStreams(
        $includeLiabilities: Boolean
        $includePending: Boolean
        $filters: JSON
      ) {
        recurringStreams(
          includeLiabilities: $includeLiabilities
          includePending: $includePending
          filters: $filters
        ) {
          id
          merchant {
            name
          }
          amount
          frequency
          nextOccurrence
          reviewStatus
          confidence
          transactionCount
        }
      }
    `

    const data = await this.graphql.query<{
      recurringStreams: any[]
    }>(query, { includeLiabilities, includePending, filters })

    return data.recurringStreams
  }

  async getAggregatedRecurringItems(options: GetAggregatedRecurringItemsOptions): Promise<any> {
    const { startDate, endDate, groupBy = 'status', filters } = options

    const query = `
      query GetAggregatedRecurringItems(
        $startDate: String!
        $endDate: String!
        $groupBy: String
        $filters: JSON
      ) {
        aggregatedRecurringItems(
          startDate: $startDate
          endDate: $endDate
          groupBy: $groupBy
          filters: $filters
        ) {
          totalAmount
          totalCount
          groupedData {
            groupKey
            amount
            count
            items {
              id
              merchant {
                name
              }
              amount
              date
            }
          }
        }
      }
    `

    const data = await this.graphql.query<{
      aggregatedRecurringItems: any
    }>(query, { startDate, endDate, groupBy, filters })

    return data.aggregatedRecurringItems
  }

  async getAllRecurringTransactionItems(options: GetAllRecurringTransactionItemsOptions = {}): Promise<any[]> {
    const { filters, includeLiabilities = true } = options

    const query = `
      query GetAllRecurringTransactionItems(
        $filters: JSON
        $includeLiabilities: Boolean
      ) {
        allRecurringTransactionItems(
          filters: $filters
          includeLiabilities: $includeLiabilities
        ) {
          id
          merchant {
            name
          }
          amount
          predictedDate
          category {
            id
            name
          }
          account {
            id
            displayName
          }
          confidence
          status
        }
      }
    `

    const data = await this.graphql.query<{
      allRecurringTransactionItems: any[]
    }>(query, { filters, includeLiabilities })

    return data.allRecurringTransactionItems
  }

  async reviewRecurringStream(streamId: string, reviewStatus: string): Promise<any> {
    const mutation = `
      mutation ReviewStream($streamId: String!, $reviewStatus: String!) {
        reviewStream(streamId: $streamId, reviewStatus: $reviewStatus) {
          stream {
            id
            reviewStatus
            updatedAt
          }
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      reviewStream: {
        stream: any
        errors: any[]
      }
    }>(mutation, { streamId, reviewStatus })

    if (result.reviewStream.errors?.length > 0) {
      throw new Error(`Stream review failed: ${result.reviewStream.errors[0].messages.join(', ')}`)
    }

    logger.info('Recurring stream reviewed successfully:', streamId)
    return result.reviewStream.stream
  }

  async markStreamAsNotRecurring(streamId: string): Promise<boolean> {
    const mutation = `
      mutation MarkAsNotRecurring($streamId: String!) {
        markAsNotRecurring(streamId: $streamId) {
          success
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      markAsNotRecurring: {
        success: boolean
        errors: any[]
      }
    }>(mutation, { streamId })

    if (result.markAsNotRecurring.errors?.length > 0) {
      throw new Error(`Mark as not recurring failed: ${result.markAsNotRecurring.errors[0].messages.join(', ')}`)
    }

    logger.info('Stream marked as not recurring successfully:', streamId)
    return result.markAsNotRecurring.success
  }

  async getRecurringMerchantSearchStatus(): Promise<any> {
    const query = `
      query RecurringMerchantSearch {
        recurringMerchantSearchStatus {
          isRunning
          lastRunAt
          completedCount
          totalCount
          estimatedTimeRemaining
        }
      }
    `

    const data = await this.graphql.query<{
      recurringMerchantSearchStatus: any
    }>(query)

    return data.recurringMerchantSearchStatus
  }

  async bulkUpdateTransactions(data: BulkUpdateTransactionsInput): Promise<BulkUpdateResult> {
    const {
      transactionIds,
      updates,
      excludedTransactionIds,
      allSelected = false,
      filters
    } = data

    const mutation = `
      mutation BulkUpdateTransactions(
        $transactionIds: [String!]!
        $updates: JSON!
        $excludedTransactionIds: [String!]
        $allSelected: Boolean
        $filters: JSON
      ) {
        bulkUpdateTransactions(
          transactionIds: $transactionIds
          updates: $updates
          excludedTransactionIds: $excludedTransactionIds
          allSelected: $allSelected
          filters: $filters
        ) {
          affectedCount
          successful
          errors {
            field
            messages
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      bulkUpdateTransactions: BulkUpdateResult
    }>(mutation, { transactionIds, updates, excludedTransactionIds, allSelected, filters })

    if (result.bulkUpdateTransactions.errors && result.bulkUpdateTransactions.errors.length > 0) {
      throw new Error(`Bulk update failed: ${result.bulkUpdateTransactions.errors[0].messages.join(', ')}`)
    }

    logger.info('Bulk transaction update completed:', result.bulkUpdateTransactions.affectedCount)
    return result.bulkUpdateTransactions
  }

  async bulkHideTransactions(transactionIds: string[], filters?: any): Promise<BulkUpdateResult> {
    return this.bulkUpdateTransactions({
      transactionIds,
      updates: { hide: true },
      filters
    })
  }

  async bulkUnhideTransactions(transactionIds: string[], filters?: any): Promise<BulkUpdateResult> {
    return this.bulkUpdateTransactions({
      transactionIds,
      updates: { hide: false },
      filters
    })
  }

  async getHiddenTransactions(options: GetHiddenTransactionsOptions = {}): Promise<PaginatedTransactions> {
    const { limit = 100, offset = 0, orderBy = 'date' } = options

    const query = `
      query GetHiddenTransactions($limit: Int, $offset: Int, $orderBy: String) {
        hiddenTransactions(limit: $limit, offset: $offset, orderBy: $orderBy) {
          totalCount
          results {
            id
            amount
            date
            merchant {
              name
            }
            category {
              id
              name
            }
            account {
              id
              displayName
            }
            isHide
          }
        }
      }
    `

    const data = await this.graphql.query<{
      hiddenTransactions: {
        totalCount: number
        results: Transaction[]
      }
    }>(query, { limit, offset, orderBy })

    return {
      transactions: data.hiddenTransactions.results,
      totalCount: data.hiddenTransactions.totalCount,
      hasMore: offset + limit < data.hiddenTransactions.totalCount,
      limit,
      offset
    }
  }
}