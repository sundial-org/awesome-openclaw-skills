import { GraphQLClient } from '../../client/graphql'
import {
  Account,
  AccountBalance,
  CreateAccountInput,
  UpdateAccountInput
} from '../../types'
import {
  GET_ACCOUNT_DETAILS,
  GET_ACCOUNT_TYPE_OPTIONS,
  GET_NET_WORTH_HISTORY
} from '../../client/graphql/operations'
import { getQueryForVerbosity, VerbosityLevel } from '../../client/graphql/operations'
import {
  validateAccountId,
  // validateDate,
  validateDateRange,
  logger
} from '../../utils'

export interface AccountsAPI {
  getAll(options?: { includeHidden?: boolean; verbosity?: VerbosityLevel }): Promise<Account[]>
  getById(id: string): Promise<Account>
  getBalances(startDate?: string, endDate?: string): Promise<AccountBalance[]>
  getTypeOptions(): Promise<{ types: Array<{ id: number; name: string; display: string }>, subtypes: Array<{ id: number; name: string; display: string; typeId: number }> }>
  getHistory(accountId: string, startDate?: string, endDate?: string): Promise<AccountBalance[]>
  getNetWorthHistory(startDate?: string, endDate?: string): Promise<Array<{ date: string; netWorth: number; assets: number; liabilities: number }>>
  createManualAccount(input: CreateAccountInput): Promise<Account>
  updateAccount(id: string, updates: UpdateAccountInput): Promise<Account>
  deleteAccount(id: string): Promise<boolean>
  requestRefresh(accountIds?: string[]): Promise<boolean>
  isRefreshComplete(refreshId?: string): Promise<boolean>
}

export class AccountsAPIImpl implements AccountsAPI {
  constructor(private graphql: GraphQLClient) {}

  async getAll(options: { includeHidden?: boolean; verbosity?: VerbosityLevel } = {}): Promise<Account[]> {
    const { includeHidden = false, verbosity = 'standard' } = options;
    logger.debug('Fetching all accounts', options)

    try {
      // Select appropriate query based on verbosity
      const query = getQueryForVerbosity('accounts', verbosity);

      const response = await this.graphql.query<{
        accounts: Account[]
      }>(query, {}, { cache: true, cacheTTL: 300000 }) // 5 minutes

      let accounts = response.accounts;

      // Filter out hidden accounts if requested
      if (!includeHidden) {
        accounts = accounts.filter((account: Account) => !account.isHidden);
      }

      return accounts;
    } catch (error) {
      logger.error('Failed to fetch accounts', error)
      throw error
    }
  }

  async getById(id: string): Promise<Account> {
    validateAccountId(id)
    logger.debug(`Fetching account: ${id}`)

    try {
      const response = await this.graphql.query<{
        account: Account
      }>(GET_ACCOUNT_DETAILS, { id }, { cache: true, cacheTTL: 300000 })

      return response.account
    } catch (error) {
      logger.error(`Failed to fetch account ${id}`, error)
      throw error
    }
  }

  async getBalances(startDate?: string, endDate?: string): Promise<AccountBalance[]> {
    validateDateRange(startDate, endDate)
    logger.debug('Fetching account balances', { startDate, endDate })

    try {
      const accounts = await this.getAll({ includeHidden: true, verbosity: 'standard' }) as Account[]

      // For now, return current balances
      // TODO: Implement actual balance history query
      return accounts.map((account: Account) => ({
        accountId: account.id,
        date: new Date().toISOString().split('T')[0],
        balance: account.currentBalance
      }))
    } catch (error) {
      logger.error('Failed to fetch account balances', error)
      throw error
    }
  }

  async getTypeOptions(): Promise<{
    types: Array<{ id: number; name: string; display: string }>
    subtypes: Array<{ id: number; name: string; display: string; typeId: number }>
  }> {
    logger.debug('Fetching account type options')

    try {
      const response = await this.graphql.query<{
        accountTypeOptions: {
          types: Array<{ id: number; name: string; display: string }>
          subtypes: Array<{ id: number; name: string; display: string; typeId: number }>
        }
      }>(GET_ACCOUNT_TYPE_OPTIONS, {}, { cache: true, cacheTTL: 1800000 }) // 30 minutes

      return response.accountTypeOptions
    } catch (error) {
      logger.error('Failed to fetch account type options', error)
      throw error
    }
  }

  async getHistory(accountId: string, startDate?: string, endDate?: string): Promise<AccountBalance[]> {
    validateAccountId(accountId)
    validateDateRange(startDate, endDate)
    logger.debug(`Fetching account history: ${accountId}`, { startDate, endDate })

    try {
      // Use the recent balances query pattern from HAR
      const ACCOUNT_RECENT_BALANCES = `
        query Web_GetAccountsPageRecentBalance($startDate: Date) {
          accounts {
            id
            recentBalances(startDate: $startDate)
            __typename
          }
        }
      `

      const response = await this.graphql.query<{
        accounts: Array<{
          id: string
          recentBalances: number[]
        }>
      }>(ACCOUNT_RECENT_BALANCES, { startDate }, { cache: true, cacheTTL: 300000 })

      // Find the specific account and format the response
      const accountData = response.accounts.find(acc => acc.id === accountId)
      if (!accountData) {
        throw new Error(`Account ${accountId} not found`)
      }

      // For now, return current balance as a single point since recentBalances format isn't clear
      // TODO: Parse recentBalances array properly when we understand the format
      const account = await this.getById(accountId)

      return [{
        accountId: account.id,
        date: new Date().toISOString().split('T')[0],
        balance: account.currentBalance
      }]
    } catch (error) {
      logger.error(`Failed to fetch account history for ${accountId}`, error)
      throw error
    }
  }

  async getNetWorthHistory(startDate?: string, endDate?: string): Promise<Array<{
    date: string
    netWorth: number
    assets: number
    liabilities: number
  }>> {
    validateDateRange(startDate, endDate)
    logger.debug('Fetching net worth history', { startDate, endDate })

    try {
      // Build filters object according to HAR pattern
      const filters: Record<string, any> = {}
      if (startDate !== undefined) filters.startDate = startDate
      if (endDate !== undefined) filters.endDate = endDate
      filters.useAdaptiveGranularity = true

      const response = await this.graphql.query<{
        aggregateSnapshots: Array<{
          date: string
          balance: number
          assetsBalance: number
          liabilitiesBalance: number
        }>
      }>(GET_NET_WORTH_HISTORY, { filters }, { cache: true, cacheTTL: 600000 }) // 10 minutes

      // Map the response to the expected format
      return response.aggregateSnapshots.map(item => ({
        date: item.date,
        netWorth: item.balance,
        assets: item.assetsBalance,
        liabilities: item.liabilitiesBalance
      }))
    } catch (error) {
      logger.error('Failed to fetch net worth history', error)
      throw error
    }
  }

  async createManualAccount(input: CreateAccountInput): Promise<Account> {
    logger.debug('Creating manual account', input)

    try {
      const CREATE_MANUAL_ACCOUNT = `
        mutation CreateManualAccount(
          $name: String!,
          $typeName: String!,
          $subtypeName: String!,
          $balance: Float!,
          $includeInNetWorth: Boolean,
          $isAsset: Boolean
        ) {
          createManualAccount(
            name: $name,
            typeName: $typeName,
            subtypeName: $subtypeName,
            balance: $balance,
            includeInNetWorth: $includeInNetWorth,
            isAsset: $isAsset
          ) {
            account {
              id
              displayName
              currentBalance
              includeInNetWorth
              isAsset
              type {
                id
                name
                display
              }
              subtype {
                id
                name
                display
              }
            }
            errors {
              message
              field
            }
          }
        }
      `

      const response = await this.graphql.mutation<{
        createManualAccount: {
          account: Account
          errors?: Array<{ message: string; field?: string }>
        }
      }>(CREATE_MANUAL_ACCOUNT, {
        name: input.name,
        typeName: input.typeName,
        subtypeName: input.subtypeName,
        balance: input.balance,
        includeInNetWorth: input.includeInNetWorth ?? true,
        isAsset: input.isAsset ?? true
      })

      if (response.createManualAccount.errors && response.createManualAccount.errors.length > 0) {
        const error = response.createManualAccount.errors[0]
        throw new Error(`Failed to create account: ${error.message}`)
      }

      return response.createManualAccount.account
    } catch (error) {
      logger.error('Failed to create manual account', error)
      throw error
    }
  }

  async updateAccount(id: string, updates: UpdateAccountInput): Promise<Account> {
    validateAccountId(id)
    logger.debug(`Updating account: ${id}`, updates)

    try {
      const UPDATE_ACCOUNT = `
        mutation UpdateAccount(
          $id: ID!,
          $displayName: String,
          $isHidden: Boolean,
          $includeInNetWorth: Boolean,
          $currentBalance: Float
        ) {
          updateAccount(
            id: $id,
            displayName: $displayName,
            isHidden: $isHidden,
            includeInNetWorth: $includeInNetWorth,
            currentBalance: $currentBalance
          ) {
            account {
              id
              displayName
              currentBalance
              includeInNetWorth
              isHidden
              updatedAt
            }
            errors {
              message
              field
            }
          }
        }
      `

      const response = await this.graphql.mutation<{
        updateAccount: {
          account: Account
          errors?: Array<{ message: string; field?: string }>
        }
      }>(UPDATE_ACCOUNT, {
        id,
        displayName: updates.displayName,
        isHidden: updates.isHidden,
        includeInNetWorth: updates.includeInNetWorth,
        currentBalance: updates.currentBalance
      })

      if (response.updateAccount.errors && response.updateAccount.errors.length > 0) {
        const error = response.updateAccount.errors[0]
        throw new Error(`Failed to update account: ${error.message}`)
      }

      return response.updateAccount.account
    } catch (error) {
      logger.error(`Failed to update account ${id}`, error)
      throw error
    }
  }

  async deleteAccount(id: string): Promise<boolean> {
    validateAccountId(id)
    logger.debug(`Deleting account: ${id}`)

    try {
      const DELETE_ACCOUNT = `
        mutation DeleteAccount($id: ID!) {
          deleteAccount(id: $id) {
            success
            errors {
              message
            }
          }
        }
      `

      const response = await this.graphql.mutation<{
        deleteAccount: {
          success: boolean
          errors?: Array<{ message: string }>
        }
      }>(DELETE_ACCOUNT, { id })

      if (response.deleteAccount.errors && response.deleteAccount.errors.length > 0) {
        const error = response.deleteAccount.errors[0]
        throw new Error(`Failed to delete account: ${error.message}`)
      }

      return response.deleteAccount.success
    } catch (error) {
      logger.error(`Failed to delete account ${id}`, error)
      throw error
    }
  }

  async requestRefresh(accountIds?: string[]): Promise<boolean> {
    logger.debug('Requesting account refresh', { accountIds })

    try {
      const REQUEST_REFRESH = `
        mutation RequestAccountsRefresh($accountIds: [ID!]) {
          requestAccountsRefresh(accountIds: $accountIds) {
            success
            refreshId
            errors {
              message
            }
          }
        }
      `

      const response = await this.graphql.mutation<{
        requestAccountsRefresh: {
          success: boolean
          refreshId?: string
          errors?: Array<{ message: string }>
        }
      }>(REQUEST_REFRESH, { accountIds })

      if (response.requestAccountsRefresh.errors && response.requestAccountsRefresh.errors.length > 0) {
        const error = response.requestAccountsRefresh.errors[0]
        throw new Error(`Failed to request refresh: ${error.message}`)
      }

      return response.requestAccountsRefresh.success
    } catch (error) {
      logger.error('Failed to request account refresh', error)
      throw error
    }
  }

  async isRefreshComplete(refreshId?: string): Promise<boolean> {
    logger.debug('Checking refresh status', { refreshId })

    try {
      const CHECK_REFRESH = `
        query CheckAccountsRefresh($refreshId: String) {
          accountsRefreshStatus(refreshId: $refreshId) {
            isComplete
            progress
            errors {
              message
            }
          }
        }
      `

      const response = await this.graphql.query<{
        accountsRefreshStatus: {
          isComplete: boolean
          progress?: number
          errors?: Array<{ message: string }>
        }
      }>(CHECK_REFRESH, { refreshId }, { cache: false })

      return response.accountsRefreshStatus.isComplete
    } catch (error) {
      logger.error('Failed to check refresh status', error)
      return false
    }
  }
}