"""実験7: ミューテーションテストで「テストが仕様をどれだけ固定しているか」を測る。
price.py / bill.py を機械的に書き換えたコピーを作り、
テストが落ちる(=殺せる)か落ちない(=生き残る)かを数える。
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VARIANTS = ["bad", "good"]


def setup(v):
    d = os.path.join(ROOT, "mut_" + v)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "app"))
    for f in ("__init__.py", "price.py", "bill.py"):
        shutil.copy(os.path.join(ROOT, "app", f), os.path.join(d, "app", f))
    shutil.copy(os.path.join(ROOT, "t_spec_%s.py" % v),
                os.path.join(d, "test_spec.py"))
    open(os.path.join(d, "pytest.ini"), "w").write(
        "[pytest]\npython_files = test_*.py\n")
    open(os.path.join(d, "setup.cfg"), "w").write(
        "[mutmut]\nsource_paths=app\nalso_copy=pytest.ini\n")
    return d


def mutmut(d, *args):
    return subprocess.run([sys.executable, "-m", "mutmut", *args],
                          cwd=d, capture_output=True, text=True).stdout


res = {}
for v in VARIANTS:
    d = setup(v)
    out = mutmut(d, "run").replace("\r", "\n")
    m = re.findall(r"(\d+)/(\d+) +🎉 (\d+).*?🙁 (\d+)", out)[-1]
    surv = re.findall(r"app\.(\w+)\.x_(\w+)__mutmut_\d+: survived",
                      mutmut(d, "results").replace("\r", "\n"))
    res[v] = {"total": int(m[1]), "kill": int(m[2]), "surv": surv}

def w(s):
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def rj(s, n):
    return " " * max(0, n - w(s)) + s


def lj(s, n):
    return s + " " * max(0, n - w(s))


print(lj("suite", 8) + rj("変異", 6) + rj("殺した", 8) + rj("残った", 8))
print("-" * 30)
for v in VARIANTS:
    r = res[v]
    print(lj(v, 8) + rj(str(r["total"]), 6) + rj(str(r["kill"]), 8)
          + rj(str(len(r["surv"])), 8))

print()
print("生き残った変異の場所")
print("-" * 30)
mods = sorted({m for v in VARIANTS for m, _ in res[v]["surv"]})
print(lj("", 12) + rj("bad", 8) + rj("good", 8))
for mod in mods:
    c = [sum(1 for m, _ in res[v]["surv"] if m == mod) for v in VARIANTS]
    print(lj(mod + ".py", 12) + rj(str(c[0]), 8) + rj(str(c[1]), 8))
