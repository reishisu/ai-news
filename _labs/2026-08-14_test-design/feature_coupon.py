"""実験5用: 「テストを書かずに機能を足すPR」を作るスクリプト。
app/coupon.py を新規追加し、bill.py から呼ぶ。テストは足さない。
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

COUPON = '''"""クーポンコードの適用。"""

CODES = {
    "WELCOME10": 0.10,
    "SPRING20": 0.20,
    "VIP50": 0.50,
}


def rate_for(code):
    if code is None:
        return 0.0
    c = code.strip().upper()
    if c not in CODES:
        raise ValueError("unknown coupon: %s" % c)
    return CODES[c]


def apply(amount, code):
    r = rate_for(code)
    return int(amount * (1 - r))
'''


def main():
    open(os.path.join(ROOT, "app/coupon.py"), "w",
         encoding="utf-8").write(COUPON)
    p = os.path.join(ROOT, "app/bill.py")
    s = open(p, encoding="utf-8").read()
    s = s.replace("from app import price",
                  "from app import coupon, price", 1)
    s = s.replace('def make_invoice(seats: int, plan: str) -> dict:',
                  'def make_invoice(seats: int, plan: str,\n'
                  '                 code: str = None) -> dict:', 1)
    s = s.replace("    subtotal = unit * months",
                  "    subtotal = unit * months\n"
                  "    subtotal = coupon.apply(subtotal, code)", 1)
    open(p, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    main()
