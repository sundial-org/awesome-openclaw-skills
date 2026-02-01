/**
 * Rarity scoring and analysis for Wojak NFTs
 */

class RarityAnalyzer {
  constructor() {
    this.traitRarity = null;
    this.nftScores = new Map();
  }

  /**
   * Calculate rarity score based on trait frequency
   * Lower frequency = higher rarity = higher score
   */
  calculateTraitRarity(allNFTs) {
    const traitCounts = {};
    const total = allNFTs.length;

    // Count occurrences of each trait value
    allNFTs.forEach(nft => {
      if (!nft.traits) return;

      nft.traits.forEach(trait => {
        const key = `${trait.trait_type}:${trait.value}`;
        traitCounts[key] = (traitCounts[key] || 0) + 1;
      });
    });

    // Calculate rarity scores (inverse frequency)
    const traitRarity = {};
    Object.entries(traitCounts).forEach(([key, count]) => {
      const frequency = count / total;
      const rarityScore = 1 / frequency; // Higher score = rarer
      traitRarity[key] = {
        count,
        frequency,
        rarityScore
      };
    });

    this.traitRarity = traitRarity;
    return traitRarity;
  }

  /**
   * Calculate overall rarity score for an NFT
   */
  calculateNFTScore(nft) {
    if (!nft.traits || !this.traitRarity) return 0;

    let totalScore = 0;
    let traitCount = 0;

    nft.traits.forEach(trait => {
      const key = `${trait.trait_type}:${trait.value}`;
      const rarity = this.traitRarity[key];
      
      if (rarity) {
        totalScore += rarity.rarityScore;
        traitCount++;
      }
    });

    // Average rarity score across all traits
    return traitCount > 0 ? totalScore / traitCount : 0;
  }

  /**
   * Get rarity tier based on score
   */
  getRarityTier(score) {
    if (score >= 10) return { tier: 'Legendary', emoji: '🌟', color: '#FFD700' };
    if (score >= 7) return { tier: 'Epic', emoji: '💎', color: '#9333EA' };
    if (score >= 5) return { tier: 'Rare', emoji: '💠', color: '#3B82F6' };
    if (score >= 3) return { tier: 'Uncommon', emoji: '🔷', color: '#10B981' };
    return { tier: 'Common', emoji: '⬜', color: '#6B7280' };
  }

  /**
   * Find rarest traits in an NFT
   */
  getRarestTraits(nft, limit = 3) {
    if (!nft.traits || !this.traitRarity) return [];

    const scored = nft.traits
      .map(trait => {
        const key = `${trait.trait_type}:${trait.value}`;
        const rarity = this.traitRarity[key];
        return {
          ...trait,
          rarityScore: rarity?.rarityScore || 0,
          frequency: rarity?.frequency || 1,
          count: rarity?.count || 0
        };
      })
      .sort((a, b) => b.rarityScore - a.rarityScore);

    return scored.slice(0, limit);
  }

  /**
   * Compare two NFTs by rarity
   */
  compareNFTs(nft1, nft2) {
    const score1 = this.calculateNFTScore(nft1);
    const score2 = this.calculateNFTScore(nft2);
    
    return {
      nft1Score: score1,
      nft2Score: score2,
      winner: score1 > score2 ? 'nft1' : score2 > score1 ? 'nft2' : 'tie',
      difference: Math.abs(score1 - score2)
    };
  }

  /**
   * Find NFTs with specific rare traits
   */
  findNFTsWithTrait(allNFTs, traitType, traitValue) {
    return allNFTs.filter(nft => {
      if (!nft.traits) return false;
      return nft.traits.some(t => 
        t.trait_type === traitType && t.value === traitValue
      );
    });
  }

  /**
   * Get trait distribution statistics
   */
  getTraitStats(allNFTs, traitType) {
    const values = {};
    
    allNFTs.forEach(nft => {
      if (!nft.traits) return;
      
      const trait = nft.traits.find(t => t.trait_type === traitType);
      if (trait) {
        values[trait.value] = (values[trait.value] || 0) + 1;
      }
    });

    const total = Object.values(values).reduce((sum, count) => sum + count, 0);
    
    return Object.entries(values)
      .map(([value, count]) => ({
        value,
        count,
        percentage: ((count / total) * 100).toFixed(2)
      }))
      .sort((a, b) => b.count - a.count);
  }

  /**
   * Simulate rarity ranking (approximation without full collection data)
   */
  estimateRank(nftId, characterType) {
    // This is a placeholder - real implementation would need full collection data
    // For now, return a rough estimate based on ID within character range
    
    const ranges = {
      'wojak': { start: 1, end: 800, avgRarity: 5.2 },
      'soyjak': { start: 801, end: 1500, avgRarity: 5.1 },
      'waifu': { start: 1501, end: 2000, avgRarity: 6.8 },
      'baddie': { start: 2001, end: 2500, avgRarity: 6.5 },
      'papa-tang': { start: 2501, end: 2600, avgRarity: 8.9 },
      'monkey-zoo': { start: 2601, end: 2900, avgRarity: 7.2 },
      'bepe-wojak': { start: 2901, end: 3100, avgRarity: 7.8 },
      'bepe-soyjak': { start: 3101, end: 3300, avgRarity: 7.6 },
      'bepe-waifu': { start: 3301, end: 3500, avgRarity: 8.1 },
      'bepe-baddie': { start: 3501, end: 3700, avgRarity: 8.0 },
      'alien-wojak': { start: 3701, end: 3850, avgRarity: 9.2 },
      'alien-soyjak': { start: 3851, end: 4000, avgRarity: 9.0 },
      'alien-waifu': { start: 4001, end: 4100, avgRarity: 9.5 },
      'alien-baddie': { start: 4101, end: 4200, avgRarity: 9.3 }
    };

    const range = ranges[characterType];
    if (!range) return null;

    // Rough estimate: position within range affects rarity
    const position = (nftId - range.start) / (range.end - range.start);
    const variance = (Math.random() - 0.5) * 2; // Add some randomness
    const estimatedScore = range.avgRarity + variance;

    return {
      estimatedScore,
      estimatedRank: Math.floor(nftId * 0.8 + Math.random() * 500), // Placeholder
      tier: this.getRarityTier(estimatedScore)
    };
  }
}

module.exports = RarityAnalyzer;
