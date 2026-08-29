#!/usr/bin/env python3
"""記事を幅380px/900pxで実際に開いて崩れを測る。

    python3 layout_qa.py ../../contents/2026-08-30_claude-automation/index.html

注意: Chromium を --window-size=380 で起動しても innerWidth は 500 に丸められる
(2026/8/30に実測)。380pxを本当に測るには Playwright で viewport を指定すること。
外部資源(giscus/goatcounter)の読み込み失敗は、この隔離環境の事情なので除外している。
"""
import sys, pathlib
from playwright.sync_api import sync_playwright
art = pathlib.Path(sys.argv[1]).resolve()
fail = 0
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                           args=["--no-sandbox"])
    for w in (380, 900):
        pg = b.new_page(viewport={"width": w, "height": 760})
        errs = []
        pg.on("pageerror", lambda e: errs.append("pageerror: %s" % e))
        pg.on("console", lambda m: errs.append("console: %s" % m.text) if m.type == "error" else None)
        pg.goto(art.as_uri()); pg.wait_for_timeout(1200)
        r = pg.evaluate("""() => {
          const iw = window.innerWidth, over = [];
          document.querySelectorAll('.code,.table,figure img,pre,table').forEach(el=>{
            const b = el.getBoundingClientRect();
            if (b.right > iw+1 || b.left < -1) over.push((el.className||el.tagName)+'@'+Math.round(b.right));
          });
          const p = document.querySelector('.code pre');
          return {iw, sx: document.documentElement.scrollWidth - iw, over: over.slice(0,8),
                  bg: p ? getComputedStyle(p).backgroundColor : 'none'};
        }""")
        # 外部資源(giscus/goatcounter)の読み込み失敗はこの隔離環境の事情。記事の欠陥ではない
        net = [e for e in errs if "Failed to load resource" in e]
        real = [e for e in errs if e not in net]
        ok = r["sx"] <= 0 and not r["over"] and not real and r["bg"] not in ("none","rgba(0, 0, 0, 0)")
        print(f"幅{r['iw']}px  横スクロール={r['sx']}  はみ出し={r['over'] or 'なし'}")
        print(f"          .code pre 背景={r['bg']}  JSエラー={real or 0}件 (外部資源の失敗 {len(net)}件は環境要因)  判定={'OK' if ok else '要修正'}")
        if not ok: fail = 1
        pg.screenshot(path=f"/tmp/art{w}.png", full_page=False)
        pg.close()
    b.close()
sys.exit(fail)
