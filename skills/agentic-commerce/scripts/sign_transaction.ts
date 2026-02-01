#!/usr/bin/env npx ts-node
/**
 * Sign and submit a Solana transaction for Purch API checkout.
 *
 * Usage:
 *   npx ts-node sign_transaction.ts <serialized_transaction> <private_key> [rpc_url]
 *
 * Or with bun:
 *   bun run sign_transaction.ts <serialized_transaction> <private_key> [rpc_url]
 *
 * Arguments:
 *   serialized_transaction  Base58-encoded transaction from /buy endpoint
 *   private_key             Base58-encoded Solana private key (64 bytes)
 *   rpc_url                 Optional: Solana RPC URL (default: mainnet-beta)
 *
 * Example:
 *   bun run sign_transaction.ts "NwbtPCP62oXk..." "5abc123..."
 */

import {
  Connection,
  Keypair,
  VersionedTransaction,
  clusterApiUrl,
} from "@solana/web3.js";
import bs58 from "bs58";

interface SignResult {
  success: boolean;
  signature?: string;
  explorerUrl?: string;
  error?: string;
}

async function signAndSendTransaction(
  serializedTx: string,
  privateKey: string,
  rpcUrl: string = clusterApiUrl("mainnet-beta")
): Promise<SignResult> {
  // Decode private key and create keypair
  let keypair: Keypair;
  try {
    const keyBytes = bs58.decode(privateKey);
    keypair = Keypair.fromSecretKey(keyBytes);
  } catch (e) {
    return { success: false, error: `Invalid private key: ${e}` };
  }

  // Decode the serialized transaction
  let transaction: VersionedTransaction;
  try {
    const txBytes = bs58.decode(serializedTx);
    transaction = VersionedTransaction.deserialize(txBytes);
  } catch (e) {
    return { success: false, error: `Invalid transaction: ${e}` };
  }

  // Sign the transaction
  try {
    transaction.sign([keypair]);
  } catch (e) {
    return { success: false, error: `Failed to sign: ${e}` };
  }

  // Connect and send
  const connection = new Connection(rpcUrl, "confirmed");

  try {
    // Send transaction
    const signature = await connection.sendRawTransaction(
      transaction.serialize(),
      { skipPreflight: false }
    );

    // Wait for confirmation
    await connection.confirmTransaction(signature, "confirmed");

    return {
      success: true,
      signature,
      explorerUrl: `https://solscan.io/tx/${signature}`,
    };
  } catch (e) {
    return { success: false, error: `Transaction failed: ${e}` };
  }
}

// CLI entry point
async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.log(`
Usage: bun run sign_transaction.ts <serialized_transaction> <private_key> [rpc_url]

Arguments:
  serialized_transaction  Base58-encoded transaction from /buy endpoint
  private_key             Base58-encoded Solana private key (64 bytes)
  rpc_url                 Optional: Solana RPC URL (default: mainnet-beta)

Required packages:
  bun add @solana/web3.js bs58
    `);
    process.exit(1);
  }

  const [serializedTx, privateKey, rpcUrl] = args;

  const result = await signAndSendTransaction(
    serializedTx,
    privateKey,
    rpcUrl || clusterApiUrl("mainnet-beta")
  );

  if (result.success) {
    console.log("✅ Transaction successful!");
    console.log(`   Signature: ${result.signature}`);
    console.log(`   Explorer:  ${result.explorerUrl}`);
  } else {
    console.error(`❌ Transaction failed: ${result.error}`);
    process.exit(1);
  }
}

main().catch(console.error);

// Export for programmatic use
export { signAndSendTransaction, SignResult };
