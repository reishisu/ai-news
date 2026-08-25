#!/usr/bin/env python3
"""記事に貼った英語原文が、取得した公式ドキュメントと一字一致するか照合する。

markdown の強調記号(** と `)は表示上は出ないので、比較前に落とす。
使い方: python3 verify_quotes.py <記事のindex.html> <取得したドキュメントのテキスト>
"""
import html, re, sys

art, doc = sys.argv[1], sys.argv[2]
src = open(doc, encoding="utf-8").read()


def norm(t):
    t = t.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", t).strip()


src_n = norm(src)
body = open(art, encoding="utf-8").read()

# code wrap ブロックの <pre> 中身のうち、英字が主体のものを原文とみなす
blocks = re.findall(r'<div class="code wrap">.*?<pre>(.*?)</pre>', body, re.S)
ng = 0
for b in blocks:
    t = html.unescape(b)
    letters = sum(c.isascii() and c.isalpha() for c in t)
    if letters < len(t) * 0.4:
        continue
    ok = norm(t) in src_n
    ng += not ok
    print(("一致  " if ok else "不一致") + " | " + norm(t)[:58] + "…")

print("\n原文ブロック %d件 / 不一致 %d件" % (len(blocks), ng))
sys.exit(1 if ng else 0)
