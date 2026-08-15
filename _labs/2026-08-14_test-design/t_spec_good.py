"""仕様書として機能するテスト。
表が仕様そのもので、落ちたときに理由の文が出る。
"""
import pytest

from app import bill

# 適用順: 席数割引 -> 年払い(10ヶ月分) -> 消費税10%
SPEC = [
    (1, "monthly", 1000, 1100, "1席は割引なし"),
    (9, "monthly", 9000, 9900, "9席までは割引なし"),
    (10, "monthly", 9000, 9900, "10席から10%引き"),
    (49, "monthly", 44100, 48510, "49席までは10%引き"),
    (50, "monthly", 40000, 44000, "50席から20%引き"),
    (3, "annual", 30000, 33000, "年払いは10ヶ月分"),
    (50, "annual", 400000, 440000, "割引と年払いは併用"),
]
IDS = ["m1", "m9", "m10", "m49", "m50", "a3", "a50"]


@pytest.mark.parametrize("seats,plan,sub,ttl,why", SPEC, ids=IDS)
def test_invoice(seats, plan, sub, ttl, why):
    inv = bill.make_invoice(seats, plan)
    assert inv["subtotal"] == sub, why
    assert inv["total"] == ttl, why
