#!/usr/bin/env python3
"""8ケースの結果を1枚の表にする。全角=2桁で数えて40桁以内に収める。"""
import json, os, unicodedata

B = os.path.dirname(os.path.abspath(__file__))
ROWS = [
    ("00-none", "設定なし(対照)"),
    ("01-allow", "allow のみ"),
    ("02-deny", "allow + deny"),
    ("03-claudemd", "CLAUDE.md承認 + deny"),
    ("04-hook-exit2", "hook exit 2"),
    ("05-hook-exit1", "hook exit 1"),
    ("06-badpath", "hook パス誤記"),
    ("07-hook-allow", "hook allow + deny"),
    ("08-timeout", "hook timeout 1s"),
]


def w(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WFA" else 1 for c in s)


def pad(s, n):
    return s + " " * (n - w(s))


LABEL = max(w(x[1]) for x in ROWS)
out = [pad("設定", LABEL) + "  push", "-" * LABEL + "  ----"]
for case, label in ROWS:
    b, a = open(f"{B}/out/{case}.truth").read().split()[2:4]
    out.append(pad(label, LABEL) + "  " + ("通る" if b != a else "止まる"))

for line in out:
    assert w(line) <= 40, f"幅超過 {w(line)}: {line}"
    print(line)
