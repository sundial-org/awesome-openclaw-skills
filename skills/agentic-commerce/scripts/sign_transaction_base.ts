#!/usr/bin/env bun
/**
 * Sign and submit a Base/EVM transaction for Purch API checkout.
 *
 * Usage:
 *   bun run sign_transaction_base.ts <serialized_transaction> <private_key> [rpc_url]
 *
 * Arguments:
 *   serialized_transaction  Hex-encoded transaction from /buy endpoint
 *   private_key             Hex private key (0x...)
 *   rpc_url                 Optional: Base RPC URL (default: https://mainnet.base.org)
 *
 * Example:
 *   bun run sign_transaction_base.ts "0x02f8..." "0xabc123..."
 *
 * Required packages:
 *   bun add viem
 */

import {
  createWalletClient,
  http,
  parseTransaction,
  type TransactionSerializable,
} from "viem";
import { base } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";

interface SignResult {
  success: boolean;
  hash?: string;
  explorerUrl?: string;
  error?: string;
}

async function signAndSendTransaction(
  serializedTx: string,
  privateKey: string,
  rpcUrl: string = "https://mainnet.base.org"
): Promise<SignResult> {
  // Validate and format private key
  let formattedKey: `0x${string}`;
  try {
    formattedKey = privateKey.startsWith("0x")
      ? (privateKey as `0x${string}`)
      : (`0x${privateKey}` as `0x${string}`);

    if (!/^0x[a-fA-F0-9]{64}$/.test(formattedKey)) {
      return { success: false, error: "Invalid private key format (must be 32 bytes hex)" };
    }
  } catch (e) {
    return { success: false, error: `Invalid private key: ${e}` };
  }

  // Create account from private key
  let account;
  try {
    account = privateKeyToAccount(formattedKey);
  } catch (e) {
    return { success: false, error: `Failed to create account: ${e}` };
  }

  // Parse the serialized transaction
  let tx: TransactionSerializable;
  try {
    const formattedTx = serializedTx.startsWith("0x")
      ? (serializedTx as `0x${string}`)
      : (`0x${serializedTx}` as `0x${string}`);
    tx = parseTransaction(formattedTx);
  } catch (e) {
    return { success: false, error: `Invalid transaction: ${e}` };
  }

  // Create wallet client
  const client = createWalletClient({
    account,
    chain: base,
    transport: http(rpcUrl),
  });

  // Send transaction
  try {
    const hash = await client.sendTransaction({
      to: tx.to,
      data: tx.data,
      value: tx.value,
      gas: tx.gas,
      maxFeePerGas: tx.maxFeePerGas,
      maxPriorityFeePerGas: tx.maxPriorityFeePerGas,
    });

    return {
      success: true,
      hash,
      explorerUrl: `https://basescan.org/tx/${hash}`,
    };
  } catch (e) {
    return { success: false, error: `Transaction failed: ${e}` };
  }
}

// CLI entry point
async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2 || args[0] === "--help") {
    console.log(`
Usage: bun run sign_transaction_base.ts <serialized_transaction> <private_key> [rpc_url]

Arguments:
  serialized_transaction  Hex-encoded transaction from /buy endpoint (0x...)
  private_key             Hex private key (0x...)
  rpc_url                 Optional: Base RPC URL (default: https://mainnet.base.org)

Required packages:
  bun add viem
    `);
    process.exit(1);
  }

  const [serializedTx, privateKey, rpcUrl] = args;

  const result = await signAndSendTransaction(
    serializedTx,
    privateKey,
    rpcUrl || "https://mainnet.base.org"
  );

  if (result.success) {
    console.log("✅ Transaction successful!");
    console.log(`   Hash:     ${result.hash}`);
    console.log(`   Explorer: ${result.explorerUrl}`);
  } else {
    console.error(`❌ Transaction failed: ${result.error}`);
    process.exit(1);
  }
}

main().catch(console.error);

export { signAndSendTransaction, SignResult };
