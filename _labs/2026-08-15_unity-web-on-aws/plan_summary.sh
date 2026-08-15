#!/bin/bash
# terraform plan の結果を、幅の狭い画面でも読める形にして出す。
# apply はしない。
set -eu
cd "$(dirname "$0")"

terraform plan -no-color -out=tfplan > plan.txt 2>&1
terraform show -json tfplan > plan.json

echo "■ 変更の件数"
jq -r '[.resource_changes[].change.actions[]]
       | group_by(.) | map("\(.[0]) : \(length)件")[]' plan.json

echo
echo "■ 作られるもの"
jq -r '.resource_changes[] | .type' plan.json

echo
echo "■ 付けるヘッダー"
jq -r '.resource_changes[].change.after
       .custom_headers_config[].items[]
       | "  " + .header, "      " + .value' plan.json
