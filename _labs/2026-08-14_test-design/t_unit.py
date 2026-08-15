"""粒度[小] price.py だけを見る。境界値を踏む。"""

import pytest

from app import price


@pytest.mark.parametrize(
    "seats, rate",
    [
        (1, 0.0),    # 下限
        (9, 0.0),    # 10席未満の上端
        (10, 0.10),  # 10%の下端
        (49, 0.10),  # 10%の上端
        (50, 0.20),  # 20%の下端
        (500, 0.20),
    ],
)
def test_rate(seats, rate):
    assert price.volume_discount_rate(seats) == rate


def test_rate_zero_seats():
    with pytest.raises(ValueError):
        price.volume_discount_rate(0)


@pytest.mark.parametrize(
    "seats, yen",
    [
        (1, 1000),
        (9, 9000),
        (10, 9000),    # 10席で10%引き
        (49, 44100),
        (50, 40000),   # 50席で20%引き
    ],
)
def test_subtotal(seats, yen):
    assert price.monthly_subtotal(seats) == yen
