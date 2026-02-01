/**
 * CAPTCHA Avoidance Service
 * 
 * Implements aggressive rate limiting and session management to prevent CAPTCHA triggers
 */

export class CaptchaAvoidanceService {
  private static instance: CaptchaAvoidanceService | null = null
  private lastAuthTime: number = 0
  private authAttempts: number = 0
  private backoffMultiplier: number = 1
  // private readonly sessionCacheTime: number = 30 * 60 * 1000 // 30 minutes
  private maxAuthAttemptsPerHour: number = 3
  private authTimeWindow: number = 60 * 60 * 1000 // 1 hour

  // Track authentication attempts in the last hour
  private recentAuthAttempts: number[] = []

  private constructor() {}

  static getInstance(): CaptchaAvoidanceService {
    if (!CaptchaAvoidanceService.instance) {
      CaptchaAvoidanceService.instance = new CaptchaAvoidanceService()
    }
    return CaptchaAvoidanceService.instance
  }

  /**
   * Check if we should allow an authentication attempt
   */
  canAuthenticate(): boolean {
    const now = Date.now()
    
    // Clean old attempts (older than 1 hour)
    this.recentAuthAttempts = this.recentAuthAttempts.filter(
      time => now - time < this.authTimeWindow
    )

    // Check if we've exceeded max attempts per hour
    if (this.recentAuthAttempts.length >= this.maxAuthAttemptsPerHour) {
      const oldestAttempt = Math.min(...this.recentAuthAttempts)
      const timeUntilAllowed = this.authTimeWindow - (now - oldestAttempt)
      throw new Error(
        `Too many authentication attempts. Please wait ${Math.ceil(timeUntilAllowed / 1000 / 60)} minutes before trying again.`
      )
    }

    // Check minimum time between attempts
    const minTimeBetweenAuth = this.getMinTimeBetweenAuth()
    const timeSinceLastAuth = now - this.lastAuthTime
    
    if (timeSinceLastAuth < minTimeBetweenAuth) {
      const waitTime = minTimeBetweenAuth - timeSinceLastAuth
      throw new Error(
        `Rate limit protection: Please wait ${Math.ceil(waitTime / 1000)} seconds before authentication.`
      )
    }

    return true
  }

  /**
   * Record an authentication attempt
   */
  recordAuthAttempt(): void {
    const now = Date.now()
    this.lastAuthTime = now
    this.recentAuthAttempts.push(now)
    this.authAttempts++
  }

  /**
   * Record a CAPTCHA encounter - increase backoff significantly
   */
  recordCaptchaEncounter(): void {
    this.backoffMultiplier = Math.min(this.backoffMultiplier * 3, 10) // Max 10x multiplier
    console.warn(`🚫 CAPTCHA encountered. Increasing rate limit backoff to ${this.backoffMultiplier}x`)
  }

  /**
   * Record successful authentication - reduce backoff
   */
  recordSuccessfulAuth(): void {
    this.backoffMultiplier = Math.max(this.backoffMultiplier * 0.8, 1) // Slowly reduce
    console.log(`✅ Successful auth. Backoff multiplier now ${this.backoffMultiplier.toFixed(1)}x`)
  }

  /**
   * Get minimum time between authentication attempts (with backoff)
   */
  private getMinTimeBetweenAuth(): number {
    const baseDelay = 5 * 60 * 1000 // 5 minutes base
    return baseDelay * this.backoffMultiplier
  }

  /**
   * Get current status for debugging
   */
  getStatus(): {
    lastAuthTime: number
    timeSinceLastAuth: number
    minTimeBetweenAuth: number
    recentAttempts: number
    backoffMultiplier: number
    canAuthenticate: boolean
  } {
    const now = Date.now()
    const timeSinceLastAuth = now - this.lastAuthTime
    const minTimeBetweenAuth = this.getMinTimeBetweenAuth()
    
    return {
      lastAuthTime: this.lastAuthTime,
      timeSinceLastAuth,
      minTimeBetweenAuth,
      recentAttempts: this.recentAuthAttempts.length,
      backoffMultiplier: this.backoffMultiplier,
      canAuthenticate: timeSinceLastAuth >= minTimeBetweenAuth && this.recentAuthAttempts.length < this.maxAuthAttemptsPerHour
    }
  }

  /**
   * Reset the service (for testing purposes)
   */
  reset(): void {
    this.lastAuthTime = 0
    this.authAttempts = 0
    this.backoffMultiplier = 1
    this.recentAuthAttempts = []
  }
}