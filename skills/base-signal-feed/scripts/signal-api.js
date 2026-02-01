const express = require('express');
const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// --- CONFIGURATION ---
const PORT = process.env.PORT || 7071;
const SERVICE_WALLET = '0xA28F38d6F607b35a718C3e6193E7B622246d5a2B';
const MIN_PAYMENT_ETH = 0.0001;
const PAYMENT_VALIDITY_DAYS = 30;
const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour
const BASE_RPC_URL = 'https://mainnet.base.org'; 

const ALERTS_PATH = '/home/linuxuser/.openclaw/workspace/tools/trading/smart-money-alerts.json';
const NEW_PAIRS_PATH = '/home/linuxuser/.openclaw/workspace/tools/trading/new-pairs.json';

const provider = new ethers.providers.JsonRpcProvider(BASE_RPC_URL);
const paymentCache = new Map();

// --- PAYMENT VERIFICATION MIDDLEWARE ---
async function verifyPaymentOnChain(payerAddress) {
    // Use Basescan API (free, no key needed for basic usage) to check incoming txs
    const url = `https://api.basescan.org/api?module=account&action=txlist&address=${SERVICE_WALLET}&startblock=0&endblock=99999999&sort=desc&page=1&offset=100`;
    try {
        const resp = await fetch(url);
        const data = await resp.json();
        if (data.status !== '1' || !Array.isArray(data.result)) return false;

        const cutoff = Math.floor((Date.now() - PAYMENT_VALIDITY_DAYS * 86400000) / 1000);
        for (const tx of data.result) {
            if (tx.from.toLowerCase() === payerAddress.toLowerCase() &&
                tx.to.toLowerCase() === SERVICE_WALLET.toLowerCase() &&
                parseInt(tx.timeStamp) >= cutoff &&
                tx.isError === '0') {
                const valueEth = parseFloat(ethers.utils.formatEther(tx.value));
                if (valueEth >= MIN_PAYMENT_ETH) return true;
            }
        }
        return false;
    } catch (e) {
        console.error('Basescan API error:', e.message);
        // Fallback: check if payer has any ETH balance (lenient during API issues)
        return false;
    }
}

async function checkPayment(req, res, next) {
    const payerAddress = req.headers['x-payer-address'];

    if (!payerAddress || !ethers.utils.isAddress(payerAddress)) {
        return res.status(400).json({
            error: 'Missing or invalid x-payer-address header',
            payment: { wallet: SERVICE_WALLET, minEth: MIN_PAYMENT_ETH, validDays: PAYMENT_VALIDITY_DAYS }
        });
    }

    const cacheEntry = paymentCache.get(payerAddress.toLowerCase());
    if (cacheEntry && Date.now() - cacheEntry.timestamp < CACHE_TTL_MS) {
        if (cacheEntry.hasPaid) return next();
        return res.status(402).json({
            error: 'Payment required. Send >= 0.0001 ETH to our wallet on Base.',
            payment: { wallet: SERVICE_WALLET, minEth: MIN_PAYMENT_ETH, validDays: PAYMENT_VALIDITY_DAYS }
        });
    }

    try {
        const hasPaid = await verifyPaymentOnChain(payerAddress);
        paymentCache.set(payerAddress.toLowerCase(), { hasPaid, timestamp: Date.now() });

        if (hasPaid) {
            next();
        } else {
            res.status(402).json({
                error: 'Payment required. Send >= 0.0001 ETH to our wallet on Base.',
                payment: { wallet: SERVICE_WALLET, minEth: MIN_PAYMENT_ETH, validDays: PAYMENT_VALIDITY_DAYS }
            });
        }
    } catch (error) {
        console.error('Payment verification error:', error);
        res.status(500).json({ error: 'Payment verification failed' });
    }
}


// --- SCORING LOGIC (Adapted from signal-scorer.js) ---

const SKIP_TOKENS = new Set([
  '0x4200000000000000000000000000000000000006', // WETH
  '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', // USDC
]);

async function getTokenInfo(tokenAddress) {
  try {
    const res = await fetch(`https://api.dexscreener.com/latest/dex/search?q=${tokenAddress}`);
    if (!res.ok) return null;
    const data = await res.json();
    const pair = data.pairs?.find(p => p.chainId === 'base');
    if (!pair) return null;
    return {
      symbol: pair.baseToken?.symbol || '???',
      priceUsd: parseFloat(pair.priceUsd || 0),
      liquidity: pair.liquidity?.usd || 0,
      volume24h: pair.volume?.h24 || 0,
    };
  } catch { return null; }
}

async function checkSafety(tokenAddress) {
  try {
    const res = await fetch(`https://api.gopluslabs.io/api/v1/token_security/8453?contract_addresses=${tokenAddress}`);
    if (!res.ok) return { safe: null };
    const data = await res.json();
    const info = data?.result?.[tokenAddress.toLowerCase()];
    if (!info) return { safe: null };
    return {
      safe: info.is_honeypot !== '1' && info.is_mintable !== '1' && parseFloat(info.sell_tax || '0') <= 0.1,
      honeypot: info.is_honeypot === '1',
      mintable: info.is_mintable === '1',
      sellTax: parseFloat(info.sell_tax || '0'),
      buyTax: parseFloat(info.buy_tax || '0'),
      verified: info.is_open_source === '1',
    };
  } catch { return { safe: null }; }
}

function getConvergence(tokenAddress) {
  try {
    if (!fs.existsSync(ALERTS_PATH)) return { count: 0 };
    const alerts = JSON.parse(fs.readFileSync(ALERTS_PATH, 'utf8'));
    const recent = alerts.filter(a => {
      const age = Date.now() - new Date(a.timestamp).getTime();
      const token = a.decoded?.token?.toLowerCase();
      return age < 24 * 3600 * 1000 && token === tokenAddress.toLowerCase() && a.decoded?.action === 'BUY';
    });
    const uniqueWallets = new Set(recent.map(a => a.wallet.toLowerCase()));
    return { count: uniqueWallets.size };
  } catch { return { count: 0 }; }
}

function getWalletReputation(walletLabel = 'unknown') {
  const label = walletLabel.toLowerCase();
  if (label.includes('jesse') || label.includes('pollak')) return 30;
  if (label.includes('whale')) return 20;
  if (label.includes('deployer') || label.includes('early')) return 20;
  return 10;
}

async function scoreSignal(tokenAddress, walletLabel) {
  if (SKIP_TOKENS.has(tokenAddress.toLowerCase())) {
    return { total: 0, action: 'ignore', reasons: ['Base/stable token'], breakdown: {} };
  }
  
  const [tokenInfo, safety, convergence] = await Promise.all([
      getTokenInfo(tokenAddress),
      checkSafety(tokenAddress),
      getConvergence(tokenAddress)
  ]);

  const reasons = [];
  const breakdown = {};
  
  const walletScore = getWalletReputation(walletLabel);
  breakdown.wallet = walletScore;

  let tokenScore = 0;
  if (tokenInfo) {
    if (tokenInfo.liquidity >= 100000) tokenScore += 10;
    else if (tokenInfo.liquidity >= 10000) tokenScore += 3;
    if (tokenInfo.volume24h >= 50000) tokenScore += 8;
  }
  breakdown.token = tokenScore;

  let safetyScore = 0;
  if (safety.safe === true) {
    safetyScore = 25;
  } else if (safety.safe === false) {
    if (safety.honeypot) reasons.push('HONEYPOT');
    if (safety.mintable) reasons.push('Mintable');
    if (safety.sellTax > 0.1) reasons.push(`High sell tax`);
  } else {
    safetyScore = 10;
  }
  breakdown.safety = safetyScore;
  
  let convergenceScore = 0;
  if (convergence.count >= 3) convergenceScore = 20;
  else if (convergence.count >= 2) convergenceScore = 12;
  breakdown.convergence = convergenceScore;
  
  const total = walletScore + tokenScore + safetyScore + convergenceScore;
  
  let action = 'ignore';
  if (safety.safe === false) action = 'ignore';
  else if (total >= 70) action = 'trade';
  else if (total >= 40) action = 'paper';

  return { total, action, reasons, breakdown, tokenInfo, safety, convergence };
}

// --- API SERVER ---
const app = express();
app.use(express.json());

app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.get('/signals', checkPayment, (req, res) => {
    try {
        if (!fs.existsSync(ALERTS_PATH)) {
            return res.json([]);
        }
        const alerts = JSON.parse(fs.readFileSync(ALERTS_PATH, 'utf8'));
        const twentyFourHoursAgo = Date.now() - 24 * 60 * 60 * 1000;
        const recentAlerts = alerts.filter(a => new Date(a.timestamp).getTime() >= twentyFourHoursAgo);
        res.json(recentAlerts);
    } catch (error) {
        console.error('Error reading signals file:', error);
        res.status(500).json({ error: 'Could not read signals data' });
    }
});

app.get('/pairs/new', checkPayment, (req, res) => {
    try {
        if (!fs.existsSync(NEW_PAIRS_PATH)) {
            return res.json([]);
        }
        const pairs = JSON.parse(fs.readFileSync(NEW_PAIRS_PATH, 'utf8'));
        res.json(pairs);
    } catch (error) {
        console.error('Error reading new pairs file:', error);
        res.status(500).json({ error: 'Could not read new pairs data' });
    }
});

app.get('/signals/score', checkPayment, async (req, res) => {
    const { token, walletLabel } = req.query;
    if (!token || !ethers.utils.isAddress(token)) {
        return res.status(400).json({ error: 'Valid "token" query parameter is required' });
    }
    try {
        const score = await scoreSignal(token, walletLabel);
        res.json(score);
    } catch (error) {
        console.error(`Error scoring token ${token}:`, error);
        res.status(500).json({ error: 'Failed to score token' });
    }
});

app.listen(PORT, () => {
    console.log(`Base Signal Feed API server running on port ${PORT}`);
});
