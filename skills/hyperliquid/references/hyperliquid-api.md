# Hyperliquid Info API (read-only)

Base URL:
- `POST https://api.hyperliquid.xyz/info`
- Header: `Content-Type: application/json`

Docs:
- Info endpoint: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
- Perps: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals
- Spot: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/spot

## Core request bodies used in v1

### Perps: universe + contexts (preferred)

```json
{ "type": "metaAndAssetCtxs", "dex": "" }
```

Response shape:
- `[ meta, assetCtxs ]`
- `meta.universe[]` aligns by index with `assetCtxs[]`

Common perps ctx fields:
- `markPx`, `midPx`, `oraclePx`, `prevDayPx`
- `dayNtlVlm`
- `openInterest`
- `funding`
- `premium`
- `impactPxs`: `[buyImpactPx, sellImpactPx]`

### Order book

```json
{ "type": "l2Book", "coin": "BTC" }
```

Optional:
- `nSigFigs`: 2|3|4|5|null
- `mantissa`: 1|2|5 (only if `nSigFigs` is 5)

### Candles

```json
{
  "type": "candleSnapshot",
  "req": {
    "coin": "BTC",
    "interval": "1h",
    "startTime": 1700000000000,
    "endTime": 1700100000000
  }
}
```

Intervals: `1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 12h, 1d, 3d, 1w, 1M`

Candle fields:
- `t` open ms, `T` close ms
- `o,h,l,c` prices
- `v` base volume, `n` trades

### Quick prices (optional)

```json
{ "type": "allMids", "dex": "" }
```

## Account (read-only)

### Perps positions + margin

```json
{ "type": "clearinghouseState", "user": "0x...", "dex": "" }
```

Key fields:
- `assetPositions[]` (per-coin positions)
- `marginSummary` / `crossMarginSummary`
- `withdrawable`

### Spot balances

```json
{ "type": "spotClearinghouseState", "user": "0x..." }
```

### Open orders

```json
{ "type": "openOrders", "user": "0x...", "dex": "" }
```

### Fills

```json
{ "type": "userFills", "user": "0x...", "aggregateByTime": true }
```

## Notes

- Some responses have element limits for time ranges; paginate by advancing `startTime`.
- Spot coin naming can require `@<index>` mapping from `spotMeta.universe`.
- Common pitfall: using an **agent wallet** address can return empty results; query the address that actually owns the account/positions (master or sub-account).
