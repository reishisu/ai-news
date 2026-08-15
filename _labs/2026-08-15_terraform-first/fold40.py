#!/usr/bin/env python3
"""表示幅40桁で折り返す。改行を足すだけで、文字は1つも変えない。

coreutils の fold はバイト数で数えるため、罫線などのマルチバイト文字を
途中で切ってしまう。ここでは表示幅(全角=2桁)で数える。

  python3 fold40.py < in.txt > out.txt
"""
import sys
import unicodedata

LIMIT = 40


def w(c):
    return 2 if unicodedata.east_asian_width(c) in "WF" else 1


def fold(line):
    if sum(w(c) for c in line) <= LIMIT:
        return [line]
    indent = len(line) - len(line.lstrip(" "))
    pad = " " * min(indent, 8)
    out, cur, cur_w, last_space = [], "", 0, -1
    for c in line:
        if cur_w + w(c) > LIMIT and cur:
            if last_space > 0:
                out.append(cur[:last_space])
                cur = pad + cur[last_space + 1:]
            else:
                out.append(cur)
                cur = pad
            cur_w = sum(w(x) for x in cur)
            last_space = -1
        if c == " " and cur.strip():
            last_space = len(cur)
        cur += c
        cur_w += w(c)
    if cur.strip():
        out.append(cur)
    return out


def main():
    for line in sys.stdin.read().splitlines():
        for piece in fold(line):
            print(piece.rstrip())


if __name__ == "__main__":
    main()
