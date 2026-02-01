import * as readline from 'readline'
import * as totp from 'otplib'
import fetch from 'node-fetch'
import { SessionStorage } from './SessionStorage'
import { CaptchaHandler } from './CaptchaHandler'
import { 
  validateLoginCredentials, 
  validateMFACredentials, 
  logger,
  MonarchAuthError,
  MonarchMFARequiredError,
  MonarchCaptchaRequiredError,
  MonarchIPBlockedError,
  MonarchSessionExpiredError,
  handleHTTPResponse,
  retryWithBackoff,
  EncryptionService
} from '../../utils'
import { SessionInfo } from '../../types'

export interface LoginOptions {
  email?: string
  password?: string
  useSavedSession?: boolean
  saveSession?: boolean
  mfaSecretKey?: string
  interactive?: boolean  // Whether to prompt user for CAPTCHA resolution
  maxCaptchaRetries?: number  // Maximum retries after CAPTCHA
}

export interface MFAOptions {
  email: string
  password: string
  code: string
}

export class AuthenticationService {
  private baseUrl: string
  private sessionStorage: SessionStorage
  private lastRequestTime = 0
  private readonly minRequestInterval = 300 // 300ms for more human-like auth requests
  private loginInProgress = false
  constructor(
    baseUrl: string = 'https://api.monarchmoney.com',
    sessionStorage?: SessionStorage
  ) {
    this.baseUrl = baseUrl
    this.sessionStorage = sessionStorage || new SessionStorage()
  }

  async login(options: LoginOptions = {}): Promise<void> {
    // Prevent concurrent login attempts
    if (this.loginInProgress) {
      logger.debug('Login already in progress, waiting...')
      // Wait for any existing login to complete
      while (this.loginInProgress) {
        await new Promise(resolve => setTimeout(resolve, 50))
      }
      return
    }

    const {
      email,
      password,
      useSavedSession = true,
      saveSession = true,
      mfaSecretKey,
      interactive = true,
      maxCaptchaRetries = 3
    } = options

    // Try to use saved session first
    if (useSavedSession && this.sessionStorage.hasValidSession()) {
      logger.info('Using saved session')
      return
    }

    // Validate credentials
    if (!email || !password) {
      throw new MonarchAuthError('Email and password are required for login')
    }

    validateLoginCredentials(email, password)
    
    // Mark login as in progress
    this.loginInProgress = true

    try {
      // Attempt login with CAPTCHA handling
      let captchaRetryCount = 0
      let lastError: Error | null = null

      while (captchaRetryCount <= maxCaptchaRetries) {
        try {
          // Attempt login with immediate MFA handling (like Python library)
          const result = await retryWithBackoff(async () => {
            return this.performLoginWithMFA(email, password, mfaSecretKey)
          })

          if (result.token) {
            // Login successful, save session
            if (saveSession) {
              this.sessionStorage.saveSession(result.token, {
                email,
                userId: result.userId,
                expiresAt: result.expiresAt,
                deviceUuid: result.deviceUuid
              })
            }
            logger.info('Login successful')
            return
          } else {
            throw new MonarchMFARequiredError('Multi-factor authentication required but no MFA secret provided')
          }

        } catch (error) {
          if (error instanceof MonarchCaptchaRequiredError) {
            captchaRetryCount++
            lastError = error
            
            if (captchaRetryCount > maxCaptchaRetries) {
              logger.error(`CAPTCHA retries exhausted after ${maxCaptchaRetries} attempts`)
              throw error
            }

            logger.warn(`CAPTCHA required (attempt ${captchaRetryCount}/${maxCaptchaRetries})`)
            
            try {
              await CaptchaHandler.handleCaptchaRequired(interactive)
              
              // Wait before retrying
              const delay = CaptchaHandler.getCaptchaRetryDelay(captchaRetryCount)
              logger.info(`Waiting ${delay}ms before retry...`)
              await new Promise(resolve => setTimeout(resolve, delay))
              
              // Continue to next attempt
              continue
              
            } catch (captchaError) {
              // User declined to handle CAPTCHA or non-interactive mode
              throw captchaError
            }
          } else {
            // Non-CAPTCHA error, throw immediately
            logger.error('Login failed', error)
            throw error
          }
        }
      }

      // If we get here, all retries failed
      throw lastError || new MonarchAuthError('Login failed after retries')

    } catch (error) {
      if (!(error instanceof MonarchCaptchaRequiredError)) {
        logger.error('Login failed', error)
      }
      throw error
    } finally {
      // Always clear the login progress flag
      this.loginInProgress = false
    }
  }

  async interactiveLogin(options: Omit<LoginOptions, 'email' | 'password'> = {}): Promise<void> {
    const {
      useSavedSession = true,
      saveSession = true,
      mfaSecretKey
    } = options

    // Try saved session first
    if (useSavedSession && this.sessionStorage.hasValidSession()) {
      logger.info('Using saved session')
      return
    }

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    })

    try {
      const email = await this.prompt(rl, 'Email: ')
      const password = await this.promptPassword(rl, 'Password: ')

      try {
        await this.login({ email, password, useSavedSession: false, saveSession, mfaSecretKey })
      } catch (error) {
        if (error instanceof MonarchMFARequiredError) {
          const mfaCode = await this.prompt(rl, 'MFA Code: ')
          await this.multiFactorAuthenticate({ email, password, code: mfaCode })
          
          if (saveSession) {
            // Session should already be saved by multiFactorAuthenticate
            logger.info('Interactive login successful with MFA')
          }
        } else {
          throw error
        }
      }
    } finally {
      rl.close()
    }
  }

  async multiFactorAuthenticate(options: MFAOptions): Promise<void> {
    const { email, password, code } = options

    validateMFACredentials(email, password, code)

    try {
      const result = await retryWithBackoff(async () => {
        return this.performMFAAuth(email, password, code)
      })

      if (result.token) {
        this.sessionStorage.saveSession(result.token, {
          email,
          userId: result.userId,
          expiresAt: result.expiresAt,
          deviceUuid: result.deviceUuid
        })
        logger.info('MFA authentication successful')
      }
    } catch (error) {
      logger.error('MFA authentication failed', error)
      throw error
    }
  }

  async validateSession(): Promise<boolean> {
    const token = this.sessionStorage.getToken()
    if (!token) {
      logger.debug('No session token found')
      return false
    }

    try {
      // Apply rate limiting before request
      await this.rateLimit()
      
      // Make a lightweight API call to validate session
      const response = await fetch(`${this.baseUrl}/graphql`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
          'User-Agent': this.getUserAgent(),
          'Origin': 'https://app.monarchmoney.com'
        },
        body: JSON.stringify({
          query: 'query { me { id email } }'
        })
      })

      if (response.status === 401 || response.status === 403) {
        logger.debug('Session validation failed - unauthorized')
        this.sessionStorage.deleteSession()
        return false
      }

      handleHTTPResponse(response)
      
      const data = await response.json() as any
      
      if (data.errors) {
        logger.debug('Session validation failed - GraphQL errors')
        return false
      }

      // Update last validated timestamp
      this.sessionStorage.updateLastValidated()
      logger.debug('Session validation successful')
      return true

    } catch (error) {
      logger.warn('Session validation failed', error)
      return false
    }
  }

  isSessionStale(): boolean {
    const sessionInfo = this.sessionStorage.getSessionInfo()
    return sessionInfo.isStale
  }

  async ensureValidSession(): Promise<void> {
    if (!this.sessionStorage.hasValidSession()) {
      throw new MonarchSessionExpiredError('No valid session available')
    }

    if (this.isSessionStale()) {
      const isValid = await this.validateSession()
      if (!isValid) {
        throw new MonarchSessionExpiredError('Session validation failed')
      }
    }
  }

  getSessionInfo(): SessionInfo {
    return this.sessionStorage.getSessionInfo()
  }

  getToken(): string | null {
    return this.sessionStorage.getToken()
  }

  getDeviceUuid(): string | null {
    return this.sessionStorage.getDeviceUuid()
  }

  saveSession(): void {
    const token = this.sessionStorage.getToken()
    if (!token) {
      throw new MonarchAuthError('No active session to save')
    }
    logger.info('Session already saved')
  }

  loadSession(): boolean {
    return this.sessionStorage.hasValidSession()
  }

  deleteSession(): void {
    this.sessionStorage.deleteSession()
    logger.info('Session deleted')
  }

  // Rate limiting helper method
  private async rateLimit(): Promise<void> {
    const now = Date.now()
    const timeSinceLastRequest = now - this.lastRequestTime
    
    if (timeSinceLastRequest < this.minRequestInterval) {
      const sleepTime = this.minRequestInterval - timeSinceLastRequest
      await new Promise(resolve => setTimeout(resolve, sleepTime))
    }
    
    this.lastRequestTime = Date.now()
  }

  // New method that sends MFA code in FIRST request like Python library
  private async performLoginWithMFA(email: string, password: string, mfaSecretKey?: string): Promise<{
    token?: string
    userId?: string
    expiresAt?: number
    deviceUuid?: string
  }> {
    // Generate fresh UUID for each request like Python library
    const deviceUuid = EncryptionService.generateDeviceUUID()

    // Prepare login data
    const loginData: Record<string, any> = {
      username: email,
      password,
      trusted_device: true,
      supports_mfa: true,
      supports_email_otp: true,
      supports_recaptcha: true
    }

    // CRITICAL: Add MFA code to FIRST request like Python library
    if (mfaSecretKey) {
      const code = totp.authenticator.generate(mfaSecretKey)
      logger.debug('Adding MFA code to initial login request like Python')

      // Use totp field for TOTP codes (like DirectAuthenticationService)
      loginData.totp = code
    }

    // Apply rate limiting before request
    await this.rateLimit()

    // Single request with MFA code (like Python library)
    const response = await fetch(`${this.baseUrl}/auth/login/`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Client-Platform': 'web',
        'Content-Type': 'application/json',
        'User-Agent': this.getUserAgent(),
        'device-uuid': deviceUuid,
        'Origin': 'https://app.monarchmoney.com',
        'x-cio-client-platform': 'web',
        'x-cio-site-id': '2598be4aa410159198b2',
        'x-gist-user-anonymous': 'false'
      },
      body: JSON.stringify(loginData)
    })

    // Debug: Log full request details
    logger.debug('Request details:', {
      url: `${this.baseUrl}/auth/login/`,
      headers: Object.fromEntries(Object.entries({
        'Accept': 'application/json',
        'Client-Platform': 'web',
        'Content-Type': 'application/json',
        'User-Agent': this.getUserAgent(),
        'device-uuid': deviceUuid,
        'Origin': 'https://app.monarchmoney.com',
        'x-cio-client-platform': 'web',
        'x-cio-site-id': '2598be4aa410159198b2',
        'x-gist-user-anonymous': 'false'
      })),
      body: loginData
    })
    logger.debug(`Authentication response status: ${response.status} ${response.statusText}`)
    
    // Get response text once to avoid consuming the stream multiple times
    const responseText = await response.text()
    let data: any
    
    try {
      data = JSON.parse(responseText)
    } catch (e) {
      // If we can't parse the response as JSON, handle as generic HTTP error
      logger.error('Failed to parse login response as JSON:', responseText)
      handleHTTPResponse(response)
      return { token: undefined }
    }

    // Check for specific error responses first
    if (response.status >= 400) {
      // Handle specific error responses
      if (data.error_code === 'CAPTCHA_REQUIRED' || data.detail?.includes('CAPTCHA')) {
        throw new MonarchCaptchaRequiredError(
          'CAPTCHA verification required. Please log in through the web interface first to clear this requirement.'
        )
      }

      // Handle "Shall Not Pass" IP blocking
      if (data.You === 'Shall Not Pass' || data.detail?.includes('Shall Not Pass') || 
          response.headers.get('you') === 'Shall Not Pass') {
        throw new MonarchIPBlockedError(
          'Your IP address has been temporarily blocked. Please wait some time before trying again, or try from a different network/IP address.'
        )
      }

      // Handle 403 MFA requirement (only if no MFA secret was provided)
      if (response.status === 403 && !mfaSecretKey) {
        throw new MonarchMFARequiredError('Multi-factor authentication required')
      }

      // Fall back to generic HTTP error handling
      handleHTTPResponse(response)
    }
    
    // Success case - parse the data as login response
    const loginResponse = data as {
      token?: string
      id?: string
      user?: { id: string }
      expires_at?: string
    }

    if (!loginResponse.token) {
      throw new MonarchAuthError('Login failed - no token received')
    }

    return {
      token: loginResponse.token,
      userId: loginResponse.id || loginResponse.user?.id,
      expiresAt: loginResponse.expires_at ? new Date(loginResponse.expires_at).getTime() : undefined,
      deviceUuid
    }
  }



  private async performMFAAuth(email: string, password: string, code: string): Promise<{
    token: string
    userId?: string
    expiresAt?: number
    deviceUuid?: string
  }> {
    const deviceUuid = this.sessionStorage.getDeviceUuid() || EncryptionService.generateDeviceUUID()
    
    // Apply rate limiting before request
    await this.rateLimit()

    const response = await fetch(`${this.baseUrl}/auth/login/`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Client-Platform': 'web', // Fixed: match Python case exactly
        'Content-Type': 'application/json',
        'User-Agent': this.getUserAgent(),
        'device-uuid': deviceUuid,
        'Origin': 'https://app.monarchmoney.com',
        'x-cio-client-platform': 'web',
        'x-cio-site-id': '2598be4aa410159198b2',
        'x-gist-user-anonymous': 'false'
      },
      body: JSON.stringify({
        username: email,
        password,
        trusted_device: true,
        supports_mfa: true,
        supports_email_otp: true,
        supports_recaptcha: true,
        totp: code
      })
    })

    // Get response text once to avoid consuming the stream multiple times
    const responseText = await response.text()
    let data: any
    
    try {
      data = JSON.parse(responseText)
    } catch (e) {
      // If we can't parse the response as JSON, handle as generic HTTP error
      logger.error('Failed to parse MFA response as JSON:', responseText)
      handleHTTPResponse(response)
      throw new MonarchAuthError('MFA authentication failed')
    }

    // Check for specific error responses first
    if (response.status >= 400) {
      // Handle CAPTCHA requirement specifically
      if (data.error_code === 'CAPTCHA_REQUIRED' || data.detail?.includes('CAPTCHA')) {
        throw new MonarchCaptchaRequiredError(
          'CAPTCHA verification required. Please log in through the web interface first to clear this requirement.'
        )
      }

      // Handle "Shall Not Pass" IP blocking
      if (data.You === 'Shall Not Pass' || data.detail?.includes('Shall Not Pass') || 
          response.headers.get('you') === 'Shall Not Pass') {
        throw new MonarchIPBlockedError(
          'Your IP address has been temporarily blocked. Please wait some time before trying again, or try from a different network/IP address.'
        )
      }

      // Handle 403 MFA requirement
      if (response.status === 403) {
        throw new MonarchMFARequiredError('Multi-factor authentication required or invalid MFA code')
      }

      // Fall back to generic HTTP error handling
      handleHTTPResponse(response)
    }
    
    // Success case - parse the data as MFA response
    const mfaResponse = data as {
      token?: string
      id?: string
      user?: { id: string }
      expires_at?: string
    }

    if (!mfaResponse.token) {
      throw new MonarchAuthError('MFA authentication failed - no token received')
    }

    return {
      token: mfaResponse.token,
      userId: mfaResponse.id || mfaResponse.user?.id,
      expiresAt: mfaResponse.expires_at ? new Date(mfaResponse.expires_at).getTime() : undefined,
      deviceUuid
    }
  }

  private getUserAgent(): string {
    return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
  }

  private prompt(rl: readline.Interface, question: string): Promise<string> {
    return new Promise(resolve => {
      rl.question(question, resolve)
    })
  }

  private promptPassword(_rl: readline.Interface, question: string): Promise<string> {
    return new Promise(resolve => {
      process.stdout.write(question)
      
      // Hide input
      const stdin = process.stdin
      stdin.setRawMode(true)
      stdin.resume()
      stdin.setEncoding('utf8')
      
      let password = ''
      
      const onData = (char: string) => {
        if (char === '\n' || char === '\r' || char === '\u0004') {
          // Enter or Ctrl+D
          stdin.setRawMode(false)
          stdin.pause()
          stdin.removeListener('data', onData)
          console.log()
          resolve(password)
        } else if (char === '\u0003') {
          // Ctrl+C
          stdin.setRawMode(false)
          stdin.pause()
          process.exit(1)
        } else if (char === '\u007f' || char === '\b') {
          // Backspace
          if (password.length > 0) {
            password = password.slice(0, -1)
            process.stdout.write('\b \b')
          }
        } else {
          password += char
          process.stdout.write('*')
        }
      }
      
      stdin.on('data', onData)
    })
  }
}