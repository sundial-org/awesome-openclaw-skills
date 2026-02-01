#!/usr/bin/env node

const { ethers } = require('ethers');

const RPC_URL = process.env.BNB_RPC_URL || 'https://bsc-dataseed.binance.org/';
const provider = new ethers.JsonRpcProvider(RPC_URL);

// Minimal ERC20 ABI for balances and transfers
const ERC20_ABI = [
  'function balanceOf(address owner) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
  'function name() view returns (string)',
  'function transfer(address to, uint256 amount) returns (bool)'
];

async function getBalance(address) {
  const balance = await provider.getBalance(address);
  console.log(JSON.stringify({
    address,
    balance: ethers.formatEther(balance),
    unit: 'BNB',
    wei: balance.toString()
  }, null, 2));
}

async function getTokenBalance(tokenAddress, walletAddress) {
  const contract = new ethers.Contract(tokenAddress, ERC20_ABI, provider);
  const [balance, decimals, symbol, name] = await Promise.all([
    contract.balanceOf(walletAddress),
    contract.decimals(),
    contract.symbol().catch(() => 'UNKNOWN'),
    contract.name().catch(() => 'Unknown Token')
  ]);
  
  const formatted = ethers.formatUnits(balance, decimals);
  console.log(JSON.stringify({
    token: { address: tokenAddress, name, symbol, decimals: Number(decimals) },
    wallet: walletAddress,
    balance: formatted,
    raw: balance.toString()
  }, null, 2));
}

async function sendBNB(toAddress, amount, privateKey) {
  const wallet = new ethers.Wallet(privateKey, provider);
  const tx = await wallet.sendTransaction({
    to: toAddress,
    value: ethers.parseEther(amount)
  });
  
  console.log(JSON.stringify({
    status: 'submitted',
    hash: tx.hash,
    from: wallet.address,
    to: toAddress,
    amount: amount,
    unit: 'BNB'
  }, null, 2));
  
  console.error('Waiting for confirmation...');
  const receipt = await tx.wait();
  
  console.log(JSON.stringify({
    status: 'confirmed',
    hash: tx.hash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString()
  }, null, 2));
}

async function sendToken(tokenAddress, toAddress, amount, privateKey) {
  const wallet = new ethers.Wallet(privateKey, provider);
  const contract = new ethers.Contract(tokenAddress, ERC20_ABI, wallet);
  
  const [decimals, symbol] = await Promise.all([
    contract.decimals(),
    contract.symbol().catch(() => 'TOKEN')
  ]);
  
  const amountWei = ethers.parseUnits(amount, decimals);
  const tx = await contract.transfer(toAddress, amountWei);
  
  console.log(JSON.stringify({
    status: 'submitted',
    hash: tx.hash,
    from: wallet.address,
    to: toAddress,
    amount: amount,
    token: symbol,
    tokenAddress: tokenAddress
  }, null, 2));
  
  console.error('Waiting for confirmation...');
  const receipt = await tx.wait();
  
  console.log(JSON.stringify({
    status: 'confirmed',
    hash: tx.hash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString()
  }, null, 2));
}

function getAddress(privateKey) {
  const wallet = new ethers.Wallet(privateKey);
  console.log(JSON.stringify({
    address: wallet.address,
    publicKey: wallet.signingKey.publicKey
  }, null, 2));
}

async function getTx(txHash) {
  const [tx, receipt] = await Promise.all([
    provider.getTransaction(txHash),
    provider.getTransactionReceipt(txHash)
  ]);
  
  if (!tx) {
    console.log(JSON.stringify({ error: 'Transaction not found' }));
    return;
  }
  
  console.log(JSON.stringify({
    hash: tx.hash,
    from: tx.from,
    to: tx.to,
    value: ethers.formatEther(tx.value),
    gasPrice: ethers.formatUnits(tx.gasPrice || 0, 'gwei'),
    status: receipt ? (receipt.status === 1 ? 'success' : 'failed') : 'pending',
    blockNumber: receipt?.blockNumber || null,
    gasUsed: receipt?.gasUsed?.toString() || null
  }, null, 2));
}

// CLI
const [,, command, ...args] = process.argv;

function getKey(args) {
  const keyIndex = args.indexOf('--key');
  if (keyIndex !== -1 && args[keyIndex + 1]) {
    return args[keyIndex + 1];
  }
  return process.env.BNB_PRIVATE_KEY;
}

async function main() {
  try {
    switch (command) {
      case 'balance':
        if (!args[0]) throw new Error('Usage: bnb.js balance <address>');
        await getBalance(args[0]);
        break;
        
      case 'token-balance':
        if (!args[0] || !args[1]) throw new Error('Usage: bnb.js token-balance <token_address> <wallet_address>');
        await getTokenBalance(args[0], args[1]);
        break;
        
      case 'send':
        const sendKey = getKey(args);
        if (!args[0] || !args[1] || !sendKey) throw new Error('Usage: bnb.js send <to> <amount> --key <private_key>');
        await sendBNB(args[0], args[1], sendKey);
        break;
        
      case 'send-token':
        const tokenKey = getKey(args);
        if (!args[0] || !args[1] || !args[2] || !tokenKey) throw new Error('Usage: bnb.js send-token <token> <to> <amount> --key <private_key>');
        await sendToken(args[0], args[1], args[2], tokenKey);
        break;
        
      case 'address':
        if (!args[0]) throw new Error('Usage: bnb.js address <private_key>');
        getAddress(args[0]);
        break;
        
      case 'tx':
        if (!args[0]) throw new Error('Usage: bnb.js tx <tx_hash>');
        await getTx(args[0]);
        break;
        
      default:
        console.log(`BNB Chain CLI

Commands:
  balance <address>                          Check BNB balance
  token-balance <token> <wallet>             Check BEP-20 token balance
  send <to> <amount> --key <key>             Send BNB
  send-token <token> <to> <amount> --key     Send BEP-20 token
  address <private_key>                      Get address from private key
  tx <hash>                                  Get transaction details

Environment:
  BNB_PRIVATE_KEY    Default private key
  BNB_RPC_URL        Custom RPC (default: bsc-dataseed.binance.org)
`);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();
