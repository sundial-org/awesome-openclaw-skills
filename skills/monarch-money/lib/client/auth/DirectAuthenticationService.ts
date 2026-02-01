import * as totp from 'otplib'
import fetch from 'node-fetch'
import { SessionStorage } from './SessionStorage'
// import { CaptchaAvoidanceService } from './CaptchaAvoidanceService'
import { logger, MonarchAuthError, EncryptionService } from '../../utils'
import { SessionInfo } from '../../types'

export interface DirectLoginOptions {
  email: string
  password: string
  mfaSecretKey: string
  saveSession?: boolean
}

/**
 * Direct authentication service that exactly replicates the working raw approach
 * This bypasses all the complex retry/error handling to ensure authentication works
 */
export class DirectAuthenticationService {
  private baseUrl: string
  private sessionStorage: SessionStorage

  constructor(
    baseUrl: string = 'https://api.monarchmoney.com',
    sessionStorage?: SessionStorage
  ) {
    this.baseUrl = baseUrl
    this.sessionStorage = sessionStorage || new SessionStorage()
  }

  /**
   * Direct login that exactly matches our working test
   */
  async login(options: DirectLoginOptions): Promise<void> {
    const { email, password, mfaSecretKey, saveSession = true } = options

    // Generate device UUID
    const deviceUuid = EncryptionService.generateDeviceUUID()
    
    // Generate TOTP code
    const mfaCode = totp.authenticator.generate(mfaSecretKey)
    logger.debug('Generated TOTP code for direct login')

    // Prepare login data (exactly as working test)
    const loginData = {
      username: email,
      password,
      trusted_device: true,
      supports_mfa: true,
      supports_email_otp: true,
      supports_recaptcha: true,
      totp: mfaCode
    }

    // Prepare headers (exactly as working test)
    const headers = {
      'Accept': 'application/json',
      'Client-Platform': 'web',
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'device-uuid': deviceUuid,
      'Origin': 'https://app.monarchmoney.com',
      'x-cio-client-platform': 'web',
      'x-cio-site-id': '2598be4aa410159198b2',
      'x-gist-user-anonymous': 'false'
    }

    logger.debug('Making direct authentication request...')

    try {
      const response = await fetch(`${this.baseUrl}/auth/login/`, {
        method: 'POST',
        headers,
        body: JSON.stringify(loginData)
      })

      logger.debug(`Direct auth response: ${response.status} ${response.statusText}`)

      if (response.status === 200) {
        const data = await response.json() as any
        logger.debug('Direct authentication successful')

        if (!data.token) {
          throw new MonarchAuthError('Login successful but no token received')
        }

        // Save session
        if (saveSession) {
          this.sessionStorage.saveSession(data.token, {
            email,
            userId: data.id,
            expiresAt: data.expires_at ? new Date(data.expires_at).getTime() : undefined,
            deviceUuid
          })
        }

        logger.info('Direct login successful')
        return

      } else {
        // Handle error response
        const errorText = await response.text()
        logger.error(`Direct auth failed: ${response.status} ${response.statusText}`)
        logger.error('Error response:', errorText)

        let errorData: any
        try {
          errorData = JSON.parse(errorText)
        } catch (e) {
          throw new MonarchAuthError(`Authentication failed: ${response.status} ${response.statusText}`)
        }

        // Handle specific errors
        if (errorData.You === 'Shall Not Pass') {
          throw new MonarchAuthError('IP address temporarily blocked. Please wait or try from different network.')
        }

        if (errorData.error_code === 'CAPTCHA_REQUIRED') {
          throw new MonarchAuthError('CAPTCHA required. Please login via web browser first.')
        }

        throw new MonarchAuthError(`Authentication failed: ${errorData.detail || response.statusText}`)
      }

    } catch (error) {
      if (error instanceof MonarchAuthError) {
        throw error
      }
      logger.error('Direct authentication network error:', error)
      throw new MonarchAuthError(`Network error during authentication: ${(error as Error).message}`)
    }
  }

  getSessionInfo(): SessionInfo {
    return this.sessionStorage.getSessionInfo()
  }

  getToken(): string | null {
    return this.sessionStorage.getToken()
  }

  hasValidSession(): boolean {
    return this.sessionStorage.hasValidSession()
  }

  deleteSession(): void {
    this.sessionStorage.deleteSession()
  }
}