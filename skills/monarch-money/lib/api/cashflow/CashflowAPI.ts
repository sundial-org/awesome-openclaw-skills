import { GraphQLClient } from '../../client/graphql'

export interface CashflowSummary {
  sumIncome: number
  sumExpense: number
  savings: number
  savingsRate: number
}

export interface CategoryAggregate {
  groupBy: {
    category: {
      id: string
      name: string
      group: {
        id: string
        type: string
      }
    }
  }
  summary: {
    sum: number
  }
}

export interface CategoryGroupAggregate {
  groupBy: {
    categoryGroup: {
      id: string
      name: string
      type: string
    }
  }
  summary: {
    sum: number
  }
}

export interface CashflowData {
  byCategory: CategoryAggregate[]
  byCategoryGroup: CategoryGroupAggregate[]
  summary?: {
    summary: CashflowSummary
  }
}

export interface TransactionFilter {
  search?: string
  categories?: string[]
  accounts?: string[]
  tags?: string[]
  startDate?: string
  endDate?: string
  minAmount?: number
  maxAmount?: number
}

export interface CashflowAPI {
  /**
   * Get cashflow analysis with category and category group breakdowns
   */
  getCashflow(options?: {
    startDate?: string
    endDate?: string
    filters?: TransactionFilter
  }): Promise<CashflowData>

  /**
   * Get cashflow summary with income, expenses, savings
   */
  getCashflowSummary(options?: {
    startDate?: string
    endDate?: string
    filters?: TransactionFilter
  }): Promise<CashflowSummary>
}

export class CashflowAPIImpl implements CashflowAPI {
  constructor(private graphql: GraphQLClient) {}

  private getCurrentMonthDates(): { startDate: string; endDate: string } {
    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth() + 1
    const startDate = `${year}-${String(month).padStart(2, '0')}-01`
    const lastDay = new Date(year, month, 0).getDate()
    const endDate = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
    return { startDate, endDate }
  }

  async getCashflow(options?: {
    startDate?: string
    endDate?: string
    filters?: TransactionFilter
  }): Promise<CashflowData> {
    const { startDate, endDate } = options?.startDate && options?.endDate 
      ? { startDate: options.startDate, endDate: options.endDate }
      : this.getCurrentMonthDates()

    const filters = {
      search: "",
      categories: [],
      accounts: [],
      tags: [],
      startDate,
      endDate,
      ...options?.filters
    }

    const query = `
      query Web_GetCashFlowPage($filters: TransactionFilterInput) {
        byCategory: aggregates(filters: $filters, groupBy: ["category"]) {
          groupBy {
            category {
              id
              name
              group {
                id
                type
                __typename
              }
              __typename
            }
            __typename
          }
          summary {
            sum
            __typename
          }
          __typename
        }
        byCategoryGroup: aggregates(filters: $filters, groupBy: ["categoryGroup"]) {
          groupBy {
            categoryGroup {
              id
              name
              type
              __typename
            }
            __typename
          }
          summary {
            sum
            __typename
          }
          __typename
        }
        byAccount: aggregates(filters: $filters, groupBy: ["account"]) {
          groupBy {
            account {
              id
              displayName
              __typename
            }
            __typename
          }
          summary {
            sum
            __typename
          }
          __typename
        }
        byMerchant: aggregates(filters: $filters, groupBy: ["merchant"], limit: 50) {
          groupBy {
            merchant {
              id
              name
              __typename
            }
            __typename
          }
          summary {
            sum
            __typename
          }
          __typename
        }
        byMonth: aggregates(filters: $filters, groupBy: ["month"]) {
          groupBy {
            month {
              date
              __typename
            }
            __typename
          }
          summary {
            sum
            count
            __typename
          }
          __typename
        }
      }
    `

    return await this.graphql.query<CashflowData>(query, { filters })
  }

  async getCashflowSummary(options?: {
    startDate?: string
    endDate?: string
    filters?: TransactionFilter
  }): Promise<CashflowSummary> {
    const { startDate, endDate } = options?.startDate && options?.endDate 
      ? { startDate: options.startDate, endDate: options.endDate }
      : this.getCurrentMonthDates()

    const filters = {
      search: "",
      categories: [],
      accounts: [],
      tags: [],
      startDate,
      endDate,
      ...options?.filters
    }

    const query = `
      query Web_GetCashFlowPage($filters: TransactionFilterInput) {
        summary: aggregates(filters: $filters, fillEmptyValues: true) {
          summary {
            sumIncome
            sumExpense
            savings
            savingsRate
            __typename
          }
          __typename
        }
      }
    `

    const result = await this.graphql.query<{
      summary: Array<{
        summary: CashflowSummary
      }>
    }>(query, { filters })

    // FIXED: Handle array response structure from actual API
    return result.summary[0].summary
  }
}