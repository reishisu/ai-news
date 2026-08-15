#!/bin/bash
# plan.bin から「作られるもの」を1行ずつ短く出す。
# 出力幅を38桁に収めるため type から aws_ を落とす。
terraform show -json plan.bin \
| jq -r '.resource_changes[]
  | select(.change.actions[0]=="create")
  | (.type | sub("^aws_";"")) + "  " + .name' \
| sort
echo "----"
terraform show -json plan.bin \
| jq -r '.resource_changes | length | "作成: \(.) 件"'
