// Thin Hyperliquid Info API client (read-only)
// Node >=18 has global fetch.

const DEFAULT_URL = process.env.HYPERLIQUID_INFO_URL || "https://api.hyperliquid.xyz/info";
const DEFAULT_TIMEOUT_MS = Number(process.env.HYPERLIQUID_TIMEOUT_MS || 10_000);

function withTimeout(ms) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), ms);
  return { controller, done: () => clearTimeout(t) };
}

export async function postInfo(body, { url = DEFAULT_URL, timeoutMs = DEFAULT_TIMEOUT_MS } = {}) {
  const { controller, done } = withTimeout(timeoutMs);
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`Hyperliquid HTTP ${res.status}: ${text?.slice(0, 400)}`);
    }
    return await res.json();
  } finally {
    done();
  }
}

export async function metaAndAssetCtxs({ dex = "" } = {}) {
  return postInfo({ type: "metaAndAssetCtxs", dex });
}

export async function l2Book({ coin, nSigFigs = null, mantissa = undefined } = {}) {
  if (!coin) throw new Error("l2Book: coin is required");
  const body = { type: "l2Book", coin };
  if (nSigFigs !== undefined) body.nSigFigs = nSigFigs;
  if (mantissa !== undefined) body.mantissa = mantissa;
  return postInfo(body);
}

export async function candleSnapshot({ coin, interval, startTime, endTime } = {}) {
  if (!coin) throw new Error("candleSnapshot: coin is required");
  if (!interval) throw new Error("candleSnapshot: interval is required");
  if (startTime == null) throw new Error("candleSnapshot: startTime is required (ms)");
  if (endTime == null) throw new Error("candleSnapshot: endTime is required (ms)");
  return postInfo({ type: "candleSnapshot", req: { coin, interval, startTime, endTime } });
}

// --- account (read-only) ---

export async function clearinghouseState({ user, dex = "" } = {}) {
  if (!user) throw new Error("clearinghouseState: user is required");
  return postInfo({ type: "clearinghouseState", user, dex });
}

export async function spotClearinghouseState({ user } = {}) {
  if (!user) throw new Error("spotClearinghouseState: user is required");
  return postInfo({ type: "spotClearinghouseState", user });
}

export async function openOrders({ user, dex = "" } = {}) {
  if (!user) throw new Error("openOrders: user is required");
  return postInfo({ type: "openOrders", user, dex });
}

export async function userFills({ user, aggregateByTime = undefined } = {}) {
  if (!user) throw new Error("userFills: user is required");
  const body = { type: "userFills", user };
  if (aggregateByTime !== undefined) body.aggregateByTime = aggregateByTime;
  return postInfo(body);
}

export function pctChange(current, prev) {
  const c = Number(current);
  const p = Number(prev);
  if (!isFinite(c) || !isFinite(p) || p === 0) return null;
  return ((c - p) / p) * 100;
}

export function fmtNum(x, { dp = 2 } = {}) {
  const n = Number(x);
  if (!isFinite(n)) return String(x ?? "");
  return n.toLocaleString(undefined, { maximumFractionDigits: dp, minimumFractionDigits: 0 });
}

export function fmtPx(x) {
  // Keep more precision for small prices.
  const n = Number(x);
  if (!isFinite(n)) return String(x ?? "");
  const abs = Math.abs(n);
  const dp = abs >= 1000 ? 2 : abs >= 1 ? 4 : 6;
  return n.toLocaleString(undefined, { maximumFractionDigits: dp, minimumFractionDigits: 0 });
}

export function fmtPct(x) {
  const n = Number(x);
  if (!isFinite(n)) return "";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}%`;
}

export function nowMs() {
  return Date.now();
}

export function intervalToMs(interval) {
  const map = {
    "1m": 60_000,
    "3m": 180_000,
    "5m": 300_000,
    "15m": 900_000,
    "30m": 1_800_000,
    "1h": 3_600_000,
    "2h": 7_200_000,
    "4h": 14_400_000,
    "8h": 28_800_000,
    "12h": 43_200_000,
    "1d": 86_400_000,
    "3d": 259_200_000,
    "1w": 604_800_000,
    // 1M is variable; approximate to 30d for sizing windows.
    "1M": 2_592_000_000,
  };
  return map[interval] ?? null;
}
