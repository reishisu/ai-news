#!/usr/bin/env python3
"""記事を幅380pxと900pxで開いて、CLAUDE.md 第7節の項目を実測する。

使い方: python3 layout_check.py <記事ディレクトリ名>
"""
import sys, pathlib, json
from playwright.sync_api import sync_playwright

art = sys.argv[1] if len(sys.argv) > 1 else "2026-08-27_001"
root = pathlib.Path(__file__).resolve().parents[2]
url = (root / "contents" / art / "index.html").as_uri()

# この環境の Chromium は /opt/pw-browsers に置いてあり、pip で入る playwright の
# 期待するビルド番号と食い違う。playwright install はしない決まりなので直接指す。
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

ng = 0
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    for width in (380, 900):
        errors = []
        blocked = []
        page = browser.new_page(viewport={"width": width, "height": 700})
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        # 外部リソース(解析・コメント欄・favicon)は、このコンテナから
        # ネットワークが塞がれているため file:// で開くと必ず落ちる。
        # 記事のJSの問題ではないので、数えるが別枠にする。
        page.on("requestfailed",
                lambda r: blocked.append(r.url.split('/')[2]
                                         if '//' in r.url else r.url))
        page.on("console", lambda m: errors.append(f"console: {m.text}")
                if m.type == "error"
                and "Failed to load resource" not in m.text else None)
        page.goto(url, wait_until="networkidle")

        over = page.evaluate(
            "document.documentElement.scrollWidth - window.innerWidth")
        spill = page.evaluate("""(w) => {
            const bad = [];
            for (const el of document.querySelectorAll('.code, .table, figure, pre, img')) {
                const r = el.getBoundingClientRect();
                if (r.right > w + 1 || r.left < -1)
                    bad.push(el.className + ' right=' + Math.round(r.right));
            }
            return bad;
        }""", width)
        bg = page.evaluate("""() => {
            const el = document.querySelector('.code pre');
            if (!el) return 'no .code pre';
            return getComputedStyle(el).backgroundColor;
        }""")
        transparent = bg in ("rgba(0, 0, 0, 0)", "transparent")

        print(f"--- 幅 {width}px ---")
        print(f"  横スクロール量        : {over}   {'OK' if over == 0 else 'NG'}")
        print(f"  はみ出し要素          : {len(spill)}   {'OK' if not spill else 'NG'}")
        for s in spill[:6]:
            print(f"      {s}")
        print(f"  .code pre の背景色    : {bg}   {'NG(透明)' if transparent else 'OK'}")
        print(f"  JSエラー              : {len(errors)}   {'OK' if not errors else 'NG'}")
        for e in errors[:5]:
            print(f"      {e}")
        print(f"  (参考)外部で落ちた先  : {sorted(set(blocked))}")
        if over or spill or errors or transparent:
            ng += 1
        page.close()

    # 仕掛け(details)の開閉が効くか
    page = browser.new_page(viewport={"width": 380, "height": 700})
    page.goto(url, wait_until="networkidle")
    d = page.query_selector("details.note-d")
    if d:
        before = d.get_attribute("open")
        page.evaluate("(el) => el.open = true", d)
        after = d.get_attribute("open")
        print(f"--- details の開閉: {before} -> {after}   "
              f"{'OK' if after is not None else 'NG'}")
    browser.close()

print("\n結果:", "全項目パス" if ng == 0 else f"{ng} 幅で問題あり")
sys.exit(1 if ng else 0)
