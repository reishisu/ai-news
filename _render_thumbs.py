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
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
CONTENTS = HERE / "contents"
FONTS = HERE / "_assets" / "fonts"
def find_chromium():
    """撮影に使うブラウザを探す。

    この実行環境では /opt/pw-browsers/chromium に居ますが、手元のPCで走らせる人も
    いるので、見つからなければ PATH と Mac の既定の場所も見ます。
    環境変数 CHROMIUM で明示することもできます。
    """
    import shutil
    env = os.environ.get("CHROMIUM")
    if env:
        return env
    for c in ("/opt/pw-browsers/chromium",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium"):
        if Path(c).exists():
            return c
    for name in ("chromium", "chromium-browser", "google-chrome",
                 "google-chrome-stable", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    return "/opt/pw-browsers/chromium"      # 見つからないときは元の場所を返す


CHROMIUM = find_chromium()
# YouTube と同じ 16:9。SNSカード(OGP)の推奨は 1.91:1 なので、
# X や Facebook では上下がわずかに切られることがある。
WIDTH, HEIGHT = 1280, 720
# 右にキャラクターを置きたくなったとき用。
# _assets/character/<カテゴリ名>.png があればそれを、無ければ default.png を使う。
# **画像を置くまではキャラ無しで組む**(文字が広く使えるので、そのほうが読める)。
CHARA_DIR = HERE / "_assets" / "character"
CHARA_W = 440                      # 画像を置いたときに右側で占める幅の上限
CHARA_H = 660                      # 同じく高さの上限(上に文字用の余白を残す)
# 置いてある画像は全身の立ち絵だが、そのまま縮めると**顔が10px程度になり表情が分からない**。
# 描画時に上から CHARA_CROP のぶんだけ切り出して(=胸から上)、大きく見せる。
# 元画像は全身のまま残してあるので、この数字を変えて撮り直すだけで比率を変えられる。
CHARA_CROP = 0.42
CAST_DIR = CHARA_DIR / "cast"      # キャラ複数 × ポーズ複数を置く場所

# カテゴリごとの配色。一覧に並べたとき、色だけで種類が分かるようにする。
#   bg1/bg2 = 背景のグラデーション、accent = 決め文句の色、chip = カテゴリ札の色
THEMES = {
    "デイリーダイジェスト": dict(bg1="#0d2f6e", bg2="#2b6fe0", accent="#5ec2ff", chip="#1e5fd0",
                          h1="#7fc4ff", h2="#2a6fd0", hi="#cfe8ff", iris="#1b64c4", pupil="#0b2a52", brow="#3a6ea8"),
    "AIで作る技術":        dict(bg1="#4a0d4e", bg2="#a81f86", accent="#ff7ad6", chip="#c9308f",
                          h1="#ffa8e4", h2="#c9308f", hi="#ffd9f2", iris="#b3247a", pupil="#4a0c30", brow="#a8407e"),
    "Web開発・インフラ":   dict(bg1="#5a2a06", bg2="#c25f0d", accent="#ffc061", chip="#e07b1a",
                          h1="#ffcf8a", h2="#d97a12", hi="#ffeccc", iris="#c06a10", pupil="#4a2a04", brow="#b5761f"),
    "クライアント技術":     dict(bg1="#04452f", bg2="#0d9c68", accent="#5ff5bb", chip="#0f8f61",
                          h1="#8ff0c6", h2="#12996b", hi="#d6fdec", iris="#0e7a52", pupil="#03301f", brow="#2f8f68"),
    "チームで作る技術":     dict(bg1="#4a3a05", bg2="#b8930c", accent="#ffe86b", chip="#c99f0d",
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


def day_number(dirname):
    """記事ディレクトリ名から、日替わりの通し番号を出す。

    背景の柄と、キャラのポーズの選択に使う。乱数は使わないので、
    同じ記事を撮り直しても必ず同じ結果になる。
    """
    import datetime
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", dirname)
    if not m:
        return sum(dirname.encode())
    n = datetime.date(*map(int, m.groups())).toordinal()
    # 同日に複数号あるとき用のずらし。翌日とぶつからないよう、
    # 1号ぶんではなく柄の総数の約半分だけ動かす。
    tail = re.search(r"_(\d+)$", dirname)
    if tail:
        n += (int(tail.group(1)) - 1) * 3
    return n


def variant_for(dirname):
    """記事ごとの柄・色味を、日付から決める。

    連続する日が必ず違う柄になるよう、日付の通し番号をそのまま使う。
    """
    n = day_number(dirname)
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
    """avail_px x avail_h に収まる最大の文字サイズと、そのときの行数を返す。

    大きいほうから試して、**実際に必要な行数**で縦が収まる最大を採る。
    行数を決め打ちして計算すると、2行で足りる文字を3行ぶんの高さで
    見積もってしまい、下half が空いて間延びする。
    """
    import math
    w = dwidth(text) or 1
    for px in range(cap, floor - 1, -2):
        per_line = 2 * avail_px / px * 0.82      # 1行に入る表示幅(余裕を見る)
        lines = max(1, math.ceil(w / per_line))
        if lines <= max_lines and lines * px * lh <= avail_h:
            return px, lines
    return floor, max_lines


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


def fit_chara(w, h):
    """元画像の大きさから、サムネイル上での表示サイズを決める。

    幅 CHARA_W・高さ CHARA_H の箱に収める。高さを見ずに幅だけ固定すると、
    縦長すぎる画像で頭が上の黒帯に切られる(bottom 基準で置いているため)。
    拡大はしない(粗くなるだけなので、小さい画像はそのまま小さく置く)。
    """
    if w <= 0 or h <= 0:
        return CHARA_W, CHARA_H
    scale = min(CHARA_W / w, CHARA_H / h, 1.0)
    return max(1, round(w * scale)), max(1, round(h * scale))


def cast_folder(category):
    """カテゴリの担当キャラのフォルダを返す。無ければ None。

    決め方は次の順。
      1. `cast/cast.json` に書いてある割り当て(手で決めたいとき)
      2. `comfy/recipe.json` の cast[].category(生成時に決めた担当をそのまま使う)
      3. どちらも無ければ None(呼び出し側で日替わりに回す)
    """
    if not CAST_DIR.is_dir():
        return None
    for path, get in ((CAST_DIR / "cast.json", lambda d: d.get(category)),
                      (CHARA_DIR / "comfy" / "recipe.json",
                       lambda d: next((c["name"] for c in d.get("cast", [])
                                       if c.get("category") == category), None))):
        if not path.is_file():
            continue
        try:
            name = get(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError, KeyError, TypeError):
            continue
        if name and (CAST_DIR / name).is_dir():
            return CAST_DIR / name
    return None


def character_path(category, dirname):
    """使うキャラクター画像のパスを返す。無ければ None。

    探す順:
      1. `cast/<担当キャラ>/*.png` … カテゴリごとに担当を決めているとき。
         同じキャラの中から、記事の日付でポーズを選ぶ(連続する日は別のポーズ)
      2. `cast/*/*.png` … 担当を決めていないときは、キャラもポーズも日替わり
      3. `<カテゴリ名>.png` → `default.png` … 1枚だけ置く従来の形
    """
    n = day_number(dirname)
    folder = cast_folder(category)
    if folder is None and CAST_DIR.is_dir():
        folders = sorted(p for p in CAST_DIR.iterdir() if p.is_dir())
        if folders:
            folder = folders[n % len(folders)]
    if folder is not None:
        shots = sorted(folder.glob("*.png"))
        if shots:
            return shots[n % len(shots)]
    for name in (f"{category}.png", "default.png"):
        path = CHARA_DIR / name
        if path.is_file():
            return path
    return None


def chara_view(path):
    """置いてある画像を、サムネイルに出す形(胸から上)にして返す。

    戻り値は (PNGのバイト列, 表示幅, 表示高さ)。開けなければ None。
    """
    import io
    try:
        with Image.open(path) as raw:
            im = raw.convert("RGBA")
    except OSError:
        return None
    if 0 < CHARA_CROP < 1:
        im = im.crop((0, 0, im.width, max(1, int(im.height * CHARA_CROP))))
        box = im.getchannel("A").getbbox()      # 切ったぶん左右に余白が出ることがある
        if box:
            im = im.crop(box)
    disp_w, disp_h = fit_chara(*im.size)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue(), disp_w, disp_h


def character_img(category, dirname):
    """右に置くキャラクター画像を返す。無ければ (空文字, 0)。

    背景透過・縦長(600x840程度以上)のPNGを想定しています。
    画像を置いていない間はキャラ無しで組み、文字を広く使います。
    画像の縦横比に合わせて表示サイズを決めるので、正方形でも横長でも
    はみ出しません(文字の幅も、実際に占める幅ぶんだけ狭まります)。
    取り込みは `_prepare_character.py` を使ってください。
    """
    path = character_path(category, dirname)
    if path is None:
        return "", 0
    view = chara_view(path)
    if view is None:
        print(f"  警告: {path.name} を画像として開けません。キャラ無しで組みます。",
              file=sys.stderr)
        return "", 0
    blob, disp_w, disp_h = view
    b64 = base64.b64encode(blob).decode("ascii")
    return (f'<img class="chara" src="data:image/png;base64,{b64}" alt="" '
            f'style="width:{disp_w}px;height:{disp_h}px">'), disp_w


def build_html(meta, dirname):
    t = THEMES.get(meta.get("category"), DEFAULT_THEME)
    title = meta.get("title") or dirname
    thumb = meta.get("thumb") or {}
    hook, main, sub = split_title(title)
    hook = thumb.get("hook", hook)
    main = thumb.get("main", main)
    sub = thumb.get("sub", sub)

    # 製品名は白いカードで横一列に置く(参考にした作りに合わせる)
    cards_src, budget = [], 30
    for x in (meta.get("tags") or []):
        x = str(x)
        if dwidth(x) + 3 > budget:
            break
        cards_src.append(x)
        budget -= dwidth(x) + 3
        if len(cards_src) >= 3:
            break
    cat = meta.get("category", "")
    e = htmlmod.escape

    chara, chara_w = character_img(cat, dirname)
    pat_key, tone = variant_for(dirname)
    pattern = PATTERNS[pat_key].format(a=t["accent"])
    bg1 = _mix(t["bg1"], t["chip"], tone["mix"])
    bg2 = _mix(t["bg2"], t["accent"], tone["mix"] * 0.6)

    # 使える横幅。左右パディング26px + キャラのぶんを引く
    avail = WIDTH - 2 * 26 - chara_w
    card_px = 30
    hook_px = size_for(hook, avail, 78, 52, 28, 1, 1.06)[0] if hook else 0

    # フック・カード・補足・フッターを引いた残りが主役の高さ
    used = 14 + 12                               # 上下パディング
    used += int(hook_px * 1.06) + 6 if hook else 0
    used += (card_px + 18 + 6) if cards_src else 0
    used += 34 + 6                               # フッター
    sub_px = size_for(sub, avail, 108, 38, 24, 2, 1.15)[0] if sub else 0
    used += int(sub_px * 1.15 * 2) + 6 if sub else 0
    main_h = max(170, HEIGHT - used)
    main_px, main_lines = size_for(main, avail, main_h, 150, 54)
    stroke_px = max(9, int(main_px * 0.13))
    # 縁の色。chip をそのまま使うと、黄色系のテーマで背景と同化して読めない。
    # 黒を混ぜて必ず背景より暗くする。
    stroke_col = _mix(t["chip"], "#000000", 0.42)

    faces = (font_face("NotoJP", "NotoSansJP-Black.ttf", 900)
             + font_face("NotoJP", "NotoSansJP-Regular.ttf", 400))

    cards = "".join(f'<span class="card">{e(x)}</span>' for x in cards_src)
    main_html = emphasize(main, [str(x) for x in (meta.get("tags") or [])], e)
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><style>
{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{WIDTH}px;height:{HEIGHT}px}}
body{{font-family:'NotoJP','IPAGothic',sans-serif;background:#000}}
.frame{{
  position:relative;width:{WIDTH}px;height:{HEIGHT}px;overflow:hidden;
  background:
    radial-gradient({tone['glow']}, {t['accent']}66 0%, transparent 56%),
    linear-gradient(135deg, {bg1} 0%, {bg2} 100%);
}}
/* 背景の柄。日付で切り替わる(PATTERNS) */
.pat{{position:absolute;inset:0;background:{pattern};pointer-events:none}}
/* 斜めの光沢。ギラつきを足す */
.shine{{
  position:absolute;inset:0;pointer-events:none;
  background:
    linear-gradient(108deg, transparent 30%, #ffffff26 42%, transparent 52%),
    linear-gradient(108deg, transparent 58%, #ffffff1a 66%, transparent 74%);
}}
.stack{{
  position:absolute;inset:0;z-index:3;
  padding:14px 26px 12px;display:flex;flex-direction:column;gap:8px;justify-content:center;
  padding-right:{26 + chara_w}px;
}}
/* 黄色の極太フック。黒の太縁で抜く */
.hook{{
  color:#ffe83d;font-weight:900;font-size:{hook_px}px;line-height:1.06;
  -webkit-text-stroke:11px #000;paint-order:stroke fill;
  filter:drop-shadow(0 0 12px #ffd21e) drop-shadow(0 4px 0 rgba(0,0,0,.5));
  letter-spacing:.01em;white-space:nowrap;overflow:hidden;
}}
/* 製品名の白カード。参考にした作りに合わせて横一列に */
.cards{{display:flex;gap:10px;align-items:center;overflow:hidden}}
.card{{
  background:#fff;color:#111;font-weight:900;font-size:{card_px}px;line-height:1;
  padding:9px 16px;border-radius:8px;white-space:nowrap;
  box-shadow:0 4px 0 rgba(0,0,0,.55);
}}
/* 主役。白抜き＋テーマ色の極太縁＋黒のフチ */
.main{{
  font-weight:900;font-size:{main_px}px;line-height:1.05;
  /* 塗りは白。内側に暗い縁を入れ、外側に白フチ＋発光を足す。
     background-clip:text でグラデーションにすると、太い text-stroke と
     干渉して文字が潰れる(実測)。塗りは単色に留める。 */
  color:#fff;
  -webkit-text-stroke:{stroke_px}px {stroke_col};paint-order:stroke fill;
  /* 外側に白のフチを4方向から。さらにテーマ色で発光させる */
  filter:
    drop-shadow(3px 0 0 #fff) drop-shadow(-3px 0 0 #fff)
    drop-shadow(0 3px 0 #fff) drop-shadow(0 -3px 0 #fff)
    drop-shadow(0 0 22px {t['accent']}) drop-shadow(0 0 44px {t['accent']})
    drop-shadow(0 8px 2px rgba(0,0,0,.6));
  overflow-wrap:anywhere;letter-spacing:-.01em;
  display:-webkit-box;-webkit-line-clamp:{main_lines};-webkit-box-orient:vertical;overflow:hidden;
}}
.main em{{font-style:normal;color:#ffe83d}}
/* 補足。白＋黒縁 */
/* 補足。背景が明るいと白文字が負けるので、暗い下地を敷く */
.sub{{
  color:#fff;font-weight:900;font-size:{sub_px}px;line-height:1.5;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;
}}
.sub b{{
  font-weight:900;background:rgba(0,0,0,.62);
  padding:2px 10px;border-radius:4px;
  box-decoration-break:clone;-webkit-box-decoration-break:clone;
}}
.foot{{
  position:absolute;left:26px;bottom:12px;display:flex;align-items:center;gap:12px;
}}
.cat{{
  background:{t['chip']};color:#fff;font-weight:900;font-size:22px;
  padding:6px 16px;border-radius:6px;white-space:nowrap;
  box-shadow:0 3px 0 rgba(0,0,0,.5);
}}
.site{{color:#ffffffbb;font-weight:900;font-size:19px;letter-spacing:.04em;white-space:nowrap}}
/* 大きさは画像ごとに決まるので style 属性で入れる(fit_chara) */
.chara{{position:absolute;right:10px;bottom:0;z-index:2;object-fit:contain}}
</style></head><body><div class="frame">
  <div class="pat"></div>
  <div class="shine"></div>
  {chara}
  <div class="stack">
    {f'<div class="hook">{e(hook)}</div>' if hook else ''}
    {f'<div class="cards">{cards}</div>' if cards else ''}
    <div class="main">{main_html}</div>
    {f'<div class="sub"><b>{e(sub)}</b></div>' if sub else ''}
    <div class="foot"><span class="cat">{e(cat)}</span><span class="site">AIニュース デイリーダイジェスト</span></div>
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
