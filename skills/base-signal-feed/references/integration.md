# Base Signal Feed API Integration

This document explains how to integrate with the Base Signal Feed API.

## Authentication

The API uses a payment-based authentication model. To access the protected endpoints, you must send at least 0.0001 ETH to the service wallet on the Base network.

- **Service Wallet Address:** `0xA28F38d6F607b35a718C3e6193E7B622246d5a2B`
- **Network:** Base
- **Amount:** >= 0.0001 ETH
- **Validity:** Payments are valid for 30 days.

Include your wallet address in the `x-payer-address` header with every request.

```
curl -H "x-payer-address: 0xYourWalletAddress" http://localhost:7071/signals
```

## Endpoints

### Health Check

- **Endpoint:** `GET /health`
- **Description:** Checks if the API server is running.
- **Returns:** `200 OK` with a JSON body `{"status": "ok"}`.

### Get Recent Signals

- **Endpoint:** `GET /signals`
- **Description:** Returns smart money swap signals from the last 24 hours.
- **Authentication:** Required.
- **Example:**
  ```bash
  curl -H "x-payer-address: 0xYourWalletAddress" http://localhost:7071/signals
  ```

### Get New Pairs

- **Endpoint:** `GET /pairs/new`
- **Description:** Returns newly detected token pairs with safety and liquidity data.
- **Authentication:** Required.
- **Example:**
  ```bash
  curl -H "x-payer-address: 0xYourWalletAddress" http://localhost:7071/pairs/new
  ```

### Score a Token

- **Endpoint:** `GET /signals/score?token=<token_address>`
- **Description:** Scores a specific token based on wallet reputation, liquidity, and safety checks.
- **Authentication:** Required.
- **Query Parameters:**
  - `token` (required): The contract address of the token to score.
- **Example:**
  ```bash
  curl -H "x-payer-address: 0xYourWalletAddress" "http://localhost:7071/signals/score?token=0x123..."
  ```
