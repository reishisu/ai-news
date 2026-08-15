#!/usr/bin/env bash
# config:cache を打つと .env が読まれなくなることの実証。
# 使い方: bash configcache.sh <example-app のパス>
set -u
APP="${1:?usage: bash configcache.sh <app dir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
export COLUMNS=40 NO_COLOR=1
run() { env -u CLAUDECODE -u AI_AGENT "$@"; }
narrow() { python3 "$HERE/narrow.py" 40; }
key() { ( cd "$APP" && run php artisan tinker --execute \
          'echo config("app.key") ? "key: あり" : "key: なし";' ) ; echo; }

echo "===== 0. .env に鍵がある状態 ====="
grep -c '^APP_KEY=base64:' "$APP/.env" | sed 's/^/.env の鍵の行数: /'
key

echo
echo "===== 1. config:cache を打つ ====="
( cd "$APP" && run php artisan config:cache 2>&1 ) | narrow

echo
echo "===== 2. .env の APP_KEY を空に ====="
sed -i 's|^APP_KEY=.*|APP_KEY=|' "$APP/.env"
grep '^APP_KEY' "$APP/.env"
key

echo
echo "===== 3. config:clear を打つ ====="
( cd "$APP" && run php artisan config:clear 2>&1 ) | narrow
key

echo
echo "===== 4. 鍵を作り直して後片付け ====="
( cd "$APP" && run php artisan key:generate 2>&1 ) | narrow
