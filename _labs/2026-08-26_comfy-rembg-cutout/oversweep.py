"""union2.py / union3.py / model_diff.py が import する locate() の置き場。

元は探索用スクリプト oversweep.py の中にあった関数で、ここには
このラボの再実行に要る locate() だけを残している。
"""
import numpy as np


def locate(cut_rgb, op, full):
    """切り抜きが元画像のどこから切られたか(間引き総当たり→精密化)。"""
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
    return bxy, best
