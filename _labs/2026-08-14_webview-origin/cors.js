// 同じHTMLを file:// と http:// から開き、APIの CORS 設定3通りに対して結果を比べる。
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const API = 'http://127.0.0.1:8803';
const PAGE = path.resolve('page.html');
const HTML = '<!doctype html><html lang="ja"><head><meta charset="utf-8"></head><body><h1>probe</h1></body></html>\n';

const MODES = [
  ['none', 'CORSヘッダーなし'],
  ['star', 'Allow-Origin: *'],
  ['allowlist', 'Allow-Origin: https://app.example.com'],
  ['echo', 'Originをそのまま返す + Credentials'],
];

async function run(p, label, url) {
  await p.goto(url);
  const rows = await p.evaluate(async ({ api, modes }) => {
    const out = [];
    for (const [mode, desc] of modes) {
      let plain, cred;
      try { const r = await fetch(api + '/' + mode); plain = 'OK ' + r.status; }
      catch (e) { plain = 'ブロック'; }
      try { const r = await fetch(api + '/' + mode, { credentials: 'include' }); cred = 'OK ' + r.status; }
      catch (e) { cred = 'ブロック'; }
      out.push([mode, desc, plain, cred]);
    }
    return { origin: String(location.origin), out };
  }, { api: API, modes: MODES });

  console.log(`■ ${label}   location.origin = ${rows.origin}`);
  console.log('  ' + 'APIのCORS設定'.padEnd(38) + 'ふつうのfetch   Cookie付きfetch');
  for (const [, desc, plain, cred] of rows.out) {
    console.log('  ' + desc.padEnd(40) + plain.padEnd(16) + cred);
  }
  console.log('');
}

(async () => {
  fs.writeFileSync(PAGE, HTML);
  fs.writeFileSync('../cache-demo/pub/page.html', HTML);

  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const p = await b.newPage();

  await run(p, 'file:// で開いた場合（WebViewでローカルHTMLを読み込んだ状態）', 'file://' + PAGE);
  await run(p, 'http:// で開いた場合（サーバーから配信した普通のページ）', 'http://127.0.0.1:8802/page.html');

  await b.close();
})();
