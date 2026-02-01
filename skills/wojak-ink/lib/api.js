const fetch = require('node-fetch');

const COLLECTION_ID = 'col10hfq4hml2z0z0wutu3a9hvt60qy9fcq4k4dznsfncey4lu6kpt3su7u9ah';
const MINTGARDEN_API = 'https://api.mintgarden.io';
const DEXIE_API = 'https://api.dexie.space/v1';

class WojakAPI {
  constructor() {
    this.cache = {
      listings: null,
      listingsTimestamp: 0,
      nfts: null,
      nftsTimestamp: 0
    };
    this.cacheDuration = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Fetch NFT metadata from MintGarden
   */
  async fetchNFTMetadata(nftId) {
    const paddedId = String(nftId).padStart(4, '0');
    try {
      const response = await fetch(`${MINTGARDEN_API}/nfts/${COLLECTION_ID}/${paddedId}`);
      if (!response.ok) return null;
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch NFT ${nftId}:`, error.message);
      return null;
    }
  }

  /**
   * Fetch collection stats from MintGarden
   */
  async fetchCollectionStats() {
    try {
      const response = await fetch(`${MINTGARDEN_API}/collections/${COLLECTION_ID}/stats`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch collection stats:', error.message);
      return null;
    }
  }

  /**
   * Fetch marketplace listings from Dexie
   */
  async fetchListings(forceRefresh = false) {
    const now = Date.now();
    if (!forceRefresh && this.cache.listings && (now - this.cache.listingsTimestamp < this.cacheDuration)) {
      return this.cache.listings;
    }

    try {
      const response = await fetch(`${DEXIE_API}/offers?type=nft&collection=${COLLECTION_ID}&status=0&page_size=100`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      const listings = (data.offers || []).map(offer => this.parseOffer(offer)).filter(Boolean);
      
      this.cache.listings = listings;
      this.cache.listingsTimestamp = now;
      
      return listings;
    } catch (error) {
      console.error('Failed to fetch listings:', error.message);
      return this.cache.listings || [];
    }
  }

  /**
   * Parse Dexie offer into simplified format
   */
  parseOffer(offer) {
    try {
      // Find the NFT being offered
      const nftOffered = offer.offered?.find(item => item.type === 'nft' || item.asset_id === COLLECTION_ID);
      if (!nftOffered) return null;

      // Extract NFT ID from name (e.g., "Wojak #0001" -> 1)
      const match = nftOffered.name?.match(/#(\d+)/);
      if (!match) return null;
      const nftId = parseInt(match[1], 10);

      // Find what's being requested (XCH or CAT)
      const requested = offer.requested?.[0];
      if (!requested) return null;

      const priceXch = requested.type === 'xch' || !requested.asset_id
        ? requested.amount / 1e12
        : null;

      return {
        nftId,
        nftName: nftOffered.name,
        priceXch,
        priceRaw: requested.amount,
        currency: requested.type || 'xch',
        tokenCode: requested.code,
        offerId: offer.id,
        dateCreated: offer.date_created
      };
    } catch (error) {
      return null;
    }
  }

  /**
   * Get floor price for a specific character type or entire collection
   */
  async getFloorPrice(characterType = null) {
    const listings = await this.fetchListings();
    
    let filtered = listings.filter(l => l.priceXch !== null);
    
    if (characterType) {
      // Filter by character type based on NFT ID ranges
      const ranges = this.getCharacterRanges();
      const range = ranges[characterType.toLowerCase()];
      if (range) {
        filtered = filtered.filter(l => l.nftId >= range.start && l.nftId <= range.end);
      }
    }

    if (filtered.length === 0) return null;

    const sorted = filtered.sort((a, b) => a.priceXch - b.priceXch);
    return sorted[0];
  }

  /**
   * Search NFTs by ID or name
   */
  async searchNFTs(query) {
    const listings = await this.fetchListings();
    const lowerQuery = query.toLowerCase();

    // Check if query is a number (NFT ID)
    const numQuery = parseInt(query, 10);
    if (!isNaN(numQuery)) {
      return listings.filter(l => l.nftId === numQuery);
    }

    // Search by name
    return listings.filter(l => l.nftName.toLowerCase().includes(lowerQuery));
  }

  /**
   * Get NFT ID ranges for each character type (approximation)
   */
  getCharacterRanges() {
    return {
      'wojak': { start: 1, end: 800 },
      'soyjak': { start: 801, end: 1500 },
      'waifu': { start: 1501, end: 2000 },
      'baddie': { start: 2001, end: 2500 },
      'papa-tang': { start: 2501, end: 2600 },
      'monkey-zoo': { start: 2601, end: 2900 },
      'bepe-wojak': { start: 2901, end: 3100 },
      'bepe-soyjak': { start: 3101, end: 3300 },
      'bepe-waifu': { start: 3301, end: 3500 },
      'bepe-baddie': { start: 3501, end: 3700 },
      'alien-wojak': { start: 3701, end: 3850 },
      'alien-soyjak': { start: 3851, end: 4000 },
      'alien-waifu': { start: 4001, end: 4100 },
      'alien-baddie': { start: 4101, end: 4200 }
    };
  }

  /**
   * Get character type from NFT ID
   */
  getCharacterType(nftId) {
    const ranges = this.getCharacterRanges();
    for (const [type, range] of Object.entries(ranges)) {
      if (nftId >= range.start && nftId <= range.end) {
        return type;
      }
    }
    return 'unknown';
  }

  /**
   * Get NFT image URL
   */
  getNFTImageUrl(nftId) {
    const paddedId = String(nftId).padStart(4, '0');
    return `https://bafybeigjkkonjzwwpopo4wn4gwrrvb7z3nwr2edj2554vx3avc5ietfjwq.ipfs.w3s.link/${paddedId}.png`;
  }
}

module.exports = WojakAPI;
