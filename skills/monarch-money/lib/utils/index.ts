// Utility exports
export * from './errors'
export * from './validation'
export * from './logger'
export * from './encryption'

// Helper utilities
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export function isNode(): boolean {
  return typeof process !== 'undefined' && process.versions?.node !== undefined
}

export function isBrowser(): boolean {
  return typeof globalThis !== 'undefined' && 
         typeof (globalThis as any).window !== 'undefined' && 
         typeof (globalThis as any).window.document !== 'undefined'
}

export function getEnvironmentVariable(name: string, defaultValue?: string): string | undefined {
  if (isNode()) {
    return process.env[name] || defaultValue
  }
  return defaultValue
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function formatPercentage(value: number, decimals: number = 2): string {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | undefined

  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

export function deepMerge<T extends Record<string, unknown>>(target: T, source: Partial<T>): T {
  const result = { ...target }

  for (const key in source) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      result[key] = deepMerge(
        target[key] as Record<string, unknown>,
        source[key] as Record<string, unknown>
      ) as T[Extract<keyof T, string>]
    } else if (source[key] !== undefined) {
      result[key] = source[key] as T[Extract<keyof T, string>]
    }
  }

  return result
}

export function pickFields<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  fields: K[]
): Pick<T, K> {
  const result = {} as Pick<T, K>
  
  for (const field of fields) {
    if (field in obj) {
      result[field] = obj[field]
    }
  }
  
  return result
}

export function omitFields<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  fields: K[]
): Omit<T, K> {
  const result = { ...obj }
  
  for (const field of fields) {
    delete result[field]
  }
  
  return result
}

export function groupBy<T, K extends string | number | symbol>(
  array: T[],
  keyFn: (item: T) => K
): Record<K, T[]> {
  return array.reduce((groups, item) => {
    const key = keyFn(item)
    if (!groups[key]) {
      groups[key] = []
    }
    groups[key].push(item)
    return groups
  }, {} as Record<K, T[]>)
}

export function chunk<T>(array: T[], size: number): T[][] {
  const chunks: T[][] = []
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size))
  }
  return chunks
}

export function unique<T>(array: T[], keyFn?: (item: T) => unknown): T[] {
  if (!keyFn) {
    return [...new Set(array)]
  }
  
  const seen = new Set()
  return array.filter(item => {
    const key = keyFn(item)
    if (seen.has(key)) {
      return false
    }
    seen.add(key)
    return true
  })
}

export function sortBy<T>(
  array: T[],
  keyFn: (item: T) => string | number,
  direction: 'asc' | 'desc' = 'asc'
): T[] {
  return [...array].sort((a, b) => {
    const aKey = keyFn(a)
    const bKey = keyFn(b)
    
    if (aKey < bKey) {
      return direction === 'asc' ? -1 : 1
    }
    if (aKey > bKey) {
      return direction === 'asc' ? 1 : -1
    }
    return 0
  })
}

export function createQueryString(params: Record<string, unknown>): string {
  const searchParams = new URLSearchParams()
  
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        value.forEach(item => searchParams.append(key, String(item)))
      } else {
        searchParams.set(key, String(value))
      }
    }
  }
  
  return searchParams.toString()
}