const fuzzy = require('./fuzzy');
const { cliError } = require('./errors');

/**
 * Resolve an entry from an object map by id or (fuzzy) name.
 *
 * Matching precedence (deterministic):
 * 1) direct id match
 * 2) exact name match (case-insensitive) – must be unique
 * 3) substring match (case-insensitive) – must be unique
 * 4) levenshtein best match – must be uniquely best and <= threshold
 *
 * @template T
 * @param {string} nameOrId
 * @param {Record<string, T>} obj
 * @param {object} opts
 * @param {string} opts.typeLabel e.g. 'device' | 'flow'
 * @param {(value: T) => string} opts.getName
 * @param {number} [opts.threshold=5]
 * @param {number} [opts.candidateLimit=20]
 * @param {number} [opts.suggestionLimit=5]
 * @returns {{id: string, value: T, name: string}}
 */
function resolveByIdOrName(nameOrId, obj, opts) {
  const typeLabel = opts?.typeLabel || 'item';
  const getName = opts?.getName || ((v) => String(v?.name || ''));
  const threshold = Number.isFinite(opts?.threshold) ? opts.threshold : 5;
  const candidateLimit = Number.isFinite(opts?.candidateLimit) ? opts.candidateLimit : 20;
  const suggestionLimit = Number.isFinite(opts?.suggestionLimit) ? opts.suggestionLimit : 5;

  const direct = obj?.[nameOrId];
  if (direct) {
    return { id: nameOrId, value: direct, name: getName(direct) };
  }

  const query = String(nameOrId || '').trim();
  if (!query) {
    throw cliError('INVALID_VALUE', `${typeLabel} query is required`);
  }
  const queryLower = query.toLowerCase();

  const entries = Object.entries(obj || {}).map(([id, value]) => {
    const name = getName(value);
    return {
      id,
      name,
      nameLower: (name || '').toLowerCase(),
      value,
    };
  });

  // 1) Exact match(es)
  const exactMatches = entries.filter((e) => e.nameLower === queryLower);
  if (exactMatches.length === 1) {
    const m = exactMatches[0];
    return { id: m.id, value: m.value, name: m.name };
  }
  if (exactMatches.length > 1) {
    throw cliError(
      'AMBIGUOUS',
      `ambiguous ${typeLabel} query '${query}' (matched ${exactMatches.length} ${typeLabel}s). Use an id.`,
      { candidates: exactMatches.slice(0, candidateLimit).map((m) => ({ id: m.id, name: m.name })) }
    );
  }

  // 2) Substring match(es)
  const substringMatches = entries.filter(
    (e) => e.nameLower.includes(queryLower) || queryLower.includes(e.nameLower)
  );
  if (substringMatches.length === 1) {
    const m = substringMatches[0];
    return { id: m.id, value: m.value, name: m.name };
  }
  if (substringMatches.length > 1) {
    throw cliError(
      'AMBIGUOUS',
      `ambiguous ${typeLabel} query '${query}' (matched ${substringMatches.length} ${typeLabel}s). Use an id.`,
      { candidates: substringMatches.slice(0, candidateLimit).map((m) => ({ id: m.id, name: m.name })) }
    );
  }

  // 3) Levenshtein best match (only if uniquely best)
  const distances = entries
    .map((e) => ({ e, d: fuzzy.levenshteinDistance(queryLower, e.nameLower) }))
    .sort((a, b) => a.d - b.d);

  const best = distances[0];
  if (!best || best.d > threshold) {
    const suggestions = fuzzy
      .fuzzySearch(query, entries, suggestionLimit)
      .map((e) => ({ id: e.id, name: e.name }))
      .filter((e) => e.name);

    throw cliError(
      'NOT_FOUND',
      `${typeLabel} not found: '${query}'`,
      suggestions.length ? { candidates: suggestions } : undefined
    );
  }

  const bestTied = distances.filter((x) => x.d === best.d && x.d <= threshold);
  if (bestTied.length !== 1) {
    throw cliError(
      'AMBIGUOUS',
      `ambiguous ${typeLabel} query '${query}' (matched ${bestTied.length} ${typeLabel}s at distance ${best.d}). Use an id.`,
      { candidates: bestTied.slice(0, candidateLimit).map((x) => ({ id: x.e.id, name: x.e.name })) }
    );
  }

  return { id: best.e.id, value: best.e.value, name: best.e.name };
}

module.exports = {
  resolveByIdOrName,
};
