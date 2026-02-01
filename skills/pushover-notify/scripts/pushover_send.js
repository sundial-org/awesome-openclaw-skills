#!/usr/bin/env node
/**
 * Send a push notification via Pushover.
 *
 * Usage:
 *   PUSHOVER_APP_TOKEN=... PUSHOVER_USER_KEY=... \
 *   node pushover_send.js --title "Hi" --message "Test" [--url "https://..."] [--url-title "Open"] \
 *     [--priority -1|0|1|2] [--sound "pushover"] [--device "iphone"] [--timestamp 1700000000]
 *
 * Notes:
 * - For priority=2 (emergency), you should also pass --retry <seconds> and --expire <seconds>.
 */

function die(msg) {
  process.stderr.write(msg + "\n");
  process.exit(2);
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) { out._.push(a); continue; }
    const key = a.slice(2);
    const next = argv[i + 1];
    const isBool = (next == null) || next.startsWith("--");
    if (isBool) {
      out[key] = true;
    } else {
      out[key] = next;
      i++;
    }
  }
  return out;
}

async function main() {
  const args = parseArgs(process.argv);

  const token = process.env.PUSHOVER_APP_TOKEN || process.env.PUSHOVER_TOKEN || args.token;
  const user = process.env.PUSHOVER_USER_KEY || process.env.PUSHOVER_USER || args.user;

  if (!token) die("Missing Pushover app token. Set PUSHOVER_APP_TOKEN (or pass --token).");
  if (!user) die("Missing Pushover user key. Set PUSHOVER_USER_KEY (or pass --user).");

  const title = args.title || "";
  const message = args.message || args.m;
  if (!message) die("Missing --message.");

  const priority = args.priority != null ? String(args.priority) : undefined;
  const retry = args.retry != null ? String(args.retry) : undefined;
  const expire = args.expire != null ? String(args.expire) : undefined;

  if (priority === "2") {
    if (!retry || !expire) {
      die("priority=2 requires --retry and --expire (in seconds). Example: --retry 60 --expire 3600");
    }
  }

  const body = new URLSearchParams();
  body.set("token", token);
  body.set("user", user);
  body.set("message", message);
  if (title) body.set("title", title);

  const optionalFields = [
    ["device", args.device],
    ["url", args.url],
    ["url_title", args["url-title"] || args.url_title],
    ["sound", args.sound],
    ["priority", priority],
    ["timestamp", args.timestamp],
    ["retry", retry],
    ["expire", expire],
  ];
  for (const [k, v] of optionalFields) {
    if (v != null && v !== "") body.set(k, String(v));
  }

  const res = await fetch("https://api.pushover.net/1/messages.json", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  const text = await res.text();
  let json;
  try { json = JSON.parse(text); } catch { json = null; }

  if (!res.ok) {
    const detail = json ? JSON.stringify(json) : text;
    die(`Pushover API error (${res.status}): ${detail}`);
  }

  // Print a compact success payload.
  if (json) {
    process.stdout.write(JSON.stringify({ ok: true, status: res.status, request: json.request }, null, 2) + "\n");
  } else {
    process.stdout.write(text + "\n");
  }
}

main().catch((err) => {
  die(err && err.stack ? err.stack : String(err));
});
