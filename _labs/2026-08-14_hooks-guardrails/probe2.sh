#!/bin/bash
# allow ルールが「どこに置かれたか」で効くかどうかを確かめる。
# 対象は ./mark.sh（marker.txt を作るだけのスクリプト）。
# ユーザ設定 /root/.claude/settings.json の allow は
# Bash(git *) / Bash(python3 *) だけなので ./mark.sh には当たらない。
# MODE = none | project | flag | flag-empty
set -u
B="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; MODE="$2"
rm -f "$B/lab/marker.txt" "$B/lab/.claude/settings.json"

ARGS=()
case "$MODE" in
  project)    cp "$B/cases/allow-mark.json" "$B/lab/.claude/settings.json" ;;
  flag)       ARGS=(--settings "$B/cases/allow-mark.json") ;;
  flag-empty) ARGS=(--settings "$B/cases/allow-empty.json") ;;
esac

cd "$B/lab" || exit 1
claude -p 'Run exactly this command with the Bash tool: ./mark.sh
Then report what happened. If it is blocked, quote the error verbatim and do NOT attempt any workaround.' \
  --output-format json --max-turns 4 --debug hooks "${ARGS[@]}" \
  > "$B/out/$CASE.json" 2> "$B/out/$CASE.debug"

if [ -f "$B/lab/marker.txt" ]; then R=CREATED; else R=blocked; fi
printf '%s %s %s\n' "$CASE" "$MODE" "$R" > "$B/out/$CASE.truth"
echo "$CASE mode=$MODE marker=$R"
