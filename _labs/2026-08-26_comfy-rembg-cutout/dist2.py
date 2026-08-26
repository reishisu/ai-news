"""drop_islands が消している塊の「大きさ」と「本体からの距離」を測り直す。

near_px=30 を入れたのに、腕の下のジャケットが消えている。
30px より遠いということなので、実際の距離を出す。
装飾（前回の実測で50〜110px）と分けられるかも同時に見る。
"""
import io, sys, contextlib
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT = Path("/home/user/ai-news-dev"); sys.path.insert(0, str(ROOT))
import rembg, _prepare_character as pc
REVIEW = ROOT / "_assets/character/_review"
SPECS = ["hinata/stop", "hinata/smug", "kotoha/angry", "aoi/angry",
         "kurumi/think", "hinata/celebrate", "aoi/sleepy"]
S = {}
def sess(n):
    if n not in S: S[n] = pc.rembg_session(n)
    return S[n]
print(f"{'対象':18}{'塊px':>8}{'本体比':>8}{'距離':>7}{'明るさ中央':>11}  判定")
for spec in SPECS:
    who, pose = spec.split("/")
    im = Image.open(REVIEW / who / f"{pose}.png").convert("RGBA")
    v = np.asarray(im.convert("RGB")).astype(np.int16).max(axis=2)
    with contextlib.redirect_stdout(io.StringIO()):
        o = rembg.remove(im, session=sess("birefnet-general-lite"))
        o = (pc.dark_assist(o, im) if pc.is_dark_bg(im) else pc.chroma_assist(o, im))[0]
    a = np.asarray(o)[:, :, 3]
    lab, n = ndimage.label(a > 16)
    if n <= 1:
        print(f"{spec:18}  塊は1つだけ"); continue
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    main = int(np.argmax(sizes)) + 1
    dist = ndimage.distance_transform_edt(lab != main)
    for i in range(1, n + 1):
        if i == main: continue
        m = lab == i
        s = int(m.sum())
        if s < 300: continue
        ratio = s / sizes[main - 1]
        d = float(dist[m].min())
        kept = (ratio >= 0.05) or (d <= 30)
        print(f"{spec:18}{s:8}{ratio*100:7.1f}%{d:7.1f}{np.median(v[m]):11.0f}"
              f"  {'残る' if kept else '**消される**'}")
