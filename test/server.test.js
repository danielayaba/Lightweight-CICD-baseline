// Tests use the native Node.js test runner (node --test) — no external
// dependency, which keeps the pipeline genuinely lightweight.
const { test } = require('node:test');
const assert = require('node:assert');
const { buildResponse, buildHealth } = require('../src/server.js');

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

test('buildHealth reports a healthy status', () => {
  const parsed = JSON.parse(buildHealth());
  assert.strictEqual(parsed.status, 'healthy');
});

// The pipeline's post-deploy check reads this field to tell a freshly started
// container from the previous version, so its shape is part of the contract.
test('buildHealth reports uptime as a non-negative integer', () => {
  const parsed = JSON.parse(buildHealth());
  assert.strictEqual(typeof parsed.uptimeSeconds, 'number');
  assert.ok(Number.isInteger(parsed.uptimeSeconds));
  assert.ok(parsed.uptimeSeconds >= 0);
});
