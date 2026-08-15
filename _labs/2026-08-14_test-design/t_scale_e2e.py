"""実験3用: 粒度[大]を200件。中身の検証は上と同じ。"""

import pytest

from t_e2e import run


@pytest.mark.parametrize("seats", range(1, 201))
def test_scale_e2e(seats):
    code, body = run({"seats": seats, "plan": "monthly"})
    assert code == 0
    assert body["amount_due"] > 0
