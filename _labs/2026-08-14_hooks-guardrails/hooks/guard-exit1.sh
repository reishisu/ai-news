#!/bin/bash
# 同じ判定だが exit 1 で返す（よくある書き間違い）
cmd=$(jq -r '.tool_input.command // ""')
case "$cmd" in
  *"git push"*)
    echo "guard: git push は禁止です (exit 1)" >&2
    exit 1 ;;
esac
exit 0
