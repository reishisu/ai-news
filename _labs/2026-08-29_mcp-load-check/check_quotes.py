#!/usr/bin/env python3
"""記事に貼った英語の原文が、公式ドキュメントと一字一句合っているかを確かめる。

  curl -sSL https://code.claude.com/docs/en/mcp.md -o mcp.md
  python3 check_quotes.py mcp.md

markdown 側の装飾(`code` / [text](url) / **bold**)だけ落として比較する。
語順・語の脱落・句読点の追加はここで落ちる。
"""
import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ART = HERE.parents[1] / "contents" / "2026-08-29_mcp-load-check" / "index.html"
doc_path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "mcp.md")

art = ART.read_text(encoding="utf-8")
doc = doc_path.read_text(encoding="utf-8")

doc = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", doc).replace("`", "").replace("*", "")
norm = lambda t: re.sub(r"\s+", " ", t).strip()
dn = norm(doc)

blocks = re.findall(
    r'<div class="code wrap"><div class="code-head">(.*?)</div><pre>(.*?)</pre>', art, re.S)
print(f"原文ブロック: {len(blocks)}")

ok = True
for head, body in blocks:
    q = norm(html.unescape(re.sub(r"<[^>]+>", "", body)))
    hit = q in dn
    print(("  一致  " if hit else "  不一致") + f" | {head}")
    if not hit:
        ok = False
        print("     貼った側:", q[:200])

print("\n" + ("すべての引用が原文と一致しました。" if ok else "★ 不一致があります。"))
sys.exit(0 if ok else 1)
