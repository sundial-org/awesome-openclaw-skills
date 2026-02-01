#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function loadDotEnv(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const text = fs.readFileSync(filePath, 'utf8');
  const env = {};
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    env[key] = value;
  }
  return env;
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('-')) {
      args._.push(token);
      continue;
    }
    if (token === '--') {
      args._.push(...argv.slice(i + 1));
      break;
    }
    const next = argv[i + 1];
    if (token.includes('=')) {
      const [key, value] = token.split('=');
      args[key.replace(/^--/, '')] = value;
    } else if (next && !next.startsWith('-')) {
      args[token.replace(/^--/, '')] = next;
      i += 1;
    } else {
      args[token.replace(/^--/, '')] = true;
    }
  }
  return args;
}

function buildBaseUrl(domain) {
  if (!domain) return '';
  if (domain.startsWith('http://') || domain.startsWith('https://')) return domain.replace(/\/$/, '');
  return `https://${domain.replace(/\/$/, '')}`;
}

function buildTableQuery(params) {
  const query = new URLSearchParams();
  const allowed = [
    'sysparm_query',
    'sysparm_display_value',
    'sysparm_exclude_reference_link',
    'sysparm_suppress_pagination_header',
    'sysparm_fields',
    'sysparm_limit',
    'sysparm_view',
    'sysparm_query_category',
    'sysparm_query_no_domain',
    'sysparm_no_count',
  ];
  if (params.sysparm_display_value === undefined) {
    query.set('sysparm_display_value', 'true');
  }
  for (const key of allowed) {
    if (params[key] !== undefined) {
      query.set(key, String(params[key]));
    }
  }
  return query.toString();
}

function buildAttachmentQuery(params) {
  const query = new URLSearchParams();
  const allowed = [
    'sysparm_query',
    'sysparm_suppress_pagination_header',
    'sysparm_limit',
    'sysparm_query_category',
  ];
  for (const key of allowed) {
    if (params[key] !== undefined) {
      query.set(key, String(params[key]));
    }
  }
  return query.toString();
}

function buildAggregateQuery(params) {
  const query = new URLSearchParams();
  const allowed = [
    'sysparm_query',
    'sysparm_avg_fields',
    'sysparm_count',
    'sysparm_min_fields',
    'sysparm_max_fields',
    'sysparm_sum_fields',
    'sysparm_group_by',
    'sysparm_order_by',
    'sysparm_having',
    'sysparm_display_value',
    'sysparm_query_category',
  ];
  for (const key of allowed) {
    if (params[key] !== undefined) {
      query.set(key, String(params[key]));
    }
  }
  return query.toString();
}

function buildServiceCatalogQuery(params) {
  const query = new URLSearchParams();
  const allowed = [
    'sysparm_view',
    'sysparm_limit',
    'sysparm_text',
    'sysparm_offset',
    'sysparm_category',
    'sysparm_type',
    'sysparm_catalog',
    'sysparm_top_level_only',
    'record_id',
    'template_id',
    'mode',
  ];
  for (const key of allowed) {
    if (params[key] !== undefined) {
      query.set(key, String(params[key]));
    }
  }
  return query.toString();
}

function resolveAuth(args, dotenv) {
  const domain = args.domain || process.env.SERVICENOW_DOMAIN || dotenv.SERVICENOW_DOMAIN;
  const username = args.username || args.user || process.env.SERVICENOW_USERNAME || dotenv.SERVICENOW_USERNAME;
  const password = args.password || args.pass || process.env.SERVICENOW_PASSWORD || dotenv.SERVICENOW_PASSWORD;
  return { domain, username, password };
}

function formatHelp() {
  return `ServiceNow Table API CLI (read-only)

Usage:
  cli.mjs list <table> [options]
  cli.mjs get <table> <sys_id> [options]
  cli.mjs batch <file.json> [options]
  cli.mjs attach list [options]
  cli.mjs attach get <sys_id>
  cli.mjs attach file <sys_id> [--out <path>]
  cli.mjs attach file-by-name <table_sys_id> <file_name> [--out <path>]
  cli.mjs stats <table> [options]
  cli.mjs schema <table>
  cli.mjs history <table> <sys_id>
  cli.mjs sc <endpoint> [args] [options]

Auth (flags override env):
  --domain <domain>     ServiceNow instance domain
  --username <user>     Basic auth username (alias: --user)
  --password <pass>     Basic auth password (alias: --pass)

Common options:
  --sysparm_query <q>
  --sysparm_fields <fields>
  --sysparm_limit <n>
  --sysparm_display_value <true|false|all>
  --sysparm_exclude_reference_link <true|false>
  --pretty              Pretty-print JSON
  --out <path>           Save binary attachment content to a file

Examples:
  node cli.mjs list incident --sysparm_limit 5 --sysparm_fields number,short_description
  node cli.mjs get incident <sys_id> --sysparm_fields number,opened_at
  node cli.mjs batch specialists/incidents.json
  node cli.mjs attach list --sysparm_query "table_name=incident" --sysparm_limit 5
  node cli.mjs attach file <sys_id> --out /tmp/error.png
  node cli.mjs stats incident --sysparm_query "active=true" --sysparm_count true
  node cli.mjs schema incident
  node cli.mjs history incident <sys_id>
  node cli.mjs sc catalogs --sysparm_text "laptop" --sysparm_limit 5
  node cli.mjs sc item-variables <item_sys_id>
`;
}

async function requestJson(baseUrl, username, password, pathAndQuery) {
  const auth = Buffer.from(`${username}:${password}`).toString('base64');
  const url = `${baseUrl}${pathAndQuery}`;
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/json',
      'Authorization': `Basic ${auth}`,
    },
  });
  const text = await response.text();
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${text.slice(0, 500)}`);
  }
  return text;
}

async function requestBinary(baseUrl, username, password, pathAndQuery) {
  const auth = Buffer.from(`${username}:${password}`).toString('base64');
  const url = `${baseUrl}${pathAndQuery}`;
  const response = await fetch(url, {
    headers: {
      'Authorization': `Basic ${auth}`,
    },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text.slice(0, 500)}`);
  }
  const arrayBuffer = await response.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

async function handleList(args, auth, pretty) {
  const table = args._[1];
  if (!table) throw new Error('Missing <table>');
  const query = buildTableQuery(args);
  const pathAndQuery = query
    ? `/api/now/table/${encodeURIComponent(table)}?${query}`
    : `/api/now/table/${encodeURIComponent(table)}`;
  return requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery, pretty);
}

async function handleGet(args, auth, pretty) {
  const table = args._[1];
  const sysId = args._[2];
  if (!table || !sysId) throw new Error('Missing <table> or <sys_id>');
  const query = buildTableQuery(args);
  const pathAndQuery = query
    ? `/api/now/table/${encodeURIComponent(table)}/${encodeURIComponent(sysId)}?${query}`
    : `/api/now/table/${encodeURIComponent(table)}/${encodeURIComponent(sysId)}`;
  return requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery, pretty);
}

async function handleBatch(args, auth, pretty) {
  const filePath = args._[1];
  if (!filePath) throw new Error('Missing <file.json>');
  const absolutePath = path.isAbsolute(filePath) ? filePath : path.join(process.cwd(), filePath);
  const text = fs.readFileSync(absolutePath, 'utf8');
  const data = JSON.parse(text);
  const requests = Array.isArray(data) ? data : data.requests;
  if (!Array.isArray(requests)) {
    throw new Error('Batch file must be an array or { "requests": [...] }');
  }

  const results = [];
  for (const req of requests) {
    const table = req.table;
    if (!table) {
      results.push({ name: req.name || null, error: 'Missing table' });
      continue;
    }
    const params = { ...req };
    delete params.name;
    delete params.table;
    delete params.sys_id;
    const query = buildTableQuery(params);

    let pathAndQuery = `/api/now/table/${encodeURIComponent(table)}`;
    if (req.sys_id) {
      pathAndQuery += `/${encodeURIComponent(req.sys_id)}`;
    }
    if (query) {
      pathAndQuery += `?${query}`;
    }

    try {
      const body = await requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery);
      results.push({ name: req.name || null, ok: true, result: JSON.parse(body) });
    } catch (error) {
      results.push({ name: req.name || null, ok: false, error: String(error) });
    }
  }

  return JSON.stringify(results, null, pretty ? 2 : 0);
}

async function handleAttachment(args, auth) {
  const sub = args._[1];
  if (sub === 'list') {
    const query = buildAttachmentQuery(args);
    const pathAndQuery = query ? `/api/now/attachment?${query}` : '/api/now/attachment';
    return requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery);
  }
  if (sub === 'get') {
    const sysId = args._[2];
    if (!sysId) throw new Error('Missing <sys_id>');
    return requestJson(auth.baseUrl, auth.username, auth.password, `/api/now/attachment/${encodeURIComponent(sysId)}`);
  }
  if (sub === 'file') {
    const sysId = args._[2];
    if (!sysId) throw new Error('Missing <sys_id>');
    const data = await requestBinary(auth.baseUrl, auth.username, auth.password, `/api/now/attachment/${encodeURIComponent(sysId)}/file`);
    return { binary: data };
  }
  if (sub === 'file-by-name') {
    const tableSysId = args._[2];
    const fileName = args._[3];
    if (!tableSysId || !fileName) throw new Error('Missing <table_sys_id> or <file_name>');
    const data = await requestBinary(
      auth.baseUrl,
      auth.username,
      auth.password,
      `/api/now/attachment/${encodeURIComponent(tableSysId)}/${encodeURIComponent(fileName)}/file`
    );
    return { binary: data };
  }
  throw new Error('Unknown attach command. Use: list | get | file | file-by-name');
}

async function handleStats(args, auth) {
  const table = args._[1];
  if (!table) throw new Error('Missing <table>');
  const query = buildAggregateQuery(args);
  const pathAndQuery = query
    ? `/api/now/stats/${encodeURIComponent(table)}?${query}`
    : `/api/now/stats/${encodeURIComponent(table)}`;
  return requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery);
}

async function handleServiceCatalog(args, auth) {
  const endpoint = args._[1];
  if (!endpoint) throw new Error('Missing <endpoint>');
  const query = buildServiceCatalogQuery(args);
  let path = '';

  switch (endpoint) {
    case 'cart':
      path = '/api/sn_sc/servicecatalog/cart';
      break;
    case 'delivery-address': {
      const userId = args._[2];
      if (!userId) throw new Error('Missing <user_id>');
      path = `/api/sn_sc/servicecatalog/cart/delivery_address/${encodeURIComponent(userId)}`;
      break;
    }
    case 'validate-categories':
      path = '/api/sn_sc/servicecatalog/catalog_builder/validate_catalog_categories';
      break;
    case 'on-change-choices': {
      const entityId = args._[2];
      if (!entityId) throw new Error('Missing <entity_id>');
      path = `/api/sn_sc/servicecatalog/catalog_client_script/on_change_choices/${encodeURIComponent(entityId)}`;
      break;
    }
    case 'catalogs':
      path = '/api/sn_sc/servicecatalog/catalogs';
      break;
    case 'catalog': {
      const sysId = args._[2];
      if (!sysId) throw new Error('Missing <sys_id>');
      path = `/api/sn_sc/servicecatalog/catalogs/${encodeURIComponent(sysId)}`;
      break;
    }
    case 'catalog-categories': {
      const sysId = args._[2];
      if (!sysId) throw new Error('Missing <sys_id>');
      path = `/api/sn_sc/servicecatalog/catalogs/${encodeURIComponent(sysId)}/categories`;
      break;
    }
    case 'category': {
      const sysId = args._[2];
      if (!sysId) throw new Error('Missing <sys_id>');
      path = `/api/sn_sc/servicecatalog/categories/${encodeURIComponent(sysId)}`;
      break;
    }
    case 'items':
      path = '/api/sn_sc/servicecatalog/items';
      break;
    case 'item': {
      const sysId = args._[2];
      if (!sysId) throw new Error('Missing <sys_id>');
      path = `/api/sn_sc/servicecatalog/items/${encodeURIComponent(sysId)}`;
      break;
    }
    case 'item-variables': {
      const sysId = args._[2];
      if (!sysId) throw new Error('Missing <sys_id>');
      path = `/api/sn_sc/servicecatalog/items/${encodeURIComponent(sysId)}/variables`;
      break;
    }
    case 'item-delegation': {
      const itemSysId = args._[2];
      const userSysId = args._[3];
      if (!itemSysId || !userSysId) throw new Error('Missing <item_sys_id> or <user_sys_id>');
      path = `/api/sn_sc/servicecatalog/items/${encodeURIComponent(itemSysId)}/delegation/${encodeURIComponent(userSysId)}`;
      break;
    }
    case 'producer-record': {
      const producerId = args._[2];
      const recordId = args._[3];
      if (!producerId || !recordId) throw new Error('Missing <producer_id> or <record_id>');
      path = `/api/sn_sc/servicecatalog/producer/${encodeURIComponent(producerId)}/record/${encodeURIComponent(recordId)}`;
      break;
    }
    case 'record-wizard': {
      const recordId = args._[2];
      const wizardId = args._[3];
      if (!recordId || !wizardId) throw new Error('Missing <record_id> or <wizard_id>');
      path = `/api/sn_sc/servicecatalog/record_id/${encodeURIComponent(recordId)}/wizard/${encodeURIComponent(wizardId)}`;
      break;
    }
    case 'generate-stage-pool': {
      const quantity = args._[2];
      if (!quantity) throw new Error('Missing <quantity>');
      path = `/api/sn_sc/servicecatalog/service_fulfillment/generateStagePoolIds/${encodeURIComponent(quantity)}`;
      break;
    }
    case 'step-configs':
      path = '/api/sn_sc/servicecatalog/service_fulfillment/step_configs';
      break;
    case 'wishlist':
      path = '/api/sn_sc/servicecatalog/wishlist';
      break;
    case 'wishlist-item': {
      const cartItemId = args._[2];
      if (!cartItemId) throw new Error('Missing <cart_item_id>');
      path = `/api/sn_sc/servicecatalog/wishlist/${encodeURIComponent(cartItemId)}`;
      break;
    }
    case 'wizard': {
      const sysId = args._[2];
      if (!sysId) throw new Error('Missing <sys_id>');
      path = `/api/sn_sc/servicecatalog/wizard/${encodeURIComponent(sysId)}`;
      break;
    }
    default:
      throw new Error('Unknown service catalog endpoint');
  }

  const pathAndQuery = query ? `${path}?${query}` : path;
  return requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery);
}

async function handleSchema(args, auth, pretty) {
  const table = args._[1];
  if (!table) throw new Error('Missing <table>');

  const query = `name=${table}^elementISNOTEMPTY`;
  const fields = 'element,column_label,internal_type,reference';

  const pathAndQuery = `/api/now/table/sys_dictionary?sysparm_query=${encodeURIComponent(query)}&sysparm_fields=${fields}`;

  return requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery, pretty);
}

async function handleHistory(args, auth, pretty) {
  const table = args._[1];
  const sysId = args._[2];
  if (!table || !sysId) throw new Error('Missing <table> or <sys_id>');

  const query = `name=${table}^element_id=${sysId}`;
  const sort = 'sys_created_on';
  const fields = 'value,element,sys_created_on,sys_created_by';

  const pathAndQuery = `/api/now/table/sys_journal_field?sysparm_query=${encodeURIComponent(query)}&sysparm_order_by=${sort}&sysparm_fields=${fields}`;

  return requestJson(auth.baseUrl, auth.username, auth.password, pathAndQuery, pretty);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0] || 'help';
  if (args.help || command === 'help' || command === '--help' || command === '-h') {
    console.log(formatHelp());
    return;
  }

  const dotenv = loadDotEnv(path.join(__dirname, '.env'));
  const { domain, username, password } = resolveAuth(args, dotenv);
  const baseUrl = buildBaseUrl(domain);

  if (!baseUrl || !username || !password) {
    throw new Error('Missing auth. Set SERVICENOW_DOMAIN, SERVICENOW_USERNAME, SERVICENOW_PASSWORD or pass --domain/--username/--password.');
  }

  const auth = { baseUrl, username, password };
  const pretty = Boolean(args.pretty);
  let text;

  if (command === 'list') {
    text = await handleList(args, auth, pretty);
  } else if (command === 'get') {
    text = await handleGet(args, auth, pretty);
  } else if (command === 'batch') {
    text = await handleBatch(args, auth, pretty);
  } else if (command === 'attach') {
    const result = await handleAttachment(args, auth);
    if (result && result.binary) {
      const outPath = args.out;
      if (outPath) {
        fs.writeFileSync(outPath, result.binary);
        console.log(`Saved ${result.binary.length} bytes to ${outPath}`);
        return;
      }
      console.log(result.binary.toString('base64'));
      return;
    }
    text = result;
  } else if (command === 'stats') {
    text = await handleStats(args, auth);
  } else if (command === 'schema') {
    text = await handleSchema(args, auth, pretty);
  } else if (command === 'history') {
    text = await handleHistory(args, auth, pretty);
  } else if (command === 'sc') {
    text = await handleServiceCatalog(args, auth);
  } else {
    throw new Error(`Unknown command: ${command}`);
  }

  if (command === 'batch') {
    console.log(text);
    return;
  }

  if (pretty) {
    try {
      console.log(JSON.stringify(JSON.parse(text), null, 2));
      return;
    } catch {
      console.log(text);
      return;
    }
  }

  console.log(text);
}

main().catch((error) => {
  console.error(`Error: ${error.message || error}`);
  process.exit(1);
});