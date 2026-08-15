#!/bin/bash
# 引数のJSONを register-task-definition に渡す。
# 出力は38桁で折り返して貼れる幅にする。
R=ap-northeast-1
for f in "$@"; do
  echo "--- $f"
  aws ecs register-task-definition \
    --cli-input-json "file://$f" --region $R 2>&1 \
    | fold -s -w 38
done
