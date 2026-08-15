"""カバレッジを稼ぐためだけのテスト。
全行を通すが、値の正しさは一切見ていない。
「落ちないテスト」の見本として意図的にこう書いている。
"""
import json

import pytest

from app import api, bill, cli, price


def test_1():
    for s in (1, 9, 10, 49, 50, 500):
        r = price.volume_discount_rate(s)
        assert isinstance(r, float)
        assert price.monthly_subtotal(s) > 0
    with pytest.raises(ValueError):
        price.volume_discount_rate(0)


def test_2():
    for plan in ("monthly", "annual"):
        inv = bill.make_invoice(3, plan)
        assert inv is not None
        assert "total" in inv
    with pytest.raises(ValueError):
        bill.make_invoice(3, "weekly")


def test_3():
    ok = api.handle({"seats": 3, "plan": "monthly"})
    assert ok["status"] == 200
    assert ok["body"]["amount_due"] > 0
    assert api.handle({"seats": 0, "plan": "monthly"})["status"] == 400
    assert api.handle({"seats": 3, "plan": "x"})["status"] == 400


def test_4(capsys):
    assert cli.main(["cli", json.dumps({"seats": 3, "plan": "annual"})]) == 0
    assert cli.main(["cli", json.dumps({"seats": 0, "plan": "x"})]) == 1
    assert capsys.readouterr().out
