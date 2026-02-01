const { ethers } = require("ethers");

// ============ CONFIG ============
const REGISTRY_ADDRESS = "0x8a11871aCFCb879cac814D02446b2795182a4c07"; // V3 Soulbound
const RPC_URL = process.env.BASE_RPC || "https://mainnet.base.org";
const REGISTRATION_FEE = "0.0001"; // ETH

// ============ ABI ============
const ABI = [
  // Read Functions
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function agents(uint256 tokenId) view returns (string endpoints, address wallet, bool isVerified)",
  "function tokenURI(uint256 tokenId) view returns (string)",
  
  // Write Functions
  "function registerAgent(address to, string uri, string endpoints, address agentWallet) payable returns (uint256)",
  "function logReputation(uint256 agentId, uint8 score) payable",
  
  // Events (Crucial for reading history)
  "event ReputationLogged(uint256 indexed agentId, uint8 score)"
];

// ============ TOOL LOGIC ============
async function getProvider() {
  return new ethers.JsonRpcProvider(RPC_URL);
}

async function getWallet(provider) {
  const pk = process.env.WALLET_PRIVATE_KEY || process.env.DEPLOYER_PRIVATE_KEY;
  if (!pk) throw new Error("Wallet private key not found in env (WALLET_PRIVATE_KEY)");
  return new ethers.Wallet(pk, provider);
}

/**
 * Check verification status
 */
async function status({ query }) {
  const provider = await getProvider();
  const contract = new ethers.Contract(REGISTRY_ADDRESS, ABI, provider);

  if (!isNaN(query)) {
    try {
      const owner = await contract.ownerOf(query);
      return `✅ Agent #${query} is VERIFIED.\nOwner: ${owner}`;
    } catch {
      return `❌ Agent #${query} NOT FOUND.`;
    }
  }
  return "🔍 Reverse lookup (Wallet -> ID) coming soon. Search by ID.";
}

/**
 * Lookup Agent Metadata
 */
async function lookup({ id }) {
  const provider = await getProvider();
  const contract = new ethers.Contract(REGISTRY_ADDRESS, ABI, provider);

  try {
    const [owner, profile, uri] = await Promise.all([
      contract.ownerOf(id),
      contract.agents(id),
      contract.tokenURI(id)
    ]);

    return JSON.stringify({
      id,
      owner,
      endpoints: profile.endpoints,
      wallet: profile.wallet,
      verified: profile.isVerified,
      uri
    }, null, 2);
  } catch (e) {
    return `❌ Error looking up Agent #${id}: ${e.message}`;
  }
}

/**
 * Calculate Reputation from Chain History
 */
async function reputation({ id }) {
  const provider = await getProvider();
  const contract = new ethers.Contract(REGISTRY_ADDRESS, ABI, provider);

  try {
    // 1. Define the filter (From Block 0 to Latest)
    const filter = contract.filters.ReputationLogged(id);
    
    // 2. Fetch all logs
    const logs = await contract.queryFilter(filter);

    if (logs.length === 0) {
      return JSON.stringify({
        id, 
        averageScore: 0, 
        totalReviews: 0, 
        status: "No History" 
      }, null, 2);
    }

    // 3. Calculate Average
    let totalScore = 0;
    logs.forEach(log => {
      totalScore += Number(log.args[1]); 
    });

    const average = (totalScore / logs.length).toFixed(2);

    return JSON.stringify({
      id,
      averageScore: average,
      totalReviews: logs.length,
      history: logs.map(l => Number(l.args[1])) // Returns array of past scores
    }, null, 2);

  } catch (e) {
    return `❌ Error calculating reputation: ${e.message}`;
  }
}

/**
 * Register Agent (Requires Wallet)
 */
async function register({ endpoints, uri, agentWallet }) {
  const provider = await getProvider();
  const wallet = await getWallet(provider);
  const contract = new ethers.Contract(REGISTRY_ADDRESS, ABI, wallet);

  const myAddress = wallet.address; 
  const agentWalletAddress = agentWallet || myAddress; 
  const metadataUri = uri || `https://moltbook.com/agent/${myAddress}`;
  const endpointsJson = typeof endpoints === 'string' ? endpoints : JSON.stringify(endpoints);

  console.log(`📝 Registering agent for ${myAddress}...`);

  try {
    const fee = ethers.parseEther(REGISTRATION_FEE);
    const tx = await contract.registerAgent(myAddress, metadataUri, endpointsJson, agentWalletAddress, { value: fee });

    console.log(`🚀 TX Sent: ${tx.hash}`);
    const receipt = await tx.wait();

    return `✅ REGISTRATION SUCCESS!\nTransaction: ${tx.hash}\nBlock: ${receipt.blockNumber}`;
  } catch (e) {
    return `❌ Registration Failed: ${e.message}`;
  }
}

/**
 * Log Reputation (Requires Wallet)
 */
async function rate({ agentId, score }) {
  const provider = await getProvider();
  const wallet = await getWallet(provider);
  const contract = new ethers.Contract(REGISTRY_ADDRESS, ABI, wallet);

  try {
    const fee = ethers.parseEther(REGISTRATION_FEE); 
    const tx = await contract.logReputation(agentId, score, { value: fee });

    console.log(`🚀 TX Sent: ${tx.hash}`);
    const receipt = await tx.wait();

    return `✅ REPUTATION LOGGED!\nTransaction: ${tx.hash}\nBlock: ${receipt.blockNumber}\nScore: ${score}/100.`;
  } catch (e) {
    return `❌ Reputation Logging Failed: ${e.message}`;
  }
}

// ============ EXPORT ============
module.exports = {
  status,
  lookup,
  reputation,
  register,
  rate
};
