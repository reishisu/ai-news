"""実験3b: どのテストがどのファイルをカバーしているか。
「E2Eは別プロセスなので、そのままではカバレッジに1行も映らない」
という事実を確かめる。
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
COLS = ["t_unit.py", "t_intg.py", "t_e2e.py", "t_cov_only.py"]
ROWS = ["app/price.py", "app/bill.py", "app/api.py", "app/cli.py"]


def cov(f):
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no", "--cov=app",
         "--cov-report=json:/tmp/_cm.json", "--cov-report=", f],
        cwd=ROOT, capture_output=True, text=True,
    )
    d = json.load(open("/tmp/_cm.json"))["files"]
    return {k: v["summary"]["percent_covered"] for k, v in d.items()}


data = {c: cov(c) for c in COLS}
print("%-13s%6s%6s%6s%6s" % ("file", "unit", "intg", "e2e", "cov1"))
print("-" * 37)
for r in ROWS:
    cells = ["%5.0f%%" % data[c].get(r, 0.0) for c in COLS]
    print("%-13s%s" % (r.replace("app/", ""), "".join(cells)))
