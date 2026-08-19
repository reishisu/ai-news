// 同じサーバー・同じ設定に対して、curl は通り、ブラウザは止まることを見る。
//
//   node browser_check.js <ページのURL> <APIのURL>
//
// 出力は幅40桁に折り返す(記事に貼るため。文言は変えない)。
// この環境には playwright-core 単体が無く、フル版の playwright だけが
// グローバルに入っている(/opt/node22/lib/node_modules/playwright)。
// どちらでも動くように両方試す。
let chromium;
try { ({ chromium } = require('playwright-core')); }
catch { ({ chromium } = require('playwright')); }

const W = 40;
function wrap(s) {
  const out = [];
  for (const line of String(s).split('\n')) {
    if (line.length <= W) { out.push(line); continue; }
    let cur = '';
    for (const word of line.split(' ')) {
      const head = cur === '' ? '' : cur + ' ';
      if ((head + word).length > W && cur !== '') { out.push(cur); cur = '  ' + word; }
      else { cur = head + word; }
    }
    if (cur) out.push(cur);
  }
  return out.join('\n');
}
const say = (s) => console.log(wrap(s));

(async () => {
  const [pageUrl, apiUrl] = process.argv.slice(2);
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    args: ['--no-sandbox'],
  });
  const page = await browser.newPage();

  const errs = [];
  page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));

  await page.goto(pageUrl + '?api=' + encodeURIComponent(apiUrl),
                  { waitUntil: 'networkidle' });
  const r = await page.evaluate(() => window.__result);

  say('ページのオリジン: ' + new URL(pageUrl).origin);
  say('API: ' + apiUrl);
  if (r.ok) {
    say('fetch: 成功 status=' + r.status);
    say('本文: ' + r.body);
  } else {
    say('fetch: 失敗');
    say(r.error);
  }
  say('-- ブラウザのコンソール');
  if (errs.length === 0) say('(エラーなし)');
  for (const e of errs) say(e);

  await browser.close();
})();
