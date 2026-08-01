// Minimal baseline application (App 1) — a dependency-free Node.js HTTP server.
// Serves as the stable, controlled baseline for the pipeline test protocol.
const http = require('http');

const PORT = process.env.PORT || 3000;

function buildResponse() {
  return JSON.stringify({
    status: 'ok',
    message: 'Lightweight CI/CD pipeline — baseline app',
    timestamp: new Date().toISOString(),
  });
}

// Health payload. uptimeSeconds is what makes post-deploy verification
// possible: right after a deploy is triggered the *previous* version is still
// answering 200, so a status code alone would confirm a deployment that has
// not happened yet. A process that started after the deploy was triggered is
// proof that a fresh container is serving. Deliberately derived from
// process.uptime() rather than a host-specific variable, so the check works on
// any target, not just Render.
function buildHealth() {
  return JSON.stringify({
    status: 'healthy',
    uptimeSeconds: Math.floor(process.uptime()),
  });
}

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(buildHealth());
    return;
  }
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(buildResponse());
});

// Only listen when the file is run directly (not while the tests import it).
if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
}

module.exports = { server, buildResponse, buildHealth };
