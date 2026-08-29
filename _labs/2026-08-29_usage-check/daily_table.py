"""ccusage daily --json を、日付・換算コスト・トークン計の表にする。"""
import json, sys
rows = json.load(sys.stdin)["daily"]
print(f'{"日付":<12}{"換算コスト":>9}{"トークン計":>17}')
for r in rows:
    print(f'{r["period"]:<12}${r["totalCost"]:>7.2f}{r["totalTokens"]:>17,}')
print(f'合計 {len(rows)}日  ${sum(r["totalCost"] for r in rows):.2f}')
