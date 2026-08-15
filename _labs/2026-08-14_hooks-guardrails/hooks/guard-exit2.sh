#!/bin/bash
# PreToolUse フック: git push だけを exit 2 で止める
cmd=$(jq -r '.tool_input.command // ""')
case "$cmd" in
  *"git push"*)
    echo "guard: git push は禁止です (exit 2)" >&2
    exit 2 ;;
esac
exit 0
