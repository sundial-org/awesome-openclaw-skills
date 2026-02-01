/**
 * AAP Server - Logging Utilities
 * 
 * Safe logging that never exposes sensitive data
 */

const LOG_LEVELS = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3
};

let currentLevel = LOG_LEVELS.info;

/**
 * Set the minimum log level
 * @param {'debug'|'info'|'warn'|'error'} level
 */
export function setLogLevel(level) {
  currentLevel = LOG_LEVELS[level] ?? LOG_LEVELS.info;
}

/**
 * Sanitize data for safe logging
 * Removes sensitive fields
 */
function sanitize(data) {
  if (!data || typeof data !== 'object') return data;
  
  const sensitive = ['privateKey', 'private_key', 'apiKey', 'api_key', 'secret', 'password', 'token'];
  const sanitized = { ...data };
  
  for (const key of sensitive) {
    if (key in sanitized) {
      sanitized[key] = '[REDACTED]';
    }
  }
  
  // Truncate long values
  if (sanitized.publicKey && sanitized.publicKey.length > 50) {
    sanitized.publicKey = sanitized.publicKey.slice(0, 50) + '...';
  }
  if (sanitized.signature && sanitized.signature.length > 50) {
    sanitized.signature = sanitized.signature.slice(0, 50) + '...';
  }
  
  return sanitized;
}

/**
 * Format log message
 */
function format(level, message, data) {
  const timestamp = new Date().toISOString();
  const prefix = `[AAP ${level.toUpperCase()}] ${timestamp}`;
  
  if (data) {
    return `${prefix} ${message} ${JSON.stringify(sanitize(data))}`;
  }
  return `${prefix} ${message}`;
}

/**
 * Log debug message
 */
export function debug(message, data) {
  if (currentLevel <= LOG_LEVELS.debug) {
    console.debug(format('debug', message, data));
  }
}

/**
 * Log info message
 */
export function info(message, data) {
  if (currentLevel <= LOG_LEVELS.info) {
    console.info(format('info', message, data));
  }
}

/**
 * Log warning message
 */
export function warn(message, data) {
  if (currentLevel <= LOG_LEVELS.warn) {
    console.warn(format('warn', message, data));
  }
}

/**
 * Log error message
 */
export function error(message, data) {
  if (currentLevel <= LOG_LEVELS.error) {
    console.error(format('error', message, data));
  }
}

/**
 * Log verification attempt
 */
export function logVerification(result, req) {
  const data = {
    publicId: result.publicId,
    verified: result.verified,
    responseTimeMs: result.responseTimeMs,
    batchPassed: result.batchResult?.passed,
    batchTotal: result.batchResult?.total,
    ip: req?.ip,
    userAgent: req?.headers?.['user-agent']?.slice(0, 50)
  };
  
  if (result.verified) {
    info('Verification successful', data);
  } else {
    warn('Verification failed', { ...data, error: result.error });
  }
}

/**
 * Log challenge generation
 */
export function logChallenge(nonce, batchSize) {
  debug('Challenge generated', { 
    nonce: nonce.slice(0, 8) + '...', 
    batchSize 
  });
}

export default {
  setLogLevel,
  debug,
  info,
  warn,
  error,
  logVerification,
  logChallenge
};
