"""実験8: 粒度によって「実行時間のばらつき」がどれだけ違うか。
同じ検証を200回ずつ、粒度[小]と粒度[大]で計る。
さらにCPUを埋めた状態(CIの混雑を模す)でもう一度[大]を計り、
「中央値の2倍」のタイムアウトを何回超えるかを数える。
"""
import json
import os
import statistics as st
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import price  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
N = 200
REQ = json.dumps({"seats": 3, "plan": "monthly"})
BURN = "import time\nt=time.time()\nwhile time.time()-t<25: pass\n"


def t_small():
    t0 = time.perf_counter()
    assert price.monthly_subtotal(3) == 3000
    return (time.perf_counter() - t0) * 1e6


def t_large():
    t0 = time.perf_counter()
    p = subprocess.run([sys.executable, "-m", "app.cli", REQ],
                       cwd=ROOT, capture_output=True, text=True)
    assert json.loads(p.stdout)["amount_due"] == 3300
    return (time.perf_counter() - t0) * 1e6


def w(s):
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def lj(s, n):
    return s + " " * max(0, n - w(s))


def rj(s, n):
    return " " * max(0, n - w(s)) + s


def show(name, v):
    print(lj(name, 10) + "".join(rj("%.0f" % x, 8)
                                 for x in (min(v), st.median(v), max(v))))


print("マイクロ秒 (1000us = 1ms)")
print(lj("", 10) + rj("最小", 8) + rj("中央", 8) + rj("最大", 8))
print("-" * 34)
small = [t_small() for _ in range(N)]
show("小unit", small)
large = [t_large() for _ in range(N)]
show("大e2e", large)

budget = st.median(large) * 2
procs = [subprocess.Popen([sys.executable, "-c", BURN]) for _ in range(8)]
time.sleep(1)
try:
    busy = [t_large() for _ in range(N)]
finally:
    for p in procs:
        p.kill()
show("大(混雑)", busy)

print()
print("予算 = 空いてる時の中央値x2 = %.0fus" % budget)
for name, v in (("空いてる時", large), ("混雑時", busy)):
    over = sum(1 for x in v if x > budget)
    print("  " + lj(name, 12)
          + "超過 %3d/%d (%.1f%%)" % (over, N, 100.0 * over / N))
