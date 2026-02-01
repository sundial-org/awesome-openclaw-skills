import { GraphQLClient } from '../../client/graphql'
import {
  TransactionCategory,
  CategoryGroup,
  TransactionTag,
  CreateCategoryInput,
  UpdateCategoryInput,
  CreateTagInput,
  BulkDeleteResult
} from '../../types'
import { validateRequired, logger } from '../../utils'

export interface CategoriesAPI {
  // Category management
  getCategories(): Promise<TransactionCategory[]>
  getCategoryById(categoryId: string): Promise<TransactionCategory>
  createCategory(data: CreateCategoryInput): Promise<TransactionCategory>
  updateCategory(categoryId: string, data: UpdateCategoryInput): Promise<TransactionCategory>
  deleteCategory(categoryId: string): Promise<boolean>
  deleteCategories(categoryIds: string[]): Promise<BulkDeleteResult>

  // Category groups
  getCategoryGroups(): Promise<CategoryGroup[]>
  getCategoryGroupById(groupId: string): Promise<CategoryGroup>

  // Tags management
  getTags(): Promise<TransactionTag[]>
  getTagById(tagId: string): Promise<TransactionTag>
  createTag(data: CreateTagInput): Promise<TransactionTag>
  updateTag(tagId: string, data: Partial<CreateTagInput>): Promise<TransactionTag>
  deleteTag(tagId: string): Promise<boolean>

  // Transaction tagging
  setTransactionTags(transactionId: string, tagIds: string[]): Promise<boolean>
  addTagToTransaction(transactionId: string, tagId: string): Promise<boolean>
  removeTagFromTransaction(transactionId: string, tagId: string): Promise<boolean>
}

export class CategoriesAPIImpl implements CategoriesAPI {
  constructor(private graphql: GraphQLClient) {}

  // Category management methods
  async getCategories(): Promise<TransactionCategory[]> {
    logger.debug('Fetching all transaction categories')
    
    // FIXED: Use exact working query from MonarchMoney web app
    const query = `
      query GetCategories {
        categories {
          ...CategoryFields
          __typename
        }
      }

      fragment CategoryFields on Category {
        id
        order
        name
        icon
        systemCategory
        isSystemCategory
        isDisabled
        group {
          id
          name
          type
          __typename
        }
        __typename
      }
    `

    const result = await this.graphql.query<{
      categories: TransactionCategory[]
    }>(query)

    logger.debug(`Retrieved ${result.categories.length} categories using web app schema`)
    return result.categories || []
  }

  async getCategoryById(categoryId: string): Promise<TransactionCategory> {
    validateRequired({ categoryId })
    logger.debug(`Fetching category by ID: ${categoryId}`)

    const query = `
      query GetTransactionCategory($categoryId: ID!) {
        transactionCategory(id: $categoryId) {
          id
          name
          displayName
          shortName
          color
          icon
          order
          isDefault
          isDisabled
          isSystemCategory
          groupId
          group {
            id
            name
            displayName
            color
            icon
            order
          }
          parentCategoryId
          parentCategory {
            id
            name
            displayName
          }
          childCategories {
            id
            name
            displayName
            color
            icon
          }
          createdAt
          updatedAt
        }
      }
    `

    const result = await this.graphql.query<{
      transactionCategory: TransactionCategory
    }>(query, { categoryId })

    if (!result.transactionCategory) {
      throw new Error(`Category not found: ${categoryId}`)
    }

    return result.transactionCategory
  }

  async createCategory(data: CreateCategoryInput): Promise<TransactionCategory> {
    validateRequired({ name: data.name })
    logger.debug(`Creating transaction category: ${data.name}`)

    const mutation = `
      mutation CreateTransactionCategory($input: CreateTransactionCategoryInput!) {
        createTransactionCategory(input: $input) {
          category {
            id
            name
            displayName
            shortName
            color
            icon
            order
            isDefault
            isDisabled
            isSystemCategory
            groupId
            parentCategoryId
            createdAt
            updatedAt
          }
          errors {
            field
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      createTransactionCategory: {
        category: TransactionCategory
        errors: Array<{ field: string; message: string }>
      }
    }>(mutation, { input: data })

    if (result.createTransactionCategory.errors?.length > 0) {
      const errorMessages = result.createTransactionCategory.errors.map(e => e.message).join(', ')
      throw new Error(`Failed to create category: ${errorMessages}`)
    }

    return result.createTransactionCategory.category
  }

  async updateCategory(categoryId: string, data: UpdateCategoryInput): Promise<TransactionCategory> {
    validateRequired({ categoryId })
    logger.debug(`Updating category: ${categoryId}`)

    const mutation = `
      mutation UpdateTransactionCategory($categoryId: ID!, $input: UpdateTransactionCategoryInput!) {
        updateTransactionCategory(id: $categoryId, input: $input) {
          category {
            id
            name
            displayName
            shortName
            color
            icon
            order
            isDefault
            isDisabled
            isSystemCategory
            groupId
            parentCategoryId
            createdAt
            updatedAt
          }
          errors {
            field
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      updateTransactionCategory: {
        category: TransactionCategory
        errors: Array<{ field: string; message: string }>
      }
    }>(mutation, { categoryId, input: data })

    if (result.updateTransactionCategory.errors?.length > 0) {
      const errorMessages = result.updateTransactionCategory.errors.map(e => e.message).join(', ')
      throw new Error(`Failed to update category: ${errorMessages}`)
    }

    return result.updateTransactionCategory.category
  }

  async deleteCategory(categoryId: string): Promise<boolean> {
    validateRequired({ categoryId })
    logger.debug(`Deleting category: ${categoryId}`)

    const mutation = `
      mutation DeleteTransactionCategory($categoryId: ID!) {
        deleteTransactionCategory(id: $categoryId) {
          success
          errors {
            field
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      deleteTransactionCategory: {
        success: boolean
        errors: Array<{ field: string; message: string }>
      }
    }>(mutation, { categoryId })

    if (result.deleteTransactionCategory.errors?.length > 0) {
      const errorMessages = result.deleteTransactionCategory.errors.map(e => e.message).join(', ')
      throw new Error(`Failed to delete category: ${errorMessages}`)
    }

    return result.deleteTransactionCategory.success
  }

  async deleteCategories(categoryIds: string[]): Promise<BulkDeleteResult> {
    validateRequired({ categoryIds })
    logger.debug(`Bulk deleting ${categoryIds.length} categories`)

    const mutation = `
      mutation DeleteTransactionCategories($categoryIds: [ID!]!) {
        deleteTransactionCategories(ids: $categoryIds) {
          deletedCount
          failedCount
          errors {
            id
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      deleteTransactionCategories: BulkDeleteResult
    }>(mutation, { categoryIds })

    return result.deleteTransactionCategories
  }

  // Category groups methods
  async getCategoryGroups(): Promise<CategoryGroup[]> {
    logger.debug('Fetching all category groups')
    
    const query = `
      query GetTransactionCategoryGroups {
        transactionCategoryGroups {
          id
          name
          displayName
          color
          icon
          order
          isDefault
          categories {
            id
            name
            displayName
            color
            icon
          }
          createdAt
          updatedAt
        }
      }
    `

    const result = await this.graphql.query<{
      transactionCategoryGroups: CategoryGroup[]
    }>(query)

    return result.transactionCategoryGroups || []
  }

  async getCategoryGroupById(groupId: string): Promise<CategoryGroup> {
    validateRequired({ groupId })
    logger.debug(`Fetching category group by ID: ${groupId}`)

    const query = `
      query GetTransactionCategoryGroup($groupId: ID!) {
        transactionCategoryGroup(id: $groupId) {
          id
          name
          displayName
          color
          icon
          order
          isDefault
          categories {
            id
            name
            displayName
            color
            icon
            order
          }
          createdAt
          updatedAt
        }
      }
    `

    const result = await this.graphql.query<{
      transactionCategoryGroup: CategoryGroup
    }>(query, { groupId })

    if (!result.transactionCategoryGroup) {
      throw new Error(`Category group not found: ${groupId}`)
    }

    return result.transactionCategoryGroup
  }

  // Tags management methods
  async getTags(): Promise<TransactionTag[]> {
    logger.debug('Fetching all transaction tags')
    
    const query = `
      query GetTransactionTags {
        transactionTags {
          id
          name
          color
          order
          isDefault
          createdAt
          updatedAt
        }
      }
    `

    const result = await this.graphql.query<{
      transactionTags: TransactionTag[]
    }>(query)

    return result.transactionTags || []
  }

  async getTagById(tagId: string): Promise<TransactionTag> {
    validateRequired({ tagId })
    logger.debug(`Fetching tag by ID: ${tagId}`)

    const query = `
      query GetTransactionTag($tagId: ID!) {
        transactionTag(id: $tagId) {
          id
          name
          color
          order
          isDefault
          createdAt
          updatedAt
        }
      }
    `

    const result = await this.graphql.query<{
      transactionTag: TransactionTag
    }>(query, { tagId })

    if (!result.transactionTag) {
      throw new Error(`Tag not found: ${tagId}`)
    }

    return result.transactionTag
  }

  async createTag(data: CreateTagInput): Promise<TransactionTag> {
    validateRequired({ name: data.name })
    logger.debug(`Creating transaction tag: ${data.name}`)

    const mutation = `
      mutation CreateTransactionTag($input: CreateTransactionTagInput!) {
        createTransactionTag(input: $input) {
          tag {
            id
            name
            color
            order
            isDefault
            createdAt
            updatedAt
          }
          errors {
            field
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      createTransactionTag: {
        tag: TransactionTag
        errors: Array<{ field: string; message: string }>
      }
    }>(mutation, { input: data })

    if (result.createTransactionTag.errors?.length > 0) {
      const errorMessages = result.createTransactionTag.errors.map(e => e.message).join(', ')
      throw new Error(`Failed to create tag: ${errorMessages}`)
    }

    return result.createTransactionTag.tag
  }

  async updateTag(tagId: string, data: Partial<CreateTagInput>): Promise<TransactionTag> {
    validateRequired({ tagId })
    logger.debug(`Updating tag: ${tagId}`)

    const mutation = `
      mutation UpdateTransactionTag($tagId: ID!, $input: UpdateTransactionTagInput!) {
        updateTransactionTag(id: $tagId, input: $input) {
          tag {
            id
            name
            color
            order
            isDefault
            createdAt
            updatedAt
          }
          errors {
            field
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      updateTransactionTag: {
        tag: TransactionTag
        errors: Array<{ field: string; message: string }>
      }
    }>(mutation, { tagId, input: data })

    if (result.updateTransactionTag.errors?.length > 0) {
      const errorMessages = result.updateTransactionTag.errors.map(e => e.message).join(', ')
      throw new Error(`Failed to update tag: ${errorMessages}`)
    }

    return result.updateTransactionTag.tag
  }

  async deleteTag(tagId: string): Promise<boolean> {
    validateRequired({ tagId })
    logger.debug(`Deleting tag: ${tagId}`)

    const mutation = `
      mutation DeleteTransactionTag($tagId: ID!) {
        deleteTransactionTag(id: $tagId) {
          success
          errors {
            field
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      deleteTransactionTag: {
        success: boolean
        errors: Array<{ field: string; message: string }>
      }
    }>(mutation, { tagId })

    if (result.deleteTransactionTag.errors?.length > 0) {
      const errorMessages = result.deleteTransactionTag.errors.map(e => e.message).join(', ')
      throw new Error(`Failed to delete tag: ${errorMessages}`)
    }

    return result.deleteTransactionTag.success
  }

  // Transaction tagging methods
  async setTransactionTags(transactionId: string, tagIds: string[]): Promise<boolean> {
    validateRequired({ transactionId, tagIds })
    logger.debug(`Setting tags for transaction ${transactionId}: ${tagIds.join(', ')}`)

    const mutation = `
      mutation SetTransactionTags($transactionId: ID!, $tagIds: [ID!]!) {
        setTransactionTags(transactionId: $transactionId, tagIds: $tagIds) {
          success
          errors {
            field
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      setTransactionTags: {
        success: boolean
        errors: Array<{ field: string; message: string }>
      }
    }>(mutation, { transactionId, tagIds })

    if (result.setTransactionTags.errors?.length > 0) {
      const errorMessages = result.setTransactionTags.errors.map(e => e.message).join(', ')
      throw new Error(`Failed to set transaction tags: ${errorMessages}`)
    }

    return result.setTransactionTags.success
  }

  async addTagToTransaction(transactionId: string, tagId: string): Promise<boolean> {
    validateRequired({ transactionId, tagId })
    logger.debug(`Adding tag ${tagId} to transaction ${transactionId}`)

    const mutation = `
      mutation AddTagToTransaction($transactionId: ID!, $tagId: ID!) {
        addTagToTransaction(transactionId: $transactionId, tagId: $tagId) {
          success
          errors {
            field
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      addTagToTransaction: {
        success: boolean
        errors: Array<{ field: string; message: string }>
      }
    }>(mutation, { transactionId, tagId })

    if (result.addTagToTransaction.errors?.length > 0) {
      const errorMessages = result.addTagToTransaction.errors.map(e => e.message).join(', ')
      throw new Error(`Failed to add tag to transaction: ${errorMessages}`)
    }

    return result.addTagToTransaction.success
  }

  async removeTagFromTransaction(transactionId: string, tagId: string): Promise<boolean> {
    validateRequired({ transactionId, tagId })
    logger.debug(`Removing tag ${tagId} from transaction ${transactionId}`)

    const mutation = `
      mutation RemoveTagFromTransaction($transactionId: ID!, $tagId: ID!) {
        removeTagFromTransaction(transactionId: $transactionId, tagId: $tagId) {
          success
          errors {
            field
            message
          }
        }
      }
    `

    const result = await this.graphql.mutation<{
      removeTagFromTransaction: {
        success: boolean
        errors: Array<{ field: string; message: string }>
      }
    }>(mutation, { transactionId, tagId })

    if (result.removeTagFromTransaction.errors?.length > 0) {
      const errorMessages = result.removeTagFromTransaction.errors.map(e => e.message).join(', ')
      throw new Error(`Failed to remove tag from transaction: ${errorMessages}`)
    }

    return result.removeTagFromTransaction.success
  }
}