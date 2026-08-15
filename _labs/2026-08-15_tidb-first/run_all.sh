#!/bin/bash
# 両方が起動している状態で走らせる検証を順に実行し、出力を保存する。
set -u
D="$(cd "$(dirname "$0")" && pwd)"
for f in 01_versions 02_ddl_dml 03_explain 03b_stats 04_bigtable \
         05_autoinc 05b_gap 06_compat 07_silent 08_vars \
         09_collation 09b_coll_meta 10_ddl_txn 11_explain_analyze; do
  php "$D/$f.php" > "$D/out_$f.txt" 2>&1
  printf '%-22s exit=%s\n' "$f" "$?"
done
