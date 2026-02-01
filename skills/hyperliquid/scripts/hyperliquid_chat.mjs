#!/usr/bin/env node
// hyperliquid_chat.mjs
// Minimal intent parser + formatter for v1.

import {
  metaAndAssetCtxs,
  l2Book,
  candleSnapshot,
  clearinghouseState,
  spotClearinghouseState,
  openOrders,
  userFills,
  pctChange,
  fmtNum,
  fmtPx,
  fmtPct,
  intervalToMs,
  nowMs,
} from "./hyperliquid_api.mjs";

import {
  loadConfig,
  setAccountAlias,
  removeAccountAlias,
  setDefaultAccount,
  resolveAccountRef,
  extractEvmAddress,
} from "./hyperliquid_config.mjs";

function stripPrefix(s) {
  const t = s.trim();
  if (t.toLowerCase().startsWith("/hl ")) return t.slice(4).trim();
  if (t.toLowerCase() === "/hl") return "";
  if (t.toLowerCase().startsWith("hl ")) return t.slice(3).trim();
  if (t.toLowerCase() === "hl") return "";
  return null;
}

function tokenize(s) {
  // Split like a shell: keep quoted segments together.
  const out = [];
  const re = /"([^"]*)"|'([^']*)'|(\S+)/g;
  for (const m of s.matchAll(re)) {
    out.push(m[1] ?? m[2] ?? m[3]);
  }
  return out.filter(Boolean);
}

function parseArgs(tokens) {
  // extremely small flag parser
  const args = { _: [] };
  for (let i = 0; i < tokens.length; i++) {
    const tok = tokens[i];
    if (tok.startsWith("--")) {
      const key = tok.slice(2);
      const next = tokens[i + 1];
      if (next && !next.startsWith("--")) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(tok);
    }
  }
  return args;
}

function guessIntentFromNL(text) {
  const t = text.toLowerCase();

  // account/positions + account aliasing
  if ((t.includes("store") || t.includes("save")) && t.includes("0x") && t.includes(" as ")) return { cmd: "account-save" };
  if ((t.includes("list") || t.includes("show")) && (t.includes("saved accounts") || t.includes("saved account") || t.includes("accounts list"))) {
    return { cmd: "account-list" };
  }

  if (t.includes("position") || t.includes("positions") || t.includes("margin")) return { cmd: "positions" };
  if (t.includes("balance") || t.includes("balances")) return { cmd: "balances" };
  if (t.includes("open orders") || t.includes("open order")) return { cmd: "orders" };
  if (t.includes("fills") || t.includes("trades") || t.includes("executions")) return { cmd: "fills" };

  // market data
  if (t.includes("overview")) return { cmd: "overview" };
  if (t.includes("mover")) return { cmd: "movers" };
  if (t.includes("funding")) {
    if (t.includes("top") || t.includes("highest")) return { cmd: "funding-top" };
    if (t.includes("bottom") || t.includes("lowest")) return { cmd: "funding-bottom" };
    return { cmd: "funding" };
  }
  if (t.includes("order book") || t.includes("book") || t.includes("l2")) return { cmd: "book" };
  if (t.includes("candle")) return { cmd: "candles" };
  if (t.includes("quote") || t.includes("price")) return { cmd: "quote" };
  return { cmd: "overview" };
}

function extractCoin(text) {
  // naive: first ALLCAPS token 2-10 chars
  const m = text.match(/\b[A-Z][A-Z0-9]{1,9}\b/);
  return m ? m[0] : null;
}

function extractUserAddress(text) {
  // Deprecated wrapper; keep for older code paths.
  return extractEvmAddress(text);
}

function shortAddr(addr) {
  if (!addr) return "";
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

async function getPerpsTable() {
  const [meta, ctxs] = await metaAndAssetCtxs({ dex: "" });
  const universe = meta?.universe ?? [];
  const rows = universe.map((u, i) => {
    const c = ctxs?.[i] ?? {};
    return { u, c };
  });
  return rows;
}

function formatQuote(coin, row) {
  const c = row.c;
  const chg = pctChange(c.markPx, c.prevDayPx);
  const lines = [];
  lines.push(`Hyperliquid ${coin} (perp)`);
  lines.push(`- mark: ${fmtPx(c.markPx)} | mid: ${c.midPx == null ? "—" : fmtPx(c.midPx)} | oracle: ${c.oraclePx == null ? "—" : fmtPx(c.oraclePx)}`);
  lines.push(`- 24h: ${c.prevDayPx == null ? "—" : fmtPct(chg)} (prev ${fmtPx(c.prevDayPx)})`);
  if (c.funding != null) lines.push(`- funding: ${fmtNum(Number(c.funding) * 100, { dp: 4 })}%`);
  if (c.openInterest != null) lines.push(`- OI: ${fmtNum(c.openInterest, { dp: 2 })}`);
  if (c.dayNtlVlm != null) lines.push(`- 24h notional: ${fmtNum(c.dayNtlVlm, { dp: 0 })}`);
  if (c.premium != null) lines.push(`- premium: ${fmtNum(Number(c.premium) * 100, { dp: 4 })}%`);
  if (Array.isArray(c.impactPxs)) lines.push(`- impact: buy ${fmtPx(c.impactPxs[0])} | sell ${fmtPx(c.impactPxs[1])}`);
  return lines.join("\n");
}

async function cmdQuote({ coin }) {
  const rows = await getPerpsTable();
  const row = rows.find((r) => r.u?.name?.toUpperCase() === coin.toUpperCase());
  if (!row) throw new Error(`Unknown perp coin: ${coin}`);
  return formatQuote(coin.toUpperCase(), row);
}

async function cmdMovers({ top = 10 }) {
  const n = Number(top);
  const rows = await getPerpsTable();
  const movers = rows
    .map((r) => {
      const c = r.c;
      const chg = pctChange(c.markPx, c.prevDayPx);
      return { coin: r.u?.name, chg, mark: c.markPx, vol: c.dayNtlVlm };
    })
    .filter((x) => x.coin && x.chg != null)
    .sort((a, b) => Math.abs(b.chg) - Math.abs(a.chg))
    .slice(0, isFinite(n) ? n : 10);

  const lines = [];
  lines.push(`Hyperliquid movers (perps, by |24h %|)`);
  for (const m of movers) {
    lines.push(`- ${m.coin}: ${fmtPct(m.chg)} | mark ${fmtPx(m.mark)} | 24h vol ${m.vol == null ? "—" : fmtNum(m.vol, { dp: 0 })}`);
  }
  return lines.join("\n");
}

async function cmdFundingRank({ n = 10, dir = "top" }) {
  const N = Number(n);
  const rows = await getPerpsTable();
  const ranked = rows
    .map((r) => ({ coin: r.u?.name, funding: Number(r.c?.funding) }))
    .filter((x) => x.coin && isFinite(x.funding))
    .sort((a, b) => (dir === "top" ? b.funding - a.funding : a.funding - b.funding))
    .slice(0, isFinite(N) ? N : 10);

  const lines = [];
  lines.push(`Hyperliquid funding (${dir})`);
  for (const x of ranked) {
    lines.push(`- ${x.coin}: ${fmtNum(x.funding * 100, { dp: 4 })}%`);
  }
  return lines.join("\n");
}

async function cmdBook({ coin }) {
  const book = await l2Book({ coin });
  const levels = book?.levels;
  if (!levels) throw new Error("No book levels returned");
  const [bids, asks] = levels;
  const bestBid = bids?.[0];
  const bestAsk = asks?.[0];
  const spread = bestBid && bestAsk ? Number(bestAsk.px) - Number(bestBid.px) : null;

  const lines = [];
  lines.push(`Hyperliquid L2 book: ${coin}`);
  if (bestBid && bestAsk) lines.push(`- best bid ${fmtPx(bestBid.px)} | best ask ${fmtPx(bestAsk.px)} | spread ${spread == null ? "—" : fmtPx(spread)}`);
  lines.push(`- bids:`);
  for (const l of (bids ?? []).slice(0, 10)) lines.push(`  - ${fmtPx(l.px)} x ${fmtNum(l.sz, { dp: 6 })} (n=${l.n})`);
  lines.push(`- asks:`);
  for (const l of (asks ?? []).slice(0, 10)) lines.push(`  - ${fmtPx(l.px)} x ${fmtNum(l.sz, { dp: 6 })} (n=${l.n})`);
  return lines.join("\n");
}

async function cmdCandles({ coin, interval = "1h", last = 48, start, end }) {
  let startTime, endTime;
  if (start && end) {
    startTime = Number(start);
    endTime = Number(end);
  } else {
    const ms = intervalToMs(interval);
    const L = Number(last);
    if (!ms || !isFinite(L)) throw new Error("Provide --start/--end (ms) or a valid --interval and --last N");
    endTime = nowMs();
    startTime = endTime - ms * L;
  }
  const candles = await candleSnapshot({ coin, interval, startTime, endTime });
  const lines = [];
  lines.push(`Hyperliquid candles: ${coin} (${interval})`);
  const tail = (candles ?? []).slice(-10);
  for (const c of tail) {
    lines.push(`- ${new Date(c.t).toISOString()} o:${fmtPx(c.o)} h:${fmtPx(c.h)} l:${fmtPx(c.l)} c:${fmtPx(c.c)} v:${fmtNum(c.v, { dp: 4 })}`);
  }
  lines.push(`(showing last ${tail.length} of ${candles?.length ?? 0})`);
  return lines.join("\n");
}

async function cmdOverview() {
  const [movers, fTop, oiTop] = await Promise.all([
    cmdMovers({ top: 5 }),
    cmdFundingRank({ n: 5, dir: "top" }),
    (async () => {
      const rows = await getPerpsTable();
      const ranked = rows
        .map((r) => ({ coin: r.u?.name, oi: Number(r.c?.openInterest) }))
        .filter((x) => x.coin && isFinite(x.oi))
        .sort((a, b) => b.oi - a.oi)
        .slice(0, 5);
      const lines = [];
      lines.push(`Hyperliquid OI (top)`);
      for (const x of ranked) lines.push(`- ${x.coin}: ${fmtNum(x.oi, { dp: 2 })}`);
      return lines.join("\n");
    })(),
  ]);

  return [movers, "", fTop, "", oiTop].join("\n");
}

function liqDistancePct({ side, markPx, liquidationPx }) {
  const m = Number(markPx);
  const l = Number(liquidationPx);
  if (!isFinite(m) || !isFinite(l) || m === 0) return null;
  // Distance as percent move from mark to liquidation.
  if (side === "long") return ((m - l) / m) * 100;
  if (side === "short") return ((l - m) / m) * 100;
  return null;
}

function formatPositions(user, st, markByCoin = new Map()) {
  const ms = st?.marginSummary;
  const cms = st?.crossMarginSummary;
  const lines = [];
  lines.push(`Hyperliquid positions (${shortAddr(user)})`);

  if (ms) {
    const av = Number(ms.accountValue);
    const mu = Number(ms.totalMarginUsed);
    const free = isFinite(av) && isFinite(mu) ? av - mu : null;
    lines.push(
      `- margin acct: value ${fmtNum(ms.accountValue, { dp: 2 })} | notional ${fmtNum(ms.totalNtlPos, { dp: 2 })} | margin used ${fmtNum(ms.totalMarginUsed, { dp: 2 })}${free == null ? "" : ` | free ${fmtNum(free, { dp: 2 })}`}`
    );
  }
  if (cms) {
    lines.push(`- cross acct: value ${fmtNum(cms.accountValue, { dp: 2 })} | notional ${fmtNum(cms.totalNtlPos, { dp: 2 })}`);
  }
  if (st?.withdrawable != null) lines.push(`- withdrawable: ${fmtNum(st.withdrawable, { dp: 2 })}`);

  const aps = st?.assetPositions ?? [];
  if (!aps.length) {
    lines.push(`- no open perp positions`);
    return lines.join("\n");
  }

  lines.push(`- open positions:`);
  for (const ap of aps) {
    const p = ap?.position;
    if (!p) continue;

    const szi = Number(p.szi);
    const side = isFinite(szi) ? (szi > 0 ? "long" : szi < 0 ? "short" : "flat") : "";
    const absSz = isFinite(szi) ? Math.abs(szi) : p.szi;

    const mark = markByCoin.get(p.coin);
    const dist = liqDistancePct({ side, markPx: mark, liquidationPx: p.liquidationPx });

    const headerBits = [
      `${p.coin} ${side}`,
      `sz ${absSz}`,
      `mark ${mark == null ? "—" : fmtPx(mark)}`,
      `entry ${fmtPx(p.entryPx)}`,
      `liq ${p.liquidationPx == null ? "—" : fmtPx(p.liquidationPx)}`,
      dist == null ? null : `liq dist ${fmtPct(dist)}`,
    ].filter(Boolean);

    const pnlBits = [
      `uPnL ${fmtNum(p.unrealizedPnl, { dp: 2 })}`,
      p.returnOnEquity == null ? null : `ROE ${fmtPct(Number(p.returnOnEquity) * 100)}`,
      p.positionValue == null ? null : `pos ${fmtNum(p.positionValue, { dp: 2 })}`,
    ].filter(Boolean);

    lines.push(`  - ${headerBits.join(" | ")}`);
    lines.push(`    - ${pnlBits.join(" | ")}`);

    if (p.leverage) {
      lines.push(
        `    - lev: ${p.leverage.type} ${p.leverage.value}x | marginUsed ${fmtNum(p.marginUsed, { dp: 2 })}${p.cumFunding?.sinceOpen == null ? "" : ` | funding since open ${fmtNum(p.cumFunding.sinceOpen, { dp: 4 })}`}`
      );
    }
  }

  return lines.join("\n");
}

async function cmdPositions({ user }) {
  const st = await clearinghouseState({ user, dex: "" });
  // Also pull current marks for nicer display.
  let markByCoin = new Map();
  try {
    const rows = await getPerpsTable();
    for (const r of rows) markByCoin.set(r.u?.name, r.c?.markPx);
  } catch {
    // ignore market-data failures; still show positions
  }
  return formatPositions(user, st, markByCoin);
}

async function cmdBalances({ user }) {
  const st = await spotClearinghouseState({ user });
  const bals = st?.balances ?? [];
  const lines = [];
  lines.push(`Hyperliquid spot balances (${shortAddr(user)})`);
  if (!bals.length) {
    lines.push(`- none`);
    return lines.join("\n");
  }
  for (const b of bals) {
    if (!b) continue;
    lines.push(`- ${b.coin}: total ${fmtNum(b.total, { dp: 8 })} | hold ${fmtNum(b.hold, { dp: 8 })}`);
  }
  return lines.join("\n");
}

async function cmdOrders({ user }) {
  const orders = await openOrders({ user, dex: "" });
  const lines = [];
  lines.push(`Hyperliquid open orders (${shortAddr(user)})`);
  if (!orders?.length) {
    lines.push(`- none`);
    return lines.join("\n");
  }
  for (const o of orders.slice(0, 20)) {
    lines.push(`- ${o.coin} ${o.side} ${o.sz} @ ${o.limitPx} (oid ${o.oid})`);
  }
  if (orders.length > 20) lines.push(`(showing 20 of ${orders.length})`);
  return lines.join("\n");
}

async function cmdFills({ user, n = 10 }) {
  const fills = await userFills({ user, aggregateByTime: true });
  const lines = [];
  lines.push(`Hyperliquid fills (${shortAddr(user)})`);
  if (!fills?.length) {
    lines.push(`- none`);
    return lines.join("\n");
  }
  for (const f of fills.slice(0, Number(n) || 10)) {
    const ts = f.time ? new Date(f.time).toISOString() : "";
    lines.push(`- ${ts} ${f.coin} ${f.side} ${f.sz} @ ${f.px} | fee ${f.fee} ${f.feeToken}`);
  }
  return lines.join("\n");
}

async function main() {
  const raw = process.argv.slice(2).join(" ").trim();
  if (!raw) {
    console.log("Usage: hyperliquid_chat.mjs \"hl quote BTC\"");
    process.exit(0);
  }

  const pref = stripPrefix(raw);
  if (pref != null) {
    const tokens = tokenize(pref);
    const args = parseArgs(tokens);
    const cmd = (args._[0] ?? "overview").toLowerCase();
    const rest0 = args._[1];

    if (cmd === "quote") return console.log(await cmdQuote({ coin: rest0 }));
    if (cmd === "movers") return console.log(await cmdMovers({ top: args.top ?? args.n ?? 10 }));
    if (cmd === "funding-top") return console.log(await cmdFundingRank({ n: args.n ?? 10, dir: "top" }));
    if (cmd === "funding-bottom") return console.log(await cmdFundingRank({ n: args.n ?? 10, dir: "bottom" }));
    if (cmd === "book") return console.log(await cmdBook({ coin: rest0 }));
    if (cmd === "candles") {
      return console.log(
        await cmdCandles({
          coin: rest0,
          interval: args.interval ?? "1h",
          last: args.last ?? 48,
          start: args.start,
          end: args.end,
        })
      );
    }

    // account (read-only) + saved aliases
    if (cmd === "positions" || cmd === "balances" || cmd === "orders" || cmd === "fills") {
      const ref = extractUserAddress(pref) ?? rest0 ?? "";
      const resolved = await resolveAccountRef(ref);
      if (!resolved.address) {
        if (resolved.source === "missing") throw new Error("No address provided and no default account set. Add one with: hl account add \"sub account 1\" HL:0x... --default");
        throw new Error(`Unknown saved account: ${resolved.label ?? ref}`);
      }
      if (cmd === "positions") return console.log(await cmdPositions({ user: resolved.address }));
      if (cmd === "balances") return console.log(await cmdBalances({ user: resolved.address }));
      if (cmd === "orders") return console.log(await cmdOrders({ user: resolved.address }));
      if (cmd === "fills") return console.log(await cmdFills({ user: resolved.address, n: args.n ?? 10 }));
    }

    if (cmd === "account") {
      const sub = (args._[1] ?? "list").toLowerCase();
      const label = args._[2];
      const addr = args._[3];

      if (sub === "list") {
        const cfg = await loadConfig();
        const keys = Object.keys(cfg.accounts || {}).sort();
        const lines = [];
        lines.push(`Hyperliquid saved accounts`);
        if (!keys.length) {
          lines.push(`- none`);
          return console.log(lines.join("\n"));
        }
        for (const k of keys) {
          const def = cfg.defaultAccount === k ? " (default)" : "";
          lines.push(`- ${k}: ${cfg.accounts[k]}${def}`);
        }
        return console.log(lines.join("\n"));
      }

      if (sub === "add") {
        if (!label || !addr) throw new Error('Usage: hl account add "sub account 1" HL:0x... [--default]');
        await setAccountAlias({ label, address: addr, makeDefault: Boolean(args.default) });
        return console.log(`Saved ${shortAddr(extractUserAddress(addr))} as "${label}"${args.default ? " (default)" : ""}`);
      }

      if (sub === "remove" || sub === "rm" || sub === "delete" || sub === "del") {
        if (!label) throw new Error('Usage: hl account remove "sub account 1"');
        await removeAccountAlias({ label });
        return console.log(`Removed saved account "${label}"`);
      }

      if (sub === "default") {
        if (!label) throw new Error('Usage: hl account default "sub account 1"');
        await setDefaultAccount({ label });
        return console.log(`Default account set to "${label}"`);
      }

      throw new Error(`Unknown account subcommand: ${sub}`);
    }

    if (cmd === "overview") return console.log(await cmdOverview());

    throw new Error(`Unknown command: ${cmd}`);
  }

  // NL fallback
  const { cmd } = guessIntentFromNL(raw);
  const coin = extractCoin(raw);

  // Natural-language account aliasing (simple v1):
  // "store this address 0x... as sub account 1" / "save ... as ..."
  if (cmd === "account-save") {
    const addr = extractUserAddress(raw);
    const m = raw.match(/\bas\s+(.+)$/i);
    const label = m ? m[1].trim() : null;
    if (!addr || !label) throw new Error('Usage: "store this address HL:0x... as sub account 1"');
    await setAccountAlias({ label, address: addr });
    return console.log(`Saved ${shortAddr(addr)} as "${label}"`);
  }

  if (cmd === "account-list") {
    const cfg = await loadConfig();
    const keys = Object.keys(cfg.accounts || {}).sort();
    const lines = [];
    lines.push(`Hyperliquid saved accounts`);
    if (!keys.length) {
      lines.push(`- none`);
      return console.log(lines.join("\n"));
    }
    for (const k of keys) {
      const def = cfg.defaultAccount === k ? " (default)" : "";
      lines.push(`- ${k}: ${cfg.accounts[k]}${def}`);
    }
    return console.log(lines.join("\n"));
  }

  // Account views: allow address OR saved label OR default.
  if (cmd === "positions" || cmd === "balances" || cmd === "orders" || cmd === "fills") {
    const ref = extractUserAddress(raw) ?? null;
    // If no explicit address, try to infer label after keywords.
    const labelGuess = (() => {
      // e.g. "show me positions of sub account 1"
      const m = raw.match(/\b(?:of|for)\s+(.+)$/i);
      return m ? m[1].trim() : "";
    })();

    const resolved = await resolveAccountRef(ref || labelGuess || "");
    if (!resolved.address) {
      if (resolved.source === "missing") {
        throw new Error('Provide an address (HL:0x...) or save one first: "store this address HL:0x... as sub account 1"');
      }
      throw new Error(`Unknown saved account: ${resolved.label}`);
    }

    if (cmd === "positions") return console.log(await cmdPositions({ user: resolved.address }));
    if (cmd === "balances") return console.log(await cmdBalances({ user: resolved.address }));
    if (cmd === "orders") return console.log(await cmdOrders({ user: resolved.address }));
    if (cmd === "fills") return console.log(await cmdFills({ user: resolved.address, n: 10 }));
  }

  if (cmd === "quote") return console.log(await cmdQuote({ coin: coin ?? "BTC" }));
  if (cmd === "movers") return console.log(await cmdMovers({ top: 10 }));
  if (cmd === "funding-top") return console.log(await cmdFundingRank({ n: 10, dir: "top" }));
  if (cmd === "funding-bottom") return console.log(await cmdFundingRank({ n: 10, dir: "bottom" }));
  if (cmd === "book") return console.log(await cmdBook({ coin: coin ?? "BTC" }));
  if (cmd === "candles") return console.log(await cmdCandles({ coin: coin ?? "BTC" }));
  return console.log(await cmdOverview());
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
