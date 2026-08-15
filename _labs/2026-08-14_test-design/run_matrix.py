"""実験1: 壊し方x粒度 の検出マトリクス。
各バグを1行だけ注入し、3つの粒度のテストを別々に走らせて
「どれが落ちるか」を数える。
"""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from bugs import BUGS

ROOT = os.path.dirname(os.path.abspath(__file__))
FILES = [("unit", "t_unit.py"), ("intg", "t_intg.py"), ("e2e", "t_e2e.py")]
XML = "/tmp/_m.xml"


def run(testfile):
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no", testfile,
         "--junitxml=" + XML],
        cwd=ROOT, capture_output=True, text=True,
    )
    s = ET.parse(XML).getroot().find("testsuite")
    total = int(s.get("tests"))
    bad = int(s.get("failures")) + int(s.get("errors"))
    return total, bad


def patch(path, before, after):
    p = os.path.join(ROOT, path)
    src = open(p, encoding="utf-8").read()
    assert before in src, "置換対象が見つからない: " + path
    open(p, "w", encoding="utf-8").write(src.replace(before, after, 1))
    return src


def cell(total, bad):
    return ("%dP" % total) if bad == 0 else ("%dF/%d" % (bad, total))


def pad(s, n):
    """全角を2桁として左詰めする(スマホ幅対策)。"""
    import unicodedata
    w = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    return s + " " * max(0, n - w)


def row(label, res):
    return pad(label, 13) + "".join(pad(c.rjust(6), 6) for c in res)


print(row("壊し方", ["  unit", "  intg", "   e2e"]))
print("-" * 31)
print(row("(なし)", [cell(*run(f)) for _, f in FILES]))

for label, path, before, after in BUGS:
    orig = patch(path, before, after)
    try:
        print(row(label, [cell(*run(f)) for _, f in FILES]))
    finally:
        open(os.path.join(ROOT, path), "w", encoding="utf-8").write(orig)
