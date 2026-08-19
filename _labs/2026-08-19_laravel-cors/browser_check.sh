#!/usr/bin/env bash
# 「サーバーは配る。止めるのはブラウザ」を、同じサーバー・同じ設定に対して
# curl と Chromium の両方から叩いて確かめる。
#
#   bash browser_check.sh [アプリの場所] [APIのポート] [ページのポート]
set -u

APP="${1:-/tmp/cors-lab}"
PORT="${2:-8123}"
PAGEPORT="${3:-8130}"
LAB="$(cd "$(dirname "$0")" && pwd)"
API="http://127.0.0.1:$PORT/api/hello"
PAGE="http://127.0.0.1:$PAGEPORT/"
SRVCFG="http://127.0.0.1:$PORT/api/corsconfig"
export NODE_PATH="${NODE_PATH:-/opt/node22/lib/node_modules}"

narrow() { tr -d '\r' | python3 "$LAB/narrow.py"; }
port_busy() { (echo > "/dev/tcp/127.0.0.1/$1") 2>/dev/null; }

cleanup() {
  for f in "$LAB/.api.pid" "$LAB/.page.pid"; do
    [ -f "$f" ] && { kill "$(cat "$f")" 2>/dev/null; sleep 1; pkill -P "$(cat "$f")" 2>/dev/null; rm -f "$f"; }
  done
}
trap cleanup EXIT

for p in "$PORT" "$PAGEPORT"; do
  port_busy "$p" && { echo "!! ポート $p が使用中です" >&2; exit 1; }
done

# 設定が反映されるまで待つ(OPcache対策。run_tests.sh と同じ理由)
wait_cfg() {
  local want got i
  want="$( cd "$APP" && php -r '$c = require "config/cors.php";
    echo json_encode([$c["allowed_origins"], $c["supports_credentials"]]);' )"
  for i in $(seq 1 40); do
    got="$(curl -s "$SRVCFG")"; [ "$got" = "$want" ] && return 0; sleep 0.5
  done
  echo "!! 設定が反映されませんでした 期待:$want 実際:$got" >&2; exit 1
}

cp "$LAB/configs/03-allowlist-2.php" "$APP/config/cors.php"
( cd "$APP" && php artisan config:clear >/dev/null 2>&1 )
( cd "$APP" && exec php artisan serve --host=127.0.0.1 --port="$PORT" ) \
    > "$LAB/serve.log" 2>&1 &
echo $! > "$LAB/.api.pid"
( cd "$LAB/page" && exec python3 -m http.server "$PAGEPORT" --bind 127.0.0.1 ) \
    > "$LAB/page.log" 2>&1 &
echo $! > "$LAB/.page.pid"
for _ in $(seq 1 30); do curl -s -o /dev/null "$API" && break; sleep 1; done
for _ in $(seq 1 30); do curl -s -o /dev/null "$PAGE" && break; sleep 1; done
wait_cfg

echo "================================"
echo "許可リストにページのオリジンが無い"
echo "================================"
( cd "$APP" && php artisan config:show cors ) 2>&1 | grep -A3 allowed_origins | narrow
echo
echo "-- curl から (ブラウザではない)"
echo "\$ curl -s -o /dev/null -D - \\"
echo " -H \"Origin: http://127.0.0.1:$PAGEPORT\" \\"
echo " \"\$API\""
curl -s -o /dev/null -D - -H "Origin: http://127.0.0.1:$PAGEPORT" "$API" \
  | grep -iE '^(HTTP/|Access-Control|Vary)' | narrow
echo
echo "\$ curl -s \"\$API\""
curl -s "$API" | narrow
echo
echo "-- Chromium から"
node "$LAB/browser_check.js" "$PAGE" "$API" 2>&1 | narrow

echo
echo "================================"
echo "ページのオリジンを許可リストに足す"
echo "================================"
cp "$LAB/configs/06-allow-page-origin.php" "$APP/config/cors.php"
wait_cfg
( cd "$APP" && php artisan config:show cors ) 2>&1 | grep -A3 allowed_origins | narrow
echo
echo "-- Chromium から(設定を足したあと)"
node "$LAB/browser_check.js" "$PAGE" "$API" 2>&1 | narrow

echo
cleanup
echo "サーバーを止めました"
