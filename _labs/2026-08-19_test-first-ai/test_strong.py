import pytest
from shipping import shipping

CASES = [
    (2999, 500),  # 境界の1円下
    (3000, 0),    # ちょうど無料
    (3001, 0),
    (0, 500),     # 何も買っていない
]


@pytest.mark.parametrize(
    "sub,want", CASES,
    ids=["2999", "3000",
         "3001", "0"])
def test_fee(sub, want):
    assert shipping(sub) == want


def test_negative():
    with pytest.raises(ValueError):
        shipping(-1)
