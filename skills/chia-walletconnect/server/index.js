const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const { verifySignature } = require('../lib/verify');
const { validateChallengeTimestamp } = require('../lib/challenge');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../webapp')));

// Store pending verifications (in production, use Redis or database)
const pendingVerifications = new Map();

/**
 * Serve the Telegram Web App
 */
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../webapp/index.html'));
});

/**
 * Webhook endpoint for verification callbacks
 * This is called by the Telegram Web App after signature is collected
 */
app.post('/api/verify', async (req, res) => {
  try {
    const { address, message, signature, publicKey, userId, timestamp } = req.body;
    
    // Validate request
    if (!address || !message || !signature) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: address, message, signature'
      });
    }
    
    // Validate timestamp (challenge must be recent)
    if (!validateChallengeTimestamp(timestamp)) {
      return res.status(400).json({
        success: false,
        error: 'Challenge expired. Please generate a new one.'
      });
    }
    
    console.log(`🔐 Verifying signature for ${address}...`);
    
    // Verify signature with MintGarden API
    const result = await verifySignature(address, message, signature, publicKey);
    
    if (result.verified) {
      console.log(`✅ Signature verified for ${address}`);
      
      // Store verification result
      pendingVerifications.set(userId, {
        address,
        verified: true,
        timestamp: Date.now()
      });
      
      // Send success response
      return res.json({
        success: true,
        verified: true,
        address,
        userId,
        message: 'Wallet ownership verified successfully!'
      });
    } else {
      console.log(`❌ Signature verification failed for ${address}`);
      
      return res.status(400).json({
        success: false,
        verified: false,
        error: result.error || 'Signature verification failed'
      });
    }
    
  } catch (error) {
    console.error('❌ Verification endpoint error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

/**
 * Get verification status for a user
 */
app.get('/api/status/:userId', (req, res) => {
  const { userId } = req.params;
  
  const verification = pendingVerifications.get(userId);
  
  if (verification) {
    res.json({
      success: true,
      ...verification
    });
  } else {
    res.json({
      success: false,
      verified: false,
      message: 'No verification found for this user'
    });
  }
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'chia-walletconnect',
    timestamp: Date.now()
  });
});

/**
 * Start server
 */
app.listen(PORT, () => {
  console.log(`🚀 Chia WalletConnect server running on port ${PORT}`);
  console.log(`📱 Web App: http://localhost:${PORT}`);
  console.log(`🔗 Webhook: http://localhost:${PORT}/api/verify`);
  console.log(`💚 Health: http://localhost:${PORT}/health`);
});

module.exports = app;
