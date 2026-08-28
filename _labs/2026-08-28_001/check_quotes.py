#!/usr/bin/env python3
"""記事の <pre> に貼った英語原文が、一次資料と一字一句合っているかを機械的に照合する。

CLAUDE.md 第2節「原文は一字も変えないこと」を、目視ではなくコードで確かめるためのもの。
2026-08-28 の号でこれを回したところ、**3種類の改変が見つかった**:

1. Cowork の引用で、原文の「→」を「>」に書き換えていた
2. 公式ドキュメントの引用で、原文に無いバッククォート（`git add`）を足していた
3. 3か所で、原文のタイポグラフィックなアポストロフィ（’ U+2019）を
   ASCIIのアポストロフィ（'）に置き換えていた

どれも読めば意味は通るが、「一字も変えない」の約束は破っている。**目視では気づけない。**

使い方:
    python3 check_quotes.py <記事のindex.html> <原典ファイル1> <原典ファイル2> ...

原典はHTMLでもMarkdownでもよい（HTMLはタグを落として比較する）。
記事側の <pre> のうち、行頭が `$` のもの（自分のターミナル出力）は照合対象から外す。
"""
import html
import re
import sys


def plain(path):
    """HTML でも Markdown でも Discourse の JSON でも、比較用のテキストにする。"""
    s = open(path, encoding="utf-8", errors="replace").read()
    if path.endswith(".json"):
        # Discourse (ask.vrchat.com) の投稿本文は post_stream.posts[].cooked にある
        import json as _json
        d = _json.loads(s)
        s = " ".join(p["cooked"] for p in d["post_stream"]["posts"])
    s = re.sub(r"<script.*?</script>", "", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", "", s, flags=re.S)
    # タグは「詰めて」落とす。空白を挟むと <code> をまたぐ語が分断される
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s)))


def quotes_in(article):
    s = open(article, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'<div class="code-head">(.*?)</div><pre>(.*?)</pre>', s, re.S):
        head = re.sub(r"<[^>]+>", "", m.group(1))
        body = html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))
        out.append((head, body))
    return out


def main():
    article, sources = sys.argv[1], sys.argv[2:]
    haystack = " \n ".join(plain(p) for p in sources)
    bad = 0
    for head, body in quotes_in(article):
        # 行頭が `$` で始まるブロックは自分のターミナル出力なので、丸ごと対象外
        if body.lstrip().startswith("$"):
            continue
        for frag in (x.strip() for x in re.split(r"\n\n|\n", body)):
            frag = frag.replace("(中略)", "").strip()
            if not frag or frag.endswith(":"):
                continue
            if re.sub(r"\s+", " ", frag) in haystack:
                continue
            bad += 1
            print(f"不一致 [{head}]")
            print(f"  記事: {frag[:120]}")
    print(f"\n不一致 {bad} 件")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
