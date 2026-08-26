"""2つのモデルの結果を**直接引き算**して比べる。

model_ab2.py の「取り残し背景」は、実は指標として弱い。
「不透明・元が暗い・外周から届かない」を数えているので、
**黒い線画と暗い髪の内側まで数えてしまう**（1枚あたり1万画素前後という
大きな数字は、ほぼこれ）。両モデルで同じだけ混ざるので差は意味を持つが、
絶対値は読み違えのもとなので、こちらで測り直す。

ここでは**片方だけが違う判断をした画素**だけを見る:

  isnetが残した背景 … isnet は不透明 / birefnet は透明 / 元が暗い(<=40)
                      ＝ birefnet が消せた背景を isnet が残した
  isnetが余分に消した … isnet は透明 / birefnet は不透明 / 元が明るい(>55)
                      ＝ birefnet が残せたキャラを isnet が消した

どちらも「相手を正解とみなす」相対的な指標だが、
**どちらの絵を選ぶと何が増えて何が減るか**は、これで正確に出る。
"""
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
from oversweep import locate  # noqa: E402

REVIEW = ROOT / "_assets/character/_review"
CAST = ROOT / "_assets/character/cast"
NPY = SCR / "isnet_alpha"
BRIGHT, DARKBG, MIN_PX = 55, 40, 400


def blobs(mask, limit=None):
    """MIN_PX以上の塊。limit を渡すと、上端がそれより上のものだけ返す。"""
    lab, n = ndimage.label(mask, structure=np.ones((3, 3), int))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        s = int((lab[sl] == i).sum())
        if s >= MIN_PX and (limit is None or sl[0].start < limit):
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

    ys, xs = np.nonzero(ab >= 8)
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    limit = y0 + (y1 - y0) * CHARA_CROP

    left = (ai >= 8) & (ab < 8) & (v <= DARKBG)      # isnet が残した背景
    over = (ai < 8) & (ab >= 8) & (v > BRIGHT)       # isnet が余分に消したキャラ
    rows.append((who, pose, int(left.sum()), blobs(left),
                 int(over.sum()), blobs(over, limit)))

print(f"BRIGHT={BRIGHT} DARKBG={DARKBG} MIN_PX={MIN_PX}"
      f"  ({len(rows)}枚を比較)\n")
print("isnet-anime を birefnet と比べたときの差分（画素）")
print(f"{'対象':22}{'残した背景':>12}{'塊':>5}{'余分に消したキャラ':>20}{'塊(可視域)':>12}")
tl = to = 0
for who, pose, l, lb, o, ob in sorted(rows, key=lambda r: -(r[2] + r[4])):
    tl += l; to += o
    if l + o < 300:
        continue
    print(f"{who + '/' + pose:22}{l:12}{len(lb):5}{o:20}{len(ob):12}")
print(f"\n合計: 残した背景 {tl}px / 余分に消したキャラ {to}px")
print(f"400px以上の塊を持つ枚数: 残し {sum(1 for r in rows if r[3])}枚 / "
      f"消し過ぎ {sum(1 for r in rows if r[5])}枚")

print("\n-- 塊の中身（400px以上のものだけ）--")
for who, pose, l, lb, o, ob in sorted(rows, key=lambda r: -(r[2] + r[4])):
    if not lb and not ob:
        continue
    print(f"{who}/{pose}")
    for s, y, x in lb[:4]:
        print(f"    残した背景   {s:7}px  (y{y},x{x})")
    for s, y, x in ob[:4]:
        print(f"    消し過ぎ★   {s:7}px  (y{y},x{x})  ← サムネに出る範囲")
