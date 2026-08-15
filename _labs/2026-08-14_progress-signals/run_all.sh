#!/usr/bin/env bash
# run_all.sh — 全部まとめて再現する
set -u
cd "$(dirname "$0")"
REAL="${REAL_REPO:-/home/user/ai-news}"
FIXNOW=2026-08-10T00:00:00Z
FIXTS=$(date -u -d "$FIXNOW" +%s)

./make_fixture.sh fixture >/dev/null

echo "=== A 実リポジトリ / 7日決め打ち ==="
./stale_v1.sh "$REAL" origin/main
echo
echo "=== B 実リポジトリ / SLE ==="
python3 flow_signals.py "$REAL"
echo
echo "=== C 検証用 / 7日決め打ち ==="
NOW_TS=$FIXTS ./stale_v1.sh fixture main
echo
echo "=== D 検証用 / SLE ==="
python3 flow_signals.py fixture --trunk main --now "$FIXNOW"
echo
echo "=== E 未統合ゼロのとき ==="
rm -rf fixture-clean && cp -r fixture fixture-clean
git -C fixture-clean branch -D hot warm cold >/dev/null 2>&1
python3 flow_signals.py fixture-clean --trunk main --now "$FIXNOW"
