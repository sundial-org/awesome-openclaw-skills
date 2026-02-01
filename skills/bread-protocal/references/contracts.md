# Contract Reference

## Addresses (Base Mainnet)

```
BREAD Token:      0xAfcAF9e3c9360412cbAa8475ed85453170E75fD5
BreadBoxFactory:  0x089C91AcF43EC36c2f80B379faAC051614461220
Bakery:           0xB29cF791D4E7512B83C49291Be9A54b68b7064b5
Oven:             0xEdB551E65cA0F15F96b97bD5b6ad1E2Be30A36Ed
Airdrop:          0xDE81dBb8933d4765a7177771945255FDc531Be16
```

## Function Selectors

### Bakery

| Function | Selector | Notes |
|----------|----------|-------|
| `propose(string,string,string,string)` | `0x945f41ab` | name, symbol, description, imageUrl |
| `backProposal(uint256)` | `0x49729de1` | Send ETH with call |
| `withdrawBacking(uint256)` | `0x7a73ab9e` | Same day only |
| `claimTokens(uint256)` | `0x46e04a2f` | After launch |
| `claimRefund(uint256)` | `0x34735cd4` | After settlement, losers only |
| `settleDay(uint256)` | `0x7f2479d1` | Anyone can call after day ends |
| `launchToken(uint256)` | `0xf752dd8d` | Anyone can call for winner |
| `getCurrentDay()` | `0x82d4a36d` | View |
| `getTimeUntilSettlement()` | `0x8c65c81f` | View |
| `getDailyProposals(uint256)` | `0x3b8d5615` | View |
| `calculateProposalFee()` | `0x09adc596` | View |
| `calculateBackingFee(uint256)` | `0x7e8de4f4` | View |

### BreadBox

| Function | Selector | Notes |
|----------|----------|-------|
| `execute(address,uint256,bytes)` | `0x1cff79cd` | Main entry point |
| `remainingTodayBread()` | `0x8f8d7f99` | View |
| `remainingTodayEth()` | `0x6fb8e58a` | View |
| `owner()` | `0x8da5cb5b` | View |
| `sessionKey()` | `0xae0e62d1` | View |

### BREAD Token (ERC-20)

| Function | Selector | Notes |
|----------|----------|-------|
| `approve(address,uint256)` | `0x095ea7b3` | Standard ERC-20 |
| `transfer(address,uint256)` | `0xa9059cbb` | Standard ERC-20 |
| `balanceOf(address)` | `0x70a08231` | View |
| `allowance(address,address)` | `0xdd62ed3e` | View |

### BreadBoxFactory

| Function | Selector | Notes |
|----------|----------|-------|
| `createBreadBox(address,uint256,uint256)` | `0x8a4068dd` | sessionKey, breadLimit, ethLimit |
| `boxOf(address)` | `0x5c622a0e` | View: owner → BreadBox |
| `isBreadBox(address)` | `0x9c52a7f1` | View |

## ABI Snippets

### Bakery Core Functions

```json
[
  {
    "name": "propose",
    "type": "function",
    "inputs": [
      {"name": "name", "type": "string"},
      {"name": "symbol", "type": "string"},
      {"name": "description", "type": "string"},
      {"name": "imageUrl", "type": "string"}
    ],
    "outputs": [{"name": "proposalId", "type": "uint256"}]
  },
  {
    "name": "backProposal",
    "type": "function",
    "stateMutability": "payable",
    "inputs": [{"name": "proposalId", "type": "uint256"}],
    "outputs": []
  },
  {
    "name": "withdrawBacking",
    "type": "function",
    "inputs": [{"name": "proposalId", "type": "uint256"}],
    "outputs": []
  },
  {
    "name": "claimTokens",
    "type": "function",
    "inputs": [{"name": "proposalId", "type": "uint256"}],
    "outputs": [{"name": "", "type": "uint256"}]
  },
  {
    "name": "claimRefund",
    "type": "function",
    "inputs": [{"name": "proposalId", "type": "uint256"}],
    "outputs": [{"name": "", "type": "uint256"}]
  }
]
```

### BreadBox Execute

```json
[
  {
    "name": "execute",
    "type": "function",
    "inputs": [
      {"name": "target", "type": "address"},
      {"name": "value", "type": "uint256"},
      {"name": "data", "type": "bytes"}
    ],
    "outputs": [{"name": "", "type": "bytes"}]
  }
]
```

### Proposal Struct

```solidity
struct Proposal {
    uint256 id;
    address creator;        // BreadBox address
    string name;
    string symbol;
    string description;
    string imageUrl;
    uint256 ethRaised;
    uint256 breadFeePaid;
    uint256 uniqueBackers;
    uint256 createdAt;
    uint256 dayNumber;
    bool launched;
    bool settled;
}
```

### Backing Struct

```solidity
struct Backing {
    uint256 ethAmount;
    uint256 breadFeePaid;
    bool claimed;
}
```

## Encoding Examples

### Propose a Token

```javascript
import { encodeFunctionData, parseEther } from 'viem';

const proposeData = encodeFunctionData({
  abi: [{
    name: 'propose',
    type: 'function',
    inputs: [
      {name: 'name', type: 'string'},
      {name: 'symbol', type: 'string'},
      {name: 'description', type: 'string'},
      {name: 'imageUrl', type: 'string'}
    ]
  }],
  functionName: 'propose',
  args: [
    'CatCoin',
    'CAT',
    'A purrfect meme coin',
    'https://i.imgur.com/cat.png'
  ]
});

// Call through BreadBox
const executeData = encodeFunctionData({
  abi: [{
    name: 'execute',
    type: 'function',
    inputs: [
      {name: 'target', type: 'address'},
      {name: 'value', type: 'uint256'},
      {name: 'data', type: 'bytes'}
    ]
  }],
  functionName: 'execute',
  args: [
    '0xB29cF791D4E7512B83C49291Be9A54b68b7064b5', // Bakery
    0n, // No ETH
    proposeData
  ]
});
```

### Back a Proposal

```javascript
// First approve BREAD
const approveData = encodeFunctionData({
  abi: [{
    name: 'approve',
    type: 'function',
    inputs: [
      {name: 'spender', type: 'address'},
      {name: 'amount', type: 'uint256'}
    ]
  }],
  functionName: 'approve',
  args: [
    '0xB29cF791D4E7512B83C49291Be9A54b68b7064b5', // Bakery
    parseEther('100') // 100 BREAD for 1 ETH backing
  ]
});

// Then back
const backData = encodeFunctionData({
  abi: [{
    name: 'backProposal',
    type: 'function',
    inputs: [{name: 'proposalId', type: 'uint256'}]
  }],
  functionName: 'backProposal',
  args: [1n] // Proposal ID
});

// Execute with 0.5 ETH
const executeData = encodeFunctionData({
  abi: [{
    name: 'execute',
    type: 'function',
    inputs: [
      {name: 'target', type: 'address'},
      {name: 'value', type: 'uint256'},
      {name: 'data', type: 'bytes'}
    ]
  }],
  functionName: 'execute',
  args: [
    '0xB29cF791D4E7512B83C49291Be9A54b68b7064b5', // Bakery
    parseEther('0.5'), // 0.5 ETH backing
    backData
  ]
});
```

## Chain Info

| Property | Value |
|----------|-------|
| Chain | Base Mainnet |
| Chain ID | 8453 |
| RPC | https://mainnet.base.org |
| Block Explorer | https://basescan.org |
| Native Token | ETH |
