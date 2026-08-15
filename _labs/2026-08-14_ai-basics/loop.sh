#!/bin/bash
MAX=5
for i in $(seq 1 $MAX); do
  echo "--- $i 回目 ---"
  if python3 -m pytest -q --tb=no; then
    echo "✅ 全部通ったので終了"
    exit 0
  fi
  echo "🔧 直します"
  ./fix_agent.sh          # ここを実際はAIの呼び出しに差し替える
done
echo "⛔ $MAX 回やっても直らないので打ち切り"
exit 1
