#!/usr/bin/env python3
"""記事に貼った端末ログが、実行結果と1行ずつ一致するかを機械的に確かめる。

使い方:
    python3 _labs/2026-08-30_claude-automation/verify_pasted.py

`.code term` のブロックだけを対象にする（実行結果を貼った箇所）。
`.code wrap` は原文引用や別採取のJSONなので対象外。記事側でそう書き分けている。
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ART = ROOT / "contents" / "2026-08-30_claude-automation" / "index.html"
LOGS = [HERE / "output.txt", HERE / "keys.txt"]


def main():
    haystack = "\n".join(p.read_text(encoding="utf-8") for p in LOGS)
    html = ART.read_text(encoding="utf-8")
    blocks = re.findall(r'class="code term">.*?<pre>(.*?)</pre>', html, re.S)
    bad = []
    checked = 0
    for b in blocks:
        text = re.sub(r"<[^>]+>", "", b)
        text = text.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
        for line in text.splitlines():
            line = line.rstrip()
            if not line.strip() or line.strip() == "(中略)":
                continue
            checked += 1
            if line not in haystack:
                bad.append(line)
    print("端末ブロック: %d 個 / 照合した行: %d" % (len(blocks), checked))
    if bad:
        print("実行結果に見つからない行:")
        for l in bad:
            print("  " + repr(l))
        return 1
    print("すべて実行結果と一致した。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
