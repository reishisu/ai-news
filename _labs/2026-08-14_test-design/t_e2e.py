"""粒度[大] 別プロセスで cli.py を起動して stdout を見る。"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def run(req: dict):
    p = subprocess.run(
        [sys.executable, "-m", "app.cli", json.dumps(req)],
        cwd=ROOT, capture_output=True, text=True,
    )
    body = json.loads(p.stdout)
    return p.returncode, body


def test_e2e_monthly_3():
    req = {"seats": 3, "plan": "monthly"}
    code, body = run(req)
    assert code == 0
    assert body["amount_due"] == 3300


def test_e2e_annual_60():
    req = {"seats": 60, "plan": "annual"}
    code, body = run(req)
    assert code == 0
    assert body["amount_due"] == 528000


def test_e2e_bad_input():
    req = {"seats": 0, "plan": "monthly"}
    code, body = run(req)
    assert code == 1
    assert body["error"] == "bad seats"
