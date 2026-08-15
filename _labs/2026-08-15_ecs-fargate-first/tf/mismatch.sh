#!/bin/bash
# タスク定義のコンテナ名は web のまま、
# サービス側だけ typo("wev")にして plan する。
terraform validate -no-color 2>&1 | tail -3
terraform plan -no-color \
  -var 'lb_container_name=wev' \
  -out=plan-typo.bin > /dev/null 2>&1
echo "plan exit = $?"
terraform show -json plan-typo.bin | jq -r '
  .resource_changes[]
  | select(.type=="aws_ecs_service")
  | .change.after.load_balancer[0].container_name
  | "service が指す名前 : \(.)"'
terraform show -json plan-typo.bin | jq -r '
  .resource_changes[]
  | select(.type=="aws_ecs_task_definition")
  | (.change.after.container_definitions | fromjson)[0].name
  | "taskdef の名前     : \(.)"'
