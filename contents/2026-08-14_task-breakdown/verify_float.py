#!/usr/bin/env python3
"""全余裕の定義を、遅延を注入して確かめる。

全余裕ぶんちょうど遅らせたら全体は延びない。
1時間(0.1日)でも足したら延びる。これが成り立てば正しい。
"""
from critical_path import TASKS, forward, backward


def span(tasks):
    days = {t[0]: t[2] for t in tasks}
    deps = {t[0]: t[3] for t in tasks}
    return max(forward(days, deps)[1].values())


def delayed(tid, add):
    return span([(i, n, d + add if i == tid else d, p)
                 for i, n, d, p in TASKS])


days = {t[0]: t[2] for t in TASKS}
deps = {t[0]: t[3] for t in TASKS}
es, ef = forward(days, deps)
base = span(TASKS)
ls = backward(days, deps, base)

print(f"基準の全体日数 : {base} 日")
print("id 全余裕 ぶん遅延 +0.1日")
for tid, name, d, dp in TASKS:
    tf = round(ls[tid] - es[tid], 6)
    a, b = delayed(tid, tf), delayed(tid, tf + 0.1)
    ok = abs(a - base) < 1e-9 and b > base + 1e-9
    print(f"{tid:<3}{tf:>5.1f}{a:>9.1f}{b:>8.1f}  "
          + ("OK" if ok else "NG"))
