#!/bin/bash
# CloudFront のレスポンスヘッダーポリシーで、
# COOP/COEP/CORP をどこに書くのかを CLI の雛形から確かめる。
# 認証情報は使わない(--generate-cli-skeleton はローカルで完結)。
set -u
cd "$(dirname "$0")"

aws cloudfront create-response-headers-policy \
  --generate-cli-skeleton > skeleton.json

echo "■ SecurityHeadersConfig の中身"
jq -r '.ResponseHeadersPolicyConfig
       .SecurityHeadersConfig | keys[]' skeleton.json

echo
echo "■ 雛形に Cross-Origin という語が出る回数"
grep -c "Cross-Origin" skeleton.json

echo
echo "■ 自由に足せる枠"
jq -r '.ResponseHeadersPolicyConfig
       .CustomHeadersConfig.Items[0] | keys[]' skeleton.json
