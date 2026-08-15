// WebView でよく踏む「オリジンが null になる」問題を実測する。
// 同じHTMLを file:// と http:// の両方で開き、何ができて何ができないかを比べる。
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const PAGE = path.resolve('page.html');

const HTML = `<!doctype html><html lang="ja"><head><meta charset="utf-8"></head>
<body><h1>probe</h1></body></html>
`;

async function probe(p, label, url) {
  await p.goto(url);
  const r = await p.evaluate(async () => {
    const out = {};
    out.origin = String(location.origin);

    try {
      localStorage.setItem('k', '1');
      out.localStorage = 'OK (' + localStorage.getItem('k') + ')';
    } catch (e) {
      out.localStorage = 'NG ' + e.name + ': ' + e.message.slice(0, 60);
    }

    try {
      const res = await fetch('http://127.0.0.1:8802/style.css');
      out.fetch = 'OK ' + res.status;
    } catch (e) {
      out.fetch = 'NG ' + e.name + ': ' + e.message.slice(0, 60);
    }

    try {
      out.crypto = typeof crypto.subtle === 'object' ? 'OK 使える' : 'NG undefined';
    } catch (e) {
      out.crypto = 'NG ' + e.name;
    }

    return out;
  });

  console.log(`--- ${label} ---`);
  console.log('  location.origin : ' + r.origin);
  console.log('  localStorage    : ' + r.localStorage);
  console.log('  fetch (別オリジン): ' + r.fetch);
  console.log('  crypto.subtle   : ' + r.crypto);
  console.log('');
}

(async () => {
  fs.writeFileSync(PAGE, HTML);
  fs.copyFileSync(PAGE, '../cache-demo/pub/page.html');

  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const p = await b.newPage();
  p.on('console', m => { if (m.type() === 'error') console.log('  [ブラウザのエラー] ' + m.text().slice(0, 110)); });

  await probe(p, 'file:// で開いた場合 (WebView の loadData / ローカルHTML相当)', 'file://' + PAGE);
  await probe(p, 'http:// で開いた場合 (普通のWebページ)', 'http://127.0.0.1:8802/page.html');

  await b.close();
})();
