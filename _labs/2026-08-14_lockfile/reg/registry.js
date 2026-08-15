// 最小の npm レジストリ。packument と tarball だけを返す。
// 使い方: PORT=8871 LOG=a.log node registry.js
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = Number(process.env.PORT || 8871);
const LOG = process.env.LOG || 'reg.log';
const TGZ = path.join(__dirname, 'tgz');
const STATE = path.join(__dirname, process.env.STATE || 'state.json');
const TAMPER = process.env.TAMPER === '1'; // tarball を1バイト書き換える
const HOST = `http://127.0.0.1:${PORT}`;

function visible() {
  return JSON.parse(fs.readFileSync(STATE, 'utf8'));
}
function log(line) {
  fs.appendFileSync(path.join(__dirname, LOG), line + '\n');
}
function tgzPath(name, ver) {
  return path.join(TGZ, `${name}-${ver}.tgz`);
}
function body(name, ver) {
  const buf = fs.readFileSync(tgzPath(name, ver));
  if (!TAMPER) return buf;
  const b = Buffer.from(buf);
  b[b.length - 1] = b[b.length - 1] ^ 0xff;
  return b;
}
function packument(name) {
  const vers = visible()[name] || [];
  const versions = {};
  for (const v of vers) {
    const buf = body(name, v);
    const integrity =
      'sha512-' + crypto.createHash('sha512').update(buf).digest('base64');
    const pj = JSON.parse(
      fs.readFileSync(path.join(__dirname, 'src', `${name}-${v}`, 'package.json'), 'utf8')
    );
    versions[v] = Object.assign({}, pj, {
      _id: `${name}@${v}`,
      dist: {
        tarball: `${HOST}/${name}/-/${name}-${v}.tgz`,
        integrity,
        shasum: crypto.createHash('sha1').update(buf).digest('hex'),
      },
    });
  }
  const latest = vers[vers.length - 1];
  return {
    _id: name,
    name,
    'dist-tags': { latest },
    versions,
    time: {},
  };
}

http
  .createServer((req, res) => {
    log(`${new Date().toISOString()} ${req.method} ${req.url}`);
    const m = req.url.match(/^\/([^/]+)\/-\/([^/]+)-(\d+\.\d+\.\d+)\.tgz$/);
    res.setHeader('Cache-Control', 'no-store');
    if (m) {
      const [, name, , ver] = m;
      if (!fs.existsSync(tgzPath(name, ver))) {
        res.writeHead(404).end('not found');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'application/octet-stream' });
      res.end(body(name, ver));
      return;
    }
    const name = decodeURIComponent(req.url.replace(/^\//, '').split('?')[0]);
    const vis = visible();
    if (!vis[name]) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end('{"error":"Not found"}');
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(packument(name)));
  })
  .listen(PORT, '127.0.0.1', () => log(`listen ${PORT} tamper=${TAMPER}`));
