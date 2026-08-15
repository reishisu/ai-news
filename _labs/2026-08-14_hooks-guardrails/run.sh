#!/bin/bash
# usage: run.sh <case> <settings.json> <prompt>
# 指定した settings.json を lab/.claude/settings.json に置き、
# lab ディレクトリで claude を headless 実行して生JSONを out/ に保存する。
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; SETTINGS="$2"; PROMPT="$3"

cp "$SETTINGS" "$BASE/lab/.claude/settings.json"
cd "$BASE/lab" || exit 1

claude -p "$PROMPT" \
  --output-format json \
  --max-turns 4 \
  --debug hooks \
  > "$BASE/out/$CASE.json" 2> "$BASE/out/$CASE.debug"
echo "exit=$? case=$CASE"
