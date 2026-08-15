#!/bin/bash
# 壊れていた版: pytest をパイプに繋ぐと、if が見るのは tail の終了状態になる
MAX=5
for i in $(seq 1 $MAX); do
  echo "--- $i 回目 ---"
  if python3 -m pytest -q --tb=no | tail -1; then
    echo "✅ 全部通ったので終了"
    exit 0
  fi
  echo "🔧 直します"
  ./fix_agent.sh
done
