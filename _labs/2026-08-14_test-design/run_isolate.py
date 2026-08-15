"""実験2: 同じ1個のバグで、粒度ごとに失敗メッセージがどう変わるか。
b4(定数の改名漏れ)を注入し、unit と e2e の生出力を並べる。
COLUMNS=40 でpytestの折返し幅をスマホに合わせている。
"""
import os
import subprocess
import sys

from bugs import BUGS

ROOT = os.path.dirname(os.path.abspath(__file__))
LABEL, PATH, BEFORE, AFTER = [b for b in BUGS if b[0].startswith("b4")][0]

env = dict(os.environ, COLUMNS="40")
p = os.path.join(ROOT, PATH)
orig = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(orig.replace(BEFORE, AFTER, 1))
try:
    for f in ("t_unit.py", "t_e2e.py"):
        print("=== %s ===" % f)
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--tb=short",
             "--no-header", f, "-x"],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        sys.stdout.write(r.stdout)
        print()
finally:
    open(p, "w", encoding="utf-8").write(orig)
