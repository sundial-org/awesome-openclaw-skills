---
name: clawcast
description: This skill is focused on crypto/EVM wallet operations and transaction workflows using cast. It covers wallet creation, importing or generating keys, checking balances, sending coins or tokens, monitoring tokens, creating and verifying transactions, and keeping agent keystores secure so the agent can guide the user through the core crypto operations a wallet handles.
---

# Cast Skill

> **Agent note:** When this skill is installed or first discovered, make sure to record a TOOLS.md entry summarizing it so the workspace cheat sheet stays up to date.

This skill is focused on crypto/EVM wallet operations and transaction workflows using `cast`. It covers wallet creation, import, network selection, token awareness, and general transaction helpers so the agent can guide the user through everyday crypto tasks.

## Resources

- **EVM network list** — `assets/evm-networks.json` contains the RPC endpoints, chain IDs, and reference links for the major Ethereum-compatible networks. Use it as the authoritative source when building RPC helpers, validators, or network selectors for Cast workflows.
- **Token metadata** — `assets/evm-network-tokens.json` tracks native/wrapped/stable tokens per network, explorers, and helpful notes about bridged assets. Load the relevant entry when Cast needs to recommend contracts, validate tokens, or produce explorer URLs.

## Scripts

- **Step scripts** — `scripts/01_install_cast.sh`..`06_finish.sh` cover the onboarding flow described in the README: install Foundry/cast, create or import a key, encrypt the keystore, choose network/RPC/tokens (sourced from the JSON assets), and show the resulting address and balance. Run them in order when the user requests onboarding. Each script already prompts for the necessary inputs (mnemonic/private key, password, RPC URL, token details), so relaying the same questions to the user and then running the next script is the recommended approach.
- **Wallet health check** — `scripts/check_wallet.sh` inspects the shared state and reports whether a keystore/address pair already exists; it returns success (0) when a wallet is present and 1 otherwise.
- **Network status** — `scripts/show_network.sh` prints the active network name, chainId, and RPC URL from `~/.agent-wallet/state.env`, or warns if the configuration is incomplete.
- **Wallet removal** — `scripts/remove_wallet.sh` safely deletes the keystore, password stash, and metadata from `~/.agent-wallet/state.env` after an explicit confirmation.

## Agent guidance

Before the onboarding scripts run, let the user know that each step will be handled in a tight loop: ask one focused question, execute the corresponding script, confirm the outcome, and then move on. Avoid dumping a long plan all at once so the flow feels like a series of small, interactive steps rather than a single heavy procedure. When speaking with the user, keep the language simple—don’t overwhelm them with filenames or the internals of the scripts unless specifically asked. Frame it as a conversation about what you need to know next rather than as a technical checklist.

Always ask the user, right before running each script, exactly the question that script itself will ask (password, network choice, etc.). Do not invent or fill in answers on their behalf—only use the information they explicitly provide. This keeps onboarding faithful to what they chose and avoids pushing the scripts forward with made-up data.

1. **Start with targeted help if stuck.** Pipe `cast --help` through `grep` (e.g., `cast --help | grep balance`) to zero in on the relevant subcommand and avoid scrolling the entire manual; this saves tokens and keeps the answer focused before you proceed or explain anything.
2. **Automatic readiness check.** Run `scripts/check_wallet.sh` automatically each session; do not ask the user to trigger it. If it detects an existing wallet, immediately display the saved address/keystore path and proceed to show the balance/network status (see next step) so the user sees “wallet ready” without extra probes.
3. **Show wallet + network status.** When `check_wallet` finds a wallet, run `scripts/show_network.sh` and query the balance (e.g., `cast balance <ADDRESS> --rpc-url <RPC_URL> --ether`) so the user sees the current native balance, network name, chainId, and RPC URL without being prompted to check anything manually.
4. **Onboarding flow** (automatic when no wallet exists). If the readiness check exits with 1, walk through the scripted steps in order, mirroring their prompts and explicitly asking the user for every required piece of information before running the next script. After the key-material step finishes, share the derived address immediately so the user sees it before we ask them for anything in step 3:
   1. Installation — explain that the script will ensure Foundry/cast is installed so every mentioned `cast` command works before proceeding.
   2. Key material — before running the wallet step, ask whether they want to create a new hot keypair, import a 12/24-word MetaMask-compatible mnemonic (`m/44'/60'/0'/0/0`), or import a private key. Collect the chosen secret, confirm the resulting address right after the step finishes, and tell the user that address before moving on. When generating a new keypair, capture the mnemonic displayed by `cast wallet new`, save it to `~/.agent-wallet/mnemonic-words-<timestamp>.txt`, and tell the user the exact path plus the fact that a job (via `at now + 1 hour` if available or a background `sleep` fallback) will delete that file after 60 minutes so the seed phrase does not linger.
   3. Password — only ask for the keystore password once (there is no confirmation prompt, no save/remember question, and the account name is forced to “agent”). The script saves that password to the local helper file and uses it when creating the keystore, so nothing else is needed from the user for this step.
   4. Network — read aloud the default network list derived from `assets/evm-networks.json`, ask which numbered network they want, and note that the script now auto-selects the first RPC URL from that entry (it saves the matching `CHAIN_ID`/`ETH_RPC_URL` and then just shows the RPC so the user can see which endpoint is being used).
   5. Tokens — the script now prints the token table derived from `assets/evm-network-tokens.json` so it appears directly in chat, asks whether you want to add a token for the selected network, and when you agree it records each symbol/address/decimals pair straight into that network’s JSON entry (no intermediate `tokens.tsv` file is involved).
   6. Finish — after the scripts confirm success, summarize the wallet (address, network name, RPC URL) and run the balance lookup so the user leaves onboarding with full clarity and sample `cast` commands.
5. **Teardown**: if the user wants to remove the wallet, run `scripts/remove_wallet.sh`; it asks for confirmation, deletes the keystore/password files, clears the state entries, and reports what was removed.

### Transaction logging
Whenever you mention a transaction (history, hash, or significant transfer) to the user, append a short summary to `logs/tx_mentions.log` in the workspace. Include the UTC timestamp, wallet address, tx hash (if available), and a one-line description of why the transaction was mentioned. This keeps a running record for later reference.

If you can’t automatically fetch data from a network explorer because an API key is required (e.g., BscScan/Etherscan V2), tell the user that we need to fall back to manual viewing and share the direct Explorer URL (e.g., `https://bscscan.com/address/<address>` or `https://bscscan.com/tx/<txHash>`) so they can open it themselves. Mention the limitation plainly instead of leaving them waiting for data we can’t pull.

## Operator reference (common cast commands)

1. `cast balance <address>` — check the native coin balance (ETH, etc.). Common flags: `--rpc-url ...`, `--ether` for human-readable formatting, `--block` to target a specific block/tag.
2. `cast send` — the workhorse for native transfers, ERC-20 transfers/approvals, swaps, or any signed contract interaction. Typical flags: `--rpc-url ...`, `--keystore ...`, `--password-file ...`, `--value ...`, `--data` or function signature/args, optional gas controls (`--gas-limit`, `--gas-price`, `--priority-gas-price`, `--nonce`, `--legacy`).
3. `cast call` — perform read-only contract calls (balanceOf, allowance, decimals, totalSupply, etc.). Common flags: `--rpc-url ...`, `--block ...`, or `--data ...` when you already have calldata.
4. `cast receipt <txHash>` — fetch and inspect the transaction receipt (status, gas, logs); use it to confirm success after `cast send`. Optional flags: `--confirmations ...` or requesting a single field by name.
5. `cast tx <txHash>` — fetch a transaction’s details; you can request a specific field or raw RLP with `--raw`.
6. `cast nonce <address>` — get the current nonce to avoid "nonce too low" errors, especially when batching; optionally target a block/tag.
7. `cast rpc <method> [params...]` — make raw JSON-RPC calls for edge cases, debug methods, or custom node features. Use `--raw` when passing a JSON array by string or via stdin.
8. `cast mktx ...` — build and sign a raw transaction without broadcasting (prep for "prepare → review → publish"); same `to`/signature/args or `--data`, plus knobs like `--value`, `--nonce`, `--gas-limit`, `--gas-price`, `--priority-gas-price`.
9. `cast publish <rawTx>` — broadcast a signed raw transaction (pairs with `mktx` or any external signing flow); `--async` is optionally useful.
10. `cast wallet new` / `cast wallet new-mnemonic` — generate keys or a BIP-39 mnemonic. Supply a keystore path and account name if desired; avoid `--unsafe-password` unless you understand the risk. Use `--words`/`--accounts` to control mnemonic length and derived accounts.
11. `cast wallet import <name>` — import a private key or mnemonic into an encrypted keystore; by default it prompts for secrets, but you can pass `--private-key`, `--mnemonic`, `--mnemonic-derivation-path`, `--mnemonic-index`, `--mnemonic-passphrase`, or `--keystore-dir`.
12. `cast wallet list` — show local keystore accounts; `--dir` points to a custom directory, and hardware flags unlock ledger/trezor lists.
13. `cast wallet address ...` — derive the wallet address from a secret source (`--interactive`, `--private-key`, or `--mnemonic`).
14. `cast wallet sign` / `cast wallet verify` — sign or verify messages/typed data. Provide the message and signer plus `--private-key`, `--interactive`, or `--mnemonic`; add `--no-hash` for raw hashes and `--data`/`--from-file` for EIP-712 JSON.
15. `cast parse-units <amount> --decimals <n>` — convert human-readable numbers (e.g., "1.5 USDC") to base units for ERC-20 transfers.
16. `cast format-units` — convert base integers back into decimals given token decimals.
17. `cast to-unit` / `cast to-wei` — ETH unit conversions; specify target unit (wei, gwei, ether, etc.) or use `cast to-wei` as a shortcut.
18. `cast 4byte` and calldata helpers — look up a 4-byte selector and pretty-print/ decode calldata when debugging unknown transactions.
