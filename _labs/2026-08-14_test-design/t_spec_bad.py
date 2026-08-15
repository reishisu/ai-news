"""仕様書として機能しないテスト。
名前が意味を持たず、モックで中身を差し替え、期待値は裸の数字。
これでも「テストがある」と言えてしまう。
"""
from unittest import mock

from app import bill


def test_1():
    with mock.patch("app.bill.price") as p:
        p.monthly_subtotal.return_value = 1000
        r = bill.make_invoice(3, "annual")
    p.monthly_subtotal.assert_called_once_with(3)
    assert isinstance(r, dict)
    assert set(r) == {"seats", "plan", "months",
                      "subtotal", "tax", "total"}


def test_2():
    with mock.patch("app.bill.price") as p:
        p.monthly_subtotal.return_value = 1000
        r = bill.make_invoice(3, "monthly")
    assert r["total"] > 0


def test_3():
    r = bill.make_invoice(50, "monthly")
    assert r["total"] == 44000
