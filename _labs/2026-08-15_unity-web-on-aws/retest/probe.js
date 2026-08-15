// Unity Web のビルド設定に効く、ブラウザ側の条件を実測する。
const { chromium } = require('playwright-core');

const width = s => [...s].reduce((n, c) => n + (/[⺀-꓏가-힣豈-﫿＀-｠]/.test(c) ? 2 : 1), 0);
const pad = (s, w) => s + ' '.repeat(Math.max(0, w - width(s)));

async function probe(p, label, url) {
  await p.goto(url);
  const r = await p.evaluate(() => {
    const out = {};
    out.isolated = String(self.crossOriginIsolated);
    out.sab = typeof SharedArrayBuffer !== 'undefined' ? 'あり' : 'なし';
    try { new SharedArrayBuffer(8); out.sabNew = '作れる'; }
    catch (e) { out.sabNew = '作れない (' + e.name + ')'; }
    out.wasm = typeof WebAssembly === 'object' ? 'あり' : 'なし';
    const c = document.createElement('canvas');
    out.webgl2 = c.getContext('webgl2') ? 'あり' : 'なし';
    out.webgpu = 'gpu' in navigator ? 'あり' : 'なし';
    out.mem = navigator.deviceMemory ? navigator.deviceMemory + 'GB' : '非公開';
    out.cores = String(navigator.hardwareConcurrency);
    return out;
  });
  console.log(`■ ${label}`);
  console.log('  ' + pad('crossOriginIsolated', 22) + r.isolated);
  console.log('  ' + pad('SharedArrayBuffer', 22) + r.sab + ' / ' + r.sabNew);
  console.log('  ' + pad('WebAssembly', 22) + r.wasm);
  console.log('  ' + pad('WebGL2', 22) + r.webgl2);
  console.log('  ' + pad('WebGPU', 22) + r.webgpu);
  console.log('  ' + pad('論理コア数', 22) + r.cores);
  console.log('');
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const p = await b.newPage();
  console.log('ブラウザ: ' + b.version() + '\n');
  await probe(p, 'ヘッダーなしで配信した場合', 'http://127.0.0.1:8811/plain/');
  await probe(p, 'COOP + COEP を付けて配信した場合', 'http://127.0.0.1:8811/coi/');
  await b.close();
})();
