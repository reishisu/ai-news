#!/bin/bash
# フックが allow を返しても deny ルールを上書きできるか
echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"guard allows"}}'
exit 0
