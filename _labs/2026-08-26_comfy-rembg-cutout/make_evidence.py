"""記事に載せる前後比較画像を、git履歴の実物から組み立てる。

すべて実データ。加工は「マゼンタ合成・切り出し・拡大・ラベル」だけで、
画素の中身には手を入れない。

  ev_severed_hair.png   … birefnet がツインテールを消した(a649572) → isnet補完で復元(現在)
  ev_black_hair.png     … alpha だけ戻して髪が真っ黒になった事故(セッション中の実写)
  ev_shadow.png         … dark_assist が腕の下の影を食った(bb1bb74) → max_grow=4 で復元(現在)
  ev_darkeat.png        … 無制限の dark_assist が消していた画素(緑)の可視化

使い方: リポジトリ直下で  python3 _labs/2026-08-26_comfy-rembg-cutout/make_evidence.py
(修正前の cast は `git show <コミット>:<パス>` で取り出す)
"""
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "contents/2026-08-26_comfy-rembg-cutout/images"
FONT = str(ROOT / "_assets/fonts/NotoSansJP-Black.ttf")
MAG = (255, 0, 255)
REVIEW = ROOT / "_assets/character/_review"
CAST = ROOT / "_assets/character/cast"


def from_git(commit, path):
    b = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"],
                       capture_output=True, check=True).stdout
    return Image.open(BytesIO(b)).convert("RGBA")


def locate(cut_rgb, op, full):
    """cast が元画像のどこから切られたか(総当たり→精密化)。"""
    oh, ow = full.shape[:2]
    ch, cw = op.shape
    ys, xs = np.nonzero(op)
    if len(ys) > 4000:
        sel = np.linspace(0, len(ys) - 1, 4000).astype(int)
        ys, xs = ys[sel], xs[sel]
    ref = cut_rgb[ys, xs].astype(np.int32)
    best, bxy = None, (0, 0)
    for step in (4, 1):
        yr = (range(0, oh - ch + 1, 4) if step == 4
              else range(max(0, bxy[0] - 4), min(oh - ch, bxy[0] + 4) + 1))
        xr = (range(0, ow - cw + 1, 4) if step == 4
              else range(max(0, bxy[1] - 4), min(ow - cw, bxy[1] + 4) + 1))
        for oy in yr:
            for ox in xr:
                d = np.abs(full[ys + oy, xs + ox, :3].astype(np.int32) - ref).mean()
                if best is None or d < best:
                    best, bxy = d, (oy, ox)
    return bxy


def on_canvas(cast_img, full):
    """cast をフルサイズ座標に戻した RGBA 配列。"""
    arr = np.asarray(cast_img)
    oy, ox = locate(arr[:, :, :3], arr[:, :, 3] >= 200, full)
    canvas = np.zeros((full.shape[0], full.shape[1], 4), np.uint8)
    canvas[oy:oy + arr.shape[0], ox:ox + arr.shape[1]] = arr
    return canvas


def magenta(rgba, full=None):
    """透明をマゼンタで塗ったRGB。full を渡すと元画像を返す(比較の左端用)。"""
    if full is not None:
        return full.copy()
    rgb = rgba[:, :, :3].copy()
    rgb[rgba[:, :, 3] < 8] = MAG
    return rgb


def panel_row(title, tiles, out, tw=380):
    """[(ラベル, ndarray)] を横に並べ、上に見出しを置いて保存。"""
    font = ImageFont.truetype(FONT, 22)
    small = ImageFont.truetype(FONT, 18)
    h, w = tiles[0][1].shape[:2]
    th = int(h * tw / w)
    pad, head, cap = 10, 44, 30
    cv = Image.new("RGB", (tw * len(tiles) + pad * (len(tiles) + 1),
                           th + head + cap + pad), (24, 25, 30))
    d = ImageDraw.Draw(cv)
    d.text((pad, 10), title, font=font, fill=(240, 242, 246))
    for i, (name, arr) in enumerate(tiles):
        x = pad + i * (tw + pad)
        cv.paste(Image.fromarray(arr).resize((tw, th), Image.LANCZOS), (x, head))
        d.text((x, head + th + 4), name, font=small, fill=(196, 200, 210))
    cv.save(out)
    print(out, cv.size, f"{out.stat().st_size // 1024}KB")


OUT.mkdir(parents=True, exist_ok=True)

# 1. birefnet がツインテールを消した → isnet 補完で復元
full = np.asarray(Image.open(REVIEW / "hinata/sleepy.png").convert("RGB"))
old = on_canvas(from_git("a649572", "_assets/character/cast/hinata/sleepy.png"), full)
new = on_canvas(Image.open(CAST / "hinata/sleepy.png").convert("RGBA"), full)
box = (slice(470, 1010), slice(0, 200))
panel_row("hinata/sleepy 左のツインテール（マゼンタ＝透明）",
          [("元画像", full[box]),
           ("birefnetのみ(修正前)", magenta(old)[box]),
           ("isnetで補完(修正後)", magenta(new)[box])],
          OUT / "ev_severed_hair.png", tw=300)

# 2. alpha だけ戻して髪が真っ黒になった事故(セッション中の実写を結合)
S = Path("/tmp/claude-0/-home-user/e21de159-f2ef-5fc4-bbe2-6bbc29ef3d0d/scratchpad")
if (S / "real_sleepy.png").exists():
    bad = Image.open(S / "real_sleepy.png")
    good = Image.open(S / "fixed_sleepy.png")
    font = ImageFont.truetype(FONT, 22)
    small = ImageFont.truetype(FONT, 18)
    tw = 330
    th = int(bad.height * tw / bad.width)
    pad, head, cap = 10, 44, 30
    cv = Image.new("RGB", (tw * 2 + pad * 3, th + head + cap + pad), (24, 25, 30))
    d = ImageDraw.Draw(cv)
    d.text((pad, 10), "isnet から alpha だけ戻した結果（左）と、RGBも戻した結果（右）",
           font=font, fill=(240, 242, 246))
    for i, (name, im) in enumerate([("alphaのみ: 髪が真っ黒", bad),
                                    ("RGBも元画像から戻す", good)]):
        x = pad + i * (tw + pad)
        cv.paste(im.resize((tw, th), Image.LANCZOS), (x, head))
        d.text((x, head + th + 4), name, font=small, fill=(196, 200, 210))
    cv.save(OUT / "ev_black_hair.png")
    print(OUT / "ev_black_hair.png", cv.size,
          f"{(OUT / 'ev_black_hair.png').stat().st_size // 1024}KB")
else:
    print("注意: 黒髪事故のスクリーンショットが見つからない(セッション外での再実行)")

# 3. dark_assist が腕の下の影を食った → max_grow=4 で復元
full2 = np.asarray(Image.open(REVIEW / "hinata/stop.png").convert("RGB"))
old2 = on_canvas(from_git("bb1bb74", "_assets/character/cast/hinata/stop.png"), full2)
new2 = on_canvas(Image.open(CAST / "hinata/stop.png").convert("RGBA"), full2)
box2 = (slice(600, 830), slice(80, 780))
font = ImageFont.truetype(FONT, 22)
small = ImageFont.truetype(FONT, 18)
tiles = [("修正前: 影が抜けてギザギザ", magenta(old2)[box2]),
         ("修正後: 影が残る", magenta(new2)[box2])]
tw2 = 700
h, w = tiles[0][1].shape[:2]
th2 = int(h * tw2 / w)
pad, head, cap = 10, 44, 30
cv = Image.new("RGB", (tw2 + pad * 2, (th2 + cap) * 2 + head + pad), (24, 25, 30))
d = ImageDraw.Draw(cv)
d.text((pad, 10), "hinata/stop 組んだ腕の下（マゼンタ＝透明）", font=font, fill=(240, 242, 246))
y = head
for name, arr in tiles:
    cv.paste(Image.fromarray(arr).resize((tw2, th2), Image.LANCZOS), (pad, y))
    d.text((pad, y + th2 + 2), name, font=small, fill=(196, 200, 210))
    y += th2 + cap
cv.save(OUT / "ev_shadow.png")
print(OUT / "ev_shadow.png", cv.size, f"{(OUT / 'ev_shadow.png').stat().st_size // 1024}KB")

# 4. 無制限 dark_assist が消していた画素(緑)
if (S / "darkeat/hinata_stop.png").exists():
    im = Image.open(S / "darkeat/hinata_stop.png")
    im.save(OUT / "ev_darkeat.png")
    print(OUT / "ev_darkeat.png", im.size,
          f"{(OUT / 'ev_darkeat.png').stat().st_size // 1024}KB")
else:
    print("注意: darkeat の可視化が見つからない(セッション外での再実行)")
