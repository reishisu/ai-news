#!/usr/bin/env python3
"""記事に貼った実行結果が output.txt の中に実在するかを機械的に照合する。

手で書き換えていないことの証明。1行でも output.txt に無ければ FAIL。
使い方: python3 verify_pasted.py
"""
import html, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ART = HERE.parent.parent / "contents" / "2026-08-14_ai-basics" / "index.html"
OUT = (HERE / "output.txt").read_text(encoding="utf-8")

# 出力ではなく、こちらが打ったコマンド・注釈の行は照合対象から外す
SKIP = re.compile(r"^\s*(\$|#|↑|$)")

ok = ng = 0
for m in re.finditer(r'<div class="code term[^"]*">.*?<pre>(.*?)</pre>',
                     ART.read_text(encoding="utf-8"), re.S):
    for line in html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).split("\n"):
        if SKIP.match(line):
            continue
        if line in OUT:
            ok += 1
        else:
            ng += 1
            print("output.txt に無い行:", repr(line))

print(f"照合: 一致 {ok} 行 / 不一致 {ng} 行")
sys.exit(1 if ng else 0)
