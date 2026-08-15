// 配信側のヘッダーだけを変えて、Unity Web のビルドが
// 読み込めるかどうかを実測する。
// 実行:
// NODE_PATH=/opt/node22/lib/node_modules/playwright/node_modules node probe.js
const { chromium } = require('playwright-core');

const W = 40;          // 1行の上限(半角換算)
const IND = '     ';   // 折り返し時の字下げ

const width = s =>
  [...s].reduce((n, c) => n + (/[^\x00-\x7f]/.test(c) ? 2 : 1), 0);

function wrap(text, indent) {
  const lim = W - width(indent);
  const out = [];
  let line = '';
  for (const ch of text) {
    if (width(line) + width(ch) > lim) { out.push(indent + line); line = ''; }
    line += ch;
  }
  if (line) out.push(indent + line);
  return out.join('\n');
}

function row(label, value) {
  const pad = ' '.repeat(Math.max(1, 22 - width(label)));
  // 1行に収まらないときは値を次の行に落とす(幅40の画面で読むため)
  if (width('  ' + label + pad + value) <= W) {
    console.log('  ' + label + pad + value);
  } else {
    console.log('  ' + label);
    console.log(wrap(value, '      '));
  }
}

// ページ側(ブラウザが与える条件)を測る
async function page(p, label, url) {
  await p.goto(url);
  const r = await p.evaluate(async () => {
    const o = {};
    o.sec = String(self.isSecureContext);
    o.iso = String(self.crossOriginIsolated);
    o.sab = typeof SharedArrayBuffer !== 'undefined' ? 'あり' : 'なし';
    let mem = null;
    try {
      mem = new WebAssembly.Memory({ initial: 1, maximum: 1, shared: true });
      o.mem = '作れる (' + mem.buffer.constructor.name + ')';
    } catch (e) { o.mem = '作れない (' + e.name + ')'; }
    // Unity のスレッドは、この共有メモリを Worker に渡して動く
    const w = new Worker(URL.createObjectURL(
      new Blob(['self.onmessage=()=>{}'], { type: 'text/javascript' })));
    try { w.postMessage(mem); o.post = '渡せる'; }
    catch (e) { o.post = '渡せない (' + e.name + ')'; }
    w.terminate();
    return o;
  });
  console.log('■ ' + label);
  row('isSecureContext', r.sec);
  row('crossOriginIsolated', r.iso);
  row('SharedArrayBuffer', r.sab);
  row('共有メモリ', r.mem);
  row('Workerへ渡す', r.post);
  console.log('');
}

// 配信ヘッダーを変えた .wasm を fetch して読む
async function loadWasm(p, url) {
  return p.evaluate(async u => {
    const res = await fetch(u).catch(e => ({ err: e.name + ': ' + e.message }));
    if (res.err) return { ok: false, msg: res.err };
    try {
      const m = await WebAssembly.instantiateStreaming(res);
      return { ok: true, msg: 'add(2,3) = ' + m.instance.exports.add(2, 3) };
    } catch (e) {
      return { ok: false, msg: e.name + ': ' + e.message };
    }
  }, url);
}

// <script src> で別オリジンの loader を読む(CORSなしの読み込み)
async function loadScript(p, url) {
  return p.evaluate(u => new Promise(done => {
    const s = document.createElement('script');
    s.src = u;
    s.onload = () => done({ ok: true, msg: '読み込めた' });
    s.onerror = () => done({ ok: false, msg: 'onerror (詳細は下の行)' });
    document.head.appendChild(s);
  }), url);
}

async function cases(p, title, list, fn) {
  console.log('■ ' + title);
  for (const [name, url, note] of list) {
    const logs = [];
    const onErr = m => { if (m.type() === 'error') logs.push(m.text()); };
    p.on('console', onErr);
    const r = await fn(p, url);
    p.off('console', onErr);
    console.log('  ' + (r.ok ? 'OK ' : 'NG ') + name);
    console.log(wrap(note, IND));
    console.log(wrap(r.msg, IND));
    for (const l of logs) console.log(wrap(l, IND));
  }
  console.log('');
}

(async () => {
  const b = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'],
  });
  const p = await b.newPage();
  console.log('ブラウザ: ' + b.version() + '\n');

  const A = 'http://127.0.0.1:8821';
  const C = 'http://127.0.0.1:8822';
  // ループバックでないIP。localhost と違い「安全な文脈」ではない。
  const IP = 'http://' + (process.env.LAN_IP || '192.0.2.2') + ':8821';

  await page(p, 'ヘッダーなしのページ', A + '/plain/');
  await page(p, 'COOP+COEP 付きのページ', A + '/coi/');
  await page(p, 'COOP+COEP 付き / IP直打ちの http', IP + '/coi/');

  await p.goto(A + '/plain/');
  // Unity の資料は「brotli は HTTPS のみ」と書いている。
  // 平文HTTPで実際に何を要求しているかを見る。
  const ae = await p.evaluate(() => fetch('/ae').then(r => r.text()));
  console.log('■ Accept-Encoding (localhost, http)');
  console.log(wrap(ae, '  '));
  await p.goto(IP + '/plain/');
  const ae2 = await p.evaluate(() => fetch('/ae').then(r => r.text()));
  console.log('■ Accept-Encoding (IP直打ち, http)');
  console.log(wrap(ae2, '  '));
  console.log('');

  await cases(p, 'IP直打ちで br を配ると', [
    ['br 申告あり', IP + '/w/br', 'Content-Encoding: br'],
    ['無圧縮', IP + '/w/ok', 'Content-Encoding なし'],
  ], loadWasm);

  await p.goto(A + '/plain/');
  await cases(p, '.wasm の配信ヘッダー', [
    ['無圧縮', A + '/w/ok', 'Content-Type: application/wasm'],
    ['型が違う', A + '/w/octet', 'Content-Type: application/octet-stream'],
    ['br 素のまま', A + '/w/br-bare', 'Content-Encoding なし'],
    ['br 申告あり', A + '/w/br', 'Content-Encoding: br'],
    ['br 申告だけ', A + '/w/br-lie', '中身は無圧縮なのに br と申告'],
    ['gz 素のまま', A + '/w/gz-bare', 'Content-Encoding なし'],
    ['gz 申告あり', A + '/w/gz', 'Content-Encoding: gzip'],
  ], loadWasm);

  await p.goto(A + '/coi/');
  await cases(p, 'COEPページ→別オリジンをfetch', [
    ['ヘッダーなし', C + '/bare/app.wasm', '配信元が何も付けていない'],
    ['CORPのみ', C + '/corp/app.wasm', 'CORP: cross-origin'],
    ['CORSあり', C + '/cors/app.wasm', 'ACAO: *'],
  ], loadWasm);

  await p.goto(A + '/coi/');
  await cases(p, 'COEPページ→別オリジンのscript', [
    ['ヘッダーなし', C + '/bare/loader.js', '配信元が何も付けていない'],
    ['CORPのみ', C + '/corp/loader.js', 'CORP: cross-origin'],
  ], loadScript);

  await b.close();
})();
