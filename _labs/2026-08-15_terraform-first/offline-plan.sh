#!/usr/bin/env bash
# plan が本当にネットワークを使っていないかを、いちばん強い形で確かめる。
#
#   ./offline-plan.sh
#
# 記事本文の実験は「プロバイダの接続先を届かないアドレスに向ける」だけだが、
# ここでは unshare -n でネットワーク名前空間ごと切り離す。
# ループバック以外の経路が無い状態で terraform plan を回す。
#
# 前提: ./init-timing.sh を先に実行して hello-init/ が init 済みであること。
set -u
cd "$(dirname "$0")"
BASE="$PWD"
OUT="$BASE/out"
WORK="$BASE/hello-init"

mkdir -p "$OUT"

# terraform の出力は端末幅に合わせて折り返されるので、パイプを挟まず
# 擬似端末(40桁)に直接出させる。
script -q -e -c "stty cols 40 rows 400; unshare -n -- bash -c \"
  echo '# ネットワークを切り離した中で実行';
  echo '\\\$ curl -sm5 https://sts.amazonaws.com';
  curl -sm5 -o /dev/null https://sts.amazonaws.com;
  echo '  exit='\\\$?' (0以外 = 外に出られない)';
  echo;
  echo '\\\$ terraform plan';
  cd '$WORK' && terraform plan -no-color;
  echo '  exit='\\\$?
\"" /dev/null | tr -d '\r' > "$OUT/22-offline-plan.txt"

cat "$OUT/22-offline-plan.txt"
