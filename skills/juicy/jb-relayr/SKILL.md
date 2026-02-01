---
name: jb-relayr
description: Relayr API reference for multi-chain transaction bundling. Pay gas on one chain, execute on many. Used for omnichain deployments, cross-chain operations, and meta-transactions.
---

# Relayr: Multi-Chain Transaction Bundling

Relayr is a meta-transaction relay service by 0xBASED that bundles transactions across chains. Users sign transactions for multiple chains, pay gas on one chain, and Relayr relayers execute on all others.

## Overview

```
1. User signs ERC2771 forward requests for each target chain
2. POST to Relayr API to get quote with payment options
3. User selects which chain to pay on
4. User sends single payment transaction
5. Relayr relayers execute on all other chains
6. Poll for bundle completion status
```

## API Base URLs

```
Production API: https://api.relayr.ba5ed.com
Dashboard: https://relayr.ba5ed.com
```

## Authentication

**No API key required.** Relayr is permissionless. Anyone can submit bundles.

---

## API Endpoints

### 1. Create Bundle Quote

```
POST /v1/bundle/prepaid
```

Creates a bundle of transactions and returns payment options.

**Request Body:**
```json
{
  "transactions": [
    {
      "chain": 1,
      "target": "0x...",
      "data": "0x...",
      "value": "0"
    }
  ],
  "virtual_nonce_mode": "Disabled"
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `chain` | number | Target chain ID |
| `target` | string | Contract to call (usually ERC2771Forwarder) |
| `data` | string | Encoded calldata |
| `value` | string | ETH value in wei (usually "0" for meta-txs) |
| `virtual_nonce_mode` | string | "Disabled" or "Enabled" for sequential ordering |

**Response:**
```json
{
  "bundle_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "payment_info": [
    {
      "chain": 1,
      "target": "0x...",
      "amount": "1234567890",
      "calldata": "0x..."
    },
    {
      "chain": 10,
      "target": "0x...",
      "amount": "987654321",
      "calldata": "0x..."
    }
  ],
  "per_txn": [
    {
      "txn_uuid": "...",
      "chain": 1,
      "gas_cost": "500000",
      "status": "Quoted"
    }
  ],
  "txn_uuids": ["uuid1", "uuid2"]
}
```

**Response Fields:**
| Field | Description |
|-------|-------------|
| `bundle_uuid` | Unique identifier for tracking |
| `payment_info` | Array of payment options (one per supported chain) |
| `payment_info[].chain` | Chain ID to pay on |
| `payment_info[].target` | Address to send payment to |
| `payment_info[].amount` | Wei amount to pay |
| `payment_info[].calldata` | Transaction data for payment |
| `per_txn` | Per-transaction details |
| `txn_uuids` | Array of transaction UUIDs |

---

### 2. Get Bundle Status

```
GET /v1/bundle/{bundle_uuid}
```

Poll this endpoint to check execution status.

**Response:**
```json
{
  "bundle_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "payment_received": true,
  "payment_chain": 1,
  "transactions": [
    {
      "txn_uuid": "...",
      "chain": 1,
      "status": "Success",
      "tx_hash": "0x...",
      "block_number": 12345678
    },
    {
      "txn_uuid": "...",
      "chain": 10,
      "status": "Pending",
      "tx_hash": null,
      "block_number": null
    }
  ]
}
```

---

### 3. Get Transaction Status

```
GET /v1/transaction/{txn_uuid}
```

Get status of individual transaction within a bundle.

---

## Transaction Status Values

| Status | Meaning |
|--------|---------|
| `Quoted` | Bundle created, awaiting payment |
| `PaymentReceived` | Payment confirmed, queued for execution |
| `Pending` | Transaction submitted, awaiting confirmation |
| `Success` | Transaction confirmed on-chain |
| `Completed` | Alias for Success |
| `Failed` | Transaction reverted |
| `Expired` | Payment not received within deadline (48h) |

---

## ERC2771 Forward Request Format

Relayr uses ERC2771 meta-transactions. The forwarder contract validates signatures and executes calls with the original sender preserved via `_msgSender()`.

### TypedData Domain

```javascript
const domain = {
  name: 'Juicebox',           // Or actual contract name
  version: '1',
  chainId: 1,                 // Target chain ID
  verifyingContract: '0x...'  // ERC2771Forwarder address
};
```

### TypedData Types

```javascript
const types = {
  ForwardRequest: [
    { name: 'from', type: 'address' },
    { name: 'to', type: 'address' },
    { name: 'value', type: 'uint256' },
    { name: 'gas', type: 'uint256' },
    { name: 'nonce', type: 'uint256' },
    { name: 'deadline', type: 'uint48' },
    { name: 'data', type: 'bytes' }
  ]
};
```

### Message Fields

| Field | Type | Description |
|-------|------|-------------|
| `from` | address | Original signer address |
| `to` | address | Target contract to call |
| `value` | uint256 | ETH to forward (usually 0) |
| `gas` | uint256 | Gas limit for execution |
| `nonce` | uint256 | User's forwarder nonce (query from contract) |
| `deadline` | uint48 | Unix timestamp expiry (max 48 hours from now) |
| `data` | bytes | Encoded function calldata |

### Getting the Nonce

Query the forwarder contract for the user's current nonce:

```javascript
const forwarder = new ethers.Contract(forwarderAddress, [
  'function nonces(address) view returns (uint256)'
], provider);

const nonce = await forwarder.nonces(userAddress);
```

---

## Complete JavaScript Example

```javascript
import { ethers } from 'ethers';

const RELAYR_API = 'https://api.relayr.ba5ed.com';

// ERC2771Forwarder addresses (same on all chains - deterministic deployment)
const FORWARDER = {
  1: '0x...', // Ethereum mainnet
  10: '0x...', // Optimism
  8453: '0x...', // Base
  42161: '0x...' // Arbitrum
};

/**
 * Deploy or execute across multiple chains with single payment
 */
async function executeOmnichain(signer, targetChains, targetContract, calldata) {
  const address = await signer.getAddress();
  const signedRequests = [];

  // Step 1: Sign forward request for each chain
  for (const chainId of targetChains) {
    // Get nonce from forwarder contract
    const nonce = await getNonce(chainId, address);

    const domain = {
      name: 'Juicebox',
      version: '1',
      chainId: chainId,
      verifyingContract: FORWARDER[chainId]
    };

    const types = {
      ForwardRequest: [
        { name: 'from', type: 'address' },
        { name: 'to', type: 'address' },
        { name: 'value', type: 'uint256' },
        { name: 'gas', type: 'uint256' },
        { name: 'nonce', type: 'uint256' },
        { name: 'deadline', type: 'uint48' },
        { name: 'data', type: 'bytes' }
      ]
    };

    // 48-hour deadline (maximum allowed)
    const deadline = Math.floor(Date.now() / 1000) + 48 * 60 * 60;

    const message = {
      from: address,
      to: targetContract,
      value: '0',
      gas: '1000000',
      nonce: nonce,
      deadline: deadline,
      data: calldata
    };

    // Sign the typed data
    const signature = await signer.signTypedData(domain, types, message);

    // Encode for forwarder.execute()
    const forwarderAbi = [
      'function execute((address from, address to, uint256 value, uint256 gas, uint256 nonce, uint48 deadline, bytes data) request, bytes signature)'
    ];
    const iface = new ethers.Interface(forwarderAbi);
    const encodedData = iface.encodeFunctionData('execute', [
      [message.from, message.to, message.value, message.gas, message.nonce, message.deadline, message.data],
      signature
    ]);

    signedRequests.push({
      chain: chainId,
      target: FORWARDER[chainId],
      data: encodedData,
      value: '0'
    });
  }

  // Step 2: Get quote from Relayr
  const quoteResponse = await fetch(`${RELAYR_API}/v1/bundle/prepaid`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      transactions: signedRequests,
      virtual_nonce_mode: 'Disabled'
    })
  });

  if (!quoteResponse.ok) {
    throw new Error(`Quote failed: ${quoteResponse.statusText}`);
  }

  const quote = await quoteResponse.json();
  console.log('Bundle UUID:', quote.bundle_uuid);
  console.log('Payment options:', quote.payment_info.map(p =>
    `Chain ${p.chain}: ${ethers.formatEther(p.amount)} ETH`
  ));

  return quote;
}

/**
 * Execute payment on chosen chain
 */
async function payForBundle(signer, paymentInfo) {
  const tx = await signer.sendTransaction({
    to: paymentInfo.target,
    value: paymentInfo.amount,
    data: paymentInfo.calldata
  });

  console.log('Payment tx:', tx.hash);
  await tx.wait();
  console.log('Payment confirmed');

  return tx;
}

/**
 * Poll until all transactions complete
 */
async function waitForCompletion(bundleUuid, onUpdate) {
  while (true) {
    const response = await fetch(`${RELAYR_API}/v1/bundle/${bundleUuid}`);
    const status = await response.json();

    if (onUpdate) onUpdate(status);

    const allDone = status.transactions.every(
      tx => ['Success', 'Completed', 'Failed'].includes(tx.status)
    );

    if (allDone) {
      const anyFailed = status.transactions.some(tx => tx.status === 'Failed');
      if (anyFailed) {
        const failed = status.transactions.filter(tx => tx.status === 'Failed');
        throw new Error(`Transactions failed on chains: ${failed.map(t => t.chain).join(', ')}`);
      }
      return status;
    }

    console.log('Status:', status.transactions.map(t => `Chain ${t.chain}: ${t.status}`).join(', '));
    await new Promise(r => setTimeout(r, 3000));
  }
}

/**
 * Helper: Get nonce from forwarder on specific chain
 */
async function getNonce(chainId, address) {
  const rpcUrls = {
    1: 'https://eth.llamarpc.com',
    10: 'https://mainnet.optimism.io',
    8453: 'https://mainnet.base.org',
    42161: 'https://arb1.arbitrum.io/rpc'
  };

  const provider = new ethers.JsonRpcProvider(rpcUrls[chainId]);
  const forwarder = new ethers.Contract(
    FORWARDER[chainId],
    ['function nonces(address) view returns (uint256)'],
    provider
  );

  return await forwarder.nonces(address);
}

/**
 * Complete flow example
 */
async function main() {
  const provider = new ethers.BrowserProvider(window.ethereum);
  const signer = await provider.getSigner();

  // Example: Deploy to Ethereum, Optimism, and Base
  const targetChains = [1, 10, 8453];
  const targetContract = '0x...'; // JBController
  const calldata = '0x...'; // launchProjectFor encoded

  // Get quote
  const quote = await executeOmnichain(signer, targetChains, targetContract, calldata);

  // Find cheapest payment option
  const cheapest = quote.payment_info.reduce((min, p) =>
    BigInt(p.amount) < BigInt(min.amount) ? p : min
  );

  console.log(`Paying ${ethers.formatEther(cheapest.amount)} ETH on chain ${cheapest.chain}`);

  // Switch chain if needed and pay
  // ... chain switching logic ...
  await payForBundle(signer, cheapest);

  // Wait for all chains to complete
  const result = await waitForCompletion(quote.bundle_uuid, (status) => {
    console.log('Update:', status.transactions.map(t => t.status));
  });

  console.log('All transactions complete!');
  console.log('Tx hashes:', result.transactions.map(t => `${t.chain}: ${t.tx_hash}`));
}
```

---

## RelayrClient Class

```javascript
class RelayrClient {
  constructor(apiUrl = 'https://api.relayr.ba5ed.com') {
    this.api = apiUrl;
  }

  async createBundle(transactions) {
    const response = await fetch(`${this.api}/v1/bundle/prepaid`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transactions,
        virtual_nonce_mode: 'Disabled'
      })
    });

    if (!response.ok) {
      throw new Error(`Relayr quote failed: ${response.statusText}`);
    }

    return await response.json();
  }

  async getBundleStatus(bundleUuid) {
    const response = await fetch(`${this.api}/v1/bundle/${bundleUuid}`);
    return await response.json();
  }

  async getTransactionStatus(txnUuid) {
    const response = await fetch(`${this.api}/v1/transaction/${txnUuid}`);
    return await response.json();
  }

  async waitForCompletion(bundleUuid, options = {}) {
    const { pollInterval = 3000, timeout = 600000, onUpdate } = options;
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const status = await this.getBundleStatus(bundleUuid);

      if (onUpdate) onUpdate(status);

      const allDone = status.transactions.every(
        tx => ['Success', 'Completed', 'Failed'].includes(tx.status)
      );

      if (allDone) {
        return status;
      }

      await new Promise(r => setTimeout(r, pollInterval));
    }

    throw new Error('Bundle completion timeout');
  }
}
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Quote failed` | Invalid transaction data | Check calldata encoding |
| `Nonce too low` | Nonce already used | Query fresh nonce from forwarder |
| `Deadline expired` | Signature expired | Re-sign with new deadline |
| `Insufficient payment` | Gas price changed | Request new quote |
| `Transaction reverted` | Contract execution failed | Debug on target chain explorer |

---

## Best Practices

1. **Always quote fresh** - Gas prices fluctuate, get a new quote immediately before paying
2. **Set reasonable gas limits** - Too low causes reverts, too high is expensive
3. **Use 48-hour deadlines** - Maximum allowed, gives time for execution
4. **Handle chain switching** - Users may need to switch wallets to pay on different chain
5. **Poll with backoff** - Start at 2-3s, increase to 10s after 30 seconds
6. **Verify nonces** - Always query fresh nonce from forwarder contract
7. **Handle partial failures** - Some chains may succeed while others fail

---

## Use Cases

- **Omnichain project deployment** - Deploy Juicebox project to multiple chains at once
- **Cross-chain configuration** - Update settings across all chains simultaneously
- **Multi-chain token operations** - Coordinate token actions across networks
- **Batch transactions** - Execute multiple transactions with single payment

---

## Related Skills

- `/jb-bendystraw` - Query cross-chain data after deployment
- `/jb-omnichain-ui` - Build UIs using Relayr
- `/jb-project` - Project deployment configurations
