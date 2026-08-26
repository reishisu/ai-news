"""事故3(alphaだけ戻して真っ黒)の数値の根拠を、決定的に再計算する。

材料は3つとも履歴・キャッシュに残っている:
  birefnetのみのcast … git a649572 の hinata/sleepy
  isnetのalpha       … 実行時の .npy キャッシュ(引数で場所を渡す)
  元画像             … _review/hinata/sleepy.png
「isnetが不透明∧birefnetが透明∧元が明るい(>100)」をalphaだけ戻した場合と、
RGBも戻した場合の、元画像との平均RGB差(3ch合計)を出す。
"""
import subprocess, sys
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
NPY = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("isnet_alpha")

full = np.asarray(Image.open(ROOT / "_assets/character/_review/hinata/sleepy.png").convert("RGB")).astype(int)
v = full.max(axis=2)
b = subprocess.run(["git", "-C", str(ROOT), "show",
                    "a649572:_assets/character/cast/hinata/sleepy.png"],
                   capture_output=True, check=True).stdout
old = np.asarray(Image.open(BytesIO(b)).convert("RGBA"))
# a649572 の hinata/sleepy は元画像と同サイズ・位置(0,0)(実測済み)
ab, argb = old[:, :, 3], old[:, :, :3].astype(int)
ai = np.load(NPY / "hinata_sleepy.npy")
add = (ai >= 8) & (ab < 8) & (v > 100)
print(f"戻した画素: {int(add.sum())}px")
# alphaだけ戻す: RGBはrembg出力(黒に潰れている)のまま
d_alpha_only = np.abs(argb[add] - full[add]).sum(axis=1).mean()
print(f"alphaのみ: 戻した画素の平均RGB差 {d_alpha_only:.0f}")
op = (ab >= 200) | add
rgb_alpha_only = argb.copy(); rgb_fixed = argb.copy(); rgb_fixed[add] = full[add]
print(f"alphaのみ: 不透明画素全体の平均RGB差 {np.abs(rgb_alpha_only[op]-full[op]).sum(axis=1).mean():.2f}")
print(f"RGBも戻す: 不透明画素全体の平均RGB差 {np.abs(rgb_fixed[op]-full[op]).sum(axis=1).mean():.2f}")
