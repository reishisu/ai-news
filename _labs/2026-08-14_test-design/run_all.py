"""全実験を順に流す。

前提:
  pip install pytest coverage pytest-cov mutmut
  git init . && git add -A && git commit -m base   (実験5で使う)
使い方:
  python3 run_all.py
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    ("1 検出マトリクス", "run_matrix.py"),
    ("2 失敗の切り分け", "run_isolate.py"),
    ("3 cov率と検出数", "run_cov.py"),
    ("3b どこを覆うか", "run_covmap.py"),
    ("3c E2Eのcov回収", "run_subproc_cov.py"),
    ("4 実行時間", "run_time.py"),
    ("5 差分カバレッジ", "run_diffcov.py"),
    ("6 仕様変更の見え方", "run_spec.py"),
    ("7 ミューテーション", "run_mutation.py"),
    ("8 実行時間のばらつき", "run_flaky.py"),
]

for title, script in STEPS:
    print("\n########## %s ##########" % title)
    sys.stdout.flush()
    subprocess.run([sys.executable, script], cwd=ROOT)
    if script == "run_diffcov.py":
        subprocess.run(["git", "checkout", "--", "app"], cwd=ROOT)
        subprocess.run(["git", "rm", "-q", "--cached", "app/coupon.py"],
                       cwd=ROOT, capture_output=True)
        p = os.path.join(ROOT, "app/coupon.py")
        if os.path.exists(p):
            os.remove(p)
