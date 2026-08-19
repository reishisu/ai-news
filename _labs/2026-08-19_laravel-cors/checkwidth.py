#!/usr/bin/env python3
"""表示幅が40桁を超える行を報告する（全角は2桁として数える）。

    python3 checkwidth.py output.txt
"""
import sys
import unicodedata


def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


over = 0
for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.rstrip("\n")
            w = width(line)
            if w > 40:
                over += 1
                print(f"{path}:{i}: {w}桁: {line}")
print(f"-- 40桁超え: {over}行")
