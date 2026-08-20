#!/usr/bin/env python3
"""公開前の表示検証(CLAUDE.md 第7節)。幅380pxと900pxで実測する。

使い方: python3 _labs/2026-08-20_001/layout_qa.py contents/2026-08-20_001/index.html
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

target = Path(sys.argv[1]).resolve()
errors = []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    for width in (380, 900):
        page = browser.new_page(viewport={"width": width, "height": 800})
        js_errors = []
        page.on("pageerror", lambda e: js_errors.append(str(e)))
        page.on("console", lambda m: js_errors.append(m.text) if m.type == "error" else None)
        page.goto(f"file://{target}")
        page.wait_for_timeout(1200)

        overflow = page.evaluate(
            "document.documentElement.scrollWidth - window.innerWidth")
        print(f"[{width}px] scrollWidth - innerWidth = {overflow}")
        if overflow > 0:
            errors.append(f"{width}px: 横スクロール {overflow}px")
            culprits = page.evaluate("""
              [...document.querySelectorAll('*')]
                .filter(e => e.getBoundingClientRect().right > window.innerWidth + 1)
                .slice(0, 8)
                .map(e => e.tagName + '.' + (e.className||'').toString().slice(0,40))
            """)
            print("  はみ出し候補:", culprits)

        out = page.evaluate("""
          [...document.querySelectorAll('.code,.table')]
            .filter(e => e.getBoundingClientRect().right > window.innerWidth + 1)
            .length
        """)
        print(f"[{width}px] はみ出す .code/.table = {out}")
        if out:
            errors.append(f"{width}px: .code/.table はみ出し {out}件")

        bg = page.evaluate("""
          (() => { const el = document.querySelector('.code pre');
            if (!el) return 'no-code';
            const b = getComputedStyle(el.parentElement).backgroundColor;
            return b; })()
        """)
        print(f"[{width}px] .code の背景 = {bg}")
        if bg in ("rgba(0, 0, 0, 0)", "transparent"):
            errors.append(f"{width}px: .code に背景色なし(CSS未適用)")

        # クイズ・チェックリストの動作
        if page.locator(".quiz .opt").count():
            page.locator(".quiz .opt").first.click()
            vis = page.locator(".quiz .ans").first.is_visible()
            print(f"[{width}px] クイズ動作(解説表示) = {vis}")
            if not vis:
                errors.append(f"{width}px: クイズの解説が出ない")
        if page.locator(".checklist input").count():
            before = page.locator(".cl-count").first.inner_text()
            page.locator(".checklist input").first.check()
            after = page.locator(".cl-count").first.inner_text()
            print(f"[{width}px] チェックリスト {before} -> {after}")
            if before == after:
                errors.append(f"{width}px: チェックのカウントが動かない")

        if js_errors:
            errors.append(f"{width}px: JSエラー {js_errors[:3]}")
        print(f"[{width}px] JSエラー = {len(js_errors)}")
        page.close()
    browser.close()

print()
if errors:
    print("NG:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK: すべての検証を通過")
