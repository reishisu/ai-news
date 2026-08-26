"""drop_islands が消している塊の「大きさ」と「本体からの距離」を測る。

docstring は「本体から離れた小さな塊」を消すと書いているが、実装は
**大きさしか見ていない**。装飾マーク(キラキラ)と、切れてしまった髪の先を
分けるには距離が要る。両方を測って、しきい値を決める材料にする。
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path("/home/user/ai-news-dev")
sys.path.insert(0, str(ROOT))
import _prepare_character as pc  # noqa: E402
from rembg import new_session, remove  # noqa: E402

SPECS = ["hinata/sleepy", "kotoha/thumbsup", "kotoha/panic", "hinata/money",
         "shirase/ok", "shirase/celebrate", "hinata/celebrate", "aoi/sleepy",
         "kurumi/sleepy", "kotoha/smug", "hinata/ok", "aoi/wave"]
sess = new_session("birefnet-general-lite")

print(f"{'対象':22}{'塊#':>4}{'画素':>8}{'本体比':>8}{'本体との距離':>13}{'元の明るさ中央':>15}")
for spec in SPECS:
    who, pose = spec.split("/")
    im = Image.open(ROOT / f"_assets/character/_review/{who}/{pose}.png").convert("RGBA")
    src = np.asarray(im.convert("RGB")).astype(np.int16)
    a = np.asarray(remove(im, session=sess))[:, :, 3]
    o, _ = pc.dark_assist(Image.fromarray(np.dstack([src.astype(np.uint8), a])), im)
    a = np.asarray(o)[:, :, 3]
    lab, n = ndimage.label(a > 16)
    if n <= 1:
        print(f"{spec:22}  塊は1つだけ")
        continue
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    main = int(np.argmax(sizes)) + 1
    # 本体からの距離マップ
    dist = ndimage.distance_transform_edt(lab != main)
    for i in range(1, n + 1):
        if i == main:
            continue
        m = lab == i
        s = int(m.sum())
        if s < 200:                       # 200px未満は本物のキラキラ候補。数だけ見る
            continue
        ratio = s / sizes[main - 1]
        d = float(dist[m].min())
        v = float(np.median(src[m].max(axis=1)))
        kept = "残す" if ratio >= 0.05 else "**消される**"
        print(f"{spec:22}{i:4}{s:8}{ratio*100:7.1f}%{d:13.1f}{v:15.0f}  {kept}")
