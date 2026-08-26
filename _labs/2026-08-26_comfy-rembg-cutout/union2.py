"""合成の「明るい」のしきい値を、絵ごとに背景から決め直す。

union.py（固定 BRIGHT=55）で hinata/money を開いたら、**背景の焦げ茶が戻っていた**。
その絵の背景は真っ黒ではなく、最大チャンネルが60前後ある。55では足りない。

そこで、しきい値を**その絵の背景の明るさから決める**:

  背景の見本 … birefnet が透明にした画素のうち、外周から繋がっているもの。
                （birefnet は「囲まれた背景」以外は正しく抜けている。実測済み）
  しきい値   … その見本の99.5パーセンタイル + 12。下限は55。

こうすると、背景が黒の絵では従来どおり55前後、焦げ茶の絵では自動で上がる。
"""
import contextlib
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path("/home/user/ai-news-dev")
SCR = Path(".")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCR))
from _render_thumbs import CHARA_CROP  # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    from oversweep import locate  # noqa: E402

REVIEW = ROOT / "_assets/character/_review"
CAST = ROOT / "_assets/character/cast"
NPY = SCR / "isnet_alpha"
DETECT, MIN_PX = 55, 400
DECOR = {("aoi", "sleepy", 204, 160), ("hinata", "celebrate", 289, 746)}


def bg_threshold(ab, v):
    """外周から繋がっている透明画素＝確実な背景。その明るさの上側から決める。"""
    trans = ab < 8
    lab, n = ndimage.label(trans, structure=np.ones((3, 3), int))
    if not n:
        return DETECT, 0
    edge = set(np.unique(np.concatenate(
        [lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    m = np.isin(lab, list(edge))
    if m.sum() < 1000:
        return DETECT, 0
    p = float(np.percentile(v[m], 99.5))
    return max(DETECT, p + 12), p


def holes(a, v, who, pose):
    ys, xs = np.nonzero(a >= 8)
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    m = np.zeros_like(a, bool)
    m[y0:y1, x0:x1] = ((a < 8) & (v > DETECT))[y0:y1, x0:x1]
    limit = y0 + (y1 - y0) * CHARA_CROP
    lab, n = ndimage.label(m, structure=np.ones((3, 3), int))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        s = int((lab[sl] == i).sum())
        if s >= MIN_PX and sl[0].start < limit \
                and (who, pose, int(sl[0].start), int(sl[1].start)) not in DECOR:
            out.append((s, int(sl[0].start), int(sl[1].start)))
    return sorted(out, reverse=True)


rows = []
for src in sorted(REVIEW.glob("*/*.png")):
    who, pose = src.parent.name, src.stem
    f = NPY / f"{who}_{pose}.npy"
    if not f.exists():
        continue
    full = np.asarray(Image.open(src).convert("RGB"))
    v = full.astype(np.int16).max(axis=2)
    cut = np.asarray(Image.open(CAST / who / f"{pose}.png").convert("RGBA"))
    ca = cut[:, :, 3]
    (oy, ox), _ = locate(cut[:, :, :3], ca >= 200, full)
    ab = np.zeros(full.shape[:2], np.uint8)
    ab[oy:oy + ca.shape[0], ox:ox + ca.shape[1]] = ca
    ai = np.load(f)
    thr, p995 = bg_threshold(ab, v)
    add = (ai >= 8) & (ab < 8) & (v > thr)
    au = ab.copy()
    au[add] = ai[add]
    rows.append((who, pose, thr, p995, holes(ab, v, who, pose),
                 holes(au, v, who, pose), int(add.sum())))

nb = sum(1 for r in rows if r[4])
nu = sum(1 for r in rows if r[5])
print(f"背景から決めたしきい値（{len(rows)}枚）\n")
print(f"服に穴のある枚数:  birefnetのみ {nb}枚 → 合成 {nu}枚")
print(f"穴の総面積:        {sum(sum(h[0] for h in r[4]) for r in rows)}px"
      f" → {sum(sum(h[0] for h in r[5]) for r in rows)}px")
print(f"戻した画素の合計:  {sum(r[6] for r in rows)}px\n")

print("しきい値が上がった絵（背景が真っ黒でないもの）")
print(f"{'対象':22}{'背景99.5%':>12}{'しきい値':>10}{'戻した':>10}")
for who, pose, thr, p, hb, hu, added in sorted(rows, key=lambda r: -r[2])[:12]:
    print(f"{who + '/' + pose:22}{p:12.0f}{thr:10.0f}{added:10}")

print("\n穴の増減")
print(f"{'対象':22}{'birefnetのみ':>14}{'合成後':>12}")
for who, pose, thr, p, hb, hu, added in sorted(
        rows, key=lambda r: -sum(h[0] for h in r[4])):
    if not hb and not hu:
        continue
    print(f"{who + '/' + pose:22}{sum(h[0] for h in hb):10}px{sum(h[0] for h in hu):10}px"
          + ("   ← 解消" if hb and not hu else ""))
