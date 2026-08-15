"""実験6: 仕様が変わったとき、テストは何を教えてくれるか。
割引ルールを改定する変更(5席から10%, 30席から25%)を price.py に入れ、
2つのテストファイルの生出力を並べる。
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "app/price.py")
CHANGE = [
    ("    if seats >= 50:\n        return 0.20",
     "    if seats >= 30:\n        return 0.25"),
    ("    if seats >= 10:\n        return 0.10",
     "    if seats >= 5:\n        return 0.10"),
]

orig = open(P, encoding="utf-8").read()
s = orig
for b, a in CHANGE:
    assert b in s
    s = s.replace(b, a, 1)
open(P, "w", encoding="utf-8").write(s)

env = dict(os.environ, COLUMNS="40")
try:
    for f in ("t_spec_bad.py", "t_spec_good.py"):
        print("=== %s ===" % f)
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--tb=short",
             "--no-header", "-rN", f],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        sys.stdout.write(r.stdout)
        print()
finally:
    open(P, "w", encoding="utf-8").write(orig)
