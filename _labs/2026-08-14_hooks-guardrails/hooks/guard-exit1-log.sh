#!/bin/bash
# exit 1 版。フックが実際に起動したことを残すためログを書く。
LOG="/tmp/claude-0/-home-user-ai-news/218add4d-91bf-5dd6-8681-3e6fbe7a6b0f/scratchpad/2026-08-14_hooks-guardrails/out/05b-hook.log"
cmd=$(jq -r '.tool_input.command // ""')
case "$cmd" in
  *"git push"*)
    echo "fired: $cmd" >> "$LOG"
    echo "guard: git push は禁止です (exit 1)" >&2
    exit 1 ;;
esac
exit 0
