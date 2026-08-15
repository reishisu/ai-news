// レイアウト崩れの再現。HTMLだけ新しくなり、CSSが古いまま残ると何が起きるか。
const { chromium } = require('playwright-core');
const fs = require('fs');
const crypto = require('crypto');
const { pad } = require('./pad');

const URL = 'http://127.0.0.1:8802/';
const put = (name, body) => fs.writeFileSync('pub/' + name, body);
const hash = name =>
  crypto.createHash('sha256').update(fs.readFileSync('pub/' + name)).digest('hex').slice(0, 8);

// v1: 見出しのクラスは title
const HTML_V1 = '<!doctype html><html lang="ja"><head><meta charset="utf-8">\n<link rel="stylesheet" href="style.css">\n</head><body><h1 class="title">見出し</h1></body></html>\n';
const CSS_V1 = '.title { color: rgb(220, 40, 40); }\n';

// v2: クラス名を headline に変更し、CSSも合わせて変更した
const HTML_V2 = '<!doctype html><html lang="ja"><head><meta charset="utf-8">\n<link rel="stylesheet" href="style.css">\n</head><body><h1 class="headline">見出し</h1></body></html>\n';
const CSS_V2 = '.headline { color: rgb(30, 160, 90); }\n';

const look = p => p.evaluate(() => {
  const h = document.querySelector('h1');
  return { cls: h.className, color: getComputedStyle(h).color };
});

const show = (label, r, note) => {
  console.log(label);
  console.log(` class=${pad(r.cls, 8)}  ${pad(r.color, 17)}${note}`);
};

(async () => {
  put('index.html', HTML_V1);
  put('style.css', CSS_V1);

  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const p = await b.newPage();

  await p.goto(URL);
  show('1. 読者が初回訪問', await look(p), '');

  await p.waitForTimeout(1200);          // 更新日時が確実に変わるように1秒待つ
  put('index.html', HTML_V2);
  put('style.css', CSS_V2);
  console.log('2. HTMLもCSSも新しくして公開');

  await p.goto(URL);
  show('3. 読者が再訪問', await look(p), '← 崩れた');

  await p.waitForTimeout(1200);
  const v = hash('style.css');
  put('index.html', HTML_V2.replace('style.css', 'style.css?v=' + v));
  console.log(`4. href に ?v=${v} を付けた`);

  await p.goto(URL);
  show('5. 読者が再訪問', await look(p), '← 直った');

  await b.close();
})();
