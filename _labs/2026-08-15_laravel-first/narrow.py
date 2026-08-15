#!/usr/bin/env python3
"""Strip ANSI, rstrip, and hard-wrap stdin to a display width (default 40).

Wrapping is done on display columns (East Asian Wide = 2) so multibyte
characters are never split mid-sequence. Nothing else is altered.
"""
import sys, re, unicodedata

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 40
ANSI = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')


def cw(ch):
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1


def wrap(s, limit):
    """Wrap at the last space before the limit; hard-wrap if there is none."""
    out = []
    while True:
        cur, n, brk = '', 0, -1
        for i, ch in enumerate(s):
            c = cw(ch)
            if n + c > limit:
                break
            if ch == ' ' and i > 0:
                brk = i
            cur += ch
            n += c
        if len(cur) == len(s):
            out.append(cur)
            return out
        if brk > 0:
            out.append(s[:brk])
            s = s[brk + 1:]
        else:
            out.append(cur)
            s = s[len(cur):]
        if not s:
            return out


data = sys.stdin.buffer.read().decode('utf-8', errors='replace')
for line in data.split('\n'):
    line = ANSI.sub('', line).rstrip()
    for piece in wrap(line, LIMIT):
        print(piece)
