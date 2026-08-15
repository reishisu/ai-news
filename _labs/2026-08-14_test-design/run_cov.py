"""実験3: カバレッジ率と「バグ検出数」は別物であることの実測。
2つのテストセットについて (a) app/ の行カバレッジ (b) 4つのバグの検出数
を測る。
"""
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

from bugs import BUGS

ROOT = os.path.dirname(os.path.abspath(__file__))
SETS = [
    ("cov_only", ["t_cov_only.py"]),
    ("3粒度セット", ["t_unit.py", "t_intg.py", "t_e2e.py"]),
]


def cov(files):
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no",
         "--cov=app", "--cov-report=json:/tmp/_c.json",
         "--cov-report=", *files],
        cwd=ROOT, capture_output=True, text=True,
    )
    d = json.load(open("/tmp/_c.json"))
    t = d["totals"]
    return t["percent_covered"], t["num_statements"], t["missing_lines"]


def fails(files):
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no", *files,
         "--junitxml=/tmp/_c.xml"],
        cwd=ROOT, capture_output=True, text=True,
    )
    s = ET.parse("/tmp/_c.xml").getroot().find("testsuite")
    return int(s.get("failures")) + int(s.get("errors"))


def pad(s, n):
    import unicodedata
    w = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    return s + " " * max(0, n - w)


print(pad("テストセット", 14) + "cov%  未到達 検出")
print("-" * 34)
for name, files in SETS:
    pct, stmts, miss = cov(files)
    caught = 0
    for _, path, before, after in BUGS:
        p = os.path.join(ROOT, path)
        orig = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(orig.replace(before, after, 1))
        try:
            if fails(files) > 0:
                caught += 1
        finally:
            open(p, "w", encoding="utf-8").write(orig)
    print(pad(name, 14) + "%5.1f %5d行 %d/%d" % (pct, miss, caught, len(BUGS)))
print()
print("(app/ の総ステートメント数: %d)" % stmts)
