#!/usr/bin/env bash
# 仕込んだ14件に、機械を4種あてる。
# 出力は narrow.py で幅37桁に折り返す(文字は変えない)。
export COLUMNS=40
cd "$(dirname "$0")"
N="python3 narrow.py"
echo "== 1. ruff / 書式と静的検査 =="
ruff check --select E,F,B \
  --output-format concise orders.py | $N
echo
echo "== 2. mypy / 型 =="
mypy --no-color-output --no-error-summary \
  orders.py | $N
echo
echo "== 3. bandit / セキュリティ =="
bandit -q -f custom \
  --msg-template "{line}: {test_id} {msg}" \
  orders.py | $N
echo "(出力なし = 指摘0件)"
echo
echo "== 4. 自作ルール house_rules.py =="
python3 house_rules.py orders.py | $N
