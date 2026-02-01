const mdns = require('multicast-dns');
const { cliError } = require('./errors');

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function normalizeName(name) {
  if (!name) return null;
  return String(name).replace(/\.$/, '');
}

async function fetchWithTimeout(url, timeoutMs) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: controller.signal });
    return res;
  } finally {
    clearTimeout(t);
  }
}

/**
 * Discover local Homey candidates via mDNS and verify by hitting the local ping endpoint.
 *
 * This is best-effort and depends on the host network supporting multicast DNS.
 *
 * @param {object} [opts]
 * @param {number} [opts.timeoutMs=6000] total discovery time
 * @param {number} [opts.pingTimeoutMs=1500] per-candidate ping timeout
 * @returns {Promise<Array<{address: string, host: string, port: number, homeyId: string|null, serviceType: string|null, instance: string|null}>>}
 */
async function discoverLocalHomeys(opts = {}) {
  const timeoutMs = Number.isFinite(opts.timeoutMs) ? opts.timeoutMs : 6000;
  const pingTimeoutMs = Number.isFinite(opts.pingTimeoutMs) ? opts.pingTimeoutMs : 1500;

  // Data we collect from mDNS.
  const serviceTypes = new Set();
  const instancesByType = new Map(); // type -> Set(instance)
  const srvByInstance = new Map(); // instance -> { target, port, type }
  const ipsByHost = new Map(); // host -> Set(ip)

  const m = mdns();

  function addIps(host, ip) {
    const h = normalizeName(host);
    if (!h || !ip) return;
    const set = ipsByHost.get(h) || new Set();
    set.add(ip);
    ipsByHost.set(h, set);
  }

  function addInstance(type, instance) {
    const t = normalizeName(type);
    const i = normalizeName(instance);
    if (!t || !i) return;
    const set = instancesByType.get(t) || new Set();
    set.add(i);
    instancesByType.set(t, set);
  }

  function onRecord(rec) {
    if (!rec || !rec.type) return;

    if (rec.type === 'PTR') {
      const name = normalizeName(rec.name);
      const data = normalizeName(rec.data);

      // Services list.
      if (name === '_services._dns-sd._udp.local') {
        if (data) serviceTypes.add(data);
        return;
      }

      // Instance list for a service type.
      if (name && data && name.endsWith('.local')) {
        addInstance(name, data);
      }
    }

    if (rec.type === 'SRV') {
      const instance = normalizeName(rec.name);
      const target = normalizeName(rec.data?.target);
      const port = rec.data?.port;
      if (!instance || !target || !Number.isFinite(port)) return;

      // Try to infer service type from the instance name (after first label).
      const parts = instance.split('.');
      const inferredType = parts.slice(1).join('.') || null;
      srvByInstance.set(instance, { target, port, type: inferredType });
      return;
    }

    if (rec.type === 'A' || rec.type === 'AAAA') {
      addIps(rec.name, rec.data);
    }
  }

  m.on('response', (packet) => {
    for (const r of packet.answers || []) onRecord(r);
    for (const r of packet.additionals || []) onRecord(r);
  });

  // Kick off discovery.
  // 1) Ask for all service types.
  m.query({
    questions: [{ name: '_services._dns-sd._udp.local', type: 'PTR' }],
  });

  // 2) Also proactively query a few likely service types (in case services list is blocked).
  const likelyTypes = [
    '_homey._tcp.local',
    '_homey._udp.local',
    '_athom._tcp.local',
    '_http._tcp.local', // fallback: filter by instance name later
  ];
  for (const t of likelyTypes) {
    m.query({ questions: [{ name: t, type: 'PTR' }] });
  }

  // Wait a bit to collect service types.
  await sleep(Math.min(1200, Math.max(300, Math.floor(timeoutMs / 5))));

  // Query PTRs for candidate service types.
  const typesToQuery = new Set(likelyTypes);
  for (const t of serviceTypes) {
    const tl = String(t).toLowerCase();
    if (tl.includes('homey') || tl.includes('athom')) {
      typesToQuery.add(t);
    }
  }

  for (const t of typesToQuery) {
    m.query({ questions: [{ name: t, type: 'PTR' }] });
  }

  // Keep querying SRV for instances we learn about until timeout.
  const deadline = Date.now() + timeoutMs;
  const queriedSrv = new Set();

  while (Date.now() < deadline) {
    for (const [type, instances] of instancesByType.entries()) {
      for (const inst of instances) {
        if (queriedSrv.has(inst)) continue;

        // Filter noisy services: for _http._tcp only consider instance names that look like Homey.
        if (type === '_http._tcp.local') {
          const il = inst.toLowerCase();
          if (!il.includes('homey') && !il.includes('athom')) continue;
        }

        queriedSrv.add(inst);
        m.query({ questions: [{ name: inst, type: 'SRV' }, { name: inst, type: 'A' }, { name: inst, type: 'AAAA' }] });
      }
    }

    await sleep(250);
  }

  m.destroy();

  // Build candidate addresses.
  const candidates = [];
  for (const [instance, srv] of srvByInstance.entries()) {
    const host = srv.target;
    const port = srv.port;

    // Prefer IPs if we saw them via mDNS; fallback to hostname.
    const ips = Array.from(ipsByHost.get(host) || []);
    const hostsToTry = ips.length ? ips : [host];

    for (const h of hostsToTry) {
      // Construct a base URL. Most Homey local endpoints accept HTTP.
      const scheme = port === 443 ? 'https' : 'http';
      const address = `${scheme}://${h}${(scheme === 'http' && port === 80) || (scheme === 'https' && port === 443) ? '' : `:${port}`}`;
      candidates.push({
        address,
        host: h,
        port,
        homeyId: null,
        serviceType: srv.type,
        instance,
      });
    }
  }

  // Dedupe by address.
  const uniq = new Map();
  for (const c of candidates) {
    if (!uniq.has(c.address)) uniq.set(c.address, c);
  }

  // Verify candidates by ping.
  const verified = [];
  for (const c of uniq.values()) {
    // Always try HTTP ping first, even if SRV says 443.
    // Reason: HTTPS might be self-signed depending on address form.
    const urlsToTry = [];
    if (c.address.startsWith('https://')) {
      urlsToTry.push(c.address.replace(/^https:\/\//, 'http://'));
      urlsToTry.push(c.address);
    } else {
      urlsToTry.push(c.address);
      urlsToTry.push(c.address.replace(/^http:\/\//, 'https://'));
    }

    let ok = false;
    for (const base of urlsToTry) {
      try {
        const res = await fetchWithTimeout(`${base}/api/manager/system/ping`, pingTimeoutMs);
        const homeyId = res.headers.get('X-Homey-ID');
        if (res.ok && homeyId) {
          verified.push({ ...c, address: base, homeyId });
          ok = true;
          break;
        }
      } catch {
        // ignore
      }
    }
    if (ok) continue;
  }

  // If we got zero SRV candidates, we may still have a common mDNS host form:
  // homey-<id>.local (HomeyAPIV3's mDNS strategy). Without an id we can't construct it.
  // So verified may be empty.
  return verified;
}

function formatCandidates(cands) {
  return cands.map((c, i) => ({
    index: i + 1,
    address: c.address,
    homeyId: c.homeyId,
    host: c.host,
    port: c.port,
  }));
}

function requireDiscovered(cands) {
  if (!cands.length) {
    throw cliError(
      'NOT_FOUND',
      'no local Homey found via mDNS (are you on the same LAN/VPN?)',
      {
        help:
          'Try one of:\n' +
          '  - Run on the same network as Homey (LAN/VPN)\n' +
          '  - Provide the address manually: homeycli auth set-local --address http://<homey-ip> ...\n' +
          '  - Use cloud mode on remote hosts: homeycli auth set-token --stdin',
      }
    );
  }
}

module.exports = {
  discoverLocalHomeys,
  formatCandidates,
  requireDiscovered,
};
