#!/usr/bin/env node
import process from "node:process";
import crypto from "node:crypto";

function getEnv(k, d) { return process.env[k] || d; }

const host = getEnv("COMFYUI_HOST", "192.168.179.111");
const port = getEnv("COMFYUI_PORT", "28188");
const user = getEnv("COMFYUI_USER", "");
const pass = getEnv("COMFYUI_PASS", "");
const envTimeoutMs = parseInt(getEnv("COMFYUI_TIMEOUT_MS", "180000"), 10);
const envPollMs = parseInt(getEnv("COMFYUI_POLL_MS", "1000"), 10);

function parseArgs(argv) {
  const out = { first: false, timeoutMs: envTimeoutMs, pollMs: envPollMs };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--first") out.first = true;
    else if (a === "--timeout-ms" && argv[i + 1]) out.timeoutMs = parseInt(argv[++i], 10);
    else if (a === "--poll-ms" && argv[i + 1]) out.pollMs = parseInt(argv[++i], 10);
  }
  return out;
}

async function readAllStdin() {
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  return Buffer.concat(chunks).toString("utf8");
}

function parseInput(s) {
  const t = (s || "").trim();
  if (!t) return null;
  try { return JSON.parse(t); } catch { return null; }
}

function authHeaders() {
  const headers = { "content-type": "application/json" };
  if (user && pass) {
    const tok = Buffer.from(user + ":" + pass).toString("base64");
    headers["authorization"] = "Basic " + tok;
  }
  return headers;
}

async function httpJson(url, opts) {
  const res = await fetch(url, opts);
  const txt = await res.text();
  let data;
  try { data = JSON.parse(txt); } catch { data = { raw: txt }; }
  return { res, data, txt };
}

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function collectImagesFromOutputs(outputs) {
  const images = [];
  if (!outputs || typeof outputs !== "object") return images;
  for (const nodeId of Object.keys(outputs)) {
    const o = outputs[nodeId];
    if (o?.images && Array.isArray(o.images)) {
      for (const img of o.images) images.push(img);
    }
  }
  return images;
}

function toViewUrl(base, img) {
  const filename = encodeURIComponent(img?.filename || "");
  const subfolder = encodeURIComponent(img?.subfolder || "");
  const type = encodeURIComponent(img?.type || "");
  return `${base}/view?filename=${filename}&subfolder=${subfolder}&type=${type}`;
}

async function main() {
  const args = parseArgs(process.argv);

  const argJson = (process.argv[2] && process.argv[2].trim().startsWith("{")) ? process.argv[2] : "";
  const bodyStr = argJson ? argJson : await readAllStdin();
  const input = parseInput(bodyStr);

  const workflow = input?.workflow || input?.prompt || null;

  if (!workflow || typeof workflow !== "object") {
    process.stdout.write(JSON.stringify({
      ok: false,
      error: "missing_workflow",
      hint: "Send JSON as {\"workflow\": {...}} or {\"prompt\": {...}}"
    }) + "\n");
    process.exit(2);
  }

  const client_id = crypto.randomUUID();
  const base = "http://" + host + ":" + port;

  const submitUrl = base + "/prompt";
  const payload = { prompt: workflow, client_id };

  const { res: sres, data: sdata } = await httpJson(submitUrl, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  if (!sres.ok) {
    process.stdout.write(JSON.stringify({
      ok: false,
      step: "submit",
      status: sres.status,
      result: sdata
    }) + "\n");
    process.exit(3);
  }

  const prompt_id = sdata?.prompt_id || sdata?.promptId || null;
  if (!prompt_id) {
    process.stdout.write(JSON.stringify({
      ok: false,
      step: "submit",
      error: "no_prompt_id_returned",
      result: sdata
    }) + "\n");
    process.exit(4);
  }

  const histUrl = base + "/history/" + encodeURIComponent(prompt_id);
  const start = Date.now();
  let lastEntry = null;
  let lastRaw = null;

  while ((Date.now() - start) < args.timeoutMs) {
    const { res: hres, data: hdata, txt } = await httpJson(histUrl, { method: "GET", headers: authHeaders() });
    lastRaw = txt;

    if (!hres.ok) { await sleep(args.pollMs); continue; }

    const entry = hdata?.[prompt_id] || hdata?.[String(prompt_id)] || null;
    lastEntry = entry;

    const completed = entry?.status?.completed === true;
    const status_str = entry?.status?.status_str || null;
    const outputs = entry?.outputs || {};

    if (!completed) { await sleep(args.pollMs); continue; }

    const imagesAll = collectImagesFromOutputs(outputs);
    const images = args.first ? (imagesAll[0] ? [imagesAll[0]] : []) : imagesAll;

    if (!images.length) {
      process.stdout.write(JSON.stringify({
        ok: false,
        step: "poll",
        error: "completed_but_no_images",
        prompt_id,
        status_str,
        outputs
      }) + "\n");
      process.exit(7);
    }

    const image_urls = images.map(img => toViewUrl(base, img));

    process.stdout.write(JSON.stringify({
      ok: true,
      prompt_id,
      status_str,
      images,
      image_urls
    }) + "\n");
    return;
  }

  process.stdout.write(JSON.stringify({
    ok: false,
    step: "poll",
    error: "timeout_waiting_for_completion",
    prompt_id,
    last_entry: lastEntry,
    last_raw: lastRaw ? String(lastRaw).slice(0, 4000) : null
  }) + "\n");
  process.exit(5);
}

main().catch(e => {
  process.stdout.write(JSON.stringify({ ok: false, error: String(e) }) + "\n");
  process.exit(1);
});
