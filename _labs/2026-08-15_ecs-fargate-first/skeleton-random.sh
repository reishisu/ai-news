#!/bin/bash
# 雛形の networkMode を10回続けて出す。
for i in $(seq 10); do
  aws ecs register-task-definition \
    --generate-cli-skeleton | jq -r .networkMode
done | sort | uniq -c | sed 's/^ */  /'
