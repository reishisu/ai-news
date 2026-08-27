#!/usr/bin/env bash
# セットアップが完了したかを、対話画面を開かずに判定する。
# 第1引数: 確かめたいプロジェクトのパス
set -eu
cd "${1:?プロジェクトのパスを渡してください}"
SID=$(python3 -c 'import uuid;print(uuid.uuid4())')

claude -p "/grill-me 動作確認" \
  --output-format stream-json --verbose \
  --session-id "$SID" < /dev/null > verify.json 2>&1

echo "--- 呼ばれたスキル ---"
grep -ao '"skill":"[^"]*"' verify.json | sort | uniq -c

echo "--- 返ってきたもの（先頭200字） ---"
python3 - <<'PY'
import json
for line in open('verify.json'):
    try: d = json.loads(line)
    except Exception: continue
    if d.get('type') == 'result':
        print(str(d.get('result'))[:200])
PY
