"""実験4: 粒度ごとの実行時間。同じ検証内容を200件ずつ書いて実測する。
3回走らせて最良値を採る。
"""
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGETS = [("小 unit", "t_scale_unit.py"), ("大 e2e", "t_scale_e2e.py")]


def once(f):
    t0 = time.perf_counter()
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no", f],
        cwd=ROOT, capture_output=True, text=True,
    )
    wall = time.perf_counter() - t0
    m = re.search(r"(\d+) passed", r.stdout)
    return wall, int(m.group(1))


def pad(s, n):
    import unicodedata
    w = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    return s + " " * max(0, n - w)


print(pad("粒度", 9) + "件数   合計s  1件ms")
print("-" * 30)
for label, f in TARGETS:
    best, n = min((once(f) for _ in range(3)), key=lambda x: x[0])
    print(pad(label, 9) + "%4d %6.2f %6.1f" % (n, best, best / n * 1000))
