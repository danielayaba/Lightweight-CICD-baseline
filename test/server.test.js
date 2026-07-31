// Tests use the native Node.js test runner (node --test) — no external
// dependency, which keeps the pipeline genuinely lightweight.
const { test } = require('node:test');
const assert = require('node:assert');
const { buildResponse } = require('../src/server.js');

test('buildResponse returns valid JSON', () => {
  const parsed = JSON.parse(buildResponse());
  assert.strictEqual(parsed.status, 'ok');
});

test('buildResponse includes a message', () => {
  const parsed = JSON.parse(buildResponse());
  assert.ok(parsed.message.length > 0);
});

test('buildResponse includes an ISO timestamp', () => {
  const parsed = JSON.parse(buildResponse());
  assert.ok(!Number.isNaN(Date.parse(parsed.timestamp)));
});
