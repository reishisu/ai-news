"""直した repair_holes を1枚で走らせ、**出来上がったPNGを背景に載せて**確かめる。

前回の見落としは「元画像にマゼンタを塗った絵」で確認したこと。
今回は cast に書き出す絵そのものを合成して見る。
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path("/home/user/ai-news-dev"); sys.path.insert(0, str(ROOT))
import _prepare_character as pc
src = ROOT / "_assets/character/_review/hinata/sleepy.png"
im = Image.open(src).convert("RGBA")
out = pc.cut_out(im)
arr = np.asarray(out)
full = np.asarray(im.convert("RGB")).astype(int)
op = arr[:, :, 3] >= 200
d = np.abs(arr[:, :, :3].astype(int) - full).sum(axis=2)
print(f"不透明画素での平均RGB差 {d[op].mean():.2f}（小さいほど元画像どおり）")
bg = Image.new("RGB", out.size, (255, 0, 255))
bg.paste(out, (0, 0), out)
bg.crop((0, 400, 260, 1100)).resize((520, 1400), Image.NEAREST).save("fixed_sleepy.png")
print("fixed_sleepy.png を書き出した")
