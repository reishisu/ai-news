#!/bin/bash
# 認証情報を持たないまま init / validate / plan まで通す。
# apply は実行しない(できない)。
set -eu
cd "$(dirname "$0")"

terraform -version | head -1
terraform init -no-color -input=false > /dev/null
terraform validate -no-color
terraform plan -no-color -out=tfplan > plan.txt 2>&1
grep -E "^Plan:" plan.txt | fold -s -w 38
echo "apply は実行していない"
