#!/usr/bin/env bash
# stale_v1.sh — よくある「N日以上動いていないブランチ」検出(決め打ちしきい値)
# 使い方: ./stale_v1.sh <repo> [trunk]
#   NOW_TS=<epoch> で現在時刻を固定できる
set -u
REPO="${1:-.}"; TRUNK="${2:-origin/main}"
DAYS="${DAYS:-7}"
NOW="${NOW_TS:-$(date +%s)}"
CUT=$(( NOW - DAYS*86400 ))

echo "== ${DAYS}日以上 動いていない枝 =="
n=0; seen=0
for ref in $(git -C "$REPO" for-each-ref \
             --format='%(refname:short)' refs/remotes refs/heads); do
  case "$ref" in */HEAD) continue;; esac
  [ "$ref" = "$TRUNK" ] && continue
  git -C "$REPO" merge-base --is-ancestor "$ref" "$TRUNK" && continue
  seen=$((seen+1))
  ts=$(git -C "$REPO" log -1 --format='%ct' "$ref")
  if [ "$ts" -lt "$CUT" ]; then
    echo "[!] ${ref#origin/}"
    n=$((n+1))
  fi
done
echo "検出 ${n}件 / 未統合 ${seen}件"
echo "しきい値 ${DAYS}日 (決め打ち)"
