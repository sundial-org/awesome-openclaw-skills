/**
 * Trait analysis and filtering
 */

class TraitAnalyzer {
  constructor() {
    this.traitTypes = [
      'Base',
      'Face',
      'Face Wear',
      'Mouth',
      'Head',
      'Clothes',
      'Background'
    ];
  }

  /**
   * Extract all unique traits from a collection
   */
  extractTraits(nfts) {
    const traits = {};

    nfts.forEach(nft => {
      if (!nft.traits) return;

      nft.traits.forEach(trait => {
        const type = trait.trait_type;
        const value = trait.value;

        if (!traits[type]) {
          traits[type] = {};
        }

        if (!traits[type][value]) {
          traits[type][value] = {
            count: 0,
            nfts: []
          };
        }

        traits[type][value].count++;
        traits[type][value].nfts.push(nft.id || nft.nftId);
      });
    });

    return traits;
  }

  /**
   * Get trait distribution for a specific type
   */
  getTraitDistribution(nfts, traitType) {
    const distribution = {};
    let total = 0;

    nfts.forEach(nft => {
      if (!nft.traits) return;

      const trait = nft.traits.find(t => t.trait_type === traitType);
      if (trait) {
        const value = trait.value;
        distribution[value] = (distribution[value] || 0) + 1;
        total++;
      }
    });

    // Calculate percentages
    const result = Object.entries(distribution).map(([value, count]) => ({
      value,
      count,
      percentage: ((count / total) * 100).toFixed(2),
      rarity: (100 / ((count / total) * 100)).toFixed(2) // Inverse of percentage
    }));

    return result.sort((a, b) => b.count - a.count);
  }

  /**
   * Find NFTs matching specific trait criteria
   */
  filterByTraits(nfts, criteria) {
    return nfts.filter(nft => {
      if (!nft.traits) return false;

      return Object.entries(criteria).every(([traitType, desiredValue]) => {
        const trait = nft.traits.find(t => t.trait_type === traitType);
        return trait && trait.value === desiredValue;
      });
    });
  }

  /**
   * Find NFTs with rare trait combinations
   */
  findRareCombinations(nfts, minRarity = 5) {
    const combinations = new Map();

    nfts.forEach(nft => {
      if (!nft.traits || nft.traits.length < 2) return;

      // Create combination key from all traits
      const combo = nft.traits
        .map(t => `${t.trait_type}:${t.value}`)
        .sort()
        .join('|');

      if (!combinations.has(combo)) {
        combinations.set(combo, {
          combo,
          count: 0,
          nfts: [],
          traits: nft.traits
        });
      }

      const entry = combinations.get(combo);
      entry.count++;
      entry.nfts.push(nft.id || nft.nftId);
    });

    // Filter by rarity (count)
    const rare = Array.from(combinations.values())
      .filter(c => c.count <= minRarity)
      .sort((a, b) => a.count - b.count);

    return rare;
  }

  /**
   * Get the rarest traits across the collection
   */
  getRarestTraits(nfts, limit = 10) {
    const allTraits = [];

    // Collect all trait occurrences
    nfts.forEach(nft => {
      if (!nft.traits) return;

      nft.traits.forEach(trait => {
        allTraits.push({
          type: trait.trait_type,
          value: trait.value
        });
      });
    });

    // Count occurrences
    const counts = {};
    allTraits.forEach(trait => {
      const key = `${trait.type}:${trait.value}`;
      counts[key] = (counts[key] || 0) + 1;
    });

    // Sort by rarity (lowest count)
    const sorted = Object.entries(counts)
      .map(([key, count]) => {
        const [type, value] = key.split(':');
        return {
          traitType: type,
          value,
          count,
          percentage: ((count / nfts.length) * 100).toFixed(2)
        };
      })
      .sort((a, b) => a.count - b.count);

    return sorted.slice(0, limit);
  }

  /**
   * Compare trait rarity between two NFTs
   */
  compareTraits(nft1, nft2, allNFTs) {
    const traits1 = this.extractTraits([nft1]);
    const traits2 = this.extractTraits([nft2]);
    
    const comparison = {
      nft1: { unique: [], rare: [], common: [] },
      nft2: { unique: [], rare: [], common: [] },
      shared: []
    };

    // Analyze NFT1 traits
    if (nft1.traits) {
      nft1.traits.forEach(trait => {
        const distribution = this.getTraitDistribution(allNFTs, trait.trait_type);
        const traitData = distribution.find(d => d.value === trait.value);
        
        const hasShared = nft2.traits?.some(t => 
          t.trait_type === trait.trait_type && t.value === trait.value
        );

        if (hasShared) {
          comparison.shared.push({ ...trait, ...traitData });
        } else if (traitData && parseFloat(traitData.percentage) < 1) {
          comparison.nft1.rare.push({ ...trait, ...traitData });
        } else if (traitData && parseFloat(traitData.percentage) < 5) {
          comparison.nft1.unique.push({ ...trait, ...traitData });
        } else {
          comparison.nft1.common.push({ ...trait, ...traitData });
        }
      });
    }

    // Analyze NFT2 traits (excluding shared)
    if (nft2.traits) {
      nft2.traits.forEach(trait => {
        const hasShared = nft1.traits?.some(t => 
          t.trait_type === trait.trait_type && t.value === trait.value
        );

        if (!hasShared) {
          const distribution = this.getTraitDistribution(allNFTs, trait.trait_type);
          const traitData = distribution.find(d => d.value === trait.value);
          
          if (traitData && parseFloat(traitData.percentage) < 1) {
            comparison.nft2.rare.push({ ...trait, ...traitData });
          } else if (traitData && parseFloat(traitData.percentage) < 5) {
            comparison.nft2.unique.push({ ...trait, ...traitData });
          } else {
            comparison.nft2.common.push({ ...trait, ...traitData });
          }
        }
      });
    }

    return comparison;
  }

  /**
   * Get trait count distribution
   */
  getTraitCountDistribution(nfts) {
    const counts = {};

    nfts.forEach(nft => {
      const count = nft.traits?.length || 0;
      counts[count] = (counts[count] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([count, total]) => ({
        traitCount: parseInt(count),
        nftCount: total,
        percentage: ((total / nfts.length) * 100).toFixed(2)
      }))
      .sort((a, b) => a.traitCount - b.traitCount);
  }

  /**
   * Find "naked floor" - cheapest NFT with specific trait
   */
  findNakedFloor(listings, traitType, traitValue) {
    const matching = listings.filter(listing => {
      if (!listing.traits) return false;
      return listing.traits.some(t => 
        t.trait_type === traitType && t.value === traitValue
      );
    });

    if (matching.length === 0) return null;

    return matching.sort((a, b) => (a.priceXch || Infinity) - (b.priceXch || Infinity))[0];
  }
}

module.exports = TraitAnalyzer;
