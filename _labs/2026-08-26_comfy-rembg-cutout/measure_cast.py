"""切り直した cast/ 80枚を測り直して、服・髪の穴を数える。

穴の定義（これまでの失敗を踏まえた最終形）:
  - 元画像が明るい(>55)のに透明になっている画素
  - その連結成分が400px以上（髪のフチの光のような点を落とす）
  - 成分の上端が、不透明部分の外接矩形の上から CHARA_CROP 以内
    （サムネに出るのは上から58%。脚・ズボンは運営者の判断で許容）
  - **浮いている装飾は除く**。aoi/sleepy の白い泡と hinata/celebrate の
    金の紙吹雪は、drop_islands が正しく消したもの。絵を開いて確認済み
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path("/home/user/ai-news-dev")
sys.path.insert(0, str(ROOT))
from _render_thumbs import CHARA_CROP  # noqa: E402

REVIEW = ROOT / "_assets/character/_review"
CAST = ROOT / "_assets/character/cast"
BRIGHT, MIN_PX = 55, 400
DECOR = {("aoi", "sleepy"), ("hinata", "celebrate")}


def locate(cut_rgb, op, full):
    oh, ow = full.shape[:2]
    ch, cw = op.shape
    ys_, xs_ = np.nonzero(op)
    if len(ys_) > 4000:
        sel = np.linspace(0, len(ys_) - 1, 4000).astype(int)
        ys_, xs_ = ys_[sel], xs_[sel]
    ref = cut_rgb[ys_, xs_].astype(np.int32)
    best, bxy = None, (0, 0)
    for step in (4, 1):
        yr = (range(0, oh - ch + 1, 4) if step == 4
              else range(max(0, bxy[0] - 4), min(oh - ch, bxy[0] + 4) + 1))
        xr = (range(0, ow - cw + 1, 4) if step == 4
              else range(max(0, bxy[1] - 4), min(ow - cw, bxy[1] + 4) + 1))
        for oy in yr:
            for ox in xr:
                d = np.abs(full[ys_ + oy, xs_ + ox, :3].astype(np.int32) - ref).mean()
                if best is None or d < best:
                    best, bxy = d, (oy, ox)
    return bxy, best


rows = []
for src in sorted(REVIEW.glob("*/*.png")):
    who, pose = src.parent.name, src.stem
    cf = CAST / who / f"{pose}.png"
    if not cf.exists():
        print(f"  cast に無い: {who}/{pose}")
        continue
    full = np.asarray(Image.open(src).convert("RGB"))
    v = full.astype(np.int16).max(axis=2)
    cut = np.asarray(Image.open(cf).convert("RGBA"))
    a = cut[:, :, 3]
    (oy, ox), err = locate(cut[:, :, :3], a >= 200, full)
    win = v[oy:oy + a.shape[0], ox:ox + a.shape[1]]
    m = (a < 8) & (win > BRIGHT)
    limit = a.shape[0] * CHARA_CROP
    lab, n = ndimage.label(m, structure=np.ones((3, 3), int))
    hs = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        s = int((lab[sl] == i).sum())
        if s >= MIN_PX and sl[0].start < limit:
            hs.append((s, int(sl[0].start), int(sl[1].start)))
    # **色も見る。** alpha だけ見ていたせいで、戻した髪が真っ黒なまま
    # 「穴は解消」と報告した(2026/8/26)。不透明画素のRGBが元画像と
    # 一致しているかを必ず併記する。
    win_rgb = full[oy:oy + a.shape[0], ox:ox + a.shape[1]].astype(int)
    op = a >= 200
    rgbd = float(np.abs(cut[:, :, :3].astype(int) - win_rgb).sum(axis=2)[op].mean())
    rows.append((who, pose, sorted(hs, reverse=True), err, rgbd))

print(f"BRIGHT={BRIGHT} MIN_PX={MIN_PX} CHARA_CROP={CHARA_CROP}"
      f"  ({len(rows)}枚)\n")
bad = [r for r in rows if r[2]]
real = [r for r in bad if (r[0], r[1]) not in DECOR]
print(f"検出された穴: {len(bad)}枚")
print(f"うち装飾(正しく消したもの)を除いた**本当の穴**: {len(real)}枚\n")
for who, pose, hs, err, rgbd in sorted(bad, key=lambda r: -sum(h[0] for h in r[2])):
    tag = "装飾（除外）" if (who, pose) in DECOR else "★ 服・髪の穴"
    print(f"  {who}/{pose:11} {sum(h[0] for h in hs):7}px  {tag}"
          f"  " + " ".join(f"{s}px(y{y},x{x})" for s, y, x in hs))
print(f"\n位置合わせ誤差の最大 {max(r[3] for r in rows):.1f}")
worst = sorted(rows, key=lambda r: -r[4])[:6]
print(f"\n不透明画素のRGBが元画像とどれだけ違うか（大きいと色が壊れている）")
print(f"{'対象':22}{'平均RGB差':>12}")
for who, pose, hs, err, rgbd in worst:
    print(f"{who + '/' + pose:22}{rgbd:12.2f}")
print(f"全80枚の最大 {max(r[4] for r in rows):.2f} / 中央値 "
      f"{sorted(r[4] for r in rows)[len(rows)//2]:.2f}"
      f"  ← 2前後なら正常（縁のアンチエイリアス処理ぶん）")
