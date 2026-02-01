const axios = require('axios');

const BASE_URL = 'https://api.spacescan.io';

class SpacescanAPI {
  constructor(apiKey = null, baseURL = BASE_URL) {
    this.apiKey = apiKey || process.env.SPACESCAN_API_KEY;
    
    if (!this.apiKey) {
      console.warn('⚠️  No Spacescan API key found. Set SPACESCAN_API_KEY environment variable.');
    }
    
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Clawdbot-Spacescan-Skill/1.0'
      }
    });
    
    // Add API key to requests if available
    if (this.apiKey) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${this.apiKey}`;
    }
  }

  // === BLOCKCHAIN ===
  
  async getLatestBlock() {
    return this._get('/block/latest');
  }

  async getBlock(heightOrHash) {
    return this._get(`/block/${heightOrHash}`);
  }

  async getBlockRange(start, end) {
    return this._get('/blocks', { start, end });
  }

  // === TRANSACTIONS ===
  
  async getTransaction(txId) {
    return this._get(`/tx/${txId}`);
  }

  async getTransactionsByBlock(height) {
    return this._get(`/block/${height}/txs`);
  }

  // === ADDRESSES ===
  
  async getAddress(address) {
    return this._get(`/address/${address}`);
  }

  async getAddressBalance(address) {
    return this._get(`/address/${address}/balance`);
  }

  async getAddressTransactions(address, options = {}) {
    const { page = 1, limit = 50 } = options;
    return this._get(`/address/${address}/txs`, { page, limit });
  }

  async getAddressCoins(address, options = {}) {
    const { page = 1, limit = 50 } = options;
    return this._get(`/address/${address}/coins`, { page, limit });
  }

  // === COINS ===
  
  async getCoin(coinId) {
    return this._get(`/coin/${coinId}`);
  }

  async getCoinChildren(coinId) {
    return this._get(`/coin/${coinId}/children`);
  }

  // === PUZZLEHASH ===
  
  async getPuzzlehash(puzzlehash) {
    return this._get(`/puzzlehash/${puzzlehash}`);
  }

  async getPuzzlehashBalance(puzzlehash) {
    return this._get(`/puzzlehash/${puzzlehash}/balance`);
  }

  // === NETWORK STATS ===
  
  async getNetworkStats() {
    return this._get('/stats');
  }

  async getNetworkInfo() {
    return this._get('/network/info');
  }

  async getNetworkSpace() {
    return this._get('/network/space');
  }

  async getBlockchainState() {
    return this._get('/blockchain/state');
  }

  // === MEMPOOL ===
  
  async getMempool() {
    return this._get('/mempool');
  }

  async getMempoolTransaction(txId) {
    return this._get(`/mempool/${txId}`);
  }

  // === CATS (Chia Asset Tokens) ===
  
  async getCAT(assetId) {
    return this._get(`/cat/${assetId}`);
  }

  async getCATList(options = {}) {
    const { page = 1, limit = 50 } = options;
    return this._get('/cats', { page, limit });
  }

  // === NFTS ===
  
  async getNFT(nftId) {
    return this._get(`/nft/${nftId}`);
  }

  async getNFTCollection(collectionId) {
    return this._get(`/nft/collection/${collectionId}`);
  }

  // === SEARCH ===
  
  async search(query) {
    return this._get('/search', { q: query });
  }

  // === PRICE ===
  
  async getXCHPrice() {
    return this._get('/coin/xch/price');
  }

  // === INTERNAL ===
  
  async _get(path, params = {}) {
    if (!this.apiKey) {
      throw new Error(
        'Spacescan API key required. Set SPACESCAN_API_KEY environment variable.\n' +
        'Get your key at: https://www.spacescan.io/apis'
      );
    }
    
    try {
      const response = await this.client.get(path, { params });
      return response.data;
    } catch (error) {
      if (error.response) {
        const msg = error.response.data?.message || error.response.statusText;
        
        if (error.response.status === 429) {
          throw new Error('Rate limit exceeded. Upgrade your Spacescan API plan at https://www.spacescan.io/apis');
        }
        
        if (error.response.status === 401 || error.response.status === 403) {
          throw new Error('Invalid API key. Check your SPACESCAN_API_KEY at https://www.spacescan.io/apis');
        }
        
        throw new Error(`Spacescan API error: ${error.response.status} - ${msg}`);
      } else if (error.request) {
        throw new Error('Spacescan API request failed: No response received');
      } else {
        throw new Error(`Spacescan API error: ${error.message}`);
      }
    }
  }

  // Check if API key is configured
  hasApiKey() {
    return !!this.apiKey;
  }
}

module.exports = SpacescanAPI;
