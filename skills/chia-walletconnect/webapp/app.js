// Telegram Web App API
const tg = window.Telegram.WebApp;

// Initialize Telegram Web App
tg.ready();
tg.expand();

// WalletConnect configuration
const WALLETCONNECT_PROJECT_ID = '6d377259062295c0f6312b4f3e7a5d9b'; // Dracattus WalletConnect ID
const CHIA_CHAIN = 'chia:mainnet';

// State management
let signClient = null;
let currentSession = null;
let currentAddress = null;
let currentPublicKey = null;
let challengeData = null;

// UI Elements
const elements = {
  statusBadge: document.getElementById('status-badge'),
  statusText: document.getElementById('status-text'),
  connectBtn: document.getElementById('connect-btn'),
  connectSection: document.getElementById('connect-section'),
  walletInfo: document.getElementById('wallet-info'),
  walletAddress: document.getElementById('wallet-address'),
  walletPubkey: document.getElementById('wallet-pubkey'),
  challengeSection: document.getElementById('challenge-section'),
  challengeMessage: document.getElementById('challenge-message'),
  signBtn: document.getElementById('sign-btn'),
  resultSection: document.getElementById('result-section'),
  resultCard: document.getElementById('result-card'),
  resultIcon: document.getElementById('result-icon'),
  resultMessage: document.getElementById('result-message'),
  resultDetails: document.getElementById('result-details'),
  errorSection: document.getElementById('error-section'),
  errorMessage: document.getElementById('error-message'),
  retryBtn: document.getElementById('retry-btn'),
  loadingOverlay: document.getElementById('loading-overlay'),
  loadingText: document.getElementById('loading-text')
};

// Event Listeners
elements.connectBtn.addEventListener('click', connectWallet);
elements.signBtn.addEventListener('click', signChallenge);
elements.retryBtn.addEventListener('click', reset);

// Initialize WalletConnect
async function initWalletConnect() {
  try {
    showLoading('Initializing WalletConnect...');
    
    // Import SignClient from global
    const { SignClient } = window.WalletConnectSignClient;
    
    signClient = await SignClient.init({
      projectId: WALLETCONNECT_PROJECT_ID,
      metadata: {
        name: 'Chia Wallet Verification',
        description: 'Verify Chia wallet ownership via Telegram',
        url: 'https://t.me', // Telegram domain
        icons: ['https://chia.net/wp-content/uploads/2022/09/chia-logo.svg']
      }
    });
    
    console.log('✅ WalletConnect initialized');
    
    // Check for existing sessions
    const sessions = signClient.session.getAll();
    if (sessions.length > 0) {
      console.log('📱 Found existing session, reconnecting...');
      currentSession = sessions[0];
      await handleSessionConnected(currentSession);
    }
    
    hideLoading();
  } catch (error) {
    console.error('❌ WalletConnect init failed:', error);
    showError('Failed to initialize WalletConnect: ' + error.message);
    hideLoading();
  }
}

// Connect wallet
async function connectWallet() {
  try {
    showLoading('Opening WalletConnect...');
    setStatus('connecting', 'Connecting...');
    
    // Create connection request
    const { uri, approval } = await signClient.connect({
      requiredNamespaces: {
        chia: {
          methods: [
            'chip0002_getPublicKeys',
            'chip0002_signMessage',
            'chia_getCurrentAddress'
          ],
          chains: [CHIA_CHAIN],
          events: []
        }
      }
    });
    
    if (uri) {
      console.log('🔗 WalletConnect URI:', uri);
      
      // Display URI for manual connection (QR code alternative)
      // In production, you'd use WalletConnect modal or deep link
      alert(`Open Sage Wallet and paste this URI:\n\n${uri}\n\nOr scan the QR code in WalletConnect modal.`);
      
      // For mobile: try deep link
      if (isMobile()) {
        const sageDeepLink = `sage://wc?uri=${encodeURIComponent(uri)}`;
        window.location.href = sageDeepLink;
      }
    }
    
    // Wait for session approval
    const session = await approval();
    console.log('✅ Session approved:', session);
    
    currentSession = session;
    await handleSessionConnected(session);
    
  } catch (error) {
    console.error('❌ Connection failed:', error);
    showError('Failed to connect wallet: ' + error.message);
    setStatus('disconnected', 'Disconnected');
    hideLoading();
  }
}

// Handle successful session connection
async function handleSessionConnected(session) {
  try {
    showLoading('Fetching wallet info...');
    
    // Extract account from session
    const accounts = session.namespaces.chia?.accounts || [];
    if (accounts.length === 0) {
      throw new Error('No Chia accounts found in session');
    }
    
    // Parse account (format: "chia:mainnet:xch1...")
    const accountString = accounts[0];
    currentAddress = accountString.split(':')[2];
    
    console.log('💼 Wallet address:', currentAddress);
    
    // Get public key using CHIP-0002
    try {
      const pubKeyResult = await signClient.request({
        topic: session.topic,
        chainId: CHIA_CHAIN,
        request: {
          method: 'chip0002_getPublicKeys',
          params: {
            limit: 1,
            offset: 0
          }
        }
      });
      
      if (pubKeyResult && pubKeyResult.length > 0) {
        currentPublicKey = pubKeyResult[0];
        console.log('🔑 Public key:', currentPublicKey);
      }
    } catch (pkError) {
      console.warn('⚠️ Could not fetch public key:', pkError);
      // Continue without public key
    }
    
    // Update UI
    elements.walletAddress.textContent = currentAddress;
    elements.walletPubkey.textContent = currentPublicKey || 'Not available';
    
    setStatus('connected', 'Connected');
    elements.connectSection.classList.add('hidden');
    elements.walletInfo.classList.remove('hidden');
    
    // Generate challenge
    generateChallenge();
    
    hideLoading();
  } catch (error) {
    console.error('❌ Failed to handle session:', error);
    showError('Failed to process wallet connection: ' + error.message);
    hideLoading();
  }
}

// Generate challenge message
function generateChallenge() {
  const timestamp = Date.now();
  const nonce = Math.random().toString(36).substring(2, 15);
  const userId = tg.initDataUnsafe?.user?.id || 'telegram_user';
  
  const message = `Verify ownership of Chia wallet:\n${currentAddress}\n\nTimestamp: ${timestamp}\nNonce: ${nonce}\nUser: ${userId}`;
  
  challengeData = {
    message,
    nonce,
    timestamp,
    address: currentAddress,
    userId
  };
  
  elements.challengeMessage.textContent = message;
  elements.challengeSection.classList.remove('hidden');
  
  console.log('📝 Challenge generated:', challengeData);
}

// Sign challenge
async function signChallenge() {
  try {
    showLoading('Requesting signature...');
    elements.signBtn.disabled = true;
    
    if (!currentSession || !challengeData) {
      throw new Error('No active session or challenge');
    }
    
    // Request signature using CHIP-0002
    const signature = await signClient.request({
      topic: currentSession.topic,
      chainId: CHIA_CHAIN,
      request: {
        method: 'chip0002_signMessage',
        params: {
          message: challengeData.message
        }
      }
    });
    
    console.log('✍️ Signature received:', signature);
    
    // Verify signature
    await verifySignature(signature);
    
  } catch (error) {
    console.error('❌ Signing failed:', error);
    showError('Failed to sign message: ' + error.message);
    elements.signBtn.disabled = false;
    hideLoading();
  }
}

// Verify signature via MintGarden API
async function verifySignature(signature) {
  try {
    showLoading('Verifying signature...');
    
    const verificationData = {
      address: currentAddress,
      message: challengeData.message,
      signature: signature,
      publicKey: currentPublicKey,
      userId: challengeData.userId,
      timestamp: challengeData.timestamp
    };
    
    // Send data back to Telegram bot
    tg.sendData(JSON.stringify(verificationData));
    
    // Show success UI (bot will handle actual verification)
    showResult({
      verified: true,
      message: 'Signature submitted successfully!',
      details: `Your wallet verification request has been sent.\n\nAddress: ${currentAddress}\n\nThe bot will confirm verification shortly.`
    });
    
    hideLoading();
    
    // Close the web app after 3 seconds
    setTimeout(() => {
      tg.close();
    }, 3000);
    
  } catch (error) {
    console.error('❌ Verification failed:', error);
    showError('Verification failed: ' + error.message);
    hideLoading();
  }
}

// UI Helper Functions
function setStatus(type, text) {
  elements.statusBadge.className = `status-badge ${type}`;
  elements.statusText.textContent = text;
}

function showLoading(text) {
  elements.loadingText.textContent = text;
  elements.loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
  elements.loadingOverlay.classList.add('hidden');
}

function showError(message) {
  elements.errorMessage.textContent = message;
  elements.errorSection.classList.remove('hidden');
  hideLoading();
}

function showResult(result) {
  elements.challengeSection.classList.add('hidden');
  elements.resultSection.classList.remove('hidden');
  
  if (result.verified) {
    elements.resultCard.classList.add('success');
    elements.resultIcon.textContent = '✅';
  } else {
    elements.resultCard.classList.add('error');
    elements.resultIcon.textContent = '❌';
  }
  
  elements.resultMessage.textContent = result.message;
  elements.resultDetails.textContent = result.details || '';
}

function reset() {
  // Disconnect session
  if (signClient && currentSession) {
    signClient.disconnect({
      topic: currentSession.topic,
      reason: getSdkError('USER_DISCONNECTED')
    });
  }
  
  // Reset state
  currentSession = null;
  currentAddress = null;
  currentPublicKey = null;
  challengeData = null;
  
  // Reset UI
  elements.connectSection.classList.remove('hidden');
  elements.walletInfo.classList.add('hidden');
  elements.challengeSection.classList.add('hidden');
  elements.resultSection.classList.add('hidden');
  elements.errorSection.classList.add('hidden');
  elements.resultCard.classList.remove('success', 'error');
  elements.signBtn.disabled = false;
  
  setStatus('disconnected', 'Disconnected');
}

function isMobile() {
  return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
}

// Initialize on load
window.addEventListener('load', () => {
  initWalletConnect();
});
