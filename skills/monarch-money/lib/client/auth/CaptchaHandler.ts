import * as readline from 'readline'

export class CaptchaHandler {
  /**
   * Handle CAPTCHA requirement by guiding user to web login
   */
  static async handleCaptchaRequired(isInteractive: boolean = true): Promise<void> {
    const message = `
🚫 CAPTCHA verification is required to proceed.

MonarchMoney has temporarily blocked API access and requires web browser verification.

To resolve this:
1. Open your web browser
2. Go to: https://app.monarchmoney.com/login
3. Log in with your credentials
4. Complete any CAPTCHA challenges shown
5. Once logged in successfully, you can return to use this library

This security measure will automatically clear after successful web login.
`

    console.log(message)

    if (isInteractive) {
      return this.waitForUserConfirmation()
    } else {
      throw new Error('CAPTCHA verification required - please login via web browser first')
    }
  }

  /**
   * Wait for user to confirm they've completed web login
   */
  private static async waitForUserConfirmation(): Promise<void> {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    })

    return new Promise((resolve) => {
      const ask = () => {
        rl.question('\nHave you completed the web login? (y/n/skip): ', (answer) => {
          const response = answer.toLowerCase().trim()
          
          if (response === 'y' || response === 'yes') {
            console.log('✅ Great! Attempting to continue with API login...')
            rl.close()
            resolve()
          } else if (response === 'skip' || response === 's') {
            console.log('⏭️ Skipping CAPTCHA resolution - this may fail')
            rl.close()
            resolve()
          } else if (response === 'n' || response === 'no') {
            console.log('⏳ Waiting for web login completion...')
            setTimeout(ask, 2000)
          } else {
            console.log('Please answer with y/yes, n/no, or skip')
            ask()
          }
        })
      }
      ask()
    })
  }

  /**
   * Check if we should retry after CAPTCHA
   */
  static shouldRetryAfterCaptcha(retryCount: number, maxRetries: number = 3): boolean {
    return retryCount < maxRetries
  }

  /**
   * Get retry delay after CAPTCHA (exponential backoff)
   */
  static getCaptchaRetryDelay(retryCount: number): number {
    return Math.min(1000 * Math.pow(2, retryCount), 10000) // Max 10 seconds
  }
}