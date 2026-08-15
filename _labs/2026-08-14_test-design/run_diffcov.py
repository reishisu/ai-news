"""実験5: 「全体カバレッジ」と「このPRで足した行のカバレッジ」の差。
テストを書かずに機能を1つ足し、両方を測る。
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SUITE = ["t_unit.py", "t_intg.py", "t_e2e.py", "t_cov_only.py"]


def cov():
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no", "--cov=app",
         "--cov-report=json:/tmp/_d.json", "--cov-report=", *SUITE],
        cwd=ROOT, capture_output=True, text=True,
    )
    return json.load(open("/tmp/_d.json"))


def added_lines():
    """git diff で追加された app/*.py の行番号。
    新規ファイルを差分に載せるため git add -N が要る。"""
    subprocess.run(["git", "add", "-N", "--", "app"], cwd=ROOT)
    r = subprocess.run(["git", "diff", "--unified=0", "HEAD", "--", "app"],
                       cwd=ROOT, capture_output=True, text=True)
    out, cur = {}, None
    for ln in r.stdout.splitlines():
        if ln.startswith("+++ b/"):
            cur = ln[6:]
            out[cur] = set()
        elif ln.startswith("@@") and cur:
            m = re.search(r"\+(\d+)(?:,(\d+))?", ln)
            start, cnt = int(m.group(1)), int(m.group(2) or 1)
            out[cur] |= set(range(start, start + cnt))
    return out


before = cov()["totals"]["percent_covered"]
subprocess.run([sys.executable, "feature_coupon.py"], cwd=ROOT, check=True)
d = cov()
after = d["totals"]["percent_covered"]

add = added_lines()
hit = miss = 0
holes = []
for f, lines in sorted(add.items()):
    info = d["files"].get(f)
    if not info:
        continue
    ex = set(info["executed_lines"])
    ms = set(info["missing_lines"])
    hit += len(lines & ex)
    miss += len(lines & ms)
    src = open(os.path.join(ROOT, f), encoding="utf-8").read().splitlines()
    for n in sorted(lines & ms):
        holes.append("%s:%d %s" % (f[4:], n, src[n - 1].strip()))

print("全体cov  変更前: %.1f%%" % before)
print("全体cov  変更後: %.1f%%" % after)
print("追加行: %d行 / 通った: %d行" % (hit + miss, hit))
print("差分cov: %.1f%%" % (100.0 * hit / max(1, hit + miss)))
print("-- 誰も通していない追加行 --")
for h in holes:
    print(h)
