import { MonarchValidationError } from './errors'

export function validateRequired(params: Record<string, unknown>): void {
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') {
      throw new MonarchValidationError(`${key} is required`, key)
    }
  }
}

export function validateEmail(email: string): void {
  if (!email) {
    throw new MonarchValidationError('Email is required', 'email')
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    throw new MonarchValidationError('Invalid email format', 'email')
  }
}

export function validatePassword(password: string): void {
  if (!password) {
    throw new MonarchValidationError('Password is required', 'password')
  }
  
  if (password.length < 6) {
    throw new MonarchValidationError('Password must be at least 6 characters', 'password')
  }
}

export function validateMFA(code: string): void {
  if (!code) {
    throw new MonarchValidationError('MFA code is required', 'mfa_code')
  }
  
  // Remove spaces and validate format
  const cleanCode = code.replace(/\s/g, '')
  
  // Email OTP: 6 digits
  // TOTP: 6 digits
  // Backup codes: variable length
  if (!/^\d{6,8}$/.test(cleanCode) && cleanCode.length < 6) {
    throw new MonarchValidationError('Invalid MFA code format', 'mfa_code')
  }
}

export function validateLoginCredentials(email: string, password: string): void {
  validateEmail(email)
  validatePassword(password)
}

export function validateMFACredentials(email: string, password: string, code: string): void {
  validateLoginCredentials(email, password)
  validateMFA(code)
}

export function validateAccountId(accountId: string): void {
  if (!accountId || typeof accountId !== 'string') {
    throw new MonarchValidationError('Valid account ID is required', 'accountId')
  }
}

export function validateTransactionId(transactionId: string): void {
  if (!transactionId || typeof transactionId !== 'string') {
    throw new MonarchValidationError('Valid transaction ID is required', 'transactionId')
  }
}

export function validateAmount(amount: number): void {
  if (typeof amount !== 'number' || isNaN(amount)) {
    throw new MonarchValidationError('Valid amount is required', 'amount')
  }
}

export function validateDate(date: string): void {
  if (!date) {
    throw new MonarchValidationError('Date is required', 'date')
  }
  
  // Validate ISO date format (YYYY-MM-DD)
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!dateRegex.test(date)) {
    throw new MonarchValidationError('Date must be in YYYY-MM-DD format', 'date')
  }
  
  const parsedDate = new Date(date)
  if (isNaN(parsedDate.getTime())) {
    throw new MonarchValidationError('Invalid date', 'date')
  }
}

export function validateDateRange(startDate?: string, endDate?: string): void {
  if (startDate) {
    validateDate(startDate)
  }
  
  if (endDate) {
    validateDate(endDate)
  }
  
  if (startDate && endDate) {
    const start = new Date(startDate)
    const end = new Date(endDate)
    
    if (start > end) {
      throw new MonarchValidationError('Start date must be before end date', 'dateRange')
    }
  }
}

export function validateLimit(limit?: number): void {
  if (limit !== undefined) {
    if (typeof limit !== 'number' || limit < 1 || limit > 1000) {
      throw new MonarchValidationError('Limit must be between 1 and 1000', 'limit')
    }
  }
}

export function validateOffset(offset?: number): void {
  if (offset !== undefined) {
    if (typeof offset !== 'number' || offset < 0) {
      throw new MonarchValidationError('Offset must be non-negative', 'offset')
    }
  }
}

export function validatePagination(limit?: number, offset?: number): void {
  validateLimit(limit)
  validateOffset(offset)
}

export function validateArrayIds(ids?: string[], fieldName: string = 'ids'): void {
  if (ids !== undefined) {
    if (!Array.isArray(ids)) {
      throw new MonarchValidationError(`${fieldName} must be an array`, fieldName)
    }
    
    if (ids.some(id => typeof id !== 'string' || !id)) {
      throw new MonarchValidationError(`All ${fieldName} must be non-empty strings`, fieldName)
    }
  }
}

export function validateTicker(ticker: string): void {
  if (!ticker || typeof ticker !== 'string') {
    throw new MonarchValidationError('Valid ticker symbol is required', 'ticker')
  }
  
  // Basic ticker validation (1-5 uppercase letters)
  const tickerRegex = /^[A-Z]{1,5}$/
  if (!tickerRegex.test(ticker.toUpperCase())) {
    throw new MonarchValidationError('Invalid ticker symbol format', 'ticker')
  }
}

export function validateQuantity(quantity: number): void {
  if (typeof quantity !== 'number' || isNaN(quantity) || quantity <= 0) {
    throw new MonarchValidationError('Quantity must be a positive number', 'quantity')
  }
}

export function validateMerchantName(merchantName: string): void {
  if (!merchantName || typeof merchantName !== 'string') {
    throw new MonarchValidationError('Merchant name is required', 'merchantName')
  }
  
  if (merchantName.length > 255) {
    throw new MonarchValidationError('Merchant name must be less than 255 characters', 'merchantName')
  }
}

export function validateCategoryName(name: string): void {
  if (!name || typeof name !== 'string') {
    throw new MonarchValidationError('Category name is required', 'name')
  }
  
  if (name.length > 100) {
    throw new MonarchValidationError('Category name must be less than 100 characters', 'name')
  }
}

export function validateGoalName(name: string): void {
  if (!name || typeof name !== 'string') {
    throw new MonarchValidationError('Goal name is required', 'name')
  }
  
  if (name.length > 100) {
    throw new MonarchValidationError('Goal name must be less than 100 characters', 'name')
  }
}

export function validateTargetAmount(amount: number): void {
  if (typeof amount !== 'number' || isNaN(amount) || amount <= 0) {
    throw new MonarchValidationError('Target amount must be a positive number', 'targetAmount')
  }
}

export function isValidUUID(uuid: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  return uuidRegex.test(uuid)
}

export function sanitizeString(input: string): string {
  // eslint-disable-next-line no-control-regex
  return input.trim().replace(/[\x00-\x1f\x7f-\x9f]/g, '')
}

export function parseAmount(amount: string | number): number {
  if (typeof amount === 'number') {
    return amount
  }
  
  // Remove currency symbols, commas, and spaces
  const cleaned = amount.replace(/[$,\s]/g, '')
  const parsed = parseFloat(cleaned)
  
  if (isNaN(parsed)) {
    throw new MonarchValidationError('Invalid amount format', 'amount')
  }
  
  return parsed
}

export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0]
}

export function parseDate(date: string | Date): Date {
  if (date instanceof Date) {
    return date
  }
  
  const parsed = new Date(date)
  if (isNaN(parsed.getTime())) {
    throw new MonarchValidationError('Invalid date format', 'date')
  }
  
  return parsed
}