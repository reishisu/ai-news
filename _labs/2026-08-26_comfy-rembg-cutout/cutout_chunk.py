"""_review/ の一部だけを切り抜いて cast/ に入れる（範囲を指定できる版）。

cutout_all.py は 26枚目で OOM kill された（rc=137 / RSS 13.9GB）。
repair_holes が isnet-anime も読むので、birefnet と合わせて2モデルが常駐し、
さらに onnxruntime のアリーナが推論ごとに伸びる。

対策は単純に**プロセスを分けること**。範囲を区切って何回かに分けて呼び、
その都度プロセスを終わらせてメモリを返す。モデルの読み込みは1回の呼び出しに
つき2回ぶん余分にかかるが、落ちるよりよい。

    python3 cutout_chunk.py <開始index> <終了index>   # 1始まり・終了を含む
"""
import io
import sys
import time
import contextlib
from pathlib import Path

ROOT = Path("/home/user/ai-news-dev")
sys.path.insert(0, str(ROOT))

import rembg  # noqa: E402

_CACHE = {}
_orig = rembg.new_session


def _cached(name=None, *a, **kw):
    if name not in _CACHE:
        t = time.monotonic()
        _CACHE[name] = _orig(name, *a, **kw) if name else _orig(*a, **kw)
        print(f"  モデル読み込み {name}: {time.monotonic() - t:.0f}秒", flush=True)
    return _CACHE[name]


rembg.new_session = _cached
import _prepare_character as pc  # noqa: E402

REVIEW = ROOT / "_assets/character/_review"
CAST = pc.CAST_DIR
files = sorted(REVIEW.glob("*/*.png"))
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
hi = int(sys.argv[2]) if len(sys.argv) > 2 else len(files)

ng = []
for i in range(lo, min(hi, len(files)) + 1):
    src = files[i - 1]
    who, pose = src.parent.name, src.stem
    t = time.monotonic()
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = pc.prepare(src, CAST / who / f"{pose}.png", do_rembg=True)
    except Exception as e:
        rc, buf = 1, io.StringIO(f"例外: {e}")
    log = buf.getvalue()
    healed = next((l.strip() for l in log.splitlines() if "戻しました" in l), "")
    if rc in (0, None):
        print(f"  [{i}/{len(files)}] {who}/{pose}  {time.monotonic() - t:.0f}秒"
              f"  {healed}", flush=True)
    else:
        ng.append((who, pose, log.strip()[:200]))
        print(f"  [{i}/{len(files)}] {who}/{pose}  失敗 {log.strip()[:200]}", flush=True)
print(f"範囲 {lo}-{hi} 終了 / 失敗 {len(ng)}件", flush=True)
