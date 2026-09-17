import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { normalizeDemoSync, compatibleFetch } from '../scripts/rook-sync-compat.mjs';

test('hosted sync preserves authored content, hashes and unrelated agents', () => {
  const featureBody = 'local_id: F-001\nname: Claim settlement\n';
  const provenance = { agentId: 'claims', authoredFeatures: ['F-001', 'F-002'], sha256: {
    'features/F-001.yaml': createHash('sha256').update(featureBody).digest('hex'),
    'features/F-002.yaml': 'a-different-authored-body',
  } };
  const scenario = { origin: 'authored', author: 'user', content_hash: 'unchanged', body: 'origin: authored\n', acceptance_criteria: ['Keep this'] };
  const payload = { project_id: 'project', agents: [{ local_id: 'claims', scenario_revisions: [scenario, { origin: 'generated', author: 'model' }], feature_revisions: [
    { feature_local_id: 'F-001', body: featureBody, author: 'model' },
    { feature_local_id: 'F-002', body: 'regenerated content', author: 'model' },
  ] }, { local_id: 'unrelated', scenario_revisions: [scenario] }] };
  const expected = JSON.parse(JSON.stringify(payload));
  expected.agents[0].scenario_revisions[0].origin = 'manual';
  expected.agents[0].feature_revisions[0].author = 'user';
  const actual = normalizeDemoSync(JSON.stringify(payload), provenance);
  assert.deepEqual(JSON.parse(actual), expected);
  assert.equal(normalizeDemoSync(actual, provenance), actual);
  assert.equal(payload.agents[0].scenario_revisions[0].origin, 'authored');
});

test('compatibility only touches POST sync to the configured API', async () => {
  const calls = [];
  const response = { ok: true };
  const fetch = compatibleFetch((...args) => { calls.push(args); return response; }, { agentId: 'claims' }, ['https://rook.example/api/v1']);
  const body = JSON.stringify({ agents: [{ local_id: 'claims', scenario_revisions: [{ origin: 'authored', author: 'user' }] }] });
  const init = { method: 'POST', headers: { authorization: 'retained' }, signal: new AbortController().signal, body };
  assert.equal(await fetch('https://rook.example/api/v1/sync', init), response);
  assert.equal(JSON.parse(calls[0][1].body).agents[0].scenario_revisions[0].origin, 'manual');
  assert.equal(calls[0][1].headers, init.headers);
  assert.equal(calls[0][1].signal, init.signal);
  for (const url of ['https://model.example/api/v1/sync', 'https://rook.example/api/v1/runs', 'https://rook.example/api/v1/sync/extra']) {
    await fetch(url, init);
    assert.equal(calls.at(-1)[1], init);
  }
  const get = { ...init, method: 'GET' };
  await fetch('https://rook.example/api/v1/sync', get);
  assert.equal(calls.at(-1)[1], get);
  assert.equal(init.body, body);
});
