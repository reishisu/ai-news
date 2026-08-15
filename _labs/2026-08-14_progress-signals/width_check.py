#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""標準入力の各行が半角40字以内か調べる(全角=2)。"""
import sys
import unicodedata


def w(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WFA" else 1 for c in s)


mx, over = 0, 0
for line in sys.stdin.read().splitlines():
    n = w(line)
    mx = max(mx, n)
    if n > 40:
        over += 1
        print("OVER %d: %s" % (n, line))
print("max=%d  over40=%d" % (mx, over))
