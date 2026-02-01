#!/usr/bin/env node

/**
 * Warren Direct Deploy - Self-contained on-chain deployment script
 *
 * Deploys HTML/files permanently to MegaETH blockchain via SSTORE2.
 * No external dependencies besides ethers.js.
 *
 * Setup:  npm init -y && npm install ethers
 * Usage:  PRIVATE_KEY=0x... node deploy.js --html "<h1>Hello</h1>" --name "My Site"
 *         PRIVATE_KEY=0x... node deploy.js --file ./site.html --name "My Site"
 */

const { ethers } = require('ethers');
const fs = require('fs');

// ============================================================================
// Configuration
// ============================================================================

const RPC_URL = process.env.RPC_URL || 'https://carrot.megaeth.com/rpc';
const CHAIN_ID = parseInt(process.env.CHAIN_ID || '6343');
const GENESIS_KEY_ADDRESS = process.env.GENESIS_KEY_ADDRESS || '0x954a7cd0e2f03041A6Abb203f4Cfd8E62D2aa692';
const MASTER_NFT_ADDRESS = process.env.MASTER_NFT_ADDRESS || '0x7bb4233017CFd4f938C61d1dCeEF4eBE837b05F9';
const CHUNK_SIZE = parseInt(process.env.CHUNK_SIZE || '100000');
const GROUP_SIZE = parseInt(process.env.GROUP_SIZE || '500');
const BATCH_SIZE = 5;
const RETRY_MAX = 3;
const RETRY_DELAY = 2000;

// ============================================================================
// Inline ABIs & Bytecode (no external files needed)
// ============================================================================

const PAGE_BYTECODE = '0x60a0604052346100e45761025c80380380610019816100fc565b9283398101906020818303126100e4578051906001600160401b0382116100e4570181601f820112156100e4578051906001600160401b0382116100e85761006a601f8301601f19166020016100fc565b92828452602083830101116100e457815f9260208093018386015e8301015280518060401b6bfe61000180600a3d393df3000161fffe8211830152600b8101601583015ff09182156100d7575260805260405161013a908161012282396080518181816044015260d50152f35b63301164255f526004601cfd5b5f80fd5b634e487b7160e01b5f52604160045260245ffd5b6040519190601f01601f191682016001600160401b038111838210176100e85760405256fe6080806040526004361015610012575f80fd5b5f3560e01c9081634822da1c146100c357506357de26a414610032575f80fd5b346100bf575f3660031901126100bf577f00000000000000000000000000000000000000000000000000000000000000006020608060405180935f19813b0164ffffffffff16905f6021830191601f8501903c808252016040810193846040528385528051938491826060850152018383015e5f828483010152603f1992601f8019910116810103010190f35b5f80fd5b346100bf575f3660031901126100bf577f00000000000000000000000000000000000000000000000000000000000000006001600160a01b03168152602090f3fea2646970667358221220fe4f8a378a0b003d3e1438e45234630293b1a4f7cf94a9f28a4c2d2531789b9d64736f6c634300081a0033';

const PAGE_ABI = [{"type":"constructor","inputs":[{"name":"_content","type":"bytes","internalType":"bytes"}],"stateMutability":"nonpayable"}];

const MASTER_NFT_ABI = [
  {"type":"function","name":"mint","inputs":[{"name":"to","type":"address"},{"name":"rootChunk","type":"address"},{"name":"depth","type":"uint8"},{"name":"totalSize","type":"uint256"},{"name":"siteType","type":"uint8"}],"outputs":[{"name":"tokenId","type":"uint256"}],"stateMutability":"nonpayable"},
  {"type":"function","name":"sites","inputs":[{"name":"","type":"uint256"}],"outputs":[{"name":"rootChunk","type":"address"},{"name":"depth","type":"uint8"},{"name":"totalSize","type":"uint256"},{"name":"siteType","type":"uint8"},{"name":"creator","type":"address"},{"name":"version","type":"uint256"},{"name":"createdAt","type":"uint256"},{"name":"updatedAt","type":"uint256"}],"stateMutability":"view"}
];

const GENESIS_KEY_ABI = [
  'function mint() external payable',
  'function balanceOf(address) view returns (uint256)',
];

const SITE_TYPES = { file: 0, image: 3, video: 4, audio: 5, script: 7 };

// ============================================================================
// Helpers
// ============================================================================

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

function isRetryable(e) {
  const msg = (e.message || '').toLowerCase();
  return msg.includes('rate') || msg.includes('429') || msg.includes('timeout') || msg.includes('nonce') || e.code === -32022;
}

async function withRetry(fn, label) {
  for (let i = 1; i <= RETRY_MAX; i++) {
    try { return await fn(); } catch (e) {
      if (isRetryable(e) && i < RETRY_MAX) {
        console.log(`  ⚠ ${label} attempt ${i} failed, retrying...`);
        await sleep(RETRY_DELAY * i);
      } else throw e;
    }
  }
}

// ============================================================================
// Genesis Key NFT
// ============================================================================

async function ensureGenesisKey(wallet) {
  const nft = new ethers.Contract(GENESIS_KEY_ADDRESS, GENESIS_KEY_ABI, wallet);
  const bal = await nft.balanceOf(wallet.address);
  if (Number(bal) > 0) {
    console.log('🔑 Genesis Key NFT: ✅ owned');
    return;
  }
  console.log('🔑 Minting Genesis Key NFT (free)...');
  const tx = await nft.mint({ gasLimit: 500000n });
  await tx.wait();
  console.log('  ✅ Genesis Key minted!');
}

// ============================================================================
// Page Deployment
// ============================================================================

async function deployPage(wallet, provider, content, nonce, label) {
  return withRetry(async () => {
    const factory = new ethers.ContractFactory(PAGE_ABI, PAGE_BYTECODE, wallet);
    const deployTx = await factory.getDeployTransaction(content);
    deployTx.gasLimit = 100_000_000n;
    if (nonce !== undefined) deployTx.nonce = nonce;
    const tx = await wallet.sendTransaction(deployTx);
    const receipt = await tx.wait();
    const code = await provider.getCode(receipt.contractAddress);
    if (!code || code.length <= 2) throw new Error(`${label}: verification failed`);
    return receipt;
  }, label);
}

// ============================================================================
// Fractal Tree
// ============================================================================

function chunkBuffer(buf, size) {
  const chunks = [];
  for (let i = 0; i < buf.length; i += size) chunks.push(buf.subarray(i, Math.min(i + size, buf.length)));
  return chunks;
}

async function deployChunks(wallet, provider, chunks) {
  const addrs = [];
  console.log(`\n📦 Phase 1: Deploying ${chunks.length} chunk(s)...`);
  for (let bs = 0; bs < chunks.length; bs += BATCH_SIZE) {
    const be = Math.min(bs + BATCH_SIZE, chunks.length);
    const batch = chunks.slice(bs, be);
    const baseNonce = await provider.getTransactionCount(wallet.address, 'latest');
    const results = await Promise.all(batch.map(async (chunk, idx) => {
      await sleep(idx * 50);
      const receipt = await deployPage(wallet, provider, chunk, baseNonce + idx, `Chunk ${bs + idx + 1}/${chunks.length}`);
      return { receipt, idx: bs + idx };
    }));
    for (const { receipt, idx } of results.sort((a, b) => a.idx - b.idx)) {
      addrs.push(receipt.contractAddress);
      console.log(`  ✅ Chunk ${idx + 1}/${chunks.length}: ${receipt.contractAddress}`);
    }
    if (be < chunks.length) await sleep(300);
  }
  return addrs;
}

async function buildTree(wallet, provider, addresses) {
  let level = [...addresses];
  let depth = 0;
  while (level.length > 1) {
    depth++;
    const parent = [];
    const groups = Math.ceil(level.length / GROUP_SIZE);
    console.log(`\n🌲 Phase 2: Building tree depth ${depth} (${groups} node(s))...`);
    const baseNonce = await provider.getTransactionCount(wallet.address, 'latest');
    for (let i = 0; i < level.length; i += GROUP_SIZE) {
      const group = level.slice(i, i + GROUP_SIZE);
      const concat = Buffer.concat(group.map(a => Buffer.from(ethers.getBytes(a))));
      const ni = Math.floor(i / GROUP_SIZE);
      await sleep(ni * 50);
      const receipt = await deployPage(wallet, provider, concat, baseNonce + ni, `Node D${depth}-${ni + 1}/${groups}`);
      parent.push(receipt.contractAddress);
      console.log(`  ✅ Node D${depth}-${ni + 1}: ${receipt.contractAddress}`);
    }
    level = parent;
  }
  return { rootChunk: level[0], depth };
}

// ============================================================================
// MasterNFT Mint
// ============================================================================

async function mintSite(wallet, rootChunk, depth, totalSize, siteType) {
  console.log('\n🎨 Phase 3: Minting site NFT...');
  const master = new ethers.Contract(MASTER_NFT_ADDRESS, MASTER_NFT_ABI, wallet);
  const tx = await master.mint(wallet.address, rootChunk, depth, totalSize, siteType, { gasLimit: 100_000_000n });
  const receipt = await tx.wait();
  const topic = ethers.id('Transfer(address,address,uint256)');
  const log = receipt.logs.find(l => l.topics?.[0] === topic);
  const tokenId = log?.topics?.[3] ? Number(BigInt(log.topics[3])) : null;
  console.log(`  ✅ Token ID: ${tokenId}, Gas: ${receipt.gasUsed}`);
  return tokenId;
}

// ============================================================================
// Main
// ============================================================================

async function deploy(privateKey, content, options = {}) {
  const { name = 'Untitled', siteType = 'file' } = options;
  const provider = new ethers.JsonRpcProvider(RPC_URL, CHAIN_ID);
  const wallet = new ethers.Wallet(privateKey, provider);

  console.log('='.repeat(60));
  console.log('Warren Direct Deploy');
  console.log('='.repeat(60));
  console.log(`Address: ${wallet.address}`);
  console.log(`Network: MegaETH Testnet (Chain ${CHAIN_ID})`);
  console.log(`Content: ${content.length} bytes | Name: ${name}`);

  const balance = await provider.getBalance(wallet.address);
  console.log(`Balance: ${ethers.formatEther(balance)} ETH`);
  if (balance === 0n) throw new Error('No ETH. Get testnet ETH from https://docs.megaeth.com/faucet');

  await ensureGenesisKey(wallet);

  const chunks = chunkBuffer(content, CHUNK_SIZE);
  const addrs = await deployChunks(wallet, provider, chunks);

  let rootChunk, depth;
  if (addrs.length === 1) { rootChunk = addrs[0]; depth = 0; }
  else { ({ rootChunk, depth } = await buildTree(wallet, provider, addrs)); }

  const tokenId = await mintSite(wallet, rootChunk, depth, content.length, SITE_TYPES[siteType] ?? 0);
  const url = `https://megawarren.xyz/loader.html?registry=${MASTER_NFT_ADDRESS}&id=${tokenId}`;

  console.log('\n' + '='.repeat(60));
  console.log('🎉 Deployment Complete!');
  console.log('='.repeat(60));
  console.log(`Token ID: ${tokenId}`);
  console.log(`URL: ${url}`);

  return { tokenId, rootChunk, depth, url };
}

// ============================================================================
// CLI
// ============================================================================

async function main() {
  const args = process.argv.slice(2);
  const getArg = (n) => { const i = args.indexOf(`--${n}`); return i >= 0 ? args[i + 1] : undefined; };

  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Warren Direct Deploy - Deploy HTML/files to MegaETH blockchain

Usage:
  PRIVATE_KEY=0x... node deploy.js --html "<h1>Hello</h1>" [options]
  PRIVATE_KEY=0x... node deploy.js --file ./site.html [options]

Options:
  --private-key <key>   Wallet private key (or set PRIVATE_KEY env)
  --html <string>       HTML content to deploy
  --file <path>         Path to file to deploy
  --name <name>         Site name (default: "Untitled")
  --type <type>         file|image|video|audio|script (default: "file")

Prerequisites:
  1. npm install ethers (run 'bash setup.sh' for quick setup)
  2. Get testnet ETH: https://docs.megaeth.com/faucet
  3. Genesis Key NFT auto-mints if needed (free on testnet)
`);
    process.exit(0);
  }

  const privateKey = getArg('private-key') || process.env.PRIVATE_KEY;
  if (!privateKey) { console.error('Error: set PRIVATE_KEY env or use --private-key'); process.exit(1); }

  const filePath = getArg('file');
  const htmlString = getArg('html');
  let content;

  if (filePath) content = fs.readFileSync(filePath);
  else if (htmlString) content = Buffer.from(htmlString, 'utf8');
  else {
    const chunks = [];
    process.stdin.resume();
    for await (const c of process.stdin) chunks.push(c);
    content = Buffer.concat(chunks);
    if (!content.length) { console.error('Error: provide --file, --html, or pipe stdin'); process.exit(1); }
  }

  if (content.length > 500 * 1024) { console.error(`Error: ${content.length} bytes exceeds 500KB limit`); process.exit(1); }

  try {
    const result = await deploy(privateKey, content, { name: getArg('name') || 'Untitled', siteType: getArg('type') || 'file' });
    console.log('\n--- JSON ---');
    console.log(JSON.stringify(result, null, 2));
  } catch (e) { console.error(`\n❌ Failed: ${e.message}`); process.exit(1); }
}

main();
