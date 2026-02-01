---
name: go4me
description: Send XCH to Twitter users via Go4Me address lookup. Use when sending Chia (XCH) to someone by their Twitter handle, looking up a Twitter user's XCH address, or tipping someone on Go4Me. Triggers on "send XCH to @user", "tip @user", "lookup @user on go4me", "what's @user's XCH address".
---

# Go4Me Skill

Send XCH to Twitter users by resolving their Go4Me addresses.

## Dependencies

- **sage-wallet** — Required for XCH transactions

## Commands

| Command | Description |
|---------|-------------|
| `/go4me lookup <user>` | Get user's XCH address and profile |
| `/go4me send <user> <amount>` | Send XCH to user (amount in XCH or mojos) |
| `/go4me tip <user>` | Send 1 mojo tip |

## Natural Language

- "Send 1 XCH to @hoffmang"
- "Tip @sage_wallet"
- "What's @bramcohen's XCH address?"
- "Look up DracattusDev on Go4Me"

## Lookup Script

```bash
source scripts/go4me-lookup.sh
go4me_lookup "DracattusDev"  # Returns JSON or exits 1
```

## Workflow

### Lookup

1. Strip `@` from username if present
2. Run `go4me_lookup "<username>"`
3. Parse JSON response for `xchAddress`, `fullName`, `username`
4. If exit code 1: user not found on Go4Me

### Send

1. Lookup user (as above)
2. If not found, report error
3. Display confirmation:
   ```
   Send <amount> to @<username> (<fullName>)?
   Address: <xchAddress>
   [Yes] [No]
   ```
4. On confirm, call sage-wallet `send_xch`:
   ```bash
   curl -s --cert $CERT --key $KEY -X POST https://127.0.0.1:9257/send_xch \
     -H "Content-Type: application/json" \
     -d '{"address":"<xchAddress>","amount":"<mojos>","fee":"0","memos":[],"auto_submit":true}'
   ```
5. Report transaction result

### Tip

Same as send with amount = 1 mojo.

## Amount Conversion

| Input | Mojos |
|-------|-------|
| `1` (no unit) | 1 mojo |
| `1 mojo` | 1 |
| `0.001 XCH` | 1000000000 |
| `1 XCH` | 1000000000000 |

Parse amount: if contains "XCH", multiply by 10^12. Default unit is mojos for small numbers, XCH for decimals.

## Error Handling

| Condition | Response |
|-----------|----------|
| User not on Go4Me | "User @{username} not found on Go4Me" |
| Invalid address | "Invalid XCH address returned from Go4Me" |
| Insufficient balance | "Insufficient balance for this transaction" |
| Network error | "Failed to connect to Go4Me" |

## Data Available

| Field | Example |
|-------|---------|
| `username` | DracattusDev |
| `fullName` | 🌱Drac 🍊 |
| `xchAddress` | xch1rvgc3naytvzhv4lxhzphrdr2fzj2ka340tdj8fflt4872t2wqveq9lwz7t |
| `description` | Bio text |
| `avatarUrl` | Profile image URL |
| `totalBadgeScore` | 220 |
