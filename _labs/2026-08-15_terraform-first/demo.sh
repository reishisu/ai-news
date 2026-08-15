#!/usr/bin/env bash
# Terraform を最初に動かす — init / validate / plan の実出力を取る
#
#   ./demo.sh
#
# apply は一切実行しない。AWSの認証情報も使わない
# (provider にダミーを書き、検証をスキップする)。
set -u
cd "$(dirname "$0")"
BASE="$PWD"
OUT="$BASE/out"
mkdir -p "$OUT"

run() { # run <番号-名前> <terraformの引数...>
  local name="$1"; shift
  local rc
  rc=$( unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE
        script -q -e -c "stty cols 40 rows 400; cd '$BASE/hello' && terraform $* 2>&1" \
          /dev/null | tr -d '\r' > "$OUT/$name.txt"
        echo "${PIPESTATUS[0]}" )
  printf 'exit=%s\n' "$rc" > "$OUT/$name.exit"
  printf '\n########## %s : terraform %s (exit=%s)\n' "$name" "$*" "$rc"
  cat "$OUT/$name.txt"
}

# ---- 正しい設定 ----
cat > "$BASE/good.tf" <<'EOF'
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"

  # 認証情報なしで plan まで進めるためのダミー。
  # 本番の設定には絶対に書かない。
  access_key                  = "dummy"
  secret_key                  = "dummy"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
}

resource "aws_ecs_cluster" "app" {
  name = "tf-hello"

  tags = {
    Env = "sandbox"
  }
}
EOF

rm -rf "$BASE/hello"; mkdir -p "$BASE/hello"
cp "$BASE/good.tf" "$BASE/hello/main.tf"

# 1. init する前に validate してみる（初心者が必ずやる）
run 01-validate-before-init validate -no-color

# 2. init
run 02-init init -no-color

# 3. validate
run 03-validate validate -no-color

# 4. plan
run 04-plan plan -no-color

# 4b. plan がAWSに一切アクセスしていないことの確認。
#     届かないアドレスに向けても plan は通る。
cp "$BASE/good.tf" "$BASE/hello/main.tf"
python3 - "$BASE/hello/main.tf" <<'PY2'
import sys
p = sys.argv[1]
s = open(p).read()
s = s.replace('  skip_region_validation      = true\n',
              '  skip_region_validation      = true\n\n'
              '  # どこにも繋がらないアドレスに向ける\n'
              '  endpoints {\n'
              '    ecs = "http://127.0.0.1:1"\n'
              '    sts = "http://127.0.0.1:1"\n'
              '  }\n')
open(p, 'w').write(s)
PY2
run 04b-offline-endpoints plan -no-color
cp "$BASE/good.tf" "$BASE/hello/main.tf"

# 5. plan は何も作っていない（stateが空）
run 05-state-list state list -no-color

# ---- ここから、わざと壊す ----

# 6. 閉じカッコを忘れる
cp "$BASE/good.tf" "$BASE/hello/main.tf"
python3 - "$BASE/hello/main.tf" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
# resource ブロックの最後の } を消す
s = s.rstrip()
assert s.endswith('}')
open(p, 'w').write(s[:-1] + '\n')
PY
run 06-missing-brace validate -no-color

# 7. 属性名を打ち間違える (name -> nmae)
cp "$BASE/good.tf" "$BASE/hello/main.tf"
sed -i 's/^  name = "tf-hello"/  nmae = "tf-hello"/' "$BASE/hello/main.tf"
run 07-typo-argument validate -no-color

# 8. 必須の引数を書き忘れる
cp "$BASE/good.tf" "$BASE/hello/main.tf"
sed -i '/^  name = "tf-hello"$/d' "$BASE/hello/main.tf"
run 08-missing-required validate -no-color

# 9. 存在しない参照を書く
cp "$BASE/good.tf" "$BASE/hello/main.tf"
sed -i 's/^    Env = "sandbox"/    Env = aws_ecs_cluster.nope.id/' "$BASE/hello/main.tf"
run 09-bad-reference validate -no-color

# 10. = を忘れる（HCLの構文エラー）
cp "$BASE/good.tf" "$BASE/hello/main.tf"
sed -i 's/^  name = "tf-hello"/  name "tf-hello"/' "$BASE/hello/main.tf"
run 10-missing-equals validate -no-color

# 11. インデントがぐちゃぐちゃ -> fmt
cp "$BASE/good.tf" "$BASE/hello/main.tf"
sed -i 's/^resource "aws_ecs_cluster" "app" {/resource "aws_ecs_cluster"   "app" {/' "$BASE/hello/main.tf"
sed -i 's/^  name = "tf-hello"/      name="tf-hello"/' "$BASE/hello/main.tf"
run 11-fmt-check fmt -check -diff -no-color

# ---- 元に戻す ----
cp "$BASE/good.tf" "$BASE/hello/main.tf"
run 12-validate-again validate -no-color

# 13. plan をファイルに保存し、中身をJSONで読む
run 13-plan-out plan -no-color -out=tfplan
( cd "$BASE/hello" && terraform show -json tfplan ) > "$BASE/hello/tfplan.json" 2>/dev/null
python3 "$BASE/summarize_plan.py" "$BASE/hello/tfplan.json" > "$OUT/14-plan-json.txt"
printf '\n########## 14-plan-json : show -json | 要約\n'
cat "$OUT/14-plan-json.txt"

# 14b. -detailed-exitcode（差分があると 2 が返る）
run 14b-detailed-exitcode plan -no-color -detailed-exitcode -compact-warnings

# 15. required_version を満たさない場合
cp "$BASE/good.tf" "$BASE/hello/main.tf"
sed -i 's/required_version = ">= 1.5.0"/required_version = ">= 99.0.0"/' "$BASE/hello/main.tf"
run 15-version-too-new validate -no-color

# 16. ダミー認証情報も skip も書かなかったら plan はどうなるか
cp "$BASE/good.tf" "$BASE/hello/main.tf"
python3 - "$BASE/hello/main.tf" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
s = re.sub(r'\n *#[^\n]*', '', s)
s = re.sub(r'\n *(access_key|secret_key|skip_[a-z_]+)[^\n]*', '', s)
open(p, 'w').write(s)
PY
run 16-no-credentials plan -no-color

# 17. 既存リソースを読む data ソースはダミーでは通らない
cp "$BASE/good.tf" "$BASE/hello/main.tf"
cat >> "$BASE/hello/main.tf" <<'EOF'

data "aws_caller_identity" "me" {}
EOF
run 17-data-source plan -no-color

cp "$BASE/good.tf" "$BASE/hello/main.tf"

# 18. init が作ったもの / lock file の中身
{
  echo '$ ls -a'
  ( cd "$BASE/hello" && ls -a | sed 's/^/  /' )
  echo ''
  echo '$ du -sh .terraform'
  ( cd "$BASE/hello" && du -sh .terraform )
  echo ''
  echo ''
  echo '$ head -7 .terraform.lock.hcl'
  head -7 "$BASE/hello/.terraform.lock.hcl"
} > "$OUT/18-files.txt"
printf '\n########## 18-files : init が作ったもの\n'
cat "$OUT/18-files.txt"

# 19. apply は実行していない。その証拠として state を確認する
{
  echo '# apply は一度も実行していない'
  echo '$ terraform state list'
  ( cd "$BASE/hello" && terraform state list -no-color 2>&1 | head -1 | sed 's/^/  /' )
  echo '$ ls terraform.tfstate'
  ( cd "$BASE/hello" && ls terraform.tfstate 2>&1 | sed 's/^/  /' )
} > "$OUT/19-no-apply.txt"
printf '\n########## 19-no-apply : applyしていない証拠\n'
cat "$OUT/19-no-apply.txt"

python3 "$BASE/make_summary.py" "$OUT" > "$OUT/00-exitcodes.txt"
printf '\n########## 00-exitcodes : 終了コード一覧\n'
cat "$OUT/00-exitcodes.txt"

# Terraform が端末幅に合わせてくれない行(init の案内文、エラーの
# 位置表示など)のために、空白位置で折り返した版も作る。
# fold は改行を足すだけで、文字は1つも変えない。
mkdir -p "$OUT/fold40"
for f in "$OUT"/*.txt; do
  python3 "$BASE/fold40.py" < "$f" > "$OUT/fold40/$(basename "$f")"
done

{
  echo "terraform : $(terraform version -json | python3 -c 'import json,sys;print(json.load(sys.stdin)["terraform_version"])')"
  echo "platform  : $(terraform version -json | python3 -c 'import json,sys;print(json.load(sys.stdin)["platform"])')"
  ( cd "$BASE/hello" && terraform version -json ) | python3 -c 'import json,sys
d=json.load(sys.stdin)
for k,v in (d.get("provider_selections") or {}).items():
    print("provider  : %s" % k.split("/",1)[1])
    print("            %s" % v)'
  echo "python3   : $(python3 -V)"
  echo "date(UTC) : $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
} > "$OUT/99-versions.txt"
printf '\n########## 99-versions : 実行環境\n'
cat "$OUT/99-versions.txt"

printf '\n########## fold40 が中身を変えていないかの確認\n'
python3 "$BASE/verify_fold.py" "$OUT" "$OUT/fold40" | tee "$OUT/98-fold-verify.txt"

printf '\n########## 表示幅チェック (40桁超えの行数)\n'
python3 "$BASE/widthcheck.py" "$OUT" "$OUT/fold40"

printf '\n########## exit code 一覧\n'
for f in "$OUT"/*.exit; do
  printf '%-22s %s\n' "$(basename "$f" .exit)" "$(cat "$f")"
done
