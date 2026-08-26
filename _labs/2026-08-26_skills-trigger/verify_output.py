#!/usr/bin/env python3
"""記事に貼った実行結果の各行が、output.txt に実在するか照合する。

「見た目を整えるつもりで空白を1つ足す」だけで嘘になるので、機械で見る。
使い方: python3 verify_output.py <記事のindex.html> <output.txt>
"""
import html, re, sys

art, out = sys.argv[1], sys.argv[2]
real = open(out, encoding="utf-8").read().splitlines()
body = open(art, encoding="utf-8").read()

bad = 0
for m in re.finditer(r'<div class="code term">.*?<pre>(.*?)</pre>', body, re.S):
    text = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
    for line in text.split("\n"):
        if not line.strip() or line.startswith("$") or line == "(中略)":
            continue          # コマンド行と中略の印は実行結果ではない
        ok = line in real
        bad += not ok
        print(("一致  " if ok else "不一致") + " | " + repr(line))

print("\n不一致 %d件" % bad)
sys.exit(1 if bad else 0)
