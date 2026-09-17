import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

// The current CLI calls hand-authored scenarios "authored"; the hosted API's
// database calls that origin "manual". Preserve the YAML, its hash and author.
export function normalizeDemoSync(body, provenance) {
  let changed = false;
  const data = JSON.parse(body);
  for (const agent of data.agents ?? []) {
    if (agent.local_id !== provenance.agentId) continue;
    for (const scenario of agent.scenario_revisions ?? []) {
      if (scenario.origin === 'authored' && scenario.author === 'user') {
        scenario.origin = 'manual';
        changed = true;
      }
    }
    // The CLI assumes all features were model-generated. Only correct the
    // exact authored feature bodies recorded in this demo's provenance.
    for (const feature of agent.feature_revisions ?? []) {
      const id = feature.feature_local_id;
      if (!provenance.authoredFeatures?.includes(id) || typeof feature.body !== 'string') continue;
      const hash = createHash('sha256').update(feature.body).digest('hex');
      if (hash === provenance.sha256?.[`features/${id}.yaml`] && feature.author === 'model') {
        feature.author = 'user';
        changed = true;
      }
    }
  }
  return changed ? JSON.stringify(data) : body;
}

export function compatibleFetch(fetch, provenance, apiBases) {
  const endpoints = new Set(apiBases.map(base => `${base.replace(/\/$/, '')}/sync`));
  return function (input, init) {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input?.url;
    if (endpoints.has(url) && init?.method === 'POST' && typeof init.body === 'string') {
      const body = normalizeDemoSync(init.body, provenance);
      if (body !== init.body) init = { ...init, body };
    }
    return fetch.call(this, input, init);
  };
}

if (process.env.ROOK_DEMO_SYNC_PROVENANCE) {
  const provenance = JSON.parse(readFileSync(process.env.ROOK_DEMO_SYNC_PROVENANCE, 'utf8'));
  const bases = process.env.ROOK_API_URL ? [process.env.ROOK_API_URL] : [
    'https://stage-rook-api.lambdatestinternal.com/api/v1',
    'https://rook-api.lambdatest.com/api/v1',
    'http://localhost:8081/api/v1',
  ];
  globalThis.fetch = compatibleFetch(globalThis.fetch, provenance, bases);
}
