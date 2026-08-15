#!/usr/bin/env python3
"""記事のサムネイル(images/thumb.png)を、記事HTMLのスクリーンショットから作り直す。

ホームのカードと、SNSでシェアしたときのOGP画像に使われます。

なぜ専用スクリプトにしたか:
  chromium に記事HTMLをそのまま撮らせると、**画面右下に浮いているシェアボタンが
  写り込みます**。またコメント欄(giscus)や計測タグは外部ホストを見に行くため、
  撮影のたびに待たされます。ここでは撮影用の一時HTMLを作って、
  それらを外してから撮ります。記事本体は書き換えません。

使い方:
  python3 _render_thumbs.py                    # 全記事
  python3 _render_thumbs.py 2026-08-15_001 …   # 記事ディレクトリ名を指定
  python3 _render_thumbs.py --stale            # 記事HTMLより古いものだけ

サムネイルは記事の見出しを写すので、**タイトルを直したら必ず撮り直すこと。**
古いままだと、ホームのカードとシェア画像だけ昔の見出しが残ります。
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTENTS = HERE / "contents"
CHROMIUM = "/opt/pw-browsers/chromium"
WIDTH, HEIGHT = 1200, 630

# 撮影時に外すもの。どれも記事の中身ではなく、外側の仕掛け。
STRIP = [
    # 右下に浮くシェアボタン一式
    (re.compile(r"<!-- ai-news-sharebar -->.*?(?=<script src=)", re.S), ""),
    # コメント欄(giscus。外部ホスト)
    (re.compile(r'<!-- ai-news-comments -->.*?</section>', re.S), ""),
    # 計測タグ(外部ホスト)
    (re.compile(r'<script data-goatcounter.*?</script>', re.S), ""),
]


def render(dirname: str) -> str:
    d = CONTENTS / dirname
    src = d / "index.html"
    if not src.exists():
        return f"{dirname}: index.html がありません"

    html = src.read_text(encoding="utf-8")
    for pat, rep in STRIP:
        html = pat.sub(rep, html)

    out = d / "images" / "thumb.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    # 相対パス(../../css/... )を保つため、記事と同じディレクトリに置く
    tmp = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".html", dir=d,
                                         encoding="utf-8", delete=False) as f:
            f.write(html)
            tmp = Path(f.name)
        r = subprocess.run(
            [CHROMIUM, "--headless", "--no-sandbox", "--disable-gpu",
             "--hide-scrollbars", "--force-color-profile=srgb",
             f"--window-size={WIDTH},{HEIGHT}",
             f"--screenshot={out}", tmp.as_uri()],
            capture_output=True, text=True, timeout=120,
        )
        if not out.exists() or out.stat().st_size == 0:
            return f"{dirname}: 生成に失敗 {r.stderr.strip()[:120]}"
        return f"{dirname}: {out.stat().st_size // 1024}KB"
    finally:
        if tmp and tmp.exists():
            tmp.unlink()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    stale_only = "--stale" in sys.argv

    names = args or sorted(p.name for p in CONTENTS.iterdir() if p.is_dir())
    if stale_only:
        keep = []
        for n in names:
            th, idx = CONTENTS / n / "images" / "thumb.png", CONTENTS / n / "index.html"
            if idx.exists() and (not th.exists() or th.stat().st_mtime < idx.stat().st_mtime):
                keep.append(n)
        names = keep

    if not names:
        print("撮り直すサムネイルはありません。")
        return
    for n in names:
        print(" ", render(n))
    print(f"サムネイルを{len(names)}枚生成しました。**Read で開いて目視確認すること。**")


if __name__ == "__main__":
    main()
