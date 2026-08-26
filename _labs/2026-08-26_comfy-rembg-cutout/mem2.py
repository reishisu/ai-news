"""アリーナを切るとどれだけ減るか。結果が変わらないことも確かめる。"""
import sys, time
from pathlib import Path
import numpy as np
from PIL import Image
import onnxruntime as ort
ROOT = Path("/home/user/ai-news-dev"); sys.path.insert(0, str(ROOT))
from rembg import new_session, remove
REVIEW = ROOT / "_assets/character/_review"
def rss():
    for l in open("/proc/self/status"):
        if l.startswith("VmRSS:"): return int(l.split()[1]) / 1024
def show(t): print(f"  {t:40} RSS {rss():7.0f} MiB", flush=True)
o = ort.SessionOptions(); o.enable_cpu_mem_arena = False
files = sorted(REVIEW.glob("*/*.png"))[:3]
show("起動時")
sb = new_session("birefnet-general-lite", sess_opts=o)
show("birefnet(アリーナ無し)作成後")
outs = []
for i, f in enumerate(files, 1):
    im = Image.open(f).convert("RGBA"); t = time.monotonic()
    outs.append(np.asarray(remove(im, session=sb))[:, :, 3])
    show(f"birefnet 推論{i} ({time.monotonic()-t:.0f}秒)")
si = new_session("isnet-anime", sess_opts=o)
show("isnet(アリーナ無し)作成後")
for i, f in enumerate(files, 1):
    im = Image.open(f).convert("RGBA"); t = time.monotonic()
    remove(im, session=si)
    show(f"isnet 推論{i} ({time.monotonic()-t:.0f}秒)")
# アリーナ有りと結果が同じか
sb2 = new_session("birefnet-general-lite")
a = np.asarray(remove(Image.open(files[0]).convert("RGBA"), session=sb2))[:, :, 3]
print(f"  アリーナ有無での alpha の差: {int(np.abs(a.astype(int)-outs[0].astype(int)).sum())}")
