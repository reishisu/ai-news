// ロックファイルの resolved は registry.npmjs.org だが、
// registry 設定を差し替えると npm はここへ取りに来る。
const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, 'mirror');
const LOG = path.join(__dirname, 'access.log');

http.createServer((req, res) => {
  const p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  const file = path.join(ROOT, p);
  fs.appendFileSync(LOG, p + '\n');
  if (fs.existsSync(file) && fs.statSync(file).isFile()) {
    res.writeHead(200, { 'content-type': 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  } else {
    res.writeHead(404); res.end('not found');
  }
}).listen(8871, '127.0.0.1', () => console.log('mirror on 8871'));
