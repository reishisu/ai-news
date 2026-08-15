"""実験3c: E2E(別プロセス)のカバレッジを拾い直せるか。
COVERAGE_PROCESS_START + sitecustomize.py + parallel=true を入れて
同じ t_e2e.py を測り直す。
"""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
RC = os.path.join(ROOT, "subproc_cov", "coveragerc")

for f in glob.glob(os.path.join(ROOT, ".coverage*")):
    os.remove(f)

env = dict(
    os.environ,
    COVERAGE_PROCESS_START=RC,
    PYTHONPATH=os.path.join(ROOT, "subproc_cov"),
)
subprocess.run([sys.executable, "-m", "coverage", "run", "--rcfile", RC,
                "-m", "pytest", "-q", "--tb=no", "t_e2e.py"],
               cwd=ROOT, env=env, capture_output=True, text=True)
n = len(glob.glob(os.path.join(ROOT, ".coverage.*")))
print("計測ファイル数: %d" % n)
subprocess.run([sys.executable, "-m", "coverage", "combine", "--rcfile", RC],
               cwd=ROOT, env=env, capture_output=True, text=True)
r = subprocess.run([sys.executable, "-m", "coverage", "report", "--rcfile", RC],
                   cwd=ROOT, env=env, capture_output=True, text=True)
sys.stdout.write(r.stdout)
