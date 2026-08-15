#!/bin/bash
cmd=$(jq -r '.tool_input.command // ""')
case "$cmd" in
  *"git push"*) echo "push禁止" >&2; exit 2 ;;
esac
exit 0
