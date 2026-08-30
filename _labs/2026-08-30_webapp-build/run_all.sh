#!/usr/bin/env bash
# 2026-08-30 webapp-build の再現一式。実行するとメモ帳アプリを作り直します。
# 前提: claude 2.1.251 / python3 + playwright + chromium
set -euo pipefail
cd "$(dirname "$0")"

echo "===== 段1 環境 ====="
claude --version
TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M JST"

echo "===== 段2 1コマンド目: メモ帳を作らせる ====="
mkdir -p app && cd app
S=$SECONDS
claude -p "ブラウザで動くメモ帳アプリを index.html 1枚だけで作って。複数メモの作成・編集・削除、localStorage保存、日本語UI。外部ライブラリ無し" \
  --allowedTools Write --output-format json > ../step2.json < /dev/null
echo "exit=$? wall=$((SECONDS-S))s"
python3 - <<'PY'
import json
d=json.load(open('../step2.json'))
for k in ('is_error','subtype','num_turns','total_cost_usd','permission_denials'):
    print(k, d.get(k))
PY
cd ..

echo "===== 段4 動作を機械で確かめる ====="
python3 test_app.py

echo "===== 段6 2コマンド目: ダークモードを足させる ====="
cd app
S=$SECONDS
claude -p "index.html のメモ帳にダークモード切替ボタンを足して。設定はlocalStorageに保存、初期値はOSの設定に従う" \
  --allowedTools "Read Edit" --output-format json > ../step6.json < /dev/null
echo "exit=$? wall=$((SECONDS-S))s"
cd ..
python3 test_dark.py
