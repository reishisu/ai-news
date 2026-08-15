#!/usr/bin/env python3
# IAMポリシーのJSONを、AWSに接続せずに検査する。
# 使うのは parliament (Duo Security製のIAMポリシーlinter)。
# CLIの `parliament --file` は端末が無い環境だと
# 「stdinと併用するな」と誤判定して落ちるので、
# ライブラリのAPIを直接呼ぶ。
import glob
import json
import sys
import textwrap

from parliament import analyze_policy_string

W = 38


def wrap(s, indent="    "):
    for line in textwrap.wrap(s, width=W, subsequent_indent=indent):
        print(line)


def main(pattern):
    for path in sorted(glob.glob(pattern)):
        print(f"### {path.rsplit('/', 1)[-1]}")
        try:
            pol = analyze_policy_string(open(path, encoding="utf-8").read())
        except Exception as e:
            wrap(f"  解析不能: {e}")
            print()
            continue
        if not pol.findings:
            print("  指摘なし")
        for f in pol.findings:
            line = f.location.get("line") if f.location else None
            head = f"  {f.issue}"
            if line:
                head += f" ({line}行目)"
            print(head)
            wrap(f"   {f.detail}", indent="   ")
        print()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "policies/*.json")
