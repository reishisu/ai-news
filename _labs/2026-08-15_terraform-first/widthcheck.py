#!/usr/bin/env python3
"""出力ファイルの各行の「表示幅」を測る。

全角(East Asian Wide/Fullwidth)は2桁、それ以外は1桁として数える。
記事は幅380pxで読まれるため、40桁を超える行があると横スクロールになる。

  python3 widthcheck.py <ディレクトリ...>
"""
import os
import sys
import unicodedata


def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def main():
    for d in sys.argv[1:]:
        names = sorted(n for n in os.listdir(d) if n.endswith(".txt"))
        if not names:
            continue
        print("[%s]" % os.path.basename(d.rstrip("/")))
        for n in names:
            with open(os.path.join(d, n)) as fh:
                over = [ln for ln in fh.read().splitlines() if width(ln) > 40]
            mark = "ok " if not over else "NG "
            print("%s%-24s %d" % (mark, n[:-4], len(over)))


if __name__ == "__main__":
    main()
