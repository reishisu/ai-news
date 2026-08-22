#!/usr/bin/env python3
"""標準入力を表示幅37桁に折り返す。文字は一字も変えない。
空白で切れるところは空白で切り、続きは2桁下げる。"""
import re
import sys
import unicodedata

W = 37
IND = "  "


def dw(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def wrap(line):
    if dw(line) <= W:
        return [line]
    toks = re.findall(r"\s+|\S+", line)
    out, cur = [], ""
    for t in toks:
        if cur and dw(cur) + dw(t) > W:
            out.append(cur.rstrip())
            cur = IND
            if t.isspace():
                continue
        while dw(cur) + dw(t) > W:          # 1語で幅を超えるとき
            n = 0
            while n < len(t) and dw(cur + t[: n + 1]) <= W:
                n += 1
            out.append(cur + t[:n])
            cur, t = IND, t[n:]
        cur += t
    if cur.strip():
        out.append(cur.rstrip())
    return out


for line in sys.stdin:
    for part in wrap(line.rstrip("\n")):
        print(part)
