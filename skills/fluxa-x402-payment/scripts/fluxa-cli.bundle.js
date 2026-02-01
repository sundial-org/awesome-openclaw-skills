#!/usr/bin/env node

// src/wallet/client.ts
var AGENT_ID_API = process.env.AGENT_ID_API || "https://agentid.fluxapay.xyz";
var WALLET_API = process.env.WALLET_API || "https://walletapi.fluxapay.xyz";
var WALLET_APP = process.env.WALLET_APP || "https://wallet.fluxapay.xyz";
var JWT_EXPIRY_BUFFER_SECONDS = 300;
var WalletApiError = class extends Error {
  status;
  details;
  constructor(message, status, details) {
    super(message);
    this.name = "WalletApiError";
    this.status = status;
    this.details = details;
  }
};
async function registerAgent(params) {
  const url = `${AGENT_ID_API}/register`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(params)
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `Agent registration failed (${response.status}): ${errorText}`
    );
  }
  const data = await response.json();
  if (!data.agent_id || !data.token || !data.jwt) {
    throw new Error(
      "Invalid registration response: missing agent_id, token, or jwt"
    );
  }
  return data;
}
async function requestX402Payment(params, jwt) {
  const url = `${WALLET_API}/api/payment/x402V1Payment`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${jwt}`
    },
    body: JSON.stringify(params)
  });
  const responseText = await response.text();
  if (!response.ok) {
    const message = responseText || `Wallet API request failed (${response.status})`;
    throw new WalletApiError(message, response.status, responseText || null);
  }
  if (!responseText) {
    throw new WalletApiError("Wallet API returned empty response", response.status, responseText);
  }
  return responseText;
}
async function createPayout(params, jwt) {
  const url = `${WALLET_API}/api/payouts`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${jwt}`,
      "x-agent-id": params.agentId
    },
    body: JSON.stringify(params)
  });
  const text = await response.text();
  if (!response.ok) {
    throw new WalletApiError(text || `Wallet API request failed (${response.status})`, response.status, text || null);
  }
  try {
    return JSON.parse(text);
  } catch (e) {
    throw new WalletApiError("Invalid payout API response (not JSON)", response.status, text);
  }
}
async function getPayoutStatus(payoutId) {
  const url = `${WALLET_API}/api/payouts/${encodeURIComponent(payoutId)}`;
  const response = await fetch(url, { method: "GET" });
  const text = await response.text();
  if (!response.ok) {
    throw new WalletApiError(text || `Wallet App status request failed (${response.status})`, response.status, text || null);
  }
  try {
    return JSON.parse(text);
  } catch {
    const end = Math.max(text.lastIndexOf("}"), text.lastIndexOf("]"));
    if (end >= 0) {
      const sliced = text.slice(0, end + 1);
      try {
        return JSON.parse(sliced);
      } catch {
      }
    }
    throw new WalletApiError("Invalid payout status response (not JSON)", response.status, text);
  }
}
function extractHost(url) {
  try {
    const parsed = new URL(url);
    return parsed.host;
  } catch (e) {
    const match = url.match(/^(?:https?:\/\/)?([^\/]+)/);
    return match ? match[1] : url;
  }
}
function getCurrencyFromAsset(assetAddress, network) {
  const normalizedAddress = assetAddress.toLowerCase();
  if (normalizedAddress === "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913" && network === "base") {
    return "USDC";
  }
  return "USDC";
}
function parseJWT(jwt) {
  try {
    const parts = jwt.split(".");
    if (parts.length !== 3) {
      return null;
    }
    const payload = parts[1];
    const decoded = Buffer.from(payload, "base64").toString("utf-8");
    return JSON.parse(decoded);
  } catch (e) {
    return null;
  }
}
function isJWTExpired(jwt) {
  const payload = parseJWT(jwt);
  if (!payload || !payload.exp) {
    return true;
  }
  const now = Math.floor(Date.now() / 1e3);
  const expiresAt = payload.exp;
  return expiresAt <= now + JWT_EXPIRY_BUFFER_SECONDS;
}
async function refreshJWT(agent_id, token) {
  const url = `${AGENT_ID_API}/refresh`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ agent_id, token })
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `JWT refresh failed (${response.status}): ${errorText}`
    );
  }
  const data = await response.json();
  if (!data.jwt) {
    throw new Error("Invalid refresh response: missing jwt");
  }
  return data.jwt;
}
async function createIntentMandate(params, jwt) {
  const url = `${WALLET_API}/api/mandates/create-intent`;
  const headers = {
    "Content-Type": "application/json"
  };
  if (jwt) {
    headers["Authorization"] = `Bearer ${jwt}`;
  }
  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(params)
  });
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    throw new WalletApiError(
      `Invalid create-intent response (not JSON): ${text}`,
      response.status,
      text
    );
  }
}
async function requestX402V3Payment(params, jwt) {
  const url = `${WALLET_API}/api/payment/x402V3Payment`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${jwt}`
    },
    body: JSON.stringify(params)
  });
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    throw new WalletApiError(
      `Invalid x402V3Payment response (not JSON): ${text}`,
      response.status,
      text
    );
  }
}
async function getMandateStatus(mandateId, jwt) {
  const url = `${WALLET_API}/api/mandates/agent/${encodeURIComponent(mandateId)}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${jwt}`
    }
  });
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    throw new WalletApiError(
      `Invalid mandate status response (not JSON): ${text}`,
      response.status,
      text
    );
  }
}

// src/store/store.ts
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
var DATA_ROOT = process.env.FLUXA_DATA_DIR ? path.resolve(process.env.FLUXA_DATA_DIR) : path.join(os.homedir(), ".fluxa-ai-wallet-mcp");
var DATA_DIR = DATA_ROOT;
var CONFIG_FILE = path.join(DATA_DIR, "config.json");
var AUDIT_FILE = path.join(DATA_DIR, "audit.log");
function ensureDataDirs() {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
}
var memory = {
  config: null
};
var defaultConfig = {
  agentId: {
    agent_id: "",
    token: "",
    jwt: ""
  }
};
async function loadConfig() {
  let cfg = null;
  if (fs.existsSync(CONFIG_FILE)) {
    try {
      cfg = JSON.parse(fs.readFileSync(CONFIG_FILE, "utf-8"));
    } catch (e) {
      console.error("[store] Failed to parse config file, using default:", e);
    }
  }
  if (!cfg) {
    cfg = defaultConfig;
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(cfg, null, 2));
  }
  memory.config = cfg;
}
function saveConfig() {
  if (!memory.config) {
    memory.config = defaultConfig;
  }
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(memory.config, null, 2));
}
async function recordAudit(event) {
  const line = JSON.stringify({ ts: Date.now(), ...event }) + "\n";
  fs.appendFileSync(AUDIT_FILE, line);
}

// src/agent/agentId.ts
var runtimeJWT = null;
function getAgentId() {
  if (!memory.config || !memory.config.agentId || !memory.config.agentId.agent_id) {
    return null;
  }
  return memory.config.agentId;
}
function getAgentIdFromEnv() {
  const agentId = process.env.AGENT_ID;
  const token = process.env.AGENT_TOKEN;
  const jwt = process.env.AGENT_JWT;
  if (agentId && token && jwt) {
    return {
      agent_id: agentId,
      token,
      jwt
    };
  }
  return null;
}
function getEffectiveAgentId() {
  const agentId = getAgentIdFromEnv() || getAgentId();
  if (agentId && runtimeJWT) {
    return {
      ...agentId,
      jwt: runtimeJWT
    };
  }
  return agentId;
}
function hasAgentId() {
  const effective = getEffectiveAgentId();
  return Boolean(
    effective && effective.agent_id && effective.token && effective.jwt
  );
}
function getRegistrationInfoFromEnv() {
  const email = process.env.AGENT_EMAIL;
  const agentName = process.env.AGENT_NAME;
  const clientInfo = process.env.CLIENT_INFO;
  if (email && agentName && clientInfo) {
    return {
      email,
      agent_name: agentName,
      client_info: clientInfo
    };
  }
  return null;
}
function saveAgentId(config) {
  if (!memory.config) {
    throw new Error("Config not initialized");
  }
  memory.config.agentId = {
    ...config,
    registered_at: config.registered_at || (/* @__PURE__ */ new Date()).toISOString()
  };
  saveConfig();
}
function updateJWT(newJWT) {
  const envId = getAgentIdFromEnv();
  if (envId) {
    runtimeJWT = newJWT;
    console.error("[agent] JWT refreshed (runtime override for env vars)");
  } else {
    if (!memory.config || !memory.config.agentId) {
      throw new Error("Cannot update JWT: Agent ID not configured");
    }
    memory.config.agentId.jwt = newJWT;
    saveConfig();
    console.error("[agent] JWT refreshed and saved to config file");
  }
}

// src/cli.ts
var DEFAULT_NETWORK = "base";
var DEFAULT_ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
function printUsage() {
  console.log(`
FluxA Wallet CLI - Standalone command-line tool for FluxA Wallet operations

USAGE:
  node fluxa-cli.bundle.js <command> [options]

COMMANDS:
  status                    Check agent configuration status
  init                      Initialize/register agent ID
  payout                    Create a payout
  payout-status             Query payout status
  x402                      Generate x402 payment header (v1)
  mandate-create            Create an intent mandate for x402 v3
  mandate-status            Query mandate status
  x402-v3                   Generate x402 v3 payment with mandate

OPTIONS FOR 'init':
  --email <email>           Email address for registration
  --name <name>             Agent name
  --client <info>           Client info description
  (Or set AGENT_EMAIL, AGENT_NAME, CLIENT_INFO environment variables)

OPTIONS FOR 'payout':
  --to <address>            Recipient address (required)
  --amount <amount>         Amount in smallest units (required)
  --id <payout_id>          Unique payout ID (required)
  --network <network>       Network (default: base)
  --asset <address>         Asset contract address (default: USDC)

OPTIONS FOR 'payout-status':
  --id <payout_id>          Payout ID to query (required)

OPTIONS FOR 'x402':
  --payload <json>          Full x402 payment payload as JSON (required)

OPTIONS FOR 'mandate-create':
  --desc <text>             Natural language description (required)
  --amount <amount>         Budget limit in atomic units (required)
  --seconds <duration>      Validity duration in seconds (default: 28800 = 8 hours)
  --category <category>     Category (default: general)
  --currency <currency>     Currency (default: USDC)

OPTIONS FOR 'mandate-status':
  --id <mandate_id>         Mandate ID to query (required)

OPTIONS FOR 'x402-v3':
  --mandate <mandate_id>    Mandate ID (required)
  --payload <json>          Full x402 payment payload as JSON (required)

ENVIRONMENT VARIABLES:
  AGENT_ID                  Pre-configured agent ID
  AGENT_TOKEN               Pre-configured agent token
  AGENT_JWT                 Pre-configured agent JWT
  AGENT_EMAIL               Email for auto-registration
  AGENT_NAME                Agent name for auto-registration
  CLIENT_INFO               Client info for auto-registration
  FLUXA_DATA_DIR            Custom data directory path

EXAMPLES:
  # Check status
  node fluxa-cli.bundle.js status

  # Initialize with parameters
  node fluxa-cli.bundle.js init --email user@example.com --name "My Agent" --client "CLI v1.0"

  # Create payout
  node fluxa-cli.bundle.js payout --to 0x1234...abcd --amount 1000000 --id pay_001

  # Query payout status
  node fluxa-cli.bundle.js payout-status --id pay_001

  # Create intent mandate (x402 v3)
  node fluxa-cli.bundle.js mandate-create --desc "Spend up to 0.1 USDC for API calls" --amount 100000

  # Query mandate status
  node fluxa-cli.bundle.js mandate-status --id mand_xxxxx
`);
}
function parseArgs(args) {
  const command = args[0] || "help";
  const options = {};
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith("--")) {
      const key = arg.slice(2);
      const value = args[i + 1];
      if (value && !value.startsWith("--")) {
        options[key] = value;
        i++;
      } else {
        options[key] = "true";
      }
    }
  }
  return { command, options };
}
function output(result) {
  console.log(JSON.stringify(result, null, 2));
}
async function ensureValidJWT() {
  const agentConfig = getEffectiveAgentId();
  if (!agentConfig) {
    return null;
  }
  let jwt = agentConfig.jwt;
  if (isJWTExpired(jwt)) {
    console.error("[cli] JWT expired or expiring soon, refreshing...");
    try {
      jwt = await refreshJWT(agentConfig.agent_id, agentConfig.token);
      updateJWT(jwt);
      console.error("[cli] JWT refreshed successfully");
    } catch (err) {
      console.error("[cli] Failed to refresh JWT:", err);
      return null;
    }
  }
  return { agent_id: agentConfig.agent_id, jwt };
}
async function cmdStatus() {
  const hasConfig = hasAgentId();
  const agentConfig = getEffectiveAgentId();
  const regInfo = getRegistrationInfoFromEnv();
  if (hasConfig && agentConfig) {
    return {
      success: true,
      data: {
        configured: true,
        agent_id: agentConfig.agent_id,
        has_token: !!agentConfig.token,
        has_jwt: !!agentConfig.jwt,
        jwt_expired: isJWTExpired(agentConfig.jwt),
        email: agentConfig.email,
        agent_name: agentConfig.agent_name
      }
    };
  }
  return {
    success: true,
    data: {
      configured: false,
      has_registration_info: !!regInfo,
      registration_email: regInfo?.email
    }
  };
}
async function cmdInit(options) {
  if (hasAgentId()) {
    const agentConfig = getEffectiveAgentId();
    return {
      success: true,
      data: {
        message: "Agent ID already configured",
        agent_id: agentConfig?.agent_id
      }
    };
  }
  const email = options.email || process.env.AGENT_EMAIL;
  const agentName = options.name || process.env.AGENT_NAME;
  const clientInfo = options.client || process.env.CLIENT_INFO;
  if (!email || !agentName || !clientInfo) {
    return {
      success: false,
      error: "Missing required parameters: --email, --name, --client (or set AGENT_EMAIL, AGENT_NAME, CLIENT_INFO)"
    };
  }
  try {
    const result = await registerAgent({ email, agent_name: agentName, client_info: clientInfo });
    saveAgentId({
      agent_id: result.agent_id,
      token: result.token,
      jwt: result.jwt,
      email,
      agent_name: agentName,
      client_info: clientInfo
    });
    await recordAudit({
      event: "agent_registered",
      agent_id: result.agent_id,
      email
    });
    return {
      success: true,
      data: {
        message: "Agent registered successfully",
        agent_id: result.agent_id
      }
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || "Registration failed"
    };
  }
}
async function cmdPayout(options) {
  const toAddress = options.to;
  const amount = options.amount;
  const payoutId = options.id;
  const network = options.network || DEFAULT_NETWORK;
  const assetAddress = options.asset || DEFAULT_ASSET;
  if (!toAddress || !amount || !payoutId) {
    return {
      success: false,
      error: "Missing required parameters: --to, --amount, --id"
    };
  }
  if (!/^0x[a-fA-F0-9]{40}$/.test(toAddress)) {
    return {
      success: false,
      error: "Invalid recipient address format"
    };
  }
  if (!/^\d+$/.test(amount)) {
    return {
      success: false,
      error: "Amount must be a positive integer (smallest units)"
    };
  }
  const auth = await ensureValidJWT();
  if (!auth) {
    return {
      success: false,
      error: 'FluxA Agent ID not initialized. Run "init" first.'
    };
  }
  const currency = getCurrencyFromAsset(assetAddress, network);
  try {
    const result = await createPayout(
      {
        agentId: auth.agent_id,
        toAddress,
        amount,
        currency,
        network,
        assetAddress,
        payoutId
      },
      auth.jwt
    );
    await recordAudit({
      event: "payout_request",
      payout_id: payoutId,
      to: toAddress,
      amount,
      status: result.status
    });
    return {
      success: true,
      data: result
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || "Payout request failed"
    };
  }
}
async function cmdPayoutStatus(options) {
  const payoutId = options.id;
  if (!payoutId) {
    return {
      success: false,
      error: "Missing required parameter: --id"
    };
  }
  try {
    const result = await getPayoutStatus(payoutId);
    await recordAudit({
      event: "payout_status_query",
      payout_id: payoutId,
      status: result.status
    });
    return {
      success: true,
      data: result
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || "Payout status query failed"
    };
  }
}
async function cmdX402(options) {
  const payloadJson = options.payload;
  if (!payloadJson) {
    return {
      success: false,
      error: "Missing required parameter: --payload (JSON string)"
    };
  }
  let payload;
  try {
    payload = JSON.parse(payloadJson);
  } catch {
    return {
      success: false,
      error: "Invalid JSON in --payload"
    };
  }
  const auth = await ensureValidJWT();
  if (!auth) {
    return {
      success: false,
      error: 'FluxA Agent ID not initialized. Run "init" first.'
    };
  }
  const accept = payload.accepts?.[0];
  if (!accept) {
    return {
      success: false,
      error: "Invalid payload: missing accepts array"
    };
  }
  const request = {
    scheme: accept.scheme || "exact",
    network: accept.network || DEFAULT_NETWORK,
    amount: accept.maxAmountRequired || "0",
    currency: getCurrencyFromAsset(accept.asset || DEFAULT_ASSET, accept.network || DEFAULT_NETWORK),
    assetAddress: accept.asset || DEFAULT_ASSET,
    payTo: accept.payTo,
    host: extractHost(accept.resource || ""),
    resource: accept.resource || "",
    description: accept.description || "",
    tokenName: accept.extra?.name || "USD Coin",
    tokenVersion: accept.extra?.version || "2",
    validityWindowSeconds: accept.maxTimeoutSeconds || 60,
    approvalId: payload.approvalId
  };
  try {
    const xPaymentHeader = await requestX402Payment(request, auth.jwt);
    await recordAudit({
      event: "x402_payment",
      resource: request.resource,
      amount: request.amount
    });
    return {
      success: true,
      data: {
        "X-PAYMENT": xPaymentHeader
      }
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || "x402 payment request failed"
    };
  }
}
var DEFAULT_MANDATE_SECONDS = 8 * 3600;
var DEFAULT_MANDATE_CATEGORY = "general";
async function cmdMandateCreate(options) {
  const description = options.desc;
  const limitAmount = options.amount;
  const validForSeconds = options.seconds;
  const category = options.category || DEFAULT_MANDATE_CATEGORY;
  const currency = options.currency || "USDC";
  if (!description || !limitAmount) {
    return {
      success: false,
      error: "Missing required parameters: --desc, --amount"
    };
  }
  if (!/^\d+$/.test(limitAmount)) {
    return {
      success: false,
      error: "Amount must be a positive integer (atomic units)"
    };
  }
  let seconds = DEFAULT_MANDATE_SECONDS;
  if (validForSeconds) {
    seconds = parseInt(validForSeconds, 10);
    if (!Number.isFinite(seconds) || seconds <= 0) {
      return {
        success: false,
        error: "Seconds must be a positive integer"
      };
    }
  }
  const auth = await ensureValidJWT();
  if (!auth) {
    return {
      success: false,
      error: 'FluxA Agent ID not initialized. Run "init" first.'
    };
  }
  try {
    const result = await createIntentMandate(
      {
        intent: {
          naturalLanguage: description,
          category,
          currency,
          limitAmount,
          validForSeconds: seconds,
          hostAllowlist: []
        }
      },
      auth.jwt
    );
    await recordAudit({
      event: "mandate_create",
      mandate_id: result.mandateId,
      limit: limitAmount,
      seconds
    });
    return {
      success: result.status === "ok",
      data: result,
      error: result.status !== "ok" ? result.message : void 0
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || "Mandate creation failed"
    };
  }
}
async function cmdMandateStatus(options) {
  const mandateId = options.id;
  if (!mandateId) {
    return {
      success: false,
      error: "Missing required parameter: --id"
    };
  }
  const auth = await ensureValidJWT();
  if (!auth) {
    return {
      success: false,
      error: 'FluxA Agent ID not initialized. Run "init" first.'
    };
  }
  try {
    const result = await getMandateStatus(mandateId, auth.jwt);
    await recordAudit({
      event: "mandate_status_query",
      mandate_id: mandateId,
      status: result.mandate?.status
    });
    return {
      success: result.status === "ok",
      data: result,
      error: result.status !== "ok" ? result.message : void 0
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || "Mandate status query failed"
    };
  }
}
async function cmdX402V3(options) {
  const mandateId = options.mandate;
  const payloadJson = options.payload;
  if (!mandateId || !payloadJson) {
    return {
      success: false,
      error: "Missing required parameters: --mandate, --payload"
    };
  }
  let payload;
  try {
    payload = JSON.parse(payloadJson);
  } catch {
    return {
      success: false,
      error: "Invalid JSON in --payload"
    };
  }
  const auth = await ensureValidJWT();
  if (!auth) {
    return {
      success: false,
      error: 'FluxA Agent ID not initialized. Run "init" first.'
    };
  }
  const accept = payload.accepts?.[0];
  if (!accept) {
    return {
      success: false,
      error: "Invalid payload: missing accepts array"
    };
  }
  try {
    const result = await requestX402V3Payment(
      {
        mandateId,
        scheme: accept.scheme || "exact",
        network: accept.network || DEFAULT_NETWORK,
        amount: accept.maxAmountRequired || "0",
        currency: getCurrencyFromAsset(accept.asset || DEFAULT_ASSET, accept.network || DEFAULT_NETWORK),
        assetAddress: accept.asset || DEFAULT_ASSET,
        payTo: accept.payTo,
        host: extractHost(accept.resource || ""),
        resource: accept.resource || "",
        description: accept.description || "",
        tokenName: accept.extra?.name || "USD Coin",
        tokenVersion: accept.extra?.version || "2",
        validityWindowSeconds: accept.maxTimeoutSeconds || 60
      },
      auth.jwt
    );
    await recordAudit({
      event: "x402_v3_payment",
      mandate_id: mandateId,
      resource: accept.resource,
      amount: accept.maxAmountRequired
    });
    return {
      success: result.status === "ok",
      data: result,
      error: result.status !== "ok" ? result.message : void 0
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || "x402 v3 payment request failed"
    };
  }
}
async function main() {
  const args = process.argv.slice(2);
  const { command, options } = parseArgs(args);
  ensureDataDirs();
  await loadConfig();
  let result;
  switch (command) {
    case "status":
      result = await cmdStatus();
      break;
    case "init":
      result = await cmdInit(options);
      break;
    case "payout":
      result = await cmdPayout(options);
      break;
    case "payout-status":
      result = await cmdPayoutStatus(options);
      break;
    case "x402":
      result = await cmdX402(options);
      break;
    case "mandate-create":
      result = await cmdMandateCreate(options);
      break;
    case "mandate-status":
      result = await cmdMandateStatus(options);
      break;
    case "x402-v3":
      result = await cmdX402V3(options);
      break;
    case "help":
    case "--help":
    case "-h":
      printUsage();
      process.exit(0);
    default:
      console.error(`Unknown command: ${command}`);
      printUsage();
      process.exit(1);
  }
  output(result);
  process.exit(result.success ? 0 : 1);
}
main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
