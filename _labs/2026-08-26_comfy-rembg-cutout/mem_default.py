"""既定(アリーナ有効)の段階別RSS。記事の第8節の「既定のまま」の数値の根拠。

アリーナ無効側は mem2.py / mem_arena_off_output.txt。
このスクリプトはOOMに近づくので、RAM16GBの環境でだけ回すこと。
"""
import sys, time
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from rembg import new_session, remove

REVIEW = ROOT / "_assets/character/_review"

def rss():
    for l in open("/proc/self/status"):
        if l.startswith("VmRSS:"):
            return int(l.split()[1]) / 1024

def show(t):
    print(f"  {t:36} RSS {rss():7.0f} MiB", flush=True)

files = sorted(REVIEW.glob("*/*.png"))[:2]
show("起動時")
sb = new_session("birefnet-general-lite")
show("birefnet セッション作成後")
for i, f in enumerate(files, 1):
    im = Image.open(f).convert("RGBA")
    t = time.monotonic()
    remove(im, session=sb)
    show(f"birefnet 推論{i}回目 ({time.monotonic()-t:.0f}秒)")
si = new_session("isnet-anime")
show("isnet セッション作成後")
im = Image.open(files[0]).convert("RGBA")
remove(im, session=si)
show("isnet 推論1回目")
