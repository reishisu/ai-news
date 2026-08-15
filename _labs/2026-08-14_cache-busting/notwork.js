// 「効きそうで効かない対処」を順に試す。CSSを緑に書き換えた後、色が変わるかを見る。
const { chromium } = require('playwright-core');
const fs = require('fs');
const { pad } = require('./pad');

const URL = 'http://127.0.0.1:8802/';
const color = p => p.evaluate(() => getComputedStyle(document.querySelector('h1')).color);
const say = async (p, label) => console.log(pad(label, 23) + await color(p));

(async () => {
  fs.writeFileSync('pub/index.html',
    '<!doctype html><html lang="ja"><head><meta charset="utf-8">\n<link rel="stylesheet" href="style.css">\n</head><body><h1 class="title">見出し</h1></body></html>\n');
  fs.writeFileSync('pub/style.css', '.title { color: rgb(220, 40, 40); }\n');

  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const ctx = await b.newContext();          // 読者のふだんのブラウザ
  const p = await ctx.newPage();

  await p.goto(URL);
  await say(p, '0. 初回アクセス');

  await p.waitForTimeout(1200);
  fs.writeFileSync('pub/style.css', '.title { color: rgb(30, 160, 90); }\n');
  console.log('   → style.css を緑に書き換えて公開した\n');

  await p.goto(URL);
  await say(p, '1. もう一度開く');

  await p.reload();
  await say(p, '2. リロード(F5)');

  fs.utimesSync('pub/style.css', new Date(), new Date());
  await p.goto(URL);
  await say(p, '3. 更新日時を新しく');

  const p2 = await ctx.newPage();            // 同じブラウザの別タブ
  await p2.goto(URL);
  await say(p2, '4. 別タブで開く');

  const p3 = await (await b.newContext()).newPage();   // シークレットウィンドウ相当
  await p3.goto(URL);
  await say(p3, '5. シークレットで開く');

  const cdp = await ctx.newCDPSession(p);              // Ctrl+Shift+R 相当
  await cdp.send('Page.reload', { ignoreCache: true });
  await p.waitForTimeout(1000);
  await say(p, '6. Ctrl+Shift+R');

  await b.close();
})();
