#!/usr/bin/env python3
"""output.txt の数字を記事HTMLの @@…@@ に流し込む。
数字を手で写さないためのもの。"""
import re, sys

out, html = sys.argv[1], sys.argv[2]
rows = []           # [(marks, "10/10"), ...] 実験1のA,B → 実験2のA,B → …
for line in open(out, encoding="utf-8"):
    m = re.match(r"--> \S+ \S+ ([o.]+) (\d+/\d+)", line)
    if m:
        rows.append((m.group(1), m.group(2)))

assert len(rows) == 6, "集計行が6本ないと埋められない: %d" % len(rows)

s = open(html, encoding="utf-8").read()
for i, key in enumerate(["1A", "1B", "2A", "2B", "3A", "3B"]):
    marks, ratio = rows[i]
    s = s.replace("@@M%s@@" % key, marks).replace("@@%s@@" % key[::-1], ratio)
open(html, "w", encoding="utf-8").write(s)

left = re.findall(r"@@\w+@@", s)
print("埋めた:", " ".join("%s=%s" % (k, r[1]) for k, r in
                          zip(["1A", "1B", "2A", "2B", "3A", "3B"], rows)))
print("残った差し込み:", left or "なし")
