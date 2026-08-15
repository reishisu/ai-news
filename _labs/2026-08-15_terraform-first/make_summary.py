#!/usr/bin/env python3
"""out/*.exit を読んで、終了コードの一覧を1枚にまとめる。

数字は demo.sh が実際に測ったものをそのまま使う（手で書かない）。
"""
import os
import sys

LABELS = [
    ("01-validate-before-init", "validate (init前)"),
    ("02-init", "init"),
    ("03-validate", "validate"),
    ("04-plan", "plan"),
    ("13-plan-out", "plan -out=tfplan"),
    ("14b-detailed-exitcode", "plan -detailed-exitcode"),
    ("11-fmt-check", "fmt -check"),
    ("05-state-list", "state list (state無)"),
    ("06-missing-brace", "validate (閉じ}無)"),
    ("07-typo-argument", "validate (名前typo)"),
    ("15-version-too-new", "validate (版不一致)"),
    ("16-no-credentials", "plan (認証情報無)"),
    ("17-data-source", "plan (dataあり)"),
]


def w(s):
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def main():
    out = sys.argv[1]
    print("%-26s%4s" % ("command", "exit"))
    print("-" * 30)
    for key, label in LABELS:
        path = os.path.join(out, key + ".exit")
        code = open(path).read().strip().split("=")[1]
        pad = " " * max(1, 26 - w(label))
        print("%s%s%4s" % (label, pad, code))


if __name__ == "__main__":
    main()
