#!/usr/bin/env python3
"""out/q*.truth から allow の置き場所の比較表を出す。全角=2桁で40桁以内。"""
import os, unicodedata

B = os.path.dirname(os.path.abspath(__file__))
ROWS = [
    ("q1-none", "どこにも書かない"),
    ("q2-project", ".claude/settings.json"),
    ("q3-flag", "--settings で渡す"),
    ("q4-flag-empty", "--settings で allow=[]"),
]


def w(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WFA" else 1 for c in s)


def pad(s, n):
    return s + " " * (n - w(s))


LABEL = max(w(x[1]) for x in ROWS)
out = [pad("allow の置き場所", LABEL) + "  marker", "-" * LABEL + "  ------"]
for case, label in ROWS:
    r = open(f"{B}/out/{case}.truth").read().split()[2]
    out.append(pad(label, LABEL) + "  " + ("作られた" if r == "CREATED" else "作られない"))

for line in out:
    assert w(line) <= 40, f"幅超過 {w(line)}: {line}"
    print(line)
