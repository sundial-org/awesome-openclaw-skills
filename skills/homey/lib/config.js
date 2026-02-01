const fs = require('fs');
const path = require('path');
const os = require('os');

function getConfigPath() {
  // Backwards compatible path (existing installs).
  return path.join(os.homedir(), '.homey', 'config.json');
}

function _readConfigFile() {
  const configPath = getConfigPath();
  try {
    if (!fs.existsSync(configPath)) return { cfg: {}, path: configPath };
    const raw = fs.readFileSync(configPath, 'utf8');
    const parsed = JSON.parse(raw);
    return { cfg: parsed && typeof parsed === 'object' ? parsed : {}, path: configPath };
  } catch {
    return { cfg: {}, path: configPath };
  }
}

function _ensureConfigDirPrivate() {
  const configPath = getConfigPath();
  const configDir = path.dirname(configPath);

  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true, mode: 0o700 });
  }

  // Best-effort: keep the directory private too (umask might be permissive).
  try {
    fs.chmodSync(configDir, 0o700);
  } catch {
    // ignore
  }

  return { configPath, configDir };
}

function _writeConfigFile(nextCfg) {
  const { configPath } = _ensureConfigDirPrivate();

  fs.writeFileSync(configPath, JSON.stringify(nextCfg, null, 2) + '\n', {
    encoding: 'utf8',
    mode: 0o600,
  });

  // Best-effort: enforce private permissions even if file already existed.
  try {
    fs.chmodSync(configPath, 0o600);
  } catch {
    // ignore
  }

  return configPath;
}

function _normalizeMode(value) {
  const v = String(value || '').trim().toLowerCase();
  if (!v) return null;
  if (v === 'auto' || v === 'local' || v === 'cloud') return v;
  return null;
}

/**
 * Backwards compatible getter for a cloud token.
 *
 * Sources (in precedence order):
 * - env: HOMEY_TOKEN
 * - config: { cloud: { token } }
 * - legacy config: { token }
 */
function getCloudTokenInfo() {
  const { cfg, path: configPath } = _readConfigFile();

  if (process.env.HOMEY_TOKEN) {
    return { token: process.env.HOMEY_TOKEN, source: 'env', path: configPath };
  }

  const token = cfg?.cloud?.token || cfg?.token || null;
  return { token, source: token ? 'config' : null, path: configPath };
}

function getLocalTokenInfo() {
  const { cfg, path: configPath } = _readConfigFile();

  if (process.env.HOMEY_LOCAL_TOKEN) {
    return { token: process.env.HOMEY_LOCAL_TOKEN, source: 'env', path: configPath };
  }

  const token = cfg?.local?.token || null;
  return { token, source: token ? 'config' : null, path: configPath };
}

function getLocalAddressInfo() {
  const { cfg, path: configPath } = _readConfigFile();

  if (process.env.HOMEY_ADDRESS) {
    return { address: process.env.HOMEY_ADDRESS, source: 'env', path: configPath };
  }

  const address = cfg?.local?.address || null;
  return { address, source: address ? 'config' : null, path: configPath };
}

function getModeInfo() {
  const { cfg, path: configPath } = _readConfigFile();

  const envMode = _normalizeMode(process.env.HOMEY_MODE);
  if (envMode) {
    return { mode: envMode, source: 'env', path: configPath };
  }

  const cfgMode = _normalizeMode(cfg?.mode);
  if (cfgMode) {
    return { mode: cfgMode, source: 'config', path: configPath };
  }

  return { mode: 'auto', source: 'default', path: configPath };
}

/**
 * Resolve the effective connection settings.
 *
 * Selection rules:
 * - If HOMEY_MODE/config.mode is 'local' -> use local
 * - If 'cloud' -> use cloud
 * - If 'auto' -> prefer local when a local address is set, otherwise cloud
 */
function getConnectionInfo() {
  const modeInfo = getModeInfo();
  const cloud = getCloudTokenInfo();
  const localToken = getLocalTokenInfo();
  const localAddress = getLocalAddressInfo();

  const wanted = modeInfo.mode;

  let selected;
  if (wanted === 'local') selected = 'local';
  else if (wanted === 'cloud') selected = 'cloud';
  else {
    // auto
    selected = localAddress.address ? 'local' : 'cloud';
  }

  return {
    path: modeInfo.path,
    modeWanted: wanted,
    modeWantedSource: modeInfo.source,
    modeSelected: selected,
    local: {
      address: localAddress.address,
      addressSource: localAddress.source,
      token: localToken.token,
      tokenSource: localToken.source,
    },
    cloud: {
      token: cloud.token,
      tokenSource: cloud.source,
    },
  };
}

function saveCloudToken(token) {
  const t = String(token || '').trim();
  const { cfg } = _readConfigFile();

  const next = { ...(cfg || {}) };
  // Migrate legacy shape to structured shape.
  delete next.token;
  next.cloud = { ...(next.cloud || {}), token: t };

  return _writeConfigFile(next);
}

function saveLocalConfig({ address, token }) {
  const a = address !== undefined ? String(address || '').trim() : undefined;
  const t = token !== undefined ? String(token || '').trim() : undefined;
  const { cfg } = _readConfigFile();

  const next = { ...(cfg || {}) };
  const local = { ...(next.local || {}) };
  if (a !== undefined && a) local.address = a;
  if (t !== undefined && t) local.token = t;
  next.local = local;

  return _writeConfigFile(next);
}

function saveLocalAddress(address) {
  return saveLocalConfig({ address, token: undefined });
}

function saveMode(mode) {
  const m = _normalizeMode(mode);
  const { cfg } = _readConfigFile();
  const next = { ...(cfg || {}) };

  if (!m) {
    delete next.mode;
  } else {
    next.mode = m;
  }

  return _writeConfigFile(next);
}

function clearCloudToken() {
  const { cfg } = _readConfigFile();
  const next = { ...(cfg || {}) };
  if (next.cloud && typeof next.cloud === 'object') {
    delete next.cloud.token;
  }
  delete next.token; // legacy
  return _writeConfigFile(next);
}

function clearLocalConfig() {
  const { cfg } = _readConfigFile();
  const next = { ...(cfg || {}) };
  if (next.local && typeof next.local === 'object') {
    delete next.local.token;
    delete next.local.address;
  }
  return _writeConfigFile(next);
}

// Backwards compatible exports (cloud token)
function getTokenInfo() {
  return getCloudTokenInfo();
}

function getToken() {
  return getCloudTokenInfo().token;
}

function saveToken(token) {
  return saveCloudToken(token);
}

module.exports = {
  getConfigPath,

  // New API
  getModeInfo,
  getCloudTokenInfo,
  getLocalTokenInfo,
  getLocalAddressInfo,
  getConnectionInfo,

  saveCloudToken,
  saveLocalConfig,
  saveLocalAddress,
  saveMode,
  clearCloudToken,
  clearLocalConfig,

  // Legacy API
  getTokenInfo,
  getToken,
  saveToken,
};
