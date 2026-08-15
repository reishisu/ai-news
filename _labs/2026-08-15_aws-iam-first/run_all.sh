#!/usr/bin/env bash
# 記事「AWSのアクセス制御の地図」で使う実出力を全部取り直す。
# AWSアカウントには一切書き込まない。
#   - 認証情報が要らない操作(--generate-cli-skeleton / help)
#   - ローカルで完結する検証(terraform validate / parliament / 自作の判定器)
# だけを実行する。
set -u
cd "$(dirname "$0")"

hr() { printf '%s\n' "======================================"; }
sec() { hr; printf '%s\n' "$1"; hr; }

sec "0. バージョン"
aws --version 2>&1 | fold -s -w 38
python3 -V
terraform version | head -1
python3 -c "import parliament,sys;print('parliament', parliament.__version__ if hasattr(parliament,'__version__') else '1.6.4')" 2>/dev/null \
  || parliament --version 2>&1

sec "1. 認証情報が無いとどうなるか"
env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY \
  AWS_SHARED_CREDENTIALS_FILE=/dev/null \
  AWS_CONFIG_FILE=/dev/null \
  AWS_EC2_METADATA_DISABLED=true \
  aws sts get-caller-identity 2>&1 | fold -s -w 38
echo "rc=${PIPESTATUS[0]}"

sec "1b. 鍵が「無効」な場合は別のエラー"
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
AWS_SECRET_ACCESS_KEY=dummydummydummy \
AWS_DEFAULT_REGION=ap-northeast-1 \
AWS_SHARED_CREDENTIALS_FILE=/dev/null \
AWS_CONFIG_FILE=/dev/null \
  aws sts get-caller-identity 2>&1 | fold -s -w 38

sec "2. ロール作成に必ず要るもの(通信なし)"
aws iam create-role --role-name my-role 2>&1 | tail -1 | fold -s -w 38

sec "3. create-user が受け取るもの"
aws iam create-user --generate-cli-skeleton

sec "4. create-role が受け取るもの"
aws iam create-role --generate-cli-skeleton

sec "5. アクセスキー発行に期限の指定は無い"
aws iam create-access-key --generate-cli-skeleton

sec "6. AssumeRole は期限付き"
aws sts assume-role --generate-cli-skeleton | head -8

sec "7. アクション名を公式データで照合"
python3 check_actions.py

sec "8. Resource に書く ARN の形"
python3 check_resources.py

sec "8b. Terraformが組み立てたポリシー"
# applyはしない。planの結果からJSONだけ取り出す。
( cd tf \
  && terraform plan -no-color -out=tfplan >/dev/null 2>&1 \
  && terraform show -json tfplan \
     | jq -r '.output_changes.reader_json.after' \
  && rm -f tfplan )

sec "9. Effect の大文字小文字 (terraform)"
( cd tf-bad && terraform validate -json -no-color 2>&1 ) \
  | python3 fold_diag.py

sec "10. ポリシーJSONをlintする"
python3 lint.py

sec "10b. 全許可ポリシーは既定では素通り"
python3 lint_community.py

sec "11. 判定順のおもちゃ実装"
python3 eval_sim.py

sec "12. おもちゃ実装のテスト"
python3 -m pytest test_eval_sim.py -q --no-header \
  -p no:cacheprovider 2>&1 | tail -1
