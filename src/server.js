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

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'healthy' }));
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

module.exports = { server, buildResponse };
