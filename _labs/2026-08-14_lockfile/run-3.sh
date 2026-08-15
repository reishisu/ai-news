#!/usr/bin/env bash
# 追試16: git(GitHub)指定の依存が npm12 で止まるかを実測する
# 使い方: bash run-3.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work3"; rm -rf "$WORK"; mkdir -p "$WORK"; cd "$WORK"
NPM12_BIN="${NPM12_BIN:-}"   # npm 12 の npm-cli.js への絶対パス
[ -n "$NPM12_BIN" ] || { echo "NPM12_BIN を指定してください"; exit 1; }

export npm_config_cache="$WORK/c"
export npm_config_audit=false npm_config_fund=false npm_config_progress=false
export npm_config_update_notifier=false

printf '{"name":"g","version":"1.0.0","dependencies":{"isarray":"github:juliangruber/isarray"}}\n' > package.json

echo "-- npm 10 --"
npm install 2>&1 | grep -v '^$' | head -1 | fold -s -w 38
rm -rf node_modules package-lock.json "$WORK/c"

echo "-- npm 12 --"
node "$NPM12_BIN" install 2>&1 | grep -v 'A complete log' | head -3 | fold -s -w 38
