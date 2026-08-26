"""(1)どの段で欠けるかを段階別に測る (2)モデルを替えて比べる。

段は cut_out() と同じ順:
    rembg → dark_assist(黒背景のとき) → drop_islands

比べる指標は2つ。**両方見ないと判断できない**:
    欠け  … 元が明るい(>55)のに透明にした画素数。少ないほど良い
    残り  … 「囲まれた背景」で、元が暗い(<=40)のに不透明のまま残した画素数。
            少ないほど良い（isnet-anime はここが弱いと社内コメントにある）
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/user/ai-news-dev")
sys.path.insert(0, str(ROOT))
import _prepare_character as pc  # noqa: E402
from rembg import new_session, remove  # noqa: E402

SPECS = ["hinata/sleepy", "shirase/ok", "kotoha/thumbsup", "kotoha/panic",
         "hinata/money", "shirase/celebrate"]
MODELS = ["birefnet-general-lite", "isnet-anime", "u2net"]
BRIGHT, DARKBG = 55, 40


def enclosed_dark(alpha, src):
    """外周から届かないのに不透明のまま残っている、暗い画素（＝取り残した背景）"""
    from collections import deque
    h, w = alpha.shape
    opaque = alpha >= 8
    dark = src.max(axis=2) <= DARKBG
    cand = opaque & dark
    # 外周に繋がる不透明な暗い画素は「キャラの暗部が外に接している」なので除く
    seen = np.zeros_like(cand)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if cand[y, x] and not seen[y, x]:
                seen[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if cand[y, x] and not seen[y, x]:
                seen[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and cand[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; q.append((ny, nx))
    return int((cand & ~seen).sum())


print("=== 段階別（現行モデル birefnet-general-lite）===")
sess = {m: None for m in MODELS}
sess["birefnet-general-lite"] = new_session("birefnet-general-lite")
print(f"{'対象':22}{'rembgで欠け':>12}{'+dark_assist':>14}{'+drop_islands':>15}")
for spec in SPECS:
    who, pose = spec.split("/")
    im = Image.open(ROOT / f"_assets/character/_review/{who}/{pose}.png").convert("RGBA")
    src = np.asarray(im.convert("RGB")).astype(np.int16)
    bright = src.max(axis=2) > BRIGHT
    a0 = np.asarray(remove(im, session=sess["birefnet-general-lite"]))[:, :, 3]
    o1, _ = pc.dark_assist(Image.fromarray(
        np.dstack([src.astype(np.uint8), a0])), im)
    a1 = np.asarray(o1)[:, :, 3]
    o2, _ = pc.drop_islands(o1)
    a2 = np.asarray(o2)[:, :, 3]
    print(f"{spec:22}{int(((a0<8)&bright).sum()):12}"
          f"{int(((a1<8)&(a0>=8)&bright).sum()):14}"
          f"{int(((a2<8)&(a1>=8)&bright).sum()):15}")

print("\n=== モデル比較（rembg単体 → dark_assist → drop_islands まで通す）===")
print(f"{'対象':22}{'モデル':24}{'欠け(少ない方が良)':>20}{'取り残し背景':>14}")
for spec in SPECS:
    who, pose = spec.split("/")
    im = Image.open(ROOT / f"_assets/character/_review/{who}/{pose}.png").convert("RGBA")
    src = np.asarray(im.convert("RGB")).astype(np.int16)
    bright = src.max(axis=2) > BRIGHT
    for m in MODELS:
        if sess[m] is None:
            sess[m] = new_session(m)
        a = np.asarray(remove(im, session=sess[m]))[:, :, 3]
        o, _ = pc.dark_assist(Image.fromarray(np.dstack([src.astype(np.uint8), a])), im)
        o, _ = pc.drop_islands(o)
        af = np.asarray(o)[:, :, 3]
        print(f"{spec:22}{m:24}{int(((af<8)&bright).sum()):20}"
              f"{enclosed_dark(af, src):14}")
