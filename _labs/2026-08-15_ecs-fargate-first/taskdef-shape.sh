#!/bin/bash
# register-task-definition の雛形。
# containerDefinitions は巨大なので鍵だけ別に出す。
S=$(aws ecs register-task-definition \
      --generate-cli-skeleton)
echo "== タスク定義の直下(抜粋) =="
echo "$S" | jq '{family, cpu, memory,
  networkMode, requiresCompatibilities,
  executionRoleArn, taskRoleArn}'
echo
echo "== containerDefinitions[0] の鍵 =="
echo "$S" | jq -r '.containerDefinitions[0]
  | keys[]' | paste -sd' ' - | fold -s -w 38
