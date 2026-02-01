import { GraphQLClient } from '../../client/graphql'

export interface RecurringTransactionStream {
  id: string
  reviewStatus: string
  frequency: string
  amount: number
  baseDate?: string
  dayOfTheMonth?: number
  isApproximate: boolean
  name: string
  logoUrl?: string
  recurringType: string
  isActive: boolean
  merchant: {
    id: string
    name: string
    logoUrl?: string
  }
  creditReportLiabilityAccount?: {
    id: string
    account: {
      id: string
      displayName: string
    }
  }
  category: {
    id: string
    name: string
  }
  account: {
    id: string
    displayName: string
  }
}

export interface RecurringTransactionItem {
  stream: RecurringTransactionStream
  date: string
  isPast: boolean
  transactionId?: string
  amount: number
  amountDiff?: number
  category: {
    id: string
    name: string
  }
  account: {
    id: string
    displayName: string
  }
}

export interface RecurringTransactionFilter {
  accounts?: string[]
  categories?: string[]
  merchants?: string[]
}

export interface RecurringAPI {
  /**
   * Get all recurring transaction streams
   */
  getRecurringStreams(options?: {
    includeLiabilities?: boolean
    includePending?: boolean
    filters?: RecurringTransactionFilter
  }): Promise<{ stream: RecurringTransactionStream }[]>

  /**
   * Get upcoming recurring transaction items for a date range
   */
  getUpcomingRecurringItems(options: {
    startDate: string
    endDate: string
    filters?: RecurringTransactionFilter
  }): Promise<RecurringTransactionItem[]>

  /**
   * Mark a recurring stream as not recurring (disable it)
   */
  markStreamAsNotRecurring(streamId: string): Promise<boolean>
}

export class RecurringAPIImpl implements RecurringAPI {
  constructor(private graphql: GraphQLClient) {}

  async getRecurringStreams(options?: {
    includeLiabilities?: boolean
    includePending?: boolean
    filters?: RecurringTransactionFilter
  }): Promise<{ stream: RecurringTransactionStream }[]> {
    const variables = {
      includeLiabilities: options?.includeLiabilities ?? true
    }

    // FIXED: Use exact working query from MonarchMoney web app
    const query = `
      query Common_GetRecurringStreams($includeLiabilities: Boolean) {
        recurringTransactionStreams(
          includePending: true
          includeLiabilities: $includeLiabilities
        ) {
          stream {
            id
            reviewStatus
            frequency
            amount
            baseDate
            dayOfTheMonth
            isApproximate
            name
            logoUrl
            recurringType
            merchant {
              id
              __typename
            }
            creditReportLiabilityAccount {
              id
              account {
                id
                __typename
              }
              lastStatement {
                id
                dueDate
                __typename
              }
              __typename
            }
            __typename
          }
          __typename
        }
      }
    `

    const result = await this.graphql.query<{
      recurringTransactionStreams: { stream: RecurringTransactionStream }[]
    }>(query, variables)

    return result.recurringTransactionStreams
  }

  async getUpcomingRecurringItems(options: {
    startDate: string
    endDate: string
    filters?: RecurringTransactionFilter
  }): Promise<RecurringTransactionItem[]> {
    const variables = {
      startDate: options.startDate,
      endDate: options.endDate,
      filters: options.filters || {}
    }

    const query = `
      query Web_GetUpcomingRecurringTransactionItems(
        $startDate: Date!, 
        $endDate: Date!, 
        $filters: RecurringTransactionFilter
      ) {
        recurringTransactionItems(
          startDate: $startDate
          endDate: $endDate
          filters: $filters
        ) {
          stream {
            id
            frequency
            amount
            isApproximate
            merchant {
              id
              name
              logoUrl
              __typename
            }
            __typename
          }
          date
          isPast
          transactionId
          amount
          amountDiff
          category {
            id
            name
            __typename
          }
          account {
            id
            displayName
            __typename
          }
          __typename
        }
      }
    `

    const result = await this.graphql.query<{
      recurringTransactionItems: RecurringTransactionItem[]
    }>(query, variables)

    return result.recurringTransactionItems
  }

  async markStreamAsNotRecurring(streamId: string): Promise<boolean> {
    const variables = { streamId }

    const mutation = `
      mutation Common_MarkAsNotRecurring($streamId: ID!) {
        markStreamAsNotRecurring(streamId: $streamId) {
          success
          errors {
            message
            field
            __typename
          }
          __typename
        }
      }
    `

    try {
      const result = await this.graphql.mutation<{
        markStreamAsNotRecurring: {
          success: boolean
          errors?: Array<{ message: string; field?: string }>
        }
      }>(mutation, variables)

      return result.markStreamAsNotRecurring.success
    } catch (error) {
      console.error('Failed to mark stream as not recurring:', error)
      return false
    }
  }
}