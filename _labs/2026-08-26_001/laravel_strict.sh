#!/usr/bin/env bash
# Laravel の in_array / doesnt_contain / contains ルールが
# 厳密比較になったかを、2つのタグのソースから直接見る。
# 出力は幅380pxに収まる長さに切っている（CLAUDE.md 第4節）。
set -u
F=src/Illuminate/Validation/Concerns/ValidatesAttributes.php
for t in v13.26.1 v13.27.0; do
  curl -sS -o "/tmp/va_$t.php" \
    "https://raw.githubusercontent.com/laravel/framework/$t/$F"
done
for r in validateInArray validateDoesntContain validateContains; do
  echo "-- $r"
  # 差分は行末に出るので、接頭辞は1桁に切り詰める（幅380px＝半角約38字）
  # - が v13.26.1、+ が v13.27.0
  for t in v13.26.1 v13.27.0; do
    [ "$t" = v13.26.1 ] && m=- || m=+
    printf '%s %s\n' "$m" \
      "$(grep -A18 "function $r" "/tmp/va_$t.php" \
         | grep -om1 'in_array([^;]*)')"
  done
done
