"""粒度[中] bill + price をつないで見る。境界は踏まない代表値。"""

import pytest

from app import bill


def test_monthly_3():
    inv = bill.make_invoice(3, "monthly")
    assert inv["months"] == 1
    assert inv["subtotal"] == 3000
    assert inv["total"] == 3300


def test_annual_3():
    # 年払い = 10ヶ月分だけ請求
    inv = bill.make_invoice(3, "annual")
    assert inv["months"] == 10
    assert inv["subtotal"] == 30000
    assert inv["total"] == 33000


def test_annual_60():
    # 60席 -> 20%引き -> 48000/月, 年払いで10ヶ月分
    inv = bill.make_invoice(60, "annual")
    assert inv["subtotal"] == 480000
    assert inv["total"] == 528000


def test_bad_plan():
    with pytest.raises(ValueError):
        bill.make_invoice(3, "weekly")
