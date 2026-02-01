/**
 * AAP Whitelist & Key Management
 * 
 * Optional: Maintain list of trusted agent public IDs
 */

/**
 * Create a whitelist manager
 * @param {Object} options
 * @param {boolean} [options.enabled=false] - Enable whitelist enforcement
 * @param {string[]} [options.allowedIds=[]] - Pre-approved public IDs
 * @param {Function} [options.onNewAgent] - Callback when new agent attempts verification
 */
export function createWhitelist(options = {}) {
  const {
    enabled = false,
    allowedIds = [],
    onNewAgent = null
  } = options;

  const whitelist = new Set(allowedIds);
  const pendingApproval = new Map();  // publicId -> { firstSeen, attempts }

  return {
    /**
     * Check if agent is allowed
     * @param {string} publicId
     * @returns {boolean}
     */
    isAllowed(publicId) {
      if (!enabled) return true;
      return whitelist.has(publicId);
    },

    /**
     * Add agent to whitelist
     * @param {string} publicId
     */
    add(publicId) {
      whitelist.add(publicId);
      pendingApproval.delete(publicId);
    },

    /**
     * Remove agent from whitelist
     * @param {string} publicId
     */
    remove(publicId) {
      whitelist.delete(publicId);
    },

    /**
     * Get all whitelisted IDs
     * @returns {string[]}
     */
    list() {
      return [...whitelist];
    },

    /**
     * Record attempt from unknown agent
     * @param {string} publicId
     * @param {Object} details
     */
    recordAttempt(publicId, details = {}) {
      if (!enabled) return;
      
      let record = pendingApproval.get(publicId);
      if (!record) {
        record = { firstSeen: Date.now(), attempts: 0, lastDetails: null };
        pendingApproval.set(publicId, record);
        
        if (onNewAgent) {
          onNewAgent(publicId, details);
        }
      }
      
      record.attempts++;
      record.lastDetails = details;
    },

    /**
     * Get pending approvals
     * @returns {Object[]}
     */
    getPending() {
      return [...pendingApproval.entries()].map(([id, data]) => ({
        publicId: id,
        ...data
      }));
    },

    /**
     * Middleware to enforce whitelist
     */
    middleware() {
      return (req, res, next) => {
        if (!enabled) return next();
        
        const publicId = req.body?.publicId;
        if (!publicId) return next();  // Will fail later anyway
        
        if (!whitelist.has(publicId)) {
          this.recordAttempt(publicId, {
            ip: req.ip,
            timestamp: Date.now()
          });
          
          return res.status(403).json({
            verified: false,
            error: 'Agent not in whitelist',
            publicId
          });
        }
        
        next();
      };
    },

    /**
     * Check if whitelist is enabled
     */
    isEnabled() {
      return enabled;
    },

    /**
     * Get stats
     */
    stats() {
      return {
        enabled,
        whitelistedCount: whitelist.size,
        pendingCount: pendingApproval.size
      };
    }
  };
}

/**
 * Key rotation helper for agents
 * 
 * Tracks key history and provides rotation utilities
 */
export function createKeyRotation(options = {}) {
  const {
    maxKeyAge = 30 * 24 * 60 * 60 * 1000,  // 30 days default
    onRotationNeeded = null
  } = options;

  const keyHistory = new Map();  // publicId -> { keys: [], currentIndex }

  return {
    /**
     * Register a key
     * @param {string} publicId
     * @param {string} publicKey
     * @param {number} [createdAt]
     */
    registerKey(publicId, publicKey, createdAt = Date.now()) {
      let history = keyHistory.get(publicId);
      if (!history) {
        history = { keys: [], currentIndex: 0 };
        keyHistory.set(publicId, history);
      }

      history.keys.push({
        publicKey,
        createdAt,
        revokedAt: null
      });
      history.currentIndex = history.keys.length - 1;
    },

    /**
     * Get current key for agent
     * @param {string} publicId
     * @returns {string|null}
     */
    getCurrentKey(publicId) {
      const history = keyHistory.get(publicId);
      if (!history) return null;
      return history.keys[history.currentIndex]?.publicKey || null;
    },

    /**
     * Check if key needs rotation
     * @param {string} publicId
     * @returns {boolean}
     */
    needsRotation(publicId) {
      const history = keyHistory.get(publicId);
      if (!history || !history.keys.length) return false;
      
      const currentKey = history.keys[history.currentIndex];
      const age = Date.now() - currentKey.createdAt;
      
      if (age > maxKeyAge) {
        if (onRotationNeeded) {
          onRotationNeeded(publicId, age);
        }
        return true;
      }
      
      return false;
    },

    /**
     * Revoke old key
     * @param {string} publicId
     * @param {number} keyIndex
     */
    revokeKey(publicId, keyIndex) {
      const history = keyHistory.get(publicId);
      if (!history || !history.keys[keyIndex]) return;
      
      history.keys[keyIndex].revokedAt = Date.now();
    },

    /**
     * Get key history for agent
     * @param {string} publicId
     * @returns {Object[]}
     */
    getHistory(publicId) {
      return keyHistory.get(publicId)?.keys || [];
    }
  };
}

export default { createWhitelist, createKeyRotation };
