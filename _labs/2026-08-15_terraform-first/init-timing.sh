#!/usr/bin/env bash
# init の所要時間と、init 直後のディレクトリの中身を測り直す。
#
#   ./init-timing.sh
#
# 元の demo.sh は `ls -a` を plan -out=tfplan のあとに撮っていたため、
# 出力に tfplan / tfplan.json が写り込んでいた。
# ここでは init を打った直後に撮り直す。所要時間も同時に測る。
#
# apply は実行しない。AWS の本物の認証情報も使わない。
set -u
cd "$(dirname "$0")"
BASE="$PWD"
OUT="$BASE/out"
WORK="$BASE/hello-init"
mkdir -p "$OUT"

unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE
unset TF_PLUGIN_CACHE_DIR

{
  echo "# init の所要時間（クリーンな作業ディレクトリ / プラグインキャッシュ無し）"
  echo "# date(UTC) : $(date -u +%FT%TZ)"
  terraform version | head -2 | sed 's/^/# /'
  echo
  for i in 1 2 3; do
    rm -rf "$WORK"; mkdir -p "$WORK"
    cp "$BASE/good.tf" "$WORK/main.tf"
    start=$(date +%s.%N)
    ( cd "$WORK" && terraform init -no-color >/dev/null 2>&1 )
    rc=$?
    end=$(date +%s.%N)
    printf 'run%d  exit=%s  %.2f sec\n' "$i" "$rc" "$(echo "$end - $start" | bc)"
  done
} > "$OUT/20-init-time.txt"

# init 直後のディレクトリの中身（幅40桁の擬似端末で採取）
script -q -e -c "stty cols 40 rows 200; cd '$WORK' && \
  echo '\$ ls -a' && ls -a | sed 's/^/  /' && \
  echo && echo '\$ du -sh .terraform' && du -sh .terraform && \
  echo && echo '\$ head -7 .terraform.lock.hcl' && head -7 .terraform.lock.hcl" \
  /dev/null | tr -d '\r' > "$OUT/21-files-after-init.txt"

cat "$OUT/20-init-time.txt"
echo
cat "$OUT/21-files-after-init.txt"
