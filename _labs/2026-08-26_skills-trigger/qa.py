import sys, pathlib, json
from playwright.sync_api import sync_playwright

art = pathlib.Path("contents/2026-08-26_skills-trigger/index.html").resolve()
url = art.as_uri()
fails = []

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    for w in (380, 900):
        errs = []
        pg = b.new_page(viewport={"width": w, "height": 700})
        pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
        pg.on("console", lambda m: errs.append(f"console.{m.type}: {m.text}") if (m.type == "error" and "Failed to load resource" not in m.text) else None)
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(1200)

        r = pg.evaluate("""(w) => {
          const out = {};
          out.overflow = document.documentElement.scrollWidth - window.innerWidth;
          const over = [];
          for (const sel of ['.code', '.table', 'figure', 'pre', 'table']) {
            document.querySelectorAll(sel).forEach((el, i) => {
              const r = el.getBoundingClientRect();
              if (r.right > w + 1 || r.left < -1) over.push(`${sel}[${i}] left=${Math.round(r.left)} right=${Math.round(r.right)}`);
            });
          }
          out.overflowing = over;
          const pre = document.querySelector('.code pre');
          out.preBg = pre ? getComputedStyle(pre).backgroundColor : 'NO PRE';
          out.counts = {
            code: document.querySelectorAll('.code').length,
            table: document.querySelectorAll('.table').length,
            fig: document.querySelectorAll('figure').length,
            checklist: document.querySelectorAll('.checklist').length,
            details: document.querySelectorAll('details').length,
            mark: document.querySelectorAll('mark').length,
          };
          out.docHeight = document.documentElement.scrollHeight;
          return out;
        }""", w)

        # checklist interaction
        cl = pg.query_selector_all('.checklist li')
        before = pg.eval_on_selector('.cl-count', 'e => e.textContent') if pg.query_selector('.cl-count') else None
        if cl:
            cl[0].query_selector('input').check()
            pg.wait_for_timeout(300)
        after = pg.eval_on_selector('.cl-count', 'e => e.textContent') if pg.query_selector('.cl-count') else None

        print(f"=== width {w} ===")
        print(f"  scrollWidth-innerWidth : {r['overflow']}")
        print(f"  はみ出し要素           : {r['overflowing'] or 'なし'}")
        print(f"  .code pre 背景色       : {r['preBg']}")
        print(f"  要素数                 : {r['counts']}")
        print(f"  JSエラー               : {errs or 'なし'}")
        print(f"  チェックリスト         : {before} -> {after}")
        print(f"  文書高                 : {r['docHeight']}px ({round(r['docHeight']/700,1)} 画面)")

        if r['overflow'] != 0: fails.append(f"w={w} 横スクロール {r['overflow']}")
        if r['overflowing']: fails.append(f"w={w} はみ出し {r['overflowing']}")
        if 'rgba(0, 0, 0, 0)' in r['preBg']: fails.append(f"w={w} pre背景なし")
        if errs: fails.append(f"w={w} JSエラー {errs}")
        if cl and before == after: fails.append(f"w={w} チェックリストが反応しない")
        pg.close()
    b.close()

print("\n" + ("NG: " + "; ".join(fails) if fails else "OK: すべてパス"))
sys.exit(1 if fails else 0)
