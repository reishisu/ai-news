"""壊し方の定義。(対象ファイル, 置換前, 置換後) の1行だけを書き換える。"""

BUGS = [
    ("b1 境界ズレ", "app/price.py",
     "    if seats >= 10:",
     "    if seats > 10:"),
    ("b2 年割無視", "app/bill.py",
     "        months = ANNUAL_PAID_MONTHS",
     "        months = 12"),
    ("b3 出力取違", "app/api.py",
     '            "amount_due": inv["total"],   # 税込',
     '            "amount_due": inv["subtotal"],'),
    ("b4 改名漏れ", "app/price.py",
     "PRICE = 1000  # 1席あたり月額(税抜)",
     "PRICE_YEN = 1000  # 1席あたり月額(税抜)"),
]
