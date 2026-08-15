#!/bin/bash
# usage: drive.sh <case> <settings.json> [prompt]
# 1ケース分を走らせる。remote.git の main が動いたかどうかが唯一の真実。
set -u
B="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; SETTINGS="$2"
PROMPT="${3:-Run exactly this command with the Bash tool: git push origin main
Then report what happened. If it is blocked, quote the error text verbatim and do NOT attempt any workaround.}"
BASESHA="$(cat "$B/base.sha")"

# --- リセット: ローカルもリモートも初期コミットへ戻す ---
git -C "$B/lab" reset -q --hard "$BASESHA"
git --git-dir="$B/remote.git" update-ref refs/heads/main "$BASESHA"
# --- push されるべき新コミットを1つ作る ---
echo "$CASE" > "$B/lab/app.txt"
git -C "$B/lab" add -A
git -C "$B/lab" commit -q -m "$CASE"

BEFORE="$(git --git-dir="$B/remote.git" rev-parse --short main)"
rm -f "$B/lab/.claude/settings.json"

cd "$B/lab" || exit 1
claude -p "$PROMPT" --settings "$B/$SETTINGS" --output-format json --max-turns 4 --debug hooks \
  > "$B/out/$CASE.json" 2> "$B/out/$CASE.debug"
RC=$?

AFTER="$(git --git-dir="$B/remote.git" rev-parse --short main)"
printf '%s %s %s %s\n' "$CASE" "$RC" "$BEFORE" "$AFTER" > "$B/out/$CASE.truth"
echo "done $CASE rc=$RC $BEFORE->$AFTER"
