#!/usr/bin/env python3
"""記事に貼ったターミナル出力が、実行結果ファイルと1行ずつ一致するか照合する。

使い方:
    python3 verify_pasted.py

出力: 一致しないブロック / 行があれば、その差分を表示する。
記事側の <span class="ok-line"> などのタグは剥がしてから比較する。
末尾の空白は無視する（HTML に貼るときに落ちるため）。
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "contents" / "2026-08-15_unity-web-on-aws" / "index.html"
LAB = pathlib.Path(__file__).resolve().parent

SOURCES = ["output.txt", "alb-attrs-out.txt", "tf-output.txt", "plan.txt"]


def norm(lines):
    return [l.rstrip() for l in lines]


def main():
    art = ART.read_text(encoding="utf-8")
    pool = []
    for name in SOURCES:
        p = LAB / name
        if p.exists():
            pool.append((name, norm(p.read_text(encoding="utf-8").splitlines())))

    blocks = re.findall(
        r'<div class="code term">\s*<div class="code-head">(.*?)</div>\s*<pre>(.*?)</pre>',
        art,
        re.S,
    )
    if not blocks:
        print("NG: term ブロックが見つからない")
        return 1

    ng = 0
    for head, body in blocks:
        text = re.sub(r"</?span[^>]*>", "", body)
        lines = norm(html.unescape(text).splitlines())
        missing = []
        for line in lines:
            if not line.strip():
                continue
            if not any(line in src for _, src in pool):
                missing.append(line)
        label = re.sub(r"<[^>]+>", "", head)[:40]
        if missing:
            ng += 1
            print(f"NG [{label}] 実行結果に無い行 {len(missing)}件:")
            for m in missing:
                print(f"    {m!r}")
        else:
            print(f"OK [{label}] {len(lines)}行すべて実行結果にある")

    # 連続性の確認: 各ブロックが実行結果の連続した並びになっているか
    for head, body in blocks:
        text = re.sub(r"</?span[^>]*>", "", body)
        lines = [l for l in norm(html.unescape(text).splitlines())]
        label = re.sub(r"<[^>]+>", "", head)[:40]
        found = False
        for _, src in pool:
            for i in range(len(src) - len(lines) + 1):
                if src[i : i + len(lines)] == lines:
                    found = True
                    break
            if found:
                break
        if not found:
            print(f"注意 [{label}] 実行結果の中で連続した並びとしては一致しない")

    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
