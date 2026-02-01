// import { MonarchErrorDetails } from '../types'

export class MonarchError extends Error {
  public code?: string
  public details?: unknown

  constructor(message: string, code?: string, details?: unknown) {
    super(message)
    this.name = 'MonarchError'
    this.code = code
    this.details = details
  }
}

export class MonarchAuthError extends MonarchError {
  constructor(message: string, details?: unknown) {
    super(message, 'AUTH_ERROR', details)
    this.name = 'MonarchAuthError'
  }
}

export class MonarchAPIError extends MonarchError {
  public statusCode?: number
  public response?: unknown

  constructor(message: string, statusCode?: number, response?: unknown) {
    super(message, 'API_ERROR', { statusCode, response })
    this.name = 'MonarchAPIError'
    this.statusCode = statusCode
    this.response = response
  }
}

export class MonarchRateLimitError extends MonarchError {
  public retryAfter?: number

  constructor(message: string, retryAfter?: number) {
    super(message, 'RATE_LIMIT', { retryAfter })
    this.name = 'MonarchRateLimitError'
    this.retryAfter = retryAfter
  }
}

export class MonarchValidationError extends MonarchError {
  public field?: string

  constructor(message: string, field?: string) {
    super(message, 'VALIDATION_ERROR', { field })
    this.name = 'MonarchValidationError'
    this.field = field
  }
}

export class MonarchNetworkError extends MonarchError {
  constructor(message: string, details?: unknown) {
    super(message, 'NETWORK_ERROR', details)
    this.name = 'MonarchNetworkError'
  }
}

export class MonarchGraphQLError extends MonarchError {
  public graphQLErrors?: Array<{
    message: string
    locations?: Array<{ line: number; column: number }>
    path?: (string | number)[]
    extensions?: Record<string, unknown>
  }>

  constructor(
    message: string,
    graphQLErrors?: MonarchGraphQLError['graphQLErrors']
  ) {
    super(message, 'GRAPHQL_ERROR', { graphQLErrors })
    this.name = 'MonarchGraphQLError'
    this.graphQLErrors = graphQLErrors
  }
}

export class MonarchSessionExpiredError extends MonarchAuthError {
  constructor(message: string = 'Session has expired') {
    super(message)
    this.name = 'MonarchSessionExpiredError'
    this.code = 'SESSION_EXPIRED'
  }
}

export class MonarchMFARequiredError extends MonarchAuthError {
  constructor(message: string = 'Multi-factor authentication required') {
    super(message)
    this.name = 'MonarchMFARequiredError'
    this.code = 'MFA_REQUIRED'
  }
}

export class MonarchCaptchaRequiredError extends MonarchAuthError {
  constructor(message: string = 'CAPTCHA verification required') {
    super(message)
    this.name = 'MonarchCaptchaRequiredError'
    this.code = 'CAPTCHA_REQUIRED'
  }
}

export class MonarchIPBlockedError extends MonarchAuthError {
  constructor(message: string = 'IP address has been temporarily blocked') {
    super(message)
    this.name = 'MonarchIPBlockedError'
    this.code = 'IP_BLOCKED'
  }
}

export class MonarchConfigError extends MonarchError {
  constructor(message: string, details?: unknown) {
    super(message, 'CONFIG_ERROR', details)
    this.name = 'MonarchConfigError'
  }
}

// Error handler utilities  
export function handleHTTPResponse(response: any): void {
  if (response.status === 401) {
    throw new MonarchAuthError('Unauthorized - check your credentials')
  }
  
  if (response.status === 403) {
    throw new MonarchAuthError('Forbidden - access denied')
  }
  
  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After')
    throw new MonarchRateLimitError(
      'Rate limit exceeded',
      retryAfter ? parseInt(retryAfter, 10) : undefined
    )
  }
  
  if (response.status >= 400 && response.status < 500) {
    throw new MonarchAPIError(
      `Client error: ${response.status} ${response.statusText}`,
      response.status
    )
  }
  
  if (response.status >= 500) {
    throw new MonarchAPIError(
      `Server error: ${response.status} ${response.statusText}`,
      response.status
    )
  }
}

export function handleGraphQLErrors(errors: unknown): never {
  if (Array.isArray(errors) && errors.length > 0) {
    const firstError = errors[0]
    const message = typeof firstError === 'object' && firstError !== null && 
      'message' in firstError ? String(firstError.message) : 'GraphQL error occurred'
    
    // Check for authentication errors in GraphQL errors
    if (message.toLowerCase().includes('unauthorized') || 
        message.toLowerCase().includes('authentication')) {
      throw new MonarchAuthError(message)
    }
    
    // Check for MFA errors
    if (message.toLowerCase().includes('mfa') || 
        message.toLowerCase().includes('multi-factor')) {
      throw new MonarchMFARequiredError(message)
    }
    
    throw new MonarchGraphQLError(message, errors)
  }
  
  throw new MonarchGraphQLError('Unknown GraphQL error occurred')
}

export function isRetryableError(error: Error): boolean {
  if (error instanceof MonarchRateLimitError) {
    return true
  }
  
  if (error instanceof MonarchNetworkError) {
    return true
  }
  
  if (error instanceof MonarchAPIError) {
    // Retry on server errors but not client errors
    return (error.statusCode && error.statusCode >= 500) || false
  }
  
  // Don't retry authentication, validation, or configuration errors
  if (error instanceof MonarchAuthError || 
      error instanceof MonarchValidationError || 
      error instanceof MonarchConfigError) {
    return false
  }
  
  return false
}

export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000,
  maxDelay: number = 60000
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      if (attempt === maxRetries || !isRetryableError(error as Error)) {
        throw error
      }
      
      let delay = baseDelay * Math.pow(2, attempt)
      
      // Use retry-after header for rate limit errors
      if (error instanceof MonarchRateLimitError && error.retryAfter) {
        delay = error.retryAfter * 1000
      }
      
      // Add jitter and respect max delay
      delay = Math.min(delay + Math.random() * 1000, maxDelay)
      
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  
  throw new MonarchError('Retry attempts exhausted')
}

// Legacy error aliases for backward compatibility
export const AuthenticationError = MonarchAuthError
export const ClientError = MonarchAPIError
export const ConfigurationError = MonarchConfigError
export const DataError = MonarchError
export const GraphQLError = MonarchGraphQLError
export const InvalidMFAError = MonarchMFARequiredError
export const LoginFailedException = MonarchAuthError
export const MFARequiredError = MonarchMFARequiredError
export const MonarchMoneyError = MonarchError
export const NetworkError = MonarchNetworkError
export const RateLimitError = MonarchRateLimitError
export const RequestFailedException = MonarchAPIError
export const RequireMFAException = MonarchMFARequiredError
export const ServerError = MonarchAPIError
export const SessionExpiredError = MonarchSessionExpiredError
export const ValidationError = MonarchValidationError

export const handle_graphql_errors = handleGraphQLErrors
export const handle_http_response = handleHTTPResponse