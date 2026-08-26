"""dark_assist の広がりに上限を付けたら、何が残って何が消えるかを測る。

いまは「暗い限り無制限」に広がるので、rembg の透明領域に接している
キャラの暗い部分（黒いショートパンツ、腕の下の影、髪の輪郭線）を
繋がっている先まで全部辿ってしまう。

上限を N 段にして、
  ・消える画素数
  ・**キャラの内側**で消える画素数（悪い方。外接矩形を25px縮めた中）
を距離ごとに出す。無制限との差が、取り戻せる量。
"""
import io, sys, contextlib
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path("/home/user/ai-news-dev"); sys.path.insert(0, str(ROOT))
import rembg, _prepare_character as pc
REVIEW = ROOT / "_assets/character/_review"
SPECS = ["hinata/stop", "hinata/smug", "kotoha/angry", "aoi/angry", "shirase/ok"]
LIMITS = [2, 4, 8, 16, 32, None]
S = {}
def sess(n):
    if n not in S: S[n] = pc.rembg_session(n)
    return S[n]

def grow_n(out, src, thr=46, limit=None):
    a = np.asarray(src.convert("RGB"), dtype=np.int16)
    dark = a.max(axis=2) < thr
    rgba = np.asarray(out.convert("RGBA"))
    seed = (rgba[:, :, 3] == 0)
    seed[0, :] |= dark[0, :]; seed[-1, :] |= dark[-1, :]
    seed[:, 0] |= dark[:, 0]; seed[:, -1] |= dark[:, -1]
    grown = seed
    step = 0
    while limit is None or step < limit:
        nxt = (grown
               | (np.roll(grown, 1, 0) & dark) | (np.roll(grown, -1, 0) & dark)
               | (np.roll(grown, 1, 1) & dark) | (np.roll(grown, -1, 1) & dark))
        if nxt.sum() == grown.sum(): break
        grown = nxt; step += 1
    return grown & (rgba[:, :, 3] > 0)

print(f"{'対象':16}" + "".join(f"{('無制限' if L is None else str(L)+'段'):>12}" for L in LIMITS))
print("  （上段=消す画素 / 下段=うちキャラ内側）")
for spec in SPECS:
    who, pose = spec.split("/")
    im = Image.open(REVIEW / who / f"{pose}.png").convert("RGBA")
    with contextlib.redirect_stdout(io.StringIO()):
        o0 = rembg.remove(im, session=sess("birefnet-general-lite"))
    a0 = np.asarray(o0)[:, :, 3]
    ys, xs = np.nonzero(a0 >= 8)
    ins = np.zeros(a0.shape, bool)
    ins[ys.min()+25:ys.max()-25, xs.min()+25:xs.max()-25] = True
    tot, inn = [], []
    for L in LIMITS:
        g = grow_n(o0, im, limit=L)
        tot.append(int(g.sum())); inn.append(int((g & ins).sum()))
    print(f"{spec:16}" + "".join(f"{t:12}" for t in tot))
    print(f"{'':16}" + "".join(f"{i:12}" for i in inn))
