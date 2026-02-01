import { GraphQLClient } from '../../client/graphql'

export interface Insight {
  id: string
  type: string
  title: string
  description: string
  category: string
  priority: number
  actionRequired: boolean
  createdAt: string
  dismissedAt?: string
  metadata?: Record<string, any>
}

export interface NetWorthHistoryPoint {
  date: string
  netWorth: number
  assets: number
  liabilities: number
}

export interface CreditScore {
  score?: number
  provider?: string
  lastUpdated?: string
  history?: Array<{
    date: string
    score: number
  }>
  factors?: Array<{
    category: string
    impact: string
    description: string
  }>
}

export interface Notification {
  id: string
  type: string
  title: string
  message: string
  priority: string
  isRead: boolean
  createdAt: string
  actionUrl?: string
}

export interface SubscriptionDetails {
  planType: string
  status: string
  billingCycle: string
  nextBillingDate?: string
  price: number
  features: string[]
}

export interface InsightsAPI {
  /**
   * Get financial insights and recommendations
   */
  getInsights(options?: {
    startDate?: string
    endDate?: string
    insightTypes?: string[]
  }): Promise<Insight[]>

  /**
   * Get net worth history over time
   */
  getNetWorthHistory(options?: {
    startDate?: string
    endDate?: string
  }): Promise<NetWorthHistoryPoint[]>

  /**
   * Get credit score monitoring data
   */
  getCreditScore(options?: {
    includeHistory?: boolean
  }): Promise<CreditScore>

  /**
   * Get account notifications and alerts
   */
  getNotifications(): Promise<Notification[]>

  /**
   * Get subscription details and plan information
   */
  getSubscriptionDetails(): Promise<SubscriptionDetails>

  /**
   * Dismiss an insight
   */
  dismissInsight(insightId: string): Promise<boolean>
}

export class InsightsAPIImpl implements InsightsAPI {
  constructor(private graphql: GraphQLClient) {}

  async getInsights(options?: {
    startDate?: string
    endDate?: string
    insightTypes?: string[]
  }): Promise<Insight[]> {
    const variables: Record<string, any> = {}
    
    if (options?.startDate) variables.startDate = options.startDate
    if (options?.endDate) variables.endDate = options.endDate
    if (options?.insightTypes) variables.insightTypes = options.insightTypes

    const query = `
      query GetInsights(
        $startDate: String,
        $endDate: String,
        $insightTypes: [String]
      ) {
        insights(
          startDate: $startDate,
          endDate: $endDate,
          insightTypes: $insightTypes
        ) {
          id
          type
          title
          description
          priority
          category
          actionRequired
          createdAt
          dismissedAt
          metadata
          __typename
        }
      }
    `

    const result = await this.graphql.query<{ insights: Insight[] }>(query, variables)
    return result.insights
  }

  async getNetWorthHistory(options?: {
    startDate?: string
    endDate?: string
  }): Promise<NetWorthHistoryPoint[]> {
    // Default to last 12 months if no dates provided
    const endDate = options?.endDate || new Date().toISOString().split('T')[0]
    const startDate = options?.startDate || new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

    const variables = { startDate, endDate }

    const query = `
      query GetNetWorthHistory($startDate: Date!, $endDate: Date!) {
        netWorthHistory(startDate: $startDate, endDate: $endDate) {
          date
          netWorth
          assets
          liabilities
          __typename
        }
      }
    `

    const result = await this.graphql.query<{
      netWorthHistory: NetWorthHistoryPoint[]
    }>(query, variables)

    return result.netWorthHistory
  }

  async getCreditScore(options?: {
    includeHistory?: boolean
  }): Promise<CreditScore> {
    const variables = {
      includeHistory: options?.includeHistory ?? true
    }

    const query = `
      query Common_GetSpinwheelCreditScoreSnapshots($includeHistory: Boolean!) {
        spinwheelCreditScoreSnapshots(includeHistory: $includeHistory) {
          score
          provider
          lastUpdated
          history {
            date
            score
            __typename
          }
          factors {
            category
            impact
            description
            __typename
          }
          __typename
        }
      }
    `

    try {
      const result = await this.graphql.query<{
        spinwheelCreditScoreSnapshots: CreditScore
      }>(query, variables)

      return result.spinwheelCreditScoreSnapshots
    } catch (error) {
      // Return empty credit score data if the service is not available
      return {
        score: undefined,
        provider: undefined,
        lastUpdated: undefined,
        history: [],
        factors: []
      }
    }
  }

  async getNotifications(): Promise<Notification[]> {
    const query = `
      query GetNotifications {
        notifications {
          id
          type
          title
          message
          priority
          isRead
          createdAt
          actionUrl
          __typename
        }
      }
    `

    const result = await this.graphql.query<{ notifications: Notification[] }>(query)
    return result.notifications
  }

  async getSubscriptionDetails(): Promise<SubscriptionDetails> {
    const query = `
      query Common_GetSubscriptionDetails {
        subscriptionDetails {
          planType
          status
          billingCycle
          nextBillingDate
          price
          features
          __typename
        }
      }
    `

    const result = await this.graphql.query<{
      subscriptionDetails: SubscriptionDetails
    }>(query)

    return result.subscriptionDetails
  }

  async dismissInsight(insightId: string): Promise<boolean> {
    const variables = { insightId }

    const mutation = `
      mutation DismissInsight($insightId: ID!) {
        dismissInsight(insightId: $insightId) {
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
        dismissInsight: {
          success: boolean
          errors?: Array<{ message: string; field?: string }>
        }
      }>(mutation, variables)

      return result.dismissInsight.success
    } catch (error) {
      console.error('Failed to dismiss insight:', error)
      return false
    }
  }
}