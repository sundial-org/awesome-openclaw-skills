import { GraphQLClient } from '../../client/graphql'

export interface Institution {
  id: string
  name: string
  url?: string
  logoUrl?: string
  primaryColor?: string
}

export interface Credential {
  id: string
  updateRequired: boolean
  disconnectedFromDataProviderAt?: string
  displayLastUpdatedAt?: string
  dataProvider: string
  institution: {
    id: string
    name: string
    url: string
  } | null
}

export interface InstitutionSettings {
  credentials: Credential[]
  accounts: Array<{
    id: string
    displayName: string
    subtype?: {
      display: string
    }
    mask?: string
    credential: {
      id: string
    }
    deletedAt?: string
  }>
  subscription: {
    isOnFreeTrial: boolean
    hasPremiumEntitlement: boolean
  }
}

export interface InstitutionsAPI {
  /**
   * Get all available financial institutions
   */
  getInstitutions(): Promise<Institution[]>

  /**
   * Get detailed institution settings including credentials and linked accounts
   */
  getInstitutionSettings(): Promise<InstitutionSettings>
}

export class InstitutionsAPIImpl implements InstitutionsAPI {
  constructor(private graphql: GraphQLClient) {}

  async getInstitutions(): Promise<Institution[]> {
    // FIXED: Since 'institutions' field doesn't exist, extract from credentials
    // Handle case where user has no institution data gracefully
    const query = `
      query {
        credentials {
          id
          institution {
            id
            name
            url
            __typename
          }
          __typename
        }
      }
    `

    const result = await this.graphql.query<{ 
      credentials: Array<{ 
        institution: Institution | null
      }> 
    }>(query)
    
    // Extract unique institutions from credentials (handle null institutions)
    const institutionsMap = new Map<string, Institution>()
    result.credentials.forEach(cred => {
      if (cred.institution && cred.institution.id) {
        institutionsMap.set(cred.institution.id, cred.institution)
      }
    })
    
    return Array.from(institutionsMap.values())
  }

  async getInstitutionSettings(): Promise<InstitutionSettings> {
    // FIXED: Use exact Python fragment structure
    const query = `
      query Web_GetInstitutionSettings {
        credentials {
          id
          updateRequired
          disconnectedFromDataProviderAt
          displayLastUpdatedAt
          dataProvider
          institution {
            id
            name
            url
            __typename
          }
          __typename
        }
        accounts(filters: {includeDeleted: true}) {
          id
          displayName
          subtype {
            display
            __typename
          }
          mask
          credential {
            id
            __typename
          }
          deletedAt
          __typename
        }
        subscription {
          isOnFreeTrial
          hasPremiumEntitlement
          __typename
        }
      }
    `

    const result = await this.graphql.query<InstitutionSettings>(query)
    return result
  }
}