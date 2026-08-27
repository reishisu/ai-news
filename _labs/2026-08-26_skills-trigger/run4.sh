#!/usr/bin/env bash
# 実験4の本体。素の /grill-me と、名前空間つきの /mattpocock-skills:grill-me を比べる。
set -eu
DIR="${1:?作業ディレクトリ}"; export CLAUDE_CONFIG_DIR="${2:?CLAUDE_CONFIG_DIR}"
cd "$DIR"
for CMD in "/grill-me テスト" "/mattpocock-skills:grill-me テスト"; do
  echo "===== $CMD ====="
  claude -p "$CMD" --output-format stream-json --verbose \
    --session-id "$(python3 -c 'import uuid;print(uuid.uuid4())')" \
    < /dev/null > out4.json 2>&1
  echo -n "呼ばれたSkill: "; grep -ao '"skill":"[^"]*"' out4.json | sort -u | tr '\n' ' '; echo
  python3 -c "
import json
for l in open('out4.json'):
    try: d=json.loads(l)
    except Exception: continue
    if d.get('type')=='result': print('返り:', str(d.get('result'))[:120])
"
done
