"""実験3用: 粒度[小]を200件。"""

import pytest

from app import price


@pytest.mark.parametrize("seats", range(1, 201))
def test_scale_unit(seats):
    v = price.monthly_subtotal(seats)
    assert isinstance(v, int) and v > 0
