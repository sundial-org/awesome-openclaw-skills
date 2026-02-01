/**
 * MoltCheck Skill
 * Security scanner for Moltbot skills
 * 
 * Usage:
 *   scan <github_url>  - Scan a repository for security issues
 *   credits            - Check your credit balance
 *   setup              - Generate API key and payment instructions
 */

const BASE_URL = 'https://moltcheck.com/api/v1'

// Get API key from environment or config
function getApiKey() {
  return process.env.MOLTCHECK_API_KEY || null
}

// Format risk severity with emoji
function severityEmoji(severity) {
  const map = {
    critical: '🔴',
    high: '🟠',
    medium: '🟡',
    low: '🔵'
  }
  return map[severity] || '⚪'
}

// Format grade with emoji
function gradeEmoji(grade) {
  const map = {
    A: '✅',
    B: '👍',
    C: '⚠️',
    D: '⚠️',
    F: '🚨'
  }
  return map[grade] || '❓'
}

/**
 * Scan a GitHub repository
 */
async function scan(url) {
  if (!url || !url.includes('github.com')) {
    return { error: 'Please provide a valid GitHub URL' }
  }

  const headers = { 'Content-Type': 'application/json' }
  const apiKey = getApiKey()
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`
  }

  try {
    const res = await fetch(`${BASE_URL}/scan`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ url })
    })

    const data = await res.json()

    if (!res.ok) {
      if (res.status === 429) {
        return { 
          error: 'Daily scan limit reached (3/day). Get an API key for more scans.',
          setup: 'Run "setup" command to get an API key'
        }
      }
      if (res.status === 402) {
        return {
          error: 'No credits remaining.',
          buyUrl: 'https://moltcheck.com/buy'
        }
      }
      return { error: data.error || 'Scan failed' }
    }

    // Format the response
    const result = {
      url: data.url,
      score: data.score,
      grade: `${gradeEmoji(data.grade)} ${data.grade}`,
      type: data.isSkill ? '🦞 Moltbot Skill' : '📦 General Repo',
      summary: data.summary,
      reportUrl: data.reportUrl
    }

    if (data.risks && data.risks.length > 0) {
      result.risks = data.risks.map(r => ({
        level: `${severityEmoji(r.severity)} ${r.severity.toUpperCase()}`,
        issue: r.description,
        file: r.location
      }))
    }

    if (data.isSkill) {
      const undeclared = data.permissions.filter(p => !data.declaredPermissions.includes(p))
      if (undeclared.length > 0) {
        result.undeclaredPermissions = undeclared
      }
    }

    if (data.creditsRemaining !== undefined) {
      result.creditsRemaining = data.creditsRemaining
    }

    return result
  } catch (e) {
    return { error: `Network error: ${e.message}` }
  }
}

/**
 * Check credit balance
 */
async function credits() {
  const apiKey = getApiKey()
  
  if (!apiKey) {
    return {
      tier: 'Free (3 scans/day)',
      note: 'Run "setup" to get an API key for unlimited scans'
    }
  }

  try {
    const res = await fetch(`${BASE_URL}/credits`, {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    })

    if (!res.ok) {
      return { error: 'Invalid API key' }
    }

    const data = await res.json()
    return {
      credits: data.credits,
      pricePerScan: data.pricing.perScan,
      buyMore: 'https://moltcheck.com/buy'
    }
  } catch (e) {
    return { error: `Network error: ${e.message}` }
  }
}

/**
 * Generate API key and get payment instructions
 */
async function setup() {
  try {
    const res = await fetch(`${BASE_URL}/credits`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })

    const data = await res.json()

    return {
      apiKey: data.apiKey,
      instructions: [
        '1. Save your API key (set as MOLTCHECK_API_KEY)',
        '2. Send SOL to add credits:',
        `   Wallet: ${data.payment.wallet}`,
        `   Memo: ${data.keyId} (REQUIRED!)`,
        '3. Credits are added automatically',
        '',
        `Pricing: ${data.payment.pricing.perScan} per scan`
      ].join('\n'),
      usage: `MOLTCHECK_API_KEY=${data.apiKey}`
    }
  } catch (e) {
    return { error: `Network error: ${e.message}` }
  }
}

// Export for use as a module
module.exports = { scan, credits, setup }

// CLI support
if (require.main === module) {
  const [,, command, ...args] = process.argv
  
  const run = async () => {
    let result
    switch (command) {
      case 'scan':
        result = await scan(args[0])
        break
      case 'credits':
        result = await credits()
        break
      case 'setup':
        result = await setup()
        break
      default:
        result = {
          commands: {
            'scan <url>': 'Scan a GitHub repository',
            'credits': 'Check your balance',
            'setup': 'Get an API key'
          }
        }
    }
    console.log(JSON.stringify(result, null, 2))
  }
  
  run()
}
