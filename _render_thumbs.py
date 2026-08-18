#!/usr/bin/env python3
"""記事のサムネイル(images/thumb.png)を作る。

ホームのカードと、SNSでシェアしたときのOGP画像に使われます。

## なぜ記事のスクリーンショットを撮らないのか

以前は記事HTMLをそのまま撮っていましたが、**全記事が同じ絵になりました。**
どの記事も上部はトップバー＋白背景＋見出しで、縮小表示のカードでは見分けが
付きません。サムネイルは「一覧の中から目当ての記事を見つける」ためのものなので、
これでは意味がありません。

そこでサムネイル専用のデザインを組み立てて描画します。ポイントは2つ:

1. **カテゴリごとに色を変える** — 一覧に並べたときに、色だけで種類が分かる
2. **決め文句を1つ、極端に大きく置く** — 縮小しても読める文字は1行だけ

## 文字はどこから取るか

**記事のタイトルから機械的に作ります。勝手な煽り文句は足しません。**
タイトルが「主題 — 補足」の形なので、そこで割って主題を大きく、補足を小さく置きます。

meta.json に `thumb` を書くと上書きできます:

```json
"thumb": { "hook": "超基礎から", "main": "Terraform 超入門", "sub": "init / validate / plan" }
```

## 使い方

```bash
python3 _render_thumbs.py                    # 全記事
python3 _render_thumbs.py 2026-08-16_001 …   # 記事ディレクトリ名を指定
python3 _render_thumbs.py --stale            # 記事HTMLより古いものだけ
```

**`_build_index.py` の後に走らせること。** 生成後は Read で目視確認すること。
"""

import base64
import html as htmlmod
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
CONTENTS = HERE / "contents"
FONTS = HERE / "_assets" / "fonts"
CHROMIUM = "/opt/pw-browsers/chromium"
WIDTH, HEIGHT = 1200, 630
# 右にキャラクターを置きたくなったとき用。
# _assets/character/<カテゴリ名>.png があればそれを、無ければ default.png を使う。
# **画像を置くまではキャラ無しで組む**(文字が広く使えるので、そのほうが読める)。
CHARA_DIR = HERE / "_assets" / "character"
CHARA_W = 268                      # 画像を置いたときに右側で占める幅

# カテゴリごとの配色。一覧に並べたとき、色だけで種類が分かるようにする。
#   bg1/bg2 = 背景のグラデーション、accent = 決め文句の色、chip = カテゴリ札の色
THEMES = {
    "デイリーダイジェスト": dict(bg1="#0b1f3a", bg2="#123a6b", accent="#4da3ff", chip="#2a78d6",
                          h1="#7fc4ff", h2="#2a6fd0", hi="#cfe8ff", iris="#1b64c4", pupil="#0b2a52", brow="#3a6ea8"),
    "AIで作る技術":        dict(bg1="#2a0b2e", bg2="#5a1450", accent="#ff5ec7", chip="#c9308f",
                          h1="#ffa8e4", h2="#c9308f", hi="#ffd9f2", iris="#b3247a", pupil="#4a0c30", brow="#a8407e"),
    "Web開発・インフラ":   dict(bg1="#2b1405", bg2="#5e2f08", accent="#ffa43d", chip="#e07b1a",
                          h1="#ffcf8a", h2="#d97a12", hi="#ffeccc", iris="#c06a10", pupil="#4a2a04", brow="#b5761f"),
    "クライアント技術":     dict(bg1="#04241b", bg2="#0a4f39", accent="#3ede9f", chip="#12996b",
                          h1="#8ff0c6", h2="#12996b", hi="#d6fdec", iris="#0e7a52", pupil="#03301f", brow="#2f8f68"),
    "チームで作る技術":     dict(bg1="#2c2405", bg2="#5c4c0a", accent="#ffd93d", chip="#d0a611",
                          h1="#ffe98a", h2="#c99f0d", hi="#fff6cc", iris="#a8830a", pupil="#3d2f01", brow="#a8871f"),
}
DEFAULT_THEME = THEMES["デイリーダイジェスト"]

DASH = re.compile(r"\s*[—–―]\s*")          # タイトルの「主題 — 補足」を割る
DAILY = re.compile(r"^AI-news：\s*([\d/]+)(\s*号外)?\s*$")


# 背景の柄。日付で切り替えて、毎日同じ絵にならないようにする。
# カテゴリの色そのものは変えない(色で種類が分かる、という利点を壊さないため)。
PATTERNS = {
    # 縮小表示でも分かるよう、柄は「大きく・濃く」する。
    # 細かい網目は 400px 幅のカードでは消えてしまう。
    "band":  ("linear-gradient(102deg, transparent 46%, {a}3a 46%, {a}3a 60%, "
              "transparent 60%, transparent 66%, {a}22 66%, {a}22 72%, transparent 72%)"),
    "rays":  ("repeating-conic-gradient(from 196deg at 112% -12%, "
              "{a}30 0deg 9deg, transparent 9deg 22deg)"),
    "dots":  "radial-gradient({a}4a 6px, transparent 6.5px) 0 0/62px 62px",
    "grid":  ("repeating-linear-gradient(0deg, {a}2e 0 2px, transparent 2px 78px),"
              "repeating-linear-gradient(90deg, {a}2e 0 2px, transparent 2px 78px)"),
    "waves": "repeating-linear-gradient(58deg, {a}30 0 7px, transparent 7px 54px)",
    "blob":  ("radial-gradient(46% 58% at 8% 92%, {a}42 0%, transparent 62%),"
              "radial-gradient(38% 48% at 74% 2%, {a}36 0%, transparent 64%),"
              "radial-gradient(26% 34% at 44% 52%, {a}20 0%, transparent 66%)"),
}
PATTERN_KEYS = list(PATTERNS)

# 明るさの振り幅。同じカテゴリ色のまま、濃さと光の位置だけ日替わりにする。
TONES = [
    dict(glow="110% 85% at 85% 8%",   mix=0.00),
    dict(glow="95% 80% at 10% 14%",   mix=0.18),
    dict(glow="120% 95% at 58% 108%", mix=0.08),
    dict(glow="85% 72% at 96% 94%",   mix=0.26),
]


def _mix(hex_color, other, ratio):
    """2色を混ぜる。同系色のまま濃さだけ動かすのに使う。"""
    def rgb(h):
        h = h.lstrip("#")
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    a, b = rgb(hex_color), rgb(other)
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * ratio) for x, y in zip(a, b))


def variant_for(dirname):
    """記事ごとの柄・色味を、日付から決める。

    連続する日が必ず違う柄になるよう、日付の通し番号をそのまま使う。
    同じ記事を撮り直しても結果は変わらない(再現性のため乱数は使わない)。
    """
    import datetime
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", dirname)
    if m:
        n = datetime.date(*map(int, m.groups())).toordinal()
        # 同日に複数号あるとき用のずらし。翌日とぶつからないよう、
        # 1号ぶんではなく柄の総数の約半分だけ動かす。
        tail = re.search(r"_(\d+)$", dirname)
        if tail:
            n += (int(tail.group(1)) - 1) * 3
    else:
        n = sum(dirname.encode())
    return PATTERN_KEYS[n % len(PATTERN_KEYS)], TONES[(n // len(PATTERN_KEYS)) % len(TONES)]


def font_face(name, filename, weight):
    """フォントを data URI で埋め込む。一時HTMLを別の場所に置いても効くように。"""
    path = FONTS / filename
    if not path.is_file():
        return ""
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return (f"@font-face{{font-family:'{name}';font-weight:{weight};font-style:normal;"
            f"src:url(data:font/ttf;base64,{b64}) format('truetype');}}")


def split_title(title):
    """タイトルを (hook, main, sub) に割る。煽り文句は作らない。"""
    parts = DASH.split(title, 1)
    head = parts[0].strip()
    sub = parts[1].strip() if len(parts) > 1 else ""

    m = DAILY.match(head)
    if m:
        # デイリーは日付を上に出し、その日の見出しを主役にする
        hook = "AI-news" + ("  号外" if m.group(2) else "")
        return f"{hook}　{m.group(1)}", sub or head, ""
    return "", head, sub


def dwidth(text):
    """全角を2、半角を1として数えた表示幅。"""
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def size_for(text, avail_px, avail_h, cap, floor, max_lines=3, lh=1.16):
    """avail_px x avail_h に max_lines 行で収まる最大の文字サイズを返す。

    行数は常に max_lines を許す。行数を減らして字を大きくしようとすると、
    "Fargate" のような分割できない英単語が来たときに折り返しが読めず、
    末尾が "…" で切れる。行数に余裕を持たせ、縦幅で頭打ちにするほうが安全。
    """
    w = dwidth(text) or 1
    by_w = int(2 * avail_px * max_lines * 0.92 / w)   # max_lines 行に収まる大きさ
    by_h = int(avail_h / (max_lines * lh))            # max_lines 行が縦に収まる大きさ
    return max(floor, min(cap, by_w, by_h)), max_lines


def emphasize(text, terms, e):
    """本文中のタグ語(製品名・技術名)を色違いにする。

    一覧に並べたとき、何の記事かが色で先に目に入る。
    タグに無い語を勝手に強調はしない。
    """
    terms = sorted({t for t in terms if len(t) >= 2}, key=len, reverse=True)
    marks = []
    for t in terms:
        i = text.find(t)
        if i >= 0 and not any(i < b and a < i + len(t) for a, b in marks):
            marks.append((i, i + len(t)))
    if not marks:
        return e(text)
    marks.sort()
    out, pos = [], 0
    for a, b in marks:
        out.append(e(text[pos:a]))
        out.append(f"<em>{e(text[a:b])}</em>")
        pos = b
    out.append(e(text[pos:]))
    return "".join(out)


def character_img(category):
    """右に置くキャラクター画像を返す。無ければ (空文字, 0)。

    `_assets/character/<カテゴリ名>.png` を優先し、無ければ `default.png`。
    背景透過・縦長(600x840程度以上)のPNGを想定しています。
    画像を置いていない間はキャラ無しで組み、文字を広く使います。
    """
    for name in (f"{category}.png", "default.png"):
        path = CHARA_DIR / name
        if path.is_file():
            b64 = base64.b64encode(path.read_bytes()).decode("ascii")
            return f'<img class="chara" src="data:image/png;base64,{b64}" alt="">', CHARA_W
    return "", 0


def build_html(meta, dirname):
    t = THEMES.get(meta.get("category"), DEFAULT_THEME)
    title = meta.get("title") or dirname
    thumb = meta.get("thumb") or {}
    hook, main, sub = split_title(title)
    hook = thumb.get("hook", hook)
    main = thumb.get("main", main)
    sub = thumb.get("sub", sub)

    # タグは下段に置くが、長いと右側のサイト名とぶつかる。
    # 表示幅の合計で打ち切る(全角1文字=2)。
    tags, budget = [], 20
    for x in (meta.get("tags") or []):
        x = str(x)
        if dwidth(x) + 3 > budget:
            break
        tags.append(x)
        budget -= dwidth(x) + 3
        if len(tags) >= 3:
            break
    cat = meta.get("category", "")
    e = htmlmod.escape

    chara, chara_w = character_img(meta.get("category", ""))
    pat_key, tone = variant_for(dirname)
    pattern = PATTERNS[pat_key].format(a=t["accent"])
    bg1 = _mix(t["bg1"], t["chip"], tone["mix"])
    bg2 = _mix(t["bg2"], t["accent"], tone["mix"] * 0.6)

    # 内側の使える大きさ。枠16px + 左右パディング52px、上下は帯96+84を引く。
    # キャラクター画像がある場合だけ、そのぶんも文字から引く
    avail = WIDTH - 2 * 16 - 2 * 52 - chara_w
    mid_h = HEIGHT - 2 * 16 - 96 - 84
    sub_px, sub_lines = size_for(sub, avail, 120, 40, 26, 2, 1.35) if sub else (0, 0)
    sub_box = int(sub_px * 1.35 * sub_lines) + 22 if sub else 0
    main_px, main_lines = size_for(main, avail, mid_h - sub_box, 108, 46)

    faces = (font_face("NotoJP", "NotoSansJP-Black.ttf", 900)
             + font_face("NotoJP", "NotoSansJP-Regular.ttf", 400))

    import hashlib
    chips = "".join(f'<span class="tag">{e(x)}</span>' for x in tags)
    main_html = emphasize(main, [str(x) for x in (meta.get("tags") or [])], e)
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{WIDTH}px;height:{HEIGHT}px}}
body{{font-family:'NotoJP','IPAGothic',sans-serif;background:{bg1}}}
.frame{{
  position:relative;width:{WIDTH}px;height:{HEIGHT}px;overflow:hidden;
  background:
    radial-gradient({tone['glow']}, {t['accent']}55 0%, transparent 58%),
    linear-gradient(135deg, {bg1} 0%, {bg2} 100%);
  border:16px solid {t['chip']};
  display:grid;grid-template-rows:96px 1fr 84px;padding:0 52px;
}}
/* 背景の柄。日付で切り替わる(PATTERNS) */
.frame::after{{
  content:"";position:absolute;inset:0;pointer-events:none;
  background:{pattern};
}}
.row{{position:relative;z-index:2;padding-right:{chara_w}px;display:flex;align-items:center;gap:18px;min-width:0}}
.cat{{
  background:{t['chip']};color:#fff;font-weight:900;font-size:27px;
  padding:9px 22px;border-radius:999px;white-space:nowrap;
  box-shadow:0 3px 0 rgba(0,0,0,.35);
}}
.hook{{
  color:{t['accent']};font-weight:900;font-size:36px;white-space:nowrap;
  text-shadow:2px 2px 0 rgba(0,0,0,.6);
}}
.mid{{
  position:relative;z-index:2;display:flex;flex-direction:column;
  justify-content:center;gap:22px;min-width:0;padding-right:{chara_w}px;
}}
.main{{
  color:#fff;font-weight:900;line-height:1.14;font-size:{main_px}px;
  overflow-wrap:anywhere;
  -webkit-text-stroke:14px {t['bg1']};paint-order:stroke fill;
  text-shadow:0 5px 0 rgba(0,0,0,.45);
  display:-webkit-box;-webkit-line-clamp:{main_lines};-webkit-box-orient:vertical;overflow:hidden;
}}
.main em{{font-style:normal;color:{t['accent']}}}
.sub{{
  color:#eaf2ff;font-weight:400;font-size:{sub_px}px;line-height:1.35;
  border-left:8px solid {t['accent']};padding-left:18px;
  text-shadow:0 2px 6px rgba(0,0,0,.7);
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;
}}
.bot{{justify-content:space-between;padding-right:{chara_w}px}}
.chara{{
  position:absolute;right:18px;bottom:0;width:{chara_w}px;height:auto;z-index:1;
  filter:drop-shadow(0 8px 20px rgba(0,0,0,.5));
}}
.tags{{display:flex;gap:12px;overflow:hidden;min-width:0;flex:1 1 auto}}
.tag{{
  background:#fff;color:{t['bg1']};font-weight:900;font-size:25px;
  padding:8px 20px;border-radius:11px;white-space:nowrap;
  box-shadow:0 3px 0 rgba(0,0,0,.3);
}}
.site{{flex:0 0 auto;color:#ffffffd0;font-weight:900;font-size:23px;letter-spacing:.05em;white-space:nowrap}}
</style></head><body><div class="frame">
  {chara}
  <div class="row">
    <span class="cat">{e(cat)}</span>
    {f'<span class="hook">{e(hook)}</span>' if hook else ''}
  </div>
  <div class="mid">
    <div class="main">{main_html}</div>
    {f'<div class="sub">{e(sub)}</div>' if sub else ''}
  </div>
  <div class="row bot">
    <div class="tags">{chips}</div>
    <div class="site">AIニュース デイリーダイジェスト</div>
  </div>
</div></body></html>"""


_OFFSET = None


def shoot(html, out, width, height):
    """HTMLを width x height ちょうどのPNGにする。

    chromium の --window-size は**ウィンドウ枠のぶんを引いた大きさ**を
    ビューポートにする(この環境では87px引かれる)。指定どおりに撮れないので、
    枠のぶんを実測して足してから撮り、上から height だけ切り出す。
    """
    global _OFFSET
    if _OFFSET is None:
        _OFFSET = measure_offset(width)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
            f.write(html)
            tmp = Path(f.name)
        raw = out.with_suffix(".raw.png")
        subprocess.run(
            [CHROMIUM, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             "--force-color-profile=srgb", "--force-device-scale-factor=1",
             "--virtual-time-budget=4000",
             f"--window-size={width},{height + _OFFSET}",
             f"--screenshot={raw}", tmp.as_uri()],
            capture_output=True, text=True, timeout=180,
        )
        if not raw.is_file() or raw.stat().st_size == 0:
            return False
        with Image.open(raw) as im:
            im.convert("RGB").crop((0, 0, width, height)).save(out, "PNG", optimize=True)
        raw.unlink()
        return True
    finally:
        if tmp and tmp.exists():
            tmp.unlink()


def measure_offset(width, probe_h=800):
    """ウィンドウ高さと実ビューポート高さの差を実測する。

    100vh を塗った箱を撮り、その色が何px目まで続くかを見る。
    chromium のバージョンで枠の厚みが変わっても自動で追従する。
    """
    probe = ("<!doctype html><meta charset=utf-8>"
             "<style>html,body{margin:0;padding:0}"
             "#v{height:100vh;background:#ff0000}</style><div id=v></div>")
    tmp = out = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
            f.write(probe)
            tmp = Path(f.name)
        out = Path(tempfile.mkstemp(suffix=".png")[1])
        subprocess.run(
            [CHROMIUM, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--virtual-time-budget=1500",
             f"--window-size={width},{probe_h}", f"--screenshot={out}", tmp.as_uri()],
            capture_output=True, text=True, timeout=90,
        )
        with Image.open(out) as im:
            px = im.convert("RGB").load()
            x = width // 2
            vh = 0
            for y in range(im.height):
                if px[x, y] == (255, 0, 0):
                    vh = y + 1
                else:
                    break
        off = max(0, probe_h - vh)
        print(f"  (ビューポート補正 {off}px を実測)")
        return off
    except Exception:
        return 0
    finally:
        for f in (tmp, out):
            if f and f.exists():
                f.unlink()


def render(dirname):
    d = CONTENTS / dirname
    if not (d / "index.html").is_file():
        return f"{dirname}: index.html がありません"
    try:
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        meta = {}

    out = d / "images" / "thumb.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not shoot(build_html(meta, dirname), out, WIDTH, HEIGHT):
        return f"{dirname}: 生成に失敗"
    return f"{dirname}: {out.stat().st_size // 1024}KB"


def main():
    if not (FONTS / "NotoSansJP-Black.ttf").is_file():
        print(f"警告: {FONTS}/NotoSansJP-Black.ttf がありません。"
              " 文字が細くなります(IPAGothicにフォールバック)。", file=sys.stderr)

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = args or sorted(p.name for p in CONTENTS.iterdir() if p.is_dir())
    if "--stale" in sys.argv:
        names = [n for n in names
                 if (CONTENTS / n / "index.html").is_file()
                 and (not (CONTENTS / n / "images" / "thumb.png").is_file()
                      or (CONTENTS / n / "images" / "thumb.png").stat().st_mtime
                      < (CONTENTS / n / "index.html").stat().st_mtime)]
    if not names:
        print("撮り直すサムネイルはありません。")
        return
    for n in names:
        print(" ", render(n))
    print(f"サムネイルを{len(names)}枚生成しました。**Read で開いて目視確認すること。**")


if __name__ == "__main__":
    main()
