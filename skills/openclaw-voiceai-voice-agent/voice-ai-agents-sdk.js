/**
 * Voice.ai Agents SDK
 * 
 * Create, manage, and deploy conversational AI voice agents.
 * 
 * @version 1.0.0
 * @author Nick Gill (https://github.com/gizmoGremlin)
 * @license MIT
 */

const https = require('https');
const http = require('http');

// ============================================================================
// Constants
// ============================================================================

const API_BASE_URL = 'https://dev.voice.ai';
const API_VERSION = 'v1';

const AGENT_STATUS = {
  PAUSED: 'paused',
  DEPLOYED: 'deployed',
  ERROR: 'error'
};

const LLM_MODELS = {
  GEMINI_FLASH_LITE: 'gemini-2.5-flash-lite',
  GEMINI_FLASH: 'gemini-2.5-flash',
  GEMINI_PRO: 'gemini-2.5-pro'
};

const TTS_MODELS = {
  ENGLISH_LATEST: 'voiceai-tts-v1-latest',
  ENGLISH_STABLE: 'voiceai-tts-v1-2025-12-19',
  MULTILINGUAL_LATEST: 'voiceai-tts-multilingual-v1-latest',
  MULTILINGUAL_STABLE: 'voiceai-tts-multilingual-v1-2025-01-14'
};

const LANGUAGES = ['auto', 'en', 'ca', 'sv', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'ru', 'nl'];

const MCP_AUTH_TYPES = {
  NONE: 'none',
  BEARER_TOKEN: 'bearer_token',
  API_KEY: 'api_key',
  CUSTOM_HEADERS: 'custom_headers'
};

// ============================================================================
// Error Classes
// ============================================================================

class VoiceAIAgentError extends Error {
  constructor(message, statusCode = null, response = null) {
    super(message);
    this.name = 'VoiceAIAgentError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

class AuthenticationError extends VoiceAIAgentError {
  constructor(message = 'Invalid or missing API key') {
    super(message, 401);
    this.name = 'AuthenticationError';
  }
}

class ValidationError extends VoiceAIAgentError {
  constructor(message, details = null) {
    super(message, 422);
    this.name = 'ValidationError';
    this.details = details;
  }
}

class NotFoundError extends VoiceAIAgentError {
  constructor(message = 'Resource not found') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

// ============================================================================
// VoiceAIAgents Client
// ============================================================================

class VoiceAIAgents {
  /**
   * Create a new VoiceAIAgents client
   * @param {string} apiKey - Voice.ai API key
   * @param {Object} options - Configuration options
   * @param {string} options.baseUrl - API base URL (default: https://dev.voice.ai)
   * @param {number} options.timeout - Request timeout in ms (default: 30000)
   */
  constructor(apiKey, options = {}) {
    if (!apiKey) {
      throw new AuthenticationError('API key is required');
    }
    
    this.apiKey = apiKey;
    this.baseUrl = options.baseUrl || API_BASE_URL;
    this.timeout = options.timeout || 30000;
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  /**
   * Make an HTTP request to the API
   * @private
   */
  _request(method, path, body = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(`/api/${API_VERSION}${path}`, this.baseUrl);
      const isHttps = url.protocol === 'https:';
      const httpModule = isHttps ? https : http;

      const options = {
        hostname: url.hostname,
        port: url.port || (isHttps ? 443 : 80),
        path: url.pathname + url.search,
        method: method,
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        timeout: this.timeout
      };

      const req = httpModule.request(options, (res) => {
        let data = '';
        
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const parsed = data ? JSON.parse(data) : {};
            
            if (res.statusCode >= 400) {
              const error = this._handleErrorResponse(res.statusCode, parsed);
              reject(error);
            } else {
              resolve(parsed);
            }
          } catch (e) {
            if (res.statusCode >= 400) {
              reject(new VoiceAIAgentError(`Request failed with status ${res.statusCode}`, res.statusCode));
            } else {
              resolve(data);
            }
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new VoiceAIAgentError('Request timeout'));
      });

      if (body) {
        req.write(JSON.stringify(body));
      }
      
      req.end();
    });
  }

  /**
   * Handle error responses
   * @private
   */
  _handleErrorResponse(statusCode, response) {
    const message = response.error || response.detail || 'Unknown error';
    
    switch (statusCode) {
      case 401:
        return new AuthenticationError(message);
      case 404:
        return new NotFoundError(message);
      case 422:
        return new ValidationError(message, response.detail);
      default:
        return new VoiceAIAgentError(message, statusCode, response);
    }
  }

  // ==========================================================================
  // Agent Management
  // ==========================================================================

  /**
   * Create a new agent
   * @param {Object} params - Agent parameters
   * @param {string} params.name - Agent name (required)
   * @param {Object} params.config - Agent configuration
   * @param {string} params.config.prompt - System prompt
   * @param {string} params.config.greeting - Initial greeting
   * @param {number} params.config.llm_temperature - LLM temperature (0-2)
   * @param {string} params.config.llm_model - LLM model
   * @param {Object} params.config.tts_params - TTS configuration
   * @param {Array} params.config.mcp_servers - MCP server configurations
   * @param {number} params.kb_id - Knowledge base ID (optional)
   * @returns {Promise<Object>} Created agent
   */
  async createAgent(params) {
    if (!params.name) {
      throw new ValidationError('Agent name is required');
    }
    if (!params.config) {
      throw new ValidationError('Agent config is required');
    }

    return this._request('POST', '/agent/', {
      name: params.name,
      config: params.config,
      kb_id: params.kb_id
    });
  }

  /**
   * List all agents
   * @returns {Promise<Array>} List of agents
   */
  async listAgents() {
    return this._request('GET', '/agent/');
  }

  /**
   * Get agent by ID
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Agent details
   */
  async getAgent(agentId) {
    if (!agentId) {
      throw new ValidationError('Agent ID is required');
    }
    return this._request('GET', `/agent/${agentId}`);
  }

  /**
   * Update an agent
   * @param {string} agentId - Agent ID
   * @param {Object} params - Update parameters
   * @returns {Promise<Object>} Updated agent
   */
  async updateAgent(agentId, params) {
    if (!agentId) {
      throw new ValidationError('Agent ID is required');
    }
    return this._request('PUT', `/agent/${agentId}`, params);
  }

  /**
   * Delete (disable) an agent
   * Agent must be paused before being deleted.
   * Disabled agents are automatically deleted after a grace period.
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Deletion confirmation with agent details
   */
  async deleteAgent(agentId) {
    if (!agentId) {
      throw new ValidationError('Agent ID is required');
    }
    return this._request('POST', `/agent/${agentId}/disable`);
  }

  /**
   * Deploy an agent (prepare for phone calls)
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Deployment response with SIP status
   */
  async deployAgent(agentId) {
    if (!agentId) {
      throw new ValidationError('Agent ID is required');
    }
    return this._request('POST', `/agent/${agentId}/deploy`);
  }

  /**
   * Pause an agent
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Updated agent
   */
  async pauseAgent(agentId) {
    if (!agentId) {
      throw new ValidationError('Agent ID is required');
    }
    return this._request('POST', `/agent/${agentId}/pause`);
  }

  // ==========================================================================
  // Knowledge Base
  // ==========================================================================

  /**
   * List knowledge bases
   * @returns {Promise<Array>} List of knowledge bases
   */
  async listKnowledgeBases() {
    return this._request('GET', '/knowledge-base/');
  }

  /**
   * Create a knowledge base
   * @param {Object} params - Knowledge base parameters
   * @param {string} params.name - Knowledge base name
   * @param {string} params.description - Description
   * @returns {Promise<Object>} Created knowledge base
   */
  async createKnowledgeBase(params) {
    return this._request('POST', '/knowledge-base/', params);
  }

  /**
   * Get knowledge base by ID
   * @param {number} kbId - Knowledge base ID
   * @returns {Promise<Object>} Knowledge base details
   */
  async getKnowledgeBase(kbId) {
    return this._request('GET', `/knowledge-base/${kbId}`);
  }

  /**
   * Delete a knowledge base
   * @param {number} kbId - Knowledge base ID
   * @returns {Promise<Object>} Deletion confirmation
   */
  async deleteKnowledgeBase(kbId) {
    return this._request('DELETE', `/knowledge-base/${kbId}`);
  }

  // ==========================================================================
  // Phone Number Management
  // ==========================================================================

  /**
   * List available phone numbers
   * @returns {Promise<Array>} List of phone numbers
   */
  async listPhoneNumbers() {
    return this._request('GET', '/phone-numbers/');
  }

  /**
   * Search for available phone numbers
   * @param {Object} params - Search parameters
   * @param {string} params.country - Country code
   * @param {string} params.area_code - Area code
   * @returns {Promise<Array>} Available phone numbers
   */
  async searchPhoneNumbers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this._request('GET', `/phone-numbers/search?${query}`);
  }

  /**
   * Assign a phone number to an agent
   * @param {string} phoneNumber - Phone number in E.164 format
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Assignment confirmation
   */
  async assignPhoneNumber(phoneNumber, agentId) {
    return this._request('POST', '/phone-numbers/assign', {
      phone_number: phoneNumber,
      agent_id: agentId
    });
  }

  /**
   * Release a phone number
   * @param {string} phoneNumber - Phone number to release
   * @returns {Promise<Object>} Release confirmation
   */
  async releasePhoneNumber(phoneNumber) {
    return this._request('POST', '/phone-numbers/release', {
      phone_number: phoneNumber
    });
  }

  // ==========================================================================
  // Analytics
  // ==========================================================================

  /**
   * Get call history for an agent
   * @param {string} agentId - Agent ID
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of results
   * @param {number} params.offset - Offset for pagination
   * @returns {Promise<Array>} Call history
   */
  async getCallHistory(agentId, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this._request('GET', `/agent/${agentId}/calls?${query}`);
  }

  /**
   * Get call details
   * @param {string} callId - Call ID
   * @returns {Promise<Object>} Call details
   */
  async getCall(callId) {
    return this._request('GET', `/calls/${callId}`);
  }

  /**
   * Get agent statistics
   * @param {string} agentId - Agent ID
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Agent statistics
   */
  async getAgentStats(agentId, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this._request('GET', `/agent/${agentId}/stats?${query}`);
  }

  // ==========================================================================
  // Helper Methods
  // ==========================================================================

  /**
   * Create default agent configuration
   * @param {Object} overrides - Configuration overrides
   * @returns {Object} Agent configuration
   */
  static createConfig(overrides = {}) {
    return {
      prompt: overrides.prompt || 'You are a helpful assistant.',
      greeting: overrides.greeting || 'Hello! How can I help you today?',
      llm_model: overrides.llm_model || LLM_MODELS.GEMINI_FLASH_LITE,
      llm_temperature: overrides.llm_temperature ?? 0.7,
      max_call_duration_seconds: overrides.max_call_duration_seconds ?? 900,
      allow_interruptions: overrides.allow_interruptions ?? true,
      auto_noise_reduction: overrides.auto_noise_reduction ?? true,
      tts_params: {
        voice_id: overrides.voice_id,
        language: overrides.language || 'en',
        temperature: overrides.tts_temperature ?? 1.0,
        top_p: overrides.top_p ?? 0.8,
        ...overrides.tts_params
      },
      mcp_servers: overrides.mcp_servers || [],
      ...overrides
    };
  }

  /**
   * Create MCP server configuration
   * @param {Object} params - Server parameters
   * @returns {Object} MCP server config
   */
  static createMCPServer(params) {
    return {
      name: params.name,
      description: params.description,
      url: params.url,
      auth_type: params.auth_type || MCP_AUTH_TYPES.NONE,
      auth_token: params.auth_token,
      headers: params.headers
    };
  }
}

// ============================================================================
// Exports
// ============================================================================

module.exports = VoiceAIAgents;
module.exports.VoiceAIAgents = VoiceAIAgents;
module.exports.VoiceAIAgentError = VoiceAIAgentError;
module.exports.AuthenticationError = AuthenticationError;
module.exports.ValidationError = ValidationError;
module.exports.NotFoundError = NotFoundError;

// Constants
module.exports.API_BASE_URL = API_BASE_URL;
module.exports.AGENT_STATUS = AGENT_STATUS;
module.exports.LLM_MODELS = LLM_MODELS;
module.exports.TTS_MODELS = TTS_MODELS;
module.exports.LANGUAGES = LANGUAGES;
module.exports.MCP_AUTH_TYPES = MCP_AUTH_TYPES;
