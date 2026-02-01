#!/usr/bin/env node
import process from "node:process";

function getEnv(k, d) { return process.env[k] || d; }

const host = getEnv("COMFYUI_HOST", "192.168.179.111");
const port = getEnv("COMFYUI_PORT", "28188");

async function readAllStdin() {
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  return Buffer.concat(chunks).toString("utf8");
}

async function main() {
  const arg = (process.argv[2] || "").trim();
  let input = null;

  if (arg) {
    try { input = JSON.parse(arg); } catch { input = { action: arg }; }
  } else {
    const s = (await readAllStdin()).trim();
    if (s) {
      try { input = JSON.parse(s); } catch { input = { action: s }; }
    }
  }

  input = input || { action: "status" };
  const action = String(input.action || "status").toLowerCase();

  if (action !== "status") {
    process.stdout.write(JSON.stringify({ ok: false, error: "only_status_supported_in_container" }) + "\n");
    return;
  }

  const url = "http://" + host + ":" + port + "/health";
  try {
    const res = await fetch(url, { method: "GET" });
    process.stdout.write(JSON.stringify({ ok: res.ok, status: res.status, host, port }) + "\n");
  } catch (e) {
    process.stdout.write(JSON.stringify({ ok: false, error: "unreachable", detail: String(e), host, port }) + "\n");
  }
}

main().catch(e => {
  process.stdout.write(JSON.stringify({ ok: false, error: String(e) }) + "\n");
  process.exit(1);
});
