const axios = require('axios');

const BASE_URL = 'https://api.mintgarden.io';

class MintGardenAPI {
  constructor(baseURL = BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Clawdbot-MintGarden-Skill/1.0'
      }
    });
  }

  // === SEARCH ===
  
  async search(query, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { query, limit };
    if (cursor) params.page = cursor;
    return this._get('/search', params);
  }

  async searchNFTs(query, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { query, limit };
    if (cursor) params.page = cursor;
    return this._get('/search/nfts', params);
  }

  async searchCollections(query, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { query, limit };
    if (cursor) params.page = cursor;
    return this._get('/search/collections', params);
  }

  async searchProfiles(query, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { query, limit };
    if (cursor) params.page = cursor;
    return this._get('/search/profiles', params);
  }

  async searchAddresses(query, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { query, limit };
    if (cursor) params.page = cursor;
    return this._get('/search/addresses', params);
  }

  // === COLLECTIONS ===
  
  async getCollections(options = {}) {
    const { 
      sort = null, 
      cursor = null, 
      limit = 50,
      verified = null 
    } = options;
    const params = { limit };
    if (sort) params.sort = sort;
    if (cursor) params.page = cursor;
    if (verified !== null) params.verified = verified;
    return this._get('/collections', params);
  }

  async getCollection(collectionId) {
    return this._get(`/collections/${collectionId}`);
  }

  async getCollectionMetadata(collectionId) {
    return this._get(`/collections/${collectionId}/metadata`);
  }

  async getCollectionNFTs(collectionId, options = {}) {
    const { cursor = null, limit = 50, sort = null } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    if (sort) params.sort = sort;
    return this._get(`/collections/${collectionId}/nfts`, params);
  }

  async getCollectionOwners(collectionId, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get(`/collections/${collectionId}/owners`, params);
  }

  async getCollectionAuctions(collectionId, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get(`/collections/${collectionId}/auctions`, params);
  }

  // === NFTs ===
  
  async getNFT(launcherId) {
    return this._get(`/nfts/${launcherId}`);
  }

  async getNFTMetadata(launcherId) {
    return this._get(`/nfts/${launcherId}/metadata`);
  }

  async getNFTLicense(launcherId) {
    return this._get(`/nfts/${launcherId}/license`);
  }

  async getNFTEvent(nftId, eventIndex) {
    return this._get(`/nfts/${nftId}/events/${eventIndex}`);
  }

  // === PROFILES ===
  
  async getProfile(identifier) {
    // identifier can be username or ID
    return this._get(`/profile/${identifier}`);
  }

  async getProfileNFTs(idHex, options = {}) {
    const { cursor = null, limit = 50, type = 'owned', collection_id = null } = options;
    const params = { limit, type };
    if (cursor) params.page = cursor;
    if (collection_id) params.collection_id = collection_id;
    return this._get(`/profile/${idHex}/nfts`, params);
  }

  async getProfileCollections(idHex, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get(`/profile/${idHex}/collections`, params);
  }

  // === EVENTS ===
  
  async getEvents(options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get('/events', params);
  }

  // === AUCTIONS ===
  
  async getAuctions(options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get('/auctions', params);
  }

  // === MINTS (OFFERS) ===
  
  async getMint(mintId) {
    return this._get(`/mints/${mintId}`);
  }

  async getMintOffers(mintId, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get(`/mints/${mintId}/offers`, params);
  }

  // === GARDENS ===
  
  async getGarden(slug) {
    return this._get(`/gardens/${slug}`);
  }

  async getGardenCollections(slug, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get(`/gardens/${slug}/collections`, params);
  }

  async getGardenEvents(slug, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get(`/gardens/${slug}/events`, params);
  }

  async getGardenProfiles(slug, options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get(`/gardens/${slug}/profiles`, params);
  }

  // === TOKENS ===
  
  async getTokens(options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get('/tokens', params);
  }

  async getToken(tokenId) {
    return this._get(`/tokens/${tokenId}`);
  }

  // === ADDRESS ===
  
  async getAddress(idHex) {
    return this._get(`/address/${idHex}`);
  }

  async getAddressNFTs(idHex, options = {}) {
    const { cursor = null, limit = 50, type = 'owned', collection_id = null } = options;
    const params = { limit, type };
    if (cursor) params.page = cursor;
    if (collection_id) params.collection_id = collection_id;
    return this._get(`/address/${idHex}/nfts`, params);
  }

  // === SUPPORTERS ===
  
  async getSupporters(options = {}) {
    const { cursor = null, limit = 50 } = options;
    const params = { limit };
    if (cursor) params.page = cursor;
    return this._get('/supporters', params);
  }

  // === INTERNAL ===
  
  async _get(path, params = {}) {
    try {
      const response = await this.client.get(path, { params });
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(`MintGarden API error: ${error.response.status} - ${error.response.data?.message || error.response.statusText}`);
      } else if (error.request) {
        throw new Error('MintGarden API request failed: No response received');
      } else {
        throw new Error(`MintGarden API error: ${error.message}`);
      }
    }
  }

  // Pagination helper (cursor-based)
  async *paginate(method, ...args) {
    let cursor = null;
    const limit = 50;
    
    while (true) {
      const options = args[args.length - 1] || {};
      options.cursor = cursor;
      options.limit = limit;
      
      const result = await method.call(this, ...args.slice(0, -1), options);
      
      if (!result || !result.items || result.items.length === 0) {
        break;
      }
      
      yield result.items;
      
      // Get next cursor from response
      if (!result.next) {
        break;
      }
      
      cursor = result.next;
    }
  }
}

module.exports = MintGardenAPI;
