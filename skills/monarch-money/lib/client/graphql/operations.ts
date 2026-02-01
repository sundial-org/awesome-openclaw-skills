/**
 * GraphQL Operations with Context Optimization
 *
 * All queries now support verbosity levels for optimal context usage:
 * - ultra-light: Essential fields only (~60-80 chars per item)
 * - light: Moderate detail (~180-220 chars per item)
 * - standard: Full detail (original query complexity)
 */

// =============================================================================
// ACCOUNT OPERATIONS
// =============================================================================

// Ultra-light accounts (essential fields only)
export const GET_ACCOUNTS_ULTRA_LIGHT = `
  query GetAccountsUltraLight {
    accounts {
      id
      displayName
      currentBalance
      type {
        name
      }
    }
  }
`;

// Light accounts (moderate detail)
export const GET_ACCOUNTS_LIGHT = `
  query GetAccountsLight {
    accounts {
      id
      displayName
      currentBalance
      mask
      isHidden
      includeInNetWorth
      updatedAt
      type {
        name
        display
      }
      institution {
        name
      }
    }
  }
`;

// Standard accounts (full detail - original complexity)
export const GET_ACCOUNT_DETAILS = `
  query Common_AccountDetails_getAccount($id: UUID!) {
    account(id: $id) {
      id
      displayName
      syncDisabled
      deactivatedAt
      isHidden
      isAsset
      mask
      createdAt
      updatedAt
      displayLastUpdatedAt
      currentBalance
      displayBalance
      includeInNetWorth
      hideFromList
      hideTransactionsFromReports
      includeBalanceInNetWorth
      includeInGoalBalance
      dataProvider
      dataProviderAccountId
      isManual
      transactionsCount
      holdingsCount
      manualInvestmentsTrackingMethod
      order
      logoUrl
      type {
        name
        display
        __typename
      }
      subtype {
        name
        display
        __typename
      }
      credential {
        id
        updateRequired
        disconnectedFromDataProviderAt
        dataProvider
        __typename
      }
      institution {
        id
        name
        __typename
      }
      __typename
    }
  }
`;

export const GET_ACCOUNTS = `
  query GetAccounts {
    accounts {
      id
      displayName
      syncDisabled
      deactivatedAt
      isHidden
      isAsset
      mask
      createdAt
      updatedAt
      displayLastUpdatedAt
      currentBalance
      displayBalance
      includeInNetWorth
      hideFromList
      hideTransactionsFromReports
      includeBalanceInNetWorth
      includeInGoalBalance
      dataProvider
      dataProviderAccountId
      isManual
      transactionsCount
      holdingsCount
      manualInvestmentsTrackingMethod
      order
      logoUrl
      type {
        name
        display
        __typename
      }
      subtype {
        name
        display
        __typename
      }
      credential {
        id
        updateRequired
        disconnectedFromDataProviderAt
        dataProvider
        __typename
      }
      institution {
        id
        name
        __typename
      }
      __typename
    }
  }
`;

// =============================================================================
// TRANSACTION OPERATIONS
// =============================================================================

// Ultra-light transactions (minimal fields)
export const GET_TRANSACTIONS_ULTRA_LIGHT = `
  query GetTransactionsUltraLight(
    $offset: Int,
    $limit: Int,
    $filters: TransactionFilterInput,
    $orderBy: TransactionOrdering
  ) {
    allTransactions(filters: $filters) {
      results(offset: $offset, limit: $limit, orderBy: $orderBy) {
        id
        amount
        date
        merchant {
          name
        }
        account {
          displayName
        }
      }
    }
  }
`;

// Light transactions (moderate detail)
export const GET_TRANSACTIONS_LIGHT = `
  query GetTransactionsLight(
    $offset: Int,
    $limit: Int,
    $filters: TransactionFilterInput,
    $orderBy: TransactionOrdering
  ) {
    allTransactions(filters: $filters) {
      results(offset: $offset, limit: $limit, orderBy: $orderBy) {
        id
        amount
        date
        pending
        needsReview
        category {
          id
          name
        }
        merchant {
          name
        }
        account {
          id
          displayName
          mask
        }
      }
    }
  }
`;

// Standard transactions (full detail - original complexity)
export const GET_TRANSACTIONS = `
  query GetTransactions(
    $offset: Int,
    $limit: Int,
    $filters: TransactionFilterInput,
    $orderBy: TransactionOrdering
  ) {
    allTransactions(filters: $filters) {
      totalCount
      results(offset: $offset, limit: $limit, orderBy: $orderBy) {
        id
        amount
        date
        hideFromReports
        plaidName
        pending
        reviewStatus
        needsReview
        dataProvider
        dataProviderDescription
        isRecurring
        notes
        isReviewed
        attachments {
          id
          extension
          filename
          publicId
          sizeBytes
          type
          __typename
        }
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
        merchant {
          id
          name
          transactionsCount
          __typename
        }
        account {
          id
          displayName
          mask
          institution {
            name
            __typename
          }
          __typename
        }
        tags {
          id
          name
          color
          order
          __typename
        }
        __typename
      }
      __typename
    }
  }
`;

// =============================================================================
// SMART SEARCH OPERATIONS
// =============================================================================

export const SMART_TRANSACTION_SEARCH = `
  query SmartTransactionSearch(
    $search: String,
    $limit: Int = 10,
    $startDate: String,
    $endDate: String,
    $minAmount: Float,
    $maxAmount: Float,
    $accountIds: [ID!],
    $categoryIds: [ID!]
  ) {
    allTransactions(filters: {
      search: $search,
      startDate: $startDate,
      endDate: $endDate,
      minAmount: $minAmount,
      maxAmount: $maxAmount,
      accountIds: $accountIds,
      categoryIds: $categoryIds,
      transactionVisibility: non_hidden_transactions_only
    }) {
      totalCount
      results(limit: $limit, orderBy: DATE_DESC) {
        id
        amount
        date
        merchant {
          name
        }
        category {
          name
        }
        account {
          displayName
          mask
        }
      }
    }
  }
`;

// =============================================================================
// CATEGORY OPERATIONS
// =============================================================================

export const GET_TRANSACTION_CATEGORIES = `
  query GetTransactionCategories {
    categories {
      id
      name
      icon
      group {
        id
        name
        type
        __typename
      }
      __typename
    }
  }
`;

export const GET_CATEGORIES_LIGHT = `
  query GetCategoriesLight {
    categories {
      id
      name
      icon
      group {
        name
      }
    }
  }
`;

// =============================================================================
// BUDGET OPERATIONS
// =============================================================================

export const GET_BUDGETS = `
  query GetBudgets(
    $startDate: String,
    $endDate: String
  ) {
    budgets(
      startDate: $startDate,
      endDate: $endDate
    ) {
      categories {
        id
        name
        budgetAmount
        spentAmount
        percentSpent
        rolloverEnabled
        rolloverAmount
        isIncome
        isTransfer
        __typename
      }
      __typename
    }
  }
`;

export const GET_BUDGETS_LIGHT = `
  query GetBudgetsLight(
    $startDate: String,
    $endDate: String
  ) {
    budgets(
      startDate: $startDate,
      endDate: $endDate
    ) {
      categories {
        id
        name
        budgetAmount
        spentAmount
        percentSpent
      }
    }
  }
`;

// =============================================================================
// SUMMARY OPERATIONS (Ultra-compact responses)
// =============================================================================

export const GET_QUICK_FINANCIAL_OVERVIEW = `
  query GetQuickFinancialOverview {
    accounts {
      currentBalance
      includeInNetWorth
    }
  }
`;

export const GET_SPENDING_BY_CATEGORY_SUMMARY = `
  query GetSpendingByCategorySummary(
    $startDate: String,
    $endDate: String,
    $limit: Int = 5
  ) {
    allTransactions(filters: {
      startDate: $startDate,
      endDate: $endDate,
      transactionVisibility: non_hidden_transactions_only
    }) {
      results(limit: 1000, orderBy: DATE_DESC) {
        amount
        category {
          name
        }
      }
    }
  }
`;

export const GET_ACCOUNT_BALANCE_TRENDS = `
  query GetAccountBalanceTrends {
    accounts {
      displayName
      currentBalance
      type {
        name
      }
      updatedAt
    }
  }
`;

// =============================================================================
// OTHER OPERATIONS (kept from original)
// =============================================================================

export const GET_ACCOUNT_TYPE_OPTIONS = `
  query GetAccountTypeOptions {
    accountTypeOptions {
      accountTypes {
        id
        name
        display
        group
        __typename
      }
      accountSubtypes {
        id
        name
        display
        accountTypeId
        __typename
      }
      __typename
    }
  }
`;

export const GET_NET_WORTH_HISTORY = `
  query Common_GetAggregateSnapshots($filters: AggregateSnapshotFilters) {
    aggregateSnapshots(filters: $filters) {
      date
      balance
      assetsBalance
      liabilitiesBalance
      __typename
    }
  }
`;

// =============================================================================
// VERBOSITY UTILITIES
// =============================================================================

export type VerbosityLevel = 'ultra-light' | 'light' | 'standard';

/**
 * Select appropriate queries based on verbosity level
 */
export function getQueryForVerbosity(queryType: 'accounts' | 'transactions' | 'categories' | 'budgets', verbosity: VerbosityLevel): string {
  switch (queryType) {
    case 'accounts':
      if (verbosity === 'ultra-light') return GET_ACCOUNTS_ULTRA_LIGHT;
      if (verbosity === 'light') return GET_ACCOUNTS_LIGHT;
      return GET_ACCOUNTS;

    case 'transactions':
      if (verbosity === 'ultra-light') return GET_TRANSACTIONS_ULTRA_LIGHT;
      if (verbosity === 'light') return GET_TRANSACTIONS_LIGHT;
      return GET_TRANSACTIONS;

    case 'categories':
      if (verbosity === 'ultra-light' || verbosity === 'light') return GET_CATEGORIES_LIGHT;
      return GET_TRANSACTION_CATEGORIES;

    case 'budgets':
      if (verbosity === 'ultra-light' || verbosity === 'light') return GET_BUDGETS_LIGHT;
      return GET_BUDGETS;

    default:
      throw new Error(`Unknown query type: ${queryType}`);
  }
}