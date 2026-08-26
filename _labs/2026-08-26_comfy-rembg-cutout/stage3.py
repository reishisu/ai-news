"""腕の下が食われるのは、どの段の仕業か。段ごとに測る。

段は cut_out() と同じ順:
    rembg → dark_assist / chroma_assist → drop_islands → repair_holes
「その段で新たに透明にした、元が明るい(>55)画素」を数える。
"""
import io, sys, contextlib
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path("/home/user/ai-news-dev"); sys.path.insert(0, str(ROOT))
import rembg
import _prepare_character as pc
REVIEW = ROOT / "_assets/character/_review"
SPECS = ["hinata/stop", "hinata/smug", "shirase/smug", "kotoha/angry"]
BRIGHT = 55
S = {}
def sess(n):
    if n not in S: S[n] = pc.rembg_session(n)
    return S[n]
print(f"{'対象':18}{'rembgで欠け':>13}{'+補助':>10}{'+drop_islands':>15}{'-repair':>10}")
for spec in SPECS:
    who, pose = spec.split("/")
    im = Image.open(REVIEW / who / f"{pose}.png").convert("RGBA")
    rgb = np.asarray(im.convert("RGB"))
    v = rgb.astype(np.int16).max(axis=2)
    bright = v > BRIGHT
    with contextlib.redirect_stdout(io.StringIO()):
        o0 = rembg.remove(im, session=sess("birefnet-general-lite"))
        a0 = np.asarray(o0)[:, :, 3]
        o1 = (pc.dark_assist(o0, im) if pc.is_dark_bg(im) else pc.chroma_assist(o0, im))[0]
        a1 = np.asarray(o1)[:, :, 3]
        o2, _ = pc.drop_islands(o1)
        a2 = np.asarray(o2)[:, :, 3]
        o3, healed = pc.repair_holes(o2, im)
        a3 = np.asarray(o3)[:, :, 3]
    print(f"{spec:18}{int(((a0<8)&bright).sum()):13}"
          f"{int(((a1<8)&(a0>=8)&bright).sum()):10}"
          f"{int(((a2<8)&(a1>=8)&bright).sum()):15}"
          f"{healed:10}")
