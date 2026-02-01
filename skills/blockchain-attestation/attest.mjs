#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

// Use createRequire for packages with ESM resolution issues
const require = createRequire(import.meta.url);
const { Command } = require('commander');
const {
  EAS,
  NO_EXPIRATION,
  SchemaEncoder,
  SchemaRegistry,
  Offchain,
  OffchainAttestationVersion
} = require('@ethereum-attestation-service/eas-sdk');
const { ethers } = require('ethers');

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CHAINS_PATH = path.join(__dirname, 'chains.json');
const SCHEMAS_PATH = path.join(__dirname, 'schemas.json');

function readJson(filePath) {
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    throw new Error(`Failed to read JSON: ${filePath}: ${err?.message || String(err)}`);
  }
}

function writeJson(filePath, obj) {
  const tmp = `${filePath}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(obj, null, 2) + '\n', 'utf8');
  fs.renameSync(tmp, filePath);
}

function nowIso() {
  return new Date().toISOString();
}

function ok(payload) {
  process.stdout.write(JSON.stringify({ success: true, ...payload }) + '\n');
}

function fail(code, message, details) {
  process.stdout.write(
    JSON.stringify({
      success: false,
      error: { code, message, details: details ?? null }
    }) + '\n'
  );
  process.exitCode = 1;
}

function requireValue(name, value) {
  if (value === undefined || value === null || value === '') {
    throw new Error(`Missing required value: ${name}`);
  }
  return value;
}

function isHexPrefixed(s) {
  return typeof s === 'string' && s.startsWith('0x');
}

function normalizeHexBytes32(hex) {
  if (typeof hex !== 'string') throw new Error('Expected hex string');
  const h = hex.startsWith('0x') ? hex.slice(2) : hex;
  if (!/^[0-9a-fA-F]+$/.test(h)) throw new Error(`Invalid hex: ${hex}`);
  if (h.length !== 64) throw new Error(`Expected 32 bytes hex (64 nybbles). Got length ${h.length}: ${hex}`);
  return '0x' + h.toLowerCase();
}

function normalizeUid(uid) {
  return normalizeHexBytes32(uid);
}

function normalizeAddress(addr) {
  if (!ethers.isAddress(addr)) throw new Error(`Invalid address: ${addr}`);
  return ethers.getAddress(addr);
}

function zeroAddress() {
  return ethers.ZeroAddress;
}

function zeroUid() {
  return ethers.ZeroHash;
}

function sha256Bytes32(data) {
  const hash = crypto.createHash('sha256').update(data).digest('hex');
  return '0x' + hash;
}

function keccakBytes32(data) {
  // ethers.keccak256 expects BytesLike
  return ethers.keccak256(data);
}

function hashFromText(text, algo) {
  const buf = Buffer.from(String(text), 'utf8');
  if (algo === 'keccak256') return keccakBytes32(buf);
  return sha256Bytes32(buf);
}

function hashFromFile(filePath, algo) {
  const buf = fs.readFileSync(filePath);
  if (algo === 'keccak256') return keccakBytes32(buf);
  return sha256Bytes32(buf);
}

function parseSchemaString(schemaString) {
  // Example: "bytes32 taskHash, bytes32 outputHash, string agentId, string metadata"
  const parts = String(schemaString)
    .split(',')
    .map((p) => p.trim())
    .filter(Boolean);

  const fields = parts.map((p) => {
    // split by whitespace, first token is type, last token is name
    const tokens = p.split(/\s+/).filter(Boolean);
    if (tokens.length < 2) throw new Error(`Invalid schema field: ${p}`);
    const type = tokens[0];
    const name = tokens[tokens.length - 1];
    return { type, name };
  });

  return {
    fields,
    types: fields.map((f) => f.type),
    names: fields.map((f) => f.name)
  };
}

function decodeEncodedData(schemaString, encodedData) {
  const { types, names } = parseSchemaString(schemaString);
  const coder = ethers.AbiCoder.defaultAbiCoder();
  const decoded = coder.decode(types, encodedData);
  const out = {};
  for (let i = 0; i < names.length; i++) out[names[i]] = decoded[i];
  return out;
}

function loadChains() {
  return readJson(CHAINS_PATH);
}

function loadSchemas() {
  return readJson(SCHEMAS_PATH);
}

function resolveChainKey(chainArg) {
  return (chainArg || process.env.EAS_CHAIN || 'base').trim();
}

function getChainConfig(chains, chainKey) {
  const cfg = chains[chainKey];
  if (!cfg) {
    const known = Object.keys(chains).join(', ');
    throw new Error(`Unknown chain key: ${chainKey}. Known: ${known}`);
  }
  return cfg;
}

function buildExplorerUrls(chainCfg, uid, mode) {
  const base = String(chainCfg.explorer).replace(/\/+$/, '');
  if (mode === 'onchain') return { view: `${base}/attestation/view/${uid}` };
  if (mode === 'offchain') return { view: `${base}/offchain/attestation/view/${uid}` };
  if (mode === 'schema') return { view: `${base}/schema/view/${uid}` };
  return { view: base };
}

function getRpcUrl(argRpc) {
  return argRpc || process.env.EAS_RPC_URL || '';
}

function getPrivateKey(argPk) {
  return argPk || process.env.EAS_PRIVATE_KEY || '';
}

function makeProvider(rpcUrl, chainId) {
  if (!rpcUrl) return null;
  // Provide chainId to avoid extra network calls when possible
  try {
    return new ethers.JsonRpcProvider(rpcUrl, chainId);
  } catch {
    return new ethers.JsonRpcProvider(rpcUrl);
  }
}

function makeSigner(privateKey, provider) {
  if (!privateKey) return null;
  if (provider) return new ethers.Wallet(privateKey, provider);
  return new ethers.Wallet(privateKey);
}

function coerceBool(v, defaultValue) {
  if (v === undefined || v === null) return defaultValue;
  if (typeof v === 'boolean') return v;
  const s = String(v).toLowerCase().trim();
  if (['true', '1', 'yes', 'y', 'on'].includes(s)) return true;
  if (['false', '0', 'no', 'n', 'off'].includes(s)) return false;
  throw new Error(`Invalid boolean: ${v}`);
}

function ensureDirForFile(filePath) {
  const dir = path.dirname(filePath);
  fs.mkdirSync(dir, { recursive: true });
}

function safeReadTextFile(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

function parseJsonOrRawString(s) {
  const trimmed = String(s ?? '').trim();
  if (!trimmed) return '';
  try {
    // If it's JSON, normalize spacing by re-stringifying
    return JSON.stringify(JSON.parse(trimmed));
  } catch {
    return trimmed;
  }
}

async function schemaRegister({ chainKey, rpcUrl, privateKey, resolver, revocable, writeBack }) {
  const chains = loadChains();
  const schemas = loadSchemas();
  const chainCfg = getChainConfig(chains, chainKey);

  const schemaString = schemas?.schema?.string;
  if (!schemaString) throw new Error('schemas.json missing schema.string');

  const resolverAddress = resolver || schemas?.schema?.resolver || zeroAddress();
  const revocableFlag = revocable ?? schemas?.schema?.revocable ?? true;

  const provider = makeProvider(rpcUrl, chainCfg.chainId);
  if (!provider) throw new Error('EAS_RPC_URL (or --rpc) is required to register schemas');

  const signer = makeSigner(privateKey, provider);
  if (!signer) throw new Error('EAS_PRIVATE_KEY (or --private-key) is required to register schemas');

  const schemaRegistry = new SchemaRegistry(chainCfg.schemaRegistry);
  schemaRegistry.connect(signer);

  const tx = await schemaRegistry.register({
    schema: schemaString,
    resolverAddress: resolverAddress,
    revocable: revocableFlag
  });

  const waitResult = await tx.wait();

  let schemaUid = null;

  // Most EAS SDK Transaction.wait() calls resolve to the UID string.
  if (typeof waitResult === 'string' && isHexPrefixed(waitResult) && waitResult.length === 66) {
    schemaUid = waitResult;
  }

  // Fallback: attempt to extract from receipt logs if available.
  if (!schemaUid) {
    const receipt = tx?.receipt;
    if (receipt?.logs && schemaRegistry?.contract?.interface) {
      for (const log of receipt.logs) {
        try {
          const parsed = schemaRegistry.contract.interface.parseLog(log);
          if (parsed?.name?.toLowerCase() === 'registered') {
            // Some versions emit: Registered(bytes32 uid, address registrar, bytes32 schemaUID, string schema, address resolver, bool revocable)
            const possible = parsed?.args?.uid || parsed?.args?.schemaUID || parsed?.args?.[0];
            if (typeof possible === 'string' && isHexPrefixed(possible) && possible.length === 66) {
              schemaUid = possible;
              break;
            }
          }
        } catch {
          // ignore
        }
      }
    }
  }

  // Last-resort: try getSchemaUID if present.
  if (!schemaUid && typeof schemaRegistry.getSchemaUID === 'function') {
    try {
      const uidMaybe = await schemaRegistry.getSchemaUID({
        schema: schemaString,
        resolverAddress: resolverAddress,
        revocable: revocableFlag
      });
      if (typeof uidMaybe === 'string' && isHexPrefixed(uidMaybe) && uidMaybe.length === 66) schemaUid = uidMaybe;
    } catch {
      // ignore
    }
  }

  if (!schemaUid) throw new Error('Failed to determine schema UID after registration');

  if (writeBack) {
    schemas.uids = schemas.uids || {};
    schemas.uids[chainKey] = schemaUid;
    schemas.schema = schemas.schema || {};
    schemas.schema.resolver = resolverAddress;
    schemas.schema.revocable = revocableFlag;
    writeJson(SCHEMAS_PATH, schemas);
  }

  return {
    chain: chainKey,
    chainName: chainCfg.name,
    schemaUid,
    schemaString,
    resolver: resolverAddress,
    revocable: revocableFlag,
    explorer: buildExplorerUrls(chainCfg, schemaUid, 'schema').view
  };
}

function requireSchemaUid(schemas, chainKey) {
  const uid = schemas?.uids?.[chainKey];
  if (uid && typeof uid === 'string' && uid.startsWith('0x') && uid.length === 66) return uid;
  throw new Error(`Schema UID missing for chain ${chainKey}. Run: node attest.mjs schema register --chain ${chainKey}`);
}

async function createAttestation({
  mode,
  chainKey,
  rpcUrl,
  privateKey,
  recipient,
  taskHash,
  outputHash,
  agentId,
  metadata,
  savePath,
  timestampAfter
}) {
  const chains = loadChains();
  const schemas = loadSchemas();
  const chainCfg = getChainConfig(chains, chainKey);

  const schemaString = schemas?.schema?.string;
  if (!schemaString) throw new Error('schemas.json missing schema.string');

  const schemaUid = requireSchemaUid(schemas, chainKey);

  const recipientAddr = recipient ? normalizeAddress(recipient) : zeroAddress();
  const agent = agentId || process.env.CLAWDBOT_AGENT_ID || process.env.AGENT_ID || 'clawdbot';
  const metadataStr = metadata ?? '{}';

  const schemaEncoder = new SchemaEncoder(schemaString);
  const encodedData = schemaEncoder.encodeData([
    { name: 'taskHash', value: normalizeHexBytes32(taskHash), type: 'bytes32' },
    { name: 'outputHash', value: normalizeHexBytes32(outputHash), type: 'bytes32' },
    { name: 'agentId', value: String(agent), type: 'string' },
    { name: 'metadata', value: String(metadataStr), type: 'string' }
  ]);

  const commonRecord = {
    createdAt: nowIso(),
    chain: chainKey,
    chainName: chainCfg.name,
    mode,
    schemaUid,
    schemaString,
    recipient: recipientAddr,
    agentId: agent,
    taskHash: normalizeHexBytes32(taskHash),
    outputHash: normalizeHexBytes32(outputHash),
    metadata: metadataStr,
    encodedData
  };

  if (mode === 'offchain') {
    const signer = makeSigner(privateKey, null);
    if (!signer) throw new Error('EAS_PRIVATE_KEY (or --private-key) is required for offchain signing');

    // Prefer EAS.getOffchain() when an RPC URL is present (lets the SDK derive domain values from chain).
    const provider = makeProvider(rpcUrl, chainCfg.chainId);
    let offchainAttestation = null;

    if (provider) {
      const signerWithProvider = makeSigner(privateKey, provider);
      const eas = new EAS(chainCfg.eas);
      // Connect signer so the SDK can read domain separator when needed.
      eas.connect(signerWithProvider);
      const offchain = await eas.getOffchain();
      offchainAttestation = await offchain.signOffchainAttestation(
        {
          schema: schemaUid,
          recipient: recipientAddr,
          time: BigInt(Math.floor(Date.now() / 1000)),
          expirationTime: NO_EXPIRATION,
          revocable: true,
          refUID: zeroUid(),
          data: encodedData
        },
        signerWithProvider
      );
    } else {
      // Offline path: use static chain config.
      const cfg = {
        address: chainCfg.eas,
        version: chainCfg.easVersion,
        chainId: chainCfg.chainId
      };
      const offchain = new Offchain(cfg, OffchainAttestationVersion.Version2);
      offchainAttestation = await offchain.signOffchainAttestation(
        {
          schema: schemaUid,
          recipient: recipientAddr,
          time: BigInt(Math.floor(Date.now() / 1000)),
          expirationTime: NO_EXPIRATION,
          revocable: true,
          refUID: zeroUid(),
          data: encodedData
        },
        signer
      );
    }

    const uid = offchainAttestation?.uid || offchainAttestation?.sig?.uid;
    if (!uid) throw new Error('Offchain attestation did not include a UID');

    const record = {
      ...commonRecord,
      uid,
      verifyUrl: buildExplorerUrls(chainCfg, uid, 'offchain').view,
      offchainAttestation
    };

    let timestampTx = null;
    if (timestampAfter) {
      if (!provider) throw new Error('EAS_RPC_URL (or --rpc) is required to timestamp onchain');
      const signerWithProvider = makeSigner(privateKey, provider);
      const eas = new EAS(chainCfg.eas);
      eas.connect(signerWithProvider);
      const tx = await eas.timestamp(normalizeUid(uid));
      await tx.wait();
      timestampTx = {
        txHash: tx?.tx?.hash || tx?.receipt?.transactionHash || null
      };
      record.timestamp = timestampTx;
    }

    if (savePath) {
      ensureDirForFile(savePath);
      fs.writeFileSync(savePath, JSON.stringify(record, null, 2) + '\n', 'utf8');
    }

    return record;
  }

  if (mode === 'onchain') {
    const rpc = rpcUrl;
    if (!rpc) throw new Error('EAS_RPC_URL (or --rpc) is required for onchain attestations');

    const provider = makeProvider(rpc, chainCfg.chainId);
    const signer = makeSigner(privateKey, provider);
    if (!signer) throw new Error('EAS_PRIVATE_KEY (or --private-key) is required for onchain attestations');

    const eas = new EAS(chainCfg.eas);
    eas.connect(signer);

    const tx = await eas.attest({
      schema: schemaUid,
      data: {
        recipient: recipientAddr,
        expirationTime: NO_EXPIRATION,
        revocable: true,
        refUID: zeroUid(),
        data: encodedData
      }
    });

    const uid = await tx.wait();

    const record = {
      ...commonRecord,
      uid,
      verifyUrl: buildExplorerUrls(chainCfg, uid, 'onchain').view,
      tx: {
        txHash: tx?.tx?.hash || tx?.receipt?.transactionHash || null,
        receipt: tx?.receipt || null
      }
    };

    if (savePath) {
      ensureDirForFile(savePath);
      fs.writeFileSync(savePath, JSON.stringify(record, null, 2) + '\n', 'utf8');
    }

    return record;
  }

  throw new Error(`Unknown mode: ${mode}`);
}

async function verifyOnchain({ chainKey, rpcUrl, uid }) {
  const chains = loadChains();
  const schemas = loadSchemas();
  const chainCfg = getChainConfig(chains, chainKey);

  const schemaString = schemas?.schema?.string;
  if (!schemaString) throw new Error('schemas.json missing schema.string');

  const rpc = rpcUrl;
  if (!rpc) throw new Error('EAS_RPC_URL (or --rpc) is required to verify onchain attestations');

  const provider = makeProvider(rpc, chainCfg.chainId);

  const eas = new EAS(chainCfg.eas);
  eas.connect(provider);

  // EAS SDK exposes getAttestation(uid) on many versions. If it is unavailable, return a minimal response.
  let attestation = null;
  try {
    if (typeof eas.getAttestation === 'function') {
      attestation = await eas.getAttestation(normalizeUid(uid));
    } else if (typeof eas.getAttestation === 'undefined') {
      throw new Error('EAS SDK method getAttestation not available');
    }
  } catch (err) {
    return {
      uid: normalizeUid(uid),
      chain: chainKey,
      chainName: chainCfg.name,
      verifyUrl: buildExplorerUrls(chainCfg, normalizeUid(uid), 'onchain').view,
      warning: 'Local fetch failed. Use verifyUrl to inspect on the explorer.',
      error: String(err?.message || err)
    };
  }

  const decoded = attestation?.data ? decodeEncodedData(schemaString, attestation.data) : null;

  return {
    uid: normalizeUid(uid),
    chain: chainKey,
    chainName: chainCfg.name,
    verifyUrl: buildExplorerUrls(chainCfg, normalizeUid(uid), 'onchain').view,
    attestation,
    decoded
  };
}

function normalizeOffchainPayload(obj) {
  if (!obj || typeof obj !== 'object') throw new Error('Invalid offchain payload (expected object)');

  // Accept either:
  // 1) { signer, sig }
  // 2) { offchainAttestation: { signer, sig } }
  // 3) { offchainAttestation: { uid, ... } } (best effort)
  const directSigner = obj.signer;
  const directSig = obj.sig;

  if (directSigner && directSig) return { signer: directSigner, sig: directSig };

  if (obj.offchainAttestation?.signer && obj.offchainAttestation?.sig) {
    return { signer: obj.offchainAttestation.signer, sig: obj.offchainAttestation.sig };
  }

  // If this is the raw object returned by signOffchainAttestation, it usually includes { signer, sig } already.
  // Some versions may return { uid, ... } only. Fail clearly.
  throw new Error('Unsupported offchain payload format. Expected fields: signer and sig.');
}

async function verifyOffchain({ payload }) {
  const { signer, sig } = normalizeOffchainPayload(payload);

  const domain = sig?.domain;
  const message = sig?.message;
  if (!domain?.verifyingContract || domain?.chainId == null || !domain?.version) {
    throw new Error('Offchain payload missing EIP712 domain fields');
  }

  const easCfg = {
    address: domain.verifyingContract,
    version: domain.version,
    chainId: Number(domain.chainId)
  };

  const offchainVersion = message?.version ?? OffchainAttestationVersion.Version2;
  const offchain = new Offchain(easCfg, offchainVersion);

  const isValid = offchain.verifyOffchainAttestationSignature(signer, sig);

  return {
    uid: sig?.uid || null,
    chainId: easCfg.chainId,
    verifyingContract: easCfg.address,
    domainVersion: easCfg.version,
    valid: Boolean(isValid)
  };
}

async function timestampUid({ chainKey, rpcUrl, privateKey, uid }) {
  const chains = loadChains();
  const chainCfg = getChainConfig(chains, chainKey);

  const rpc = rpcUrl;
  if (!rpc) throw new Error('EAS_RPC_URL (or --rpc) is required to timestamp');

  const provider = makeProvider(rpc, chainCfg.chainId);
  const signer = makeSigner(privateKey, provider);
  if (!signer) throw new Error('EAS_PRIVATE_KEY (or --private-key) is required to timestamp');

  const eas = new EAS(chainCfg.eas);
  eas.connect(signer);

  const tx = await eas.timestamp(normalizeUid(uid));
  await tx.wait();

  return {
    chain: chainKey,
    chainName: chainCfg.name,
    uid: normalizeUid(uid),
    txHash: tx?.tx?.hash || tx?.receipt?.transactionHash || null
  };
}

async function revokeUid({ chainKey, rpcUrl, privateKey, uid, mode }) {
  const chains = loadChains();
  const schemas = loadSchemas();
  const chainCfg = getChainConfig(chains, chainKey);

  const rpc = rpcUrl;
  if (!rpc) throw new Error('EAS_RPC_URL (or --rpc) is required to revoke');

  const provider = makeProvider(rpc, chainCfg.chainId);
  const signer = makeSigner(privateKey, provider);
  if (!signer) throw new Error('EAS_PRIVATE_KEY (or --private-key) is required to revoke');

  const eas = new EAS(chainCfg.eas);
  eas.connect(signer);

  if (mode === 'offchain') {
    const tx = await eas.revokeOffchain(normalizeUid(uid));
    await tx.wait();
    return {
      chain: chainKey,
      chainName: chainCfg.name,
      mode,
      uid: normalizeUid(uid),
      txHash: tx?.tx?.hash || tx?.receipt?.transactionHash || null
    };
  }

  if (mode === 'onchain') {
    const schemaUid = requireSchemaUid(schemas, chainKey);
    const tx = await eas.revoke({
      schema: schemaUid,
      data: { uid: normalizeUid(uid) }
    });
    await tx.wait();
    return {
      chain: chainKey,
      chainName: chainCfg.name,
      mode,
      uid: normalizeUid(uid),
      schemaUid,
      txHash: tx?.tx?.hash || tx?.receipt?.transactionHash || null
    };
  }

  throw new Error(`Unknown revoke mode: ${mode}`);
}

async function main() {
  const program = new Command();

  program
    .name('attest')
    .description('Create and verify EAS attestations (opinionated defaults for Clawdbot)')
    .showHelpAfterError(true);

  program
    .command('hash')
    .description('Hash a text or file to bytes32 (sha256 default)')
    .option('--algo <algo>', 'sha256 or keccak256', 'sha256')
    .option('--text <text>', 'text to hash')
    .option('--file <path>', 'file path to hash')
    .action((opts) => {
      try {
        const algo = (opts.algo || 'sha256').toLowerCase().trim();
        if (!['sha256', 'keccak256'].includes(algo)) throw new Error('algo must be sha256 or keccak256');

        const hasText = opts.text !== undefined;
        const hasFile = opts.file !== undefined;

        if (hasText === hasFile) throw new Error('Provide exactly one of --text or --file');

        const digest = hasText ? hashFromText(opts.text, algo) : hashFromFile(opts.file, algo);

        ok({
          algo,
          digest: normalizeHexBytes32(digest),
          source: hasText ? { kind: 'text' } : { kind: 'file', path: opts.file }
        });
      } catch (err) {
        fail('HASH_ERROR', err?.message || String(err));
      }
    });

  const schemaCmd = program.command('schema').description('Schema management');

  schemaCmd
    .command('info')
    .description('Show the schema string and configured UIDs')
    .action(() => {
      try {
        const schemas = loadSchemas();
        ok({ schema: schemas.schema, uids: schemas.uids });
      } catch (err) {
        fail('SCHEMA_INFO_ERROR', err?.message || String(err));
      }
    });

  schemaCmd
    .command('register')
    .description('Register the schema onchain and store the UID into schemas.json')
    .option('--chain <chain>', 'chain key (base or base_sepolia)', 'base')
    .option('--rpc <url>', 'RPC URL (overrides EAS_RPC_URL)')
    .option('--private-key <hex>', 'private key (overrides EAS_PRIVATE_KEY)')
    .option('--resolver <address>', 'resolver address (default zero address)')
    .option('--revocable <bool>', 'true or false (default true)')
    .option('--no-write', 'do not write schemas.json (prints UID only)')
    .action(async (opts) => {
      try {
        const chainKey = resolveChainKey(opts.chain);
        const rpcUrl = getRpcUrl(opts.rpc);
        const privateKey = getPrivateKey(opts.privateKey);
        const resolver = opts.resolver ? normalizeAddress(opts.resolver) : null;
        const revocable = opts.revocable !== undefined ? coerceBool(opts.revocable, true) : null;
        const writeBack = Boolean(opts.write);

        const result = await schemaRegister({
          chainKey,
          rpcUrl,
          privateKey,
          resolver,
          revocable,
          writeBack
        });

        ok(result);
      } catch (err) {
        fail('SCHEMA_REGISTER_ERROR', err?.message || String(err));
      }
    });

  program
    .command('attest')
    .description('Create an attestation (offchain default)')
    .option('--mode <mode>', 'offchain or onchain', 'offchain')
    .option('--chain <chain>', 'chain key (base or base_sepolia)', 'base')
    .option('--rpc <url>', 'RPC URL (overrides EAS_RPC_URL)')
    .option('--private-key <hex>', 'private key (overrides EAS_PRIVATE_KEY)')
    .option('--recipient <address>', 'recipient address (default zero address)')
    .option('--agent-id <id>', 'agent id (default env CLAWDBOT_AGENT_ID or "clawdbot")')
    .option('--metadata <string>', 'metadata string or JSON')
    .option('--metadata-file <path>', 'read metadata from file')
    .option('--hash-algo <algo>', 'sha256 or keccak256', 'sha256')
    .option('--task-hash <hex>', 'bytes32 task hash (0x...)')
    .option('--task-text <text>', 'task text to hash')
    .option('--task-file <path>', 'task file to hash')
    .option('--output-hash <hex>', 'bytes32 output hash (0x...)')
    .option('--output-text <text>', 'output text to hash')
    .option('--output-file <path>', 'output file to hash')
    .option('--save <path>', 'write a JSON record to this path')
    .option('--timestamp', 'after offchain signing, timestamp the UID onchain')
    .action(async (opts) => {
      try {
        const mode = String(opts.mode || 'offchain').toLowerCase().trim();
        if (!['offchain', 'onchain'].includes(mode)) throw new Error('mode must be offchain or onchain');

        const chainKey = resolveChainKey(opts.chain);
        const rpcUrl = getRpcUrl(opts.rpc);
        const privateKey = getPrivateKey(opts.privateKey);

        const algo = String(opts.hashAlgo || 'sha256').toLowerCase().trim();
        if (!['sha256', 'keccak256'].includes(algo)) throw new Error('hash-algo must be sha256 or keccak256');

        // task hash sources
        const taskSources = [opts.taskHash, opts.taskText, opts.taskFile].filter((v) => v !== undefined);
        if (taskSources.length !== 1) throw new Error('Provide exactly one of --task-hash, --task-text, --task-file');

        // output hash sources
        const outSources = [opts.outputHash, opts.outputText, opts.outputFile].filter((v) => v !== undefined);
        if (outSources.length !== 1) throw new Error('Provide exactly one of --output-hash, --output-text, --output-file');

        const taskHash =
          opts.taskHash !== undefined
            ? normalizeHexBytes32(opts.taskHash)
            : opts.taskText !== undefined
              ? normalizeHexBytes32(hashFromText(opts.taskText, algo))
              : normalizeHexBytes32(hashFromFile(opts.taskFile, algo));

        const outputHash =
          opts.outputHash !== undefined
            ? normalizeHexBytes32(opts.outputHash)
            : opts.outputText !== undefined
              ? normalizeHexBytes32(hashFromText(opts.outputText, algo))
              : normalizeHexBytes32(hashFromFile(opts.outputFile, algo));

        let metadataStr = opts.metadata !== undefined ? parseJsonOrRawString(opts.metadata) : '{}';
        if (opts.metadataFile) {
          metadataStr = parseJsonOrRawString(safeReadTextFile(opts.metadataFile));
        }

        const recipient = opts.recipient ? normalizeAddress(opts.recipient) : zeroAddress();
        const agentId = opts.agentId ? String(opts.agentId) : null;
        const savePath = opts.save ? String(opts.save) : null;
        const timestampAfter = Boolean(opts.timestamp);

        const record = await createAttestation({
          mode,
          chainKey,
          rpcUrl,
          privateKey,
          recipient,
          taskHash,
          outputHash,
          agentId,
          metadata: metadataStr,
          savePath,
          timestampAfter
        });

        ok(record);
      } catch (err) {
        fail('ATTEST_ERROR', err?.message || String(err));
      }
    });

  program
    .command('verify')
    .description('Verify an onchain UID or an offchain payload')
    .option('--chain <chain>', 'chain key (base or base_sepolia)', 'base')
    .option('--rpc <url>', 'RPC URL (overrides EAS_RPC_URL)')
    .option('--uid <hex>', 'onchain UID to fetch and decode')
    .option('--offchain-file <path>', 'offchain attestation JSON file (as produced by this skill)')
    .option('--offchain-json <json>', 'offchain attestation JSON string')
    .action(async (opts) => {
      try {
        const chainKey = resolveChainKey(opts.chain);
        const rpcUrl = getRpcUrl(opts.rpc);

        const hasUid = opts.uid !== undefined;
        const hasOffFile = opts.offchainFile !== undefined;
        const hasOffJson = opts.offchainJson !== undefined;

        const count = [hasUid, hasOffFile, hasOffJson].filter(Boolean).length;
        if (count !== 1) throw new Error('Provide exactly one of --uid, --offchain-file, --offchain-json');

        if (hasUid) {
          const res = await verifyOnchain({ chainKey, rpcUrl, uid: opts.uid });
          ok(res);
          return;
        }

        const payload = hasOffFile ? JSON.parse(fs.readFileSync(opts.offchainFile, 'utf8')) : JSON.parse(opts.offchainJson);
        const res = await verifyOffchain({ payload });
        ok(res);
      } catch (err) {
        fail('VERIFY_ERROR', err?.message || String(err));
      }
    });

  program
    .command('timestamp')
    .description('Timestamp a UID onchain (commonly used to anchor an offchain attestation UID)')
    .option('--chain <chain>', 'chain key (base or base_sepolia)', 'base')
    .option('--rpc <url>', 'RPC URL (overrides EAS_RPC_URL)')
    .option('--private-key <hex>', 'private key (overrides EAS_PRIVATE_KEY)')
    .requiredOption('--uid <hex>', 'UID to timestamp (bytes32)')
    .action(async (opts) => {
      try {
        const chainKey = resolveChainKey(opts.chain);
        const rpcUrl = getRpcUrl(opts.rpc);
        const privateKey = getPrivateKey(opts.privateKey);

        const res = await timestampUid({ chainKey, rpcUrl, privateKey, uid: opts.uid });
        ok(res);
      } catch (err) {
        fail('TIMESTAMP_ERROR', err?.message || String(err));
      }
    });

  program
    .command('revoke')
    .description('Revoke an attestation (onchain or offchain revocation record)')
    .option('--mode <mode>', 'onchain or offchain', 'onchain')
    .option('--chain <chain>', 'chain key (base or base_sepolia)', 'base')
    .option('--rpc <url>', 'RPC URL (overrides EAS_RPC_URL)')
    .option('--private-key <hex>', 'private key (overrides EAS_PRIVATE_KEY)')
    .requiredOption('--uid <hex>', 'UID to revoke (bytes32)')
    .action(async (opts) => {
      try {
        const chainKey = resolveChainKey(opts.chain);
        const rpcUrl = getRpcUrl(opts.rpc);
        const privateKey = getPrivateKey(opts.privateKey);
        const mode = String(opts.mode || 'onchain').toLowerCase().trim();
        if (!['onchain', 'offchain'].includes(mode)) throw new Error('mode must be onchain or offchain');

        const res = await revokeUid({ chainKey, rpcUrl, privateKey, uid: opts.uid, mode });
        ok(res);
      } catch (err) {
        fail('REVOKE_ERROR', err?.message || String(err));
      }
    });

  await program.parseAsync(process.argv);

  if (!process.exitCode) process.exitCode = 0;
}

main().catch((err) => {
  fail('FATAL', err?.message || String(err));
});
