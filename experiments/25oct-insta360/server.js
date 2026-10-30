// Tiny HTTPS + WebSocket relay.
// Phone (phone.html) -> sends orientation -> server -> broadcasts to viewers (index.html).
// HTTPS is required because phones only expose motion sensors on secure pages.

import https from 'node:https';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import selfsigned from 'selfsigned';
import { WebSocketServer } from 'ws';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC = path.join(__dirname, 'public');
const PORT = Number(process.env.PORT) || 8443;

// --- self-signed cert, cached in ./certs so the phone only has to accept it once
const certDir = path.join(__dirname, 'certs');
const keyPath = path.join(certDir, 'key.pem');
const certPath = path.join(certDir, 'cert.pem');
if (!fs.existsSync(keyPath) || !fs.existsSync(certPath)) {
  fs.mkdirSync(certDir, { recursive: true });
  const pems = selfsigned.generate([{ name: 'commonName', value: 'insta360-imu.local' }], {
    days: 365,
    keySize: 2048,
  });
  fs.writeFileSync(keyPath, pems.private);
  fs.writeFileSync(certPath, pems.cert);
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.mp4': 'video/mp4',
};

const server = https.createServer(
  { key: fs.readFileSync(keyPath), cert: fs.readFileSync(certPath) },
  (req, res) => {
    let urlPath = decodeURIComponent(new URL(req.url, 'https://x').pathname);
    if (urlPath === '/') urlPath = '/index.html';
    if (urlPath === '/phone') urlPath = '/phone.html';
    const filePath = path.normalize(path.join(PUBLIC, urlPath));
    if (!filePath.startsWith(PUBLIC)) {
      res.writeHead(403).end();
      return;
    }
    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(404).end('Not found');
        return;
      }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(filePath)] || 'application/octet-stream' });
      res.end(data);
    });
  }
);

// --- WebSocket relay: phone messages go to every viewer, viewer messages go to every phone
// (orientation one way, WebRTC signalling for the live view both ways)
const wss = new WebSocketServer({ server, path: '/ws' });
wss.on('connection', (ws, req) => {
  const role = new URL(req.url, 'https://x').searchParams.get('role') || 'viewer';
  ws.role = role;
  console.log(`[ws] ${role} connected (${req.socket.remoteAddress})`);
  broadcastStatus();

  ws.on('message', (data) => {
    const target = ws.role === 'phone' ? 'viewer' : 'phone';
    for (const client of wss.clients) {
      if (client !== ws && client.role === target && client.readyState === 1) client.send(data.toString());
    }
  });
  ws.on('close', () => {
    console.log(`[ws] ${role} disconnected`);
    broadcastStatus();
  });
});

function broadcastStatus() {
  const phones = [...wss.clients].filter((c) => c.role === 'phone').length;
  const msg = JSON.stringify({ type: 'status', phones });
  for (const c of wss.clients) if (c.role === 'viewer' && c.readyState === 1) c.send(msg);
}

server.listen(PORT, '0.0.0.0', () => {
  const ips = Object.values(os.networkInterfaces())
    .flat()
    .filter((i) => i && i.family === 'IPv4' && !i.internal)
    .map((i) => i.address);
  console.log('\n  Insta360 IMU viewer running\n');
  console.log(`  Viewer (laptop):  https://localhost:${PORT}/`);
  for (const ip of ips) console.log(`  Phone:            https://${ip}:${PORT}/phone`);
  console.log('\n  Phone and laptop must be on the same Wi-Fi. Accept the certificate warning on both.\n');
});
