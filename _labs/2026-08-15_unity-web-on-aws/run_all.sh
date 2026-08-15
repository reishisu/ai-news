#!/bin/bash
# 記事に貼った実測を、まとめて取り直す。
# 使い方: ./run_all.sh   (出力は output.txt)
set -u
cd "$(dirname "$0")"

export NODE_PATH=/opt/node22/lib/node_modules/playwright/node_modules

{
  echo "### 環境"
  python3 -V
  node -v
  /opt/pw-browsers/chromium --version
  terraform version | head -1
  aws --version 2>&1 | cut -d' ' -f1
  echo

  python3 make_assets.py
  echo

  python3 serve.py &
  SRV=$!
  until curl -sf -o /dev/null http://127.0.0.1:8821/plain/; do sleep 0.2; done

  echo "### ブラウザでの実測"
  node probe.js
  echo

  echo "### 配信ヘッダーの確認"
  ./check_headers.sh http://127.0.0.1:8821/coi/
  echo
  ./check_headers.sh http://127.0.0.1:8821/w/br

  kill $SRV
  echo

  echo "### aws s3 cp が付ける Content-Type"
  echo "(S3には上げていない)"
  python3 s3_guess.py
  echo

  echo "### 本物のAWSは触れない"
  ./aws_creds.sh
  echo

  echo "### CloudFront の雛形(認証情報なし)"
  ./aws_check.sh
  echo

  echo "### terraform (apply はしない)"
  ./tf_check.sh
  echo
  ./plan_summary.sh
} 2>&1 | tee output.txt
