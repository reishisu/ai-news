#!/bin/bash
# allow ルールが本当に効いているかを確かめる。
# 対象は touch。ユーザ設定 /root/.claude/settings.json は
# Bash(git *) と Bash(python3 *) しか許可していないので、
# touch は「何もしなければ止まる」コマンドになる。
set -u
B="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; MODE="$2"   # MODE = none | project | flag
rm -f "$B/lab/marker.txt"
rm -f "$B/lab/.claude/settings.json"

S="$B/cases/allow-touch.json"
ARGS=()
case "$MODE" in
  project) cp "$S" "$B/lab/.claude/settings.json" ;;
  flag)    ARGS=(--settings "$S") ;;
esac

cd "$B/lab" || exit 1
claude -p 'Run exactly this command with the Bash tool: touch marker.txt
Then report what happened. If it is blocked, quote the error verbatim and do NOT attempt any workaround.' \
  --output-format json --max-turns 4 --debug hooks "${ARGS[@]}" \
  > "$B/out/$CASE.json" 2> "$B/out/$CASE.debug"

if [ -f "$B/lab/marker.txt" ]; then R=CREATED; else R=blocked; fi
echo "$CASE mode=$MODE marker=$R"
