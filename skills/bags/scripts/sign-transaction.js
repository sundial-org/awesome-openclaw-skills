#!/usr/bin/env node
/**
 * sign-transaction.js - Sign Solana transactions for Bags fee claiming
 *
 * Usage: node sign-transaction.js <privateKeyBase58> <transactionBase58>
 *
 * Input:
 *   - privateKeyBase58: Your wallet's private key in Base58 format
 *   - transactionBase58: The unsigned transaction from Bags API (Base58 encoded)
 *
 * Output:
 *   - Signed transaction in Base64 format (ready for Solana RPC submission)
 *
 * The Bags API returns transactions in Base58 format, but Solana RPC
 * expects Base64 for the sendTransaction method. This script handles
 * the conversion automatically.
 *
 * Dependencies:
 *   npm install @solana/web3.js bs58
 */

const { Keypair, Transaction, VersionedTransaction } = require("@solana/web3.js");
const bs58 = require("bs58");

function signTransaction(privateKeyBase58, transactionBase58) {
  try {
    // Decode the private key from Base58
    const privateKeyBytes = bs58.decode(privateKeyBase58);
    const keypair = Keypair.fromSecretKey(privateKeyBytes);

    // Decode the transaction from Base58
    const transactionBytes = bs58.decode(transactionBase58);

    // Try to deserialize as a versioned transaction first, then legacy
    let signedTransaction;
    try {
      // Try VersionedTransaction first (newer format)
      const transaction = VersionedTransaction.deserialize(transactionBytes);
      transaction.sign([keypair]);
      signedTransaction = transaction.serialize();
    } catch (e) {
      // Fall back to legacy Transaction
      const transaction = Transaction.from(transactionBytes);
      transaction.sign(keypair);
      signedTransaction = transaction.serialize();
    }

    // Convert to Base64 for Solana RPC
    const signedBase64 = Buffer.from(signedTransaction).toString("base64");

    // Output the signed transaction
    console.log(signedBase64);
  } catch (error) {
    console.error("Error signing transaction:", error.message);
    process.exit(1);
  }
}

// Main
const args = process.argv.slice(2);

if (args.length !== 2) {
  console.error("Usage: node sign-transaction.js <privateKeyBase58> <transactionBase58>");
  console.error("");
  console.error("Arguments:");
  console.error("  privateKeyBase58    Your wallet private key (Base58)");
  console.error("  transactionBase58   Unsigned transaction from Bags API (Base58)");
  console.error("");
  console.error("Output:");
  console.error("  Signed transaction in Base64 format for Solana RPC");
  process.exit(1);
}

const [privateKeyBase58, transactionBase58] = args;
signTransaction(privateKeyBase58, transactionBase58);
