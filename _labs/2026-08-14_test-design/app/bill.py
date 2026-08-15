"""請求明細の組み立て。price を使う。"""

from app import coupon, price

TAX_RATE = 0.10
ANNUAL_PAID_MONTHS = 10  # 年払いは2ヶ月分無料 => 10ヶ月分だけ請求


def make_invoice(seats: int, plan: str,
                 code: str = None) -> dict:
    """席数とプランから請求明細を作る。"""
    if plan == "annual":
        months = ANNUAL_PAID_MONTHS
    elif plan == "monthly":
        months = 1
    else:
        raise ValueError("unknown plan: %s" % plan)

    unit = price.monthly_subtotal(seats)
    subtotal = unit * months
    subtotal = coupon.apply(subtotal, code)
    tax = int(subtotal * TAX_RATE)
    return {
        "seats": seats,
        "plan": plan,
        "months": months,
        "subtotal": subtotal,
        "tax": tax,
        "total": subtotal + tax,
    }
