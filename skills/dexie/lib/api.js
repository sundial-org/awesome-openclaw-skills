const axios = require('axios');

const BASE_URL = 'https://api.dexie.space/v1';

class DexieAPI {
  constructor(baseURL = BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Clawdbot-Dexie-Skill/1.0'
      }
    });
  }

  // === OFFERS ===
  
  async getOffers(options = {}) {
    const {
      page = 1,
      page_size = 20,
      status = null,
      offered = null,
      requested = null,
      compact = false,
      sort = null
    } = options;
    
    const params = { page, page_size, compact };
    if (status !== null) params.status = status;
    if (offered) params.offered = offered;
    if (requested) params.requested = requested;
    if (sort) params.sort = sort;
    
    return this._get('/offers', params);
  }

  async getOffer(offerId) {
    return this._get(`/offers/${offerId}`);
  }

  // === ASSETS (TOKENS) ===
  
  async getAssets(options = {}) {
    const { page = 1, page_size = 50, sort = 'volume' } = options;
    return this._get('/assets', { page, page_size, sort });
  }

  async getAsset(assetId) {
    return this._get(`/assets/${assetId}`);
  }

  // === PAIRS ===
  
  async getPairs() {
    return this._get('/pairs');
  }

  async getPair(pairId) {
    return this._get(`/pairs/${pairId}`);
  }

  // === STATS ===
  
  async getStats() {
    return this._get('/stats');
  }

  // === CATs (Chia Asset Tokens) ===
  
  async searchCATs(query, options = {}) {
    const { page = 1, page_size = 20 } = options;
    return this._get('/cats/search', { q: query, page, page_size });
  }

  // === INTERNAL ===
  
  async _get(path, params = {}) {
    try {
      const response = await this.client.get(path, { params });
      return response.data;
    } catch (error) {
      if (error.response) {
        const msg = error.response.data?.error_message || error.response.statusText;
        throw new Error(`Dexie API error: ${error.response.status} - ${msg}`);
      } else if (error.request) {
        throw new Error('Dexie API request failed: No response received');
      } else {
        throw new Error(`Dexie API error: ${error.message}`);
      }
    }
  }

  // Pagination helper
  async *paginate(method, ...args) {
    let page = 1;
    const page_size = 50;
    
    while (true) {
      const options = args[args.length - 1] || {};
      options.page = page;
      options.page_size = page_size;
      
      const result = await method.call(this, ...args.slice(0, -1), options);
      
      if (!result || !result.success || !result.offers && !result.assets) {
        break;
      }
      
      const items = result.offers || result.assets || [];
      if (items.length === 0) {
        break;
      }
      
      yield items;
      
      if (items.length < page_size) {
        break;
      }
      
      page++;
    }
  }
}

module.exports = DexieAPI;
