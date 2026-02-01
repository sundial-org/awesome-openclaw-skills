const fs = require('fs');
const path = require('path');

/**
 * Price history tracking and analysis
 */
class PriceHistory {
  constructor(dataDir = path.join(__dirname, '../data')) {
    this.dataDir = dataDir;
    this.historyFile = path.join(dataDir, 'price_history.json');
    this.salesFile = path.join(dataDir, 'sales.json');
    
    this.ensureDataDir();
    this.history = this.loadHistory();
    this.sales = this.loadSales();
  }

  /**
   * Ensure data directory exists
   */
  ensureDataDir() {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
  }

  /**
   * Load price history from disk
   */
  loadHistory() {
    try {
      if (fs.existsSync(this.historyFile)) {
        const data = fs.readFileSync(this.historyFile, 'utf8');
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('Failed to load price history:', error.message);
    }
    return { floor: [], average: [], volume: [] };
  }

  /**
   * Load sales records from disk
   */
  loadSales() {
    try {
      if (fs.existsSync(this.salesFile)) {
        const data = fs.readFileSync(this.salesFile, 'utf8');
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('Failed to load sales:', error.message);
    }
    return [];
  }

  /**
   * Save price history to disk
   */
  saveHistory() {
    try {
      fs.writeFileSync(this.historyFile, JSON.stringify(this.history, null, 2));
    } catch (error) {
      console.error('Failed to save price history:', error.message);
    }
  }

  /**
   * Save sales records to disk
   */
  saveSales() {
    try {
      fs.writeFileSync(this.salesFile, JSON.stringify(this.sales, null, 2));
    } catch (error) {
      console.error('Failed to save sales:', error.message);
    }
  }

  /**
   * Record a new floor price snapshot
   */
  recordFloorPrice(floorPrice, characterType = null) {
    const timestamp = Date.now();
    const record = {
      timestamp,
      date: new Date().toISOString(),
      price: floorPrice,
      characterType
    };

    this.history.floor.push(record);
    
    // Keep only last 1000 records
    if (this.history.floor.length > 1000) {
      this.history.floor = this.history.floor.slice(-1000);
    }

    this.saveHistory();
    return record;
  }

  /**
   * Record a sale
   */
  recordSale(nftId, price, characterType, buyer = null, seller = null) {
    const sale = {
      timestamp: Date.now(),
      date: new Date().toISOString(),
      nftId,
      price,
      characterType,
      buyer,
      seller
    };

    this.sales.push(sale);
    
    // Keep only last 10000 sales
    if (this.sales.length > 10000) {
      this.sales = this.sales.slice(-10000);
    }

    this.saveSales();
    return sale;
  }

  /**
   * Get price history for a time range
   */
  getFloorHistory(hours = 24, characterType = null) {
    const cutoff = Date.now() - (hours * 60 * 60 * 1000);
    
    let filtered = this.history.floor.filter(r => r.timestamp >= cutoff);
    
    if (characterType) {
      filtered = filtered.filter(r => r.characterType === characterType);
    }

    return filtered;
  }

  /**
   * Get recent sales
   */
  getRecentSales(limit = 10, characterType = null) {
    let filtered = [...this.sales];
    
    if (characterType) {
      filtered = filtered.filter(s => s.characterType === characterType);
    }

    return filtered
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }

  /**
   * Calculate price statistics
   */
  getPriceStats(hours = 24, characterType = null) {
    const history = this.getFloorHistory(hours, characterType);
    
    if (history.length === 0) {
      return null;
    }

    const prices = history.map(r => r.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const avg = prices.reduce((sum, p) => sum + p, 0) / prices.length;
    
    const first = history[0].price;
    const last = history[history.length - 1].price;
    const change = last - first;
    const changePercent = ((change / first) * 100).toFixed(2);

    return {
      min,
      max,
      avg,
      current: last,
      change,
      changePercent: parseFloat(changePercent),
      dataPoints: history.length,
      timeRange: hours
    };
  }

  /**
   * Calculate volume statistics
   */
  getVolumeStats(hours = 24, characterType = null) {
    const cutoff = Date.now() - (hours * 60 * 60 * 1000);
    
    let filtered = this.sales.filter(s => s.timestamp >= cutoff);
    
    if (characterType) {
      filtered = filtered.filter(s => s.characterType === characterType);
    }

    if (filtered.length === 0) {
      return null;
    }

    const totalVolume = filtered.reduce((sum, s) => sum + s.price, 0);
    const avgSalePrice = totalVolume / filtered.length;
    const salesCount = filtered.length;

    return {
      totalVolume,
      avgSalePrice,
      salesCount,
      timeRange: hours
    };
  }

  /**
   * Get top sales
   */
  getTopSales(limit = 10, characterType = null) {
    let filtered = [...this.sales];
    
    if (characterType) {
      filtered = filtered.filter(s => s.characterType === characterType);
    }

    return filtered
      .sort((a, b) => b.price - a.price)
      .slice(0, limit);
  }

  /**
   * Detect price trends
   */
  detectTrend(hours = 24, characterType = null) {
    const history = this.getFloorHistory(hours, characterType);
    
    if (history.length < 2) {
      return { trend: 'unknown', confidence: 0 };
    }

    // Simple linear regression
    const prices = history.map((r, i) => ({ x: i, y: r.price }));
    const n = prices.length;
    
    const sumX = prices.reduce((sum, p) => sum + p.x, 0);
    const sumY = prices.reduce((sum, p) => sum + p.y, 0);
    const sumXY = prices.reduce((sum, p) => sum + (p.x * p.y), 0);
    const sumX2 = prices.reduce((sum, p) => sum + (p.x * p.x), 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    
    let trend = 'stable';
    if (slope > 0.01) trend = 'rising';
    else if (slope < -0.01) trend = 'falling';
    
    const confidence = Math.min(Math.abs(slope) * 100, 100);

    return {
      trend,
      confidence: confidence.toFixed(1),
      slope: slope.toFixed(4)
    };
  }

  /**
   * Export data for analysis
   */
  exportData() {
    return {
      history: this.history,
      sales: this.sales,
      exported: new Date().toISOString()
    };
  }

  /**
   * Import data
   */
  importData(data) {
    if (data.history) {
      this.history = data.history;
      this.saveHistory();
    }
    if (data.sales) {
      this.sales = data.sales;
      this.saveSales();
    }
  }

  /**
   * Clear old data
   */
  clearOldData(daysToKeep = 30) {
    const cutoff = Date.now() - (daysToKeep * 24 * 60 * 60 * 1000);
    
    this.history.floor = this.history.floor.filter(r => r.timestamp >= cutoff);
    this.sales = this.sales.filter(s => s.timestamp >= cutoff);
    
    this.saveHistory();
    this.saveSales();
    
    return {
      floorRecordsKept: this.history.floor.length,
      salesRecordsKept: this.sales.length
    };
  }
}

module.exports = PriceHistory;
