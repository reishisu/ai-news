#!/usr/bin/env python3
"""fold40.py が文字を足したり消したりしていないことを確かめる。

空白をすべて取り除いた文字列が、元と折り返し後で一致すれば
「改行と行頭の空白しか足していない」と言える。

  python3 verify_fold.py out out/fold40
"""
import os
import re
import sys


def strip_ws(s):
    return re.sub(r"\s+", "", s)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    ok = ng = 0
    for n in sorted(os.listdir(dst)):
        a = strip_ws(open(os.path.join(src, n)).read())
        b = strip_ws(open(os.path.join(dst, n)).read())
        if a == b:
            ok += 1
        else:
            ng += 1
            print("NG %s" % n)
    print("文字が一致したファイル : %d" % ok)
    print("一致しなかったファイル : %d" % ng)


if __name__ == "__main__":
    main()
