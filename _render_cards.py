#!/usr/bin/env python3
"""「今日の3行まとめ」をSNS共有用のカード画像(summary-card.png)にする。

サムネイル(thumb.png)が「見出し1つを大きく」なのに対し、こちらは
**中身が読める共有画像**。白いパネルに番号付きの3行を置く
(動画版のスライドと同じ見た目。デザインの出どころは動画パイプライン)。

- 出力: contents/<記事>/images/summary-card.png (1280x720)
- HTMLからは参照しない。og:image / twitter:image もサムネイルのまま
  (変えるなら運営者の判断で _build_index.py を直す)。
  X などで手動シェアするときに、添付画像として使う
- 「今日の3行まとめ」が無い記事(連載など)はスキップする

## 使い方

```bash
python3 _render_cards.py                     # 全記事(3行まとめのある号だけ)
python3 _render_cards.py 2026-08-18_001      # 1記事だけ
python3 _render_cards.py --stale             # 記事HTMLより古いものだけ
```

生成後は **Read で開いて目視確認**すること(サムネイルと同じ決まり)。
"""

import html as htmlmod
import json
import re
import sys
from pathlib import Path

import _render_thumbs as thumbs

HERE = Path(__file__).resolve().parent
CONTENTS = HERE / "contents"
WIDTH, HEIGHT = 1280, 720

SUMMARY_SEC = re.compile(
    r'<section class="summary">.*?</section>', flags=re.DOTALL)
LI_HEAD = re.compile(r"<li>\s*<b>(.*?)</b>", flags=re.DOTALL)
DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")


def extract_summary(html):
    """記事HTMLから「今日の3行まとめ」の太字見出し3つを取り出す。"""
    m = SUMMARY_SEC.search(html)
    if not m or "3行まとめ" not in m.group(0):
        return []
    items = []
    for raw in LI_HEAD.findall(m.group(0)):
        text = re.sub(r"<[^>]+>", "", raw)
        text = htmlmod.unescape(re.sub(r"\s+", " ", text)).strip()
        if text:
            items.append(text)
    return items[:3]


def build_html(dirname, meta, items):
    cat = meta.get("category", "デイリーダイジェスト")
    t = thumbs.THEMES.get(cat, thumbs.DEFAULT_THEME)
    pat_key, tone = thumbs.variant_for(dirname)
    pattern = thumbs.PATTERNS[pat_key].format(a=t["accent"])
    bg1 = thumbs._mix(t["bg1"], t["chip"], tone["mix"])
    bg2 = thumbs._mix(t["bg2"], t["accent"], tone["mix"] * 0.6)
    faces = (thumbs.font_face("NotoJP", "NotoSansJP-Black.ttf", 900)
             + thumbs.font_face("NotoJP", "NotoSansJP-Regular.ttf", 400))
    e = htmlmod.escape

    m = DATE_RE.match(dirname)
    date = f"{m.group(1)}/{m.group(2)}/{m.group(3)}" if m else dirname
    rows = "".join(
        f'<div class="row"><span class="no">{i + 1}</span><span>{e(x)}</span></div>'
        for i, x in enumerate(items))

    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{WIDTH}px;height:{HEIGHT}px}}
body{{font-family:'NotoJP','IPAGothic',sans-serif}}
.frame{{
  position:relative;width:{WIDTH}px;height:{HEIGHT}px;overflow:hidden;
  background:
    radial-gradient({tone['glow']}, {t['accent']}66 0%, transparent 56%),
    linear-gradient(135deg, {bg1} 0%, {bg2} 100%);
}}
.pat{{position:absolute;inset:0;background:{pattern}}}
.panel{{
  position:absolute;left:44px;right:44px;top:40px;bottom:40px;
  background:#fff;border-radius:24px;overflow:hidden;
  box-shadow:0 18px 50px rgba(0,0,0,.38);
  display:flex;flex-direction:column;
}}
.pbar{{height:10px;background:linear-gradient(90deg,{t['chip']},{t['accent']})}}
.phead{{display:flex;align-items:center;gap:18px;padding:26px 38px 6px}}
.chipname{{
  background:{t['chip']};color:#fff;font-weight:900;font-size:26px;
  padding:6px 18px;border-radius:8px;white-space:nowrap;
  box-shadow:0 6px 14px rgba(0,0,0,.25);
}}
.ptitle{{color:#141d33;font-weight:900;font-size:44px}}
.date{{margin-left:auto;color:#5b6472;font-weight:900;font-size:26px}}
.rows{{flex:1;display:flex;flex-direction:column;gap:16px;justify-content:center;
  padding:14px 38px 20px;min-height:0}}
.row{{
  display:flex;gap:18px;align-items:center;background:#f1f4fa;
  border-radius:14px;padding:16px 20px;color:#1d2740;font-weight:900;font-size:30px;
  line-height:1.4;overflow-wrap:break-word;word-break:auto-phrase;line-break:strict;
}}
.row .no{{
  flex:0 0 auto;width:42px;height:42px;border-radius:50%;background:{t['chip']};
  color:#fff;display:flex;align-items:center;justify-content:center;font-size:23px;
}}
.foot{{padding:0 38px 18px;color:#5b6472;font-weight:900;font-size:20px}}
</style></head><body><div class="frame">
  <div class="pat"></div>
  <div class="panel">
    <div class="pbar"></div>
    <div class="phead">
      <span class="chipname">今日の3行まとめ</span>
      <span class="date">AI-news　{e(date)}</span>
    </div>
    <div class="rows">{rows}</div>
    <div class="foot">AIニュース デイリーダイジェスト</div>
  </div>
</div></body></html>"""


def render(dirname):
    d = CONTENTS / dirname
    html_path = d / "index.html"
    if not html_path.is_file():
        return f"{dirname}: index.html がありません"
    items = extract_summary(html_path.read_text(encoding="utf-8"))
    if not items:
        return f"{dirname}: 3行まとめが無いのでスキップ"
    try:
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        meta = {}
    out = d / "images" / "summary-card.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not thumbs.shoot(build_html(dirname, meta, items), out, WIDTH, HEIGHT):
        return f"{dirname}: 生成に失敗"
    return f"{dirname}: {out.stat().st_size // 1024}KB"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = args or sorted(p.name for p in CONTENTS.iterdir() if p.is_dir())
    if "--stale" in sys.argv:
        names = [n for n in names
                 if (CONTENTS / n / "index.html").is_file()
                 and (not (CONTENTS / n / "images" / "summary-card.png").is_file()
                      or (CONTENTS / n / "images" / "summary-card.png").stat().st_mtime
                      < (CONTENTS / n / "index.html").stat().st_mtime)]
    done = 0
    for n in names:
        msg = render(n)
        if "スキップ" not in msg or args:
            print(" ", msg)
        done += "KB" in msg
    print(f"カードを{done}枚生成しました。**Read で開いて目視確認すること。**")


if __name__ == "__main__":
    main()
