"""合成のしきい値を固定値で振って比べる。

union2.py の「背景から自動で決める」は失敗した。理由がはっきりしている:
**birefnet が消してしまった髪も、外周から繋がった透明領域に入る**ので、
背景の見本に金髪(明るさ254)が混ざり、しきい値が266まで上がった。
自分の誤りを見本にして自分を直そうとしていた（循環）。

なので固定値で振って、
  ・穴がいくつ残るか
  ・戻した画素が何px か
  ・戻した画素のうち「暗めのもの」が何px か（背景を巻き込んだ疑い）
を並べて、目で見る候補を絞る。
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
THRS = [55, 70, 85, 100, 120, 150]
DECOR = {("aoi", "sleepy", 204, 160), ("hinata", "celebrate", 289, 746)}


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


cache = []
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
    cache.append((who, pose, v, ab, np.load(f)))

base = {(w, p): holes(ab, v, w, p) for w, p, v, ab, ai in cache}
nb = sum(1 for h in base.values() if h)
print(f"birefnetのみ: 服に穴 {nb}枚 / "
      f"{sum(sum(x[0] for x in h) for h in base.values())}px（装飾2件は除外済み）\n")
print(f"{'しきい値':>8}{'穴の枚数':>10}{'穴の総面積':>12}{'戻した画素':>12}"
      f"{'うち明るさ100未満':>18}")
detail = {}
for thr in THRS:
    n = tot = added = dim = 0
    d = []
    for who, pose, v, ab, ai in cache:
        m = (ai >= 8) & (ab < 8) & (v > thr)
        au = ab.copy()
        au[m] = ai[m]
        h = holes(au, v, who, pose)
        if h:
            n += 1
            tot += sum(x[0] for x in h)
            d.append((who, pose, sum(x[0] for x in h)))
        added += int(m.sum())
        dim += int((m & (v < 100)).sum())
    detail[thr] = d
    print(f"{thr:8}{n:10}{tot:12}{added:12}{dim:18}")

print("\n各しきい値で穴が残る絵")
for thr in THRS:
    print(f"  {thr:3}: " + ("、".join(f"{w}/{p} {s}px" for w, p, s in detail[thr])
                            or "なし"))
