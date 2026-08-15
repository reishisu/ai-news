// 実験1: プロファイル(データ置き場)が別か同じかで
// ログイン状態が引き継がれるかを測る
const { chromium } = require('playwright-core');
const URL = 'http://127.0.0.1:8863/';
const EXE = '/opt/pw-browsers/chromium';

async function open(label, dir, doLogin) {
  const ctx = await chromium.launchPersistentContext(dir, {
    executablePath: EXE, args: ['--no-sandbox'],
  });
  const page = await ctx.newPage();
  await page.goto(URL);
  if (doLogin) {
    await page.fill('#u', 'alice');
    await page.fill('#p', 'hunter2');
    await Promise.all([page.waitForNavigation(), page.click('#go')]);
  }
  const status = await page.textContent('#status');
  const cookies = await ctx.cookies(URL);
  const sid = cookies.find(c => c.name === 'sid');
  const ls = await page.evaluate(() => localStorage.getItem('tag'));
  console.log(label);
  console.log('  status: ' + status);
  console.log('  sid   : ' + (sid ? sid.value : '(なし)'));
  console.log('  ls.tag: ' + (ls || '(なし)'));
  await ctx.close();
}

(async () => {
  const P = process.argv[2]; // プロファイル置き場
  await open('1 本体ブラウザ(ログイン実行)', P + '/browser', true);
  await open('2 アプリAのWebView(別領域)', P + '/appA', false);
  await open('3 アプリBのWebView(別領域)', P + '/appB', false);
  await open('4 アプリ内タブ(本体と同領域)', P + '/browser', false);
})();
