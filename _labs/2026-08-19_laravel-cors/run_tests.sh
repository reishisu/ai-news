#!/usr/bin/env bash
# LaravelのCORSを curl で実測する。
#
#   bash run_tests.sh [アプリの場所] [ポート]         # 記事用(40桁に折り返す)
#   NARROW=0 bash run_tests.sh [アプリの場所] [ポート]  # 生のヘッダーを全部
#
# ・表示するコマンド文字列と eval に渡す文字列は同一。ズレようがない。
# ・コマンドはすべてアプリのディレクトリで実行する(パスを短く保つため)。
# ・折り返し(narrow.py)以外、出力は一切加工していない。
set -u

APP="${1:-/tmp/cors-lab}"
PORT="${2:-8123}"
NARROW="${NARROW:-1}"
LAB="$(cd "$(dirname "$0")" && pwd)"

# コマンドの中で使う変数。長いURLを直書きしないで済ませるため。
export API="http://127.0.0.1:$PORT/api/hello"
export WEB="http://127.0.0.1:$PORT/hello"
export OK_ORIGIN="https://game.example.com"
export NG_ORIGIN="https://evil.example.com"
export CFG="$LAB/configs"
export COLUMNS=40          # artisan の表を40桁に収める
SRVCFG="http://127.0.0.1:$PORT/api/corsconfig"
export SAPI="http://127.0.0.1:$PORT/api/sapi"

# ---- 出力の整形 -------------------------------------------------
narrow() { if [ "$NARROW" = "1" ]; then tr -d '\r' | python3 "$LAB/narrow.py"; else tr -d '\r'; fi; }
heads()  { if [ "$NARROW" = "1" ]; then grep -iE '^(HTTP/|Access-Control|Vary)'; else cat; fi; }

run()  { echo "\$ $1"; ( cd "$APP" && eval "$1" ) 2>&1 | narrow; echo; }
show() { echo "\$ $1"; ( cd "$APP" && eval "$1" ) 2>&1 | heads | narrow; echo; }

sec() { echo; echo "================================"; echo "$1"; echo "================================"; }
sub() { echo; echo "-- $1"; }

# ---- 設定の入れ替え ---------------------------------------------
# php artisan serve は cli-server SAPI で動き、そこでは opcache.enable_cli=0
# でも **OPcacheが有効** (opcache.revalidate_freq=2秒)。
# config/cors.php を cp した直後に測ると、古い設定のまま返ってくることがある。
# 実際これで3回の実行が3回とも違う結果になった（README「ハマった点」）。
# なので「サーバー自身が新しい設定を見た」と言うまで待ってから測る。
wait_cfg() {
  local want got i
  want="$( cd "$APP" && php -r '$c = require "config/cors.php";
    echo json_encode([$c["allowed_origins"], $c["supports_credentials"]]);' )"
  for i in $(seq 1 40); do
    got="$(curl -s "$SRVCFG")"
    [ "$got" = "$want" ] && return 0
    sleep 0.5
  done
  echo "!! 設定がサーバーに反映されませんでした" >&2
  echo "   期待: $want" >&2
  echo "   実際: $got" >&2
  exit 1
}
wait_default() {          # config/cors.php を消した状態(=フレームワーク既定)を待つ
  local got i
  for i in $(seq 1 40); do
    got="$(curl -s "$SRVCFG")"
    [ "$got" = '[["*"],false]' ] && return 0
    sleep 0.5
  done
  echo "!! 既定値に戻りませんでした (実際: $got)" >&2
  exit 1
}

# ---- サーバー ---------------------------------------------------
# 注意: php artisan serve は「親(artisan) + 子(php -S)」の2プロセス。
# 親は子が死ぬと**勝手に建て直す**ので、子だけ殺すと孤児が残って
# ポートを掴み続ける。必ず親 → 子 の順で殺すこと。
# (これを間違えて、前回の測定値が1回だけ再現しなかった。README参照)
port_busy() { (echo > "/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; }

start_server() {
  if port_busy; then
    echo "!! ポート $PORT は既に使われています。" >&2
    echo "   別のサーバーが応答すると測定値が汚れるので中止します。" >&2
    exit 1
  fi
  # exec を付けると、サブシェルが php 本体に置き換わるので
  # $! が「artisan serve のPID」になる。付けないと中間のシェルのPIDが取れ、
  # kill しても artisan serve が生き残ってポートを掴み続ける。
  ( cd "$APP" && exec php artisan serve --host=127.0.0.1 --port="$PORT" ) \
      > "$LAB/serve.log" 2>&1 &
  echo $! > "$LAB/serve.pid"
  for _ in $(seq 1 30); do
    curl -s -o /dev/null "$API" && return 0
    sleep 1
  done
  echo "!! サーバーが起動しませんでした。$LAB/serve.log を見てください" >&2
  cat "$LAB/serve.log" >&2
  exit 1
}
stop_server() {
  if [ -f "$LAB/serve.pid" ]; then
    P="$(cat "$LAB/serve.pid")"
    kill "$P" 2>/dev/null         # 先に親(artisan serve)
    sleep 1
    pkill -P "$P" 2>/dev/null     # 残っていれば子(php -S)
    rm -f "$LAB/serve.pid"
  fi
  for _ in $(seq 1 10); do
    port_busy || return 0
    sleep 1
  done
  echo "!! ポート $PORT がまだ塞がっています" >&2
}
trap stop_server EXIT

# 前回の config:cache が残っていると実験1が狂うので必ず消す
( cd "$APP" && php artisan config:clear >/dev/null 2>&1 )

# php artisan serve をここで起こす。以降のcurlは全部これに当たる。
start_server

# =================================================================
sec "0. 環境"
run "php artisan --version"
run "php -r 'echo PHP_VERSION,PHP_EOL;'"
echo "コマンドの中で使う変数:"
echo "API=$API"
echo "WEB=$WEB"
echo "OK_ORIGIN=$OK_ORIGIN"
echo "NG_ORIGIN=$NG_ORIGIN"

sub "0a. CORSは全リクエストを通る"
run 'php artisan tinker --execute='"'"'
use Illuminate\Contracts\Http\Kernel;
foreach (app(Kernel::class)
  ->getGlobalMiddleware() as $m)
  echo class_basename($m), PHP_EOL;'"'"''

sub "0b. serve は cli-server + OPcache"
run 'curl -s "$SAPI" | jq -r ".[]"'

# =================================================================
sec "1. config/cors.php が無い状態"
rm -f "$APP/config/cors.php"
wait_default
echo "(config/cors.php は置いていない)"

sub "1a. それでも設定は存在する"
run "php artisan config:show cors"

sub "1b. api/* のGETに Origin を付ける"
show 'curl -s -o /dev/null -D - \
 -H "Origin: $OK_ORIGIN" \
 "$API"'

sub "1c. api/ で始まらないパスに同じことを"
show 'curl -s -o /dev/null -D - \
 -H "Origin: $OK_ORIGIN" \
 "$WEB"'

sub "1d. Origin を付けない"
show 'curl -s -o /dev/null -D - "$API"'

# =================================================================
sec "2. 許可オリジンを1件だけ書く"
sub "2a. 設定ファイルを出す"
run "php artisan config:publish cors"
run 'cp $CFG/02-allowlist-1.php \
 config/cors.php'
wait_cfg
run "php artisan config:show cors"

sub "2b. 許可したオリジンから"
show 'curl -s -o /dev/null -D - \
 -H "Origin: $OK_ORIGIN" \
 "$API"'

sub "2c. 許可していないオリジンから"
show 'curl -s -o /dev/null -D - \
 -H "Origin: $NG_ORIGIN" \
 "$API"'

sub "2d. 本文は返ってくるのか"
run 'curl -s \
 -H "Origin: $NG_ORIGIN" \
 "$API"'

# =================================================================
sec "3. 許可オリジンを2件にする"
run 'cp $CFG/03-allowlist-2.php \
 config/cors.php'
wait_cfg
run "php artisan config:show cors"

sub "3a. 許可したオリジンから"
show 'curl -s -o /dev/null -D - \
 -H "Origin: $OK_ORIGIN" \
 "$API"'

sub "3b. 許可していないオリジンから"
show 'curl -s -o /dev/null -D - \
 -H "Origin: $NG_ORIGIN" \
 "$API"'

# =================================================================
sec "4. preflight (OPTIONS)"
echo "(許可オリジン2件のまま)"

sub "4a. 許可したオリジンから"
show 'curl -s -o /dev/null -D - -X OPTIONS \
 -H "Origin: $OK_ORIGIN" \
 -H "Access-Control-Request-Method: \
POST" \
 -H "Access-Control-Request-Headers: \
content-type" \
 "$API"'

sub "4b. 許可していないオリジンから"
show 'curl -s -o /dev/null -D - -X OPTIONS \
 -H "Origin: $NG_ORIGIN" \
 -H "Access-Control-Request-Method: \
POST" \
 -H "Access-Control-Request-Headers: \
content-type" \
 "$API"'

sub "4c. 許可オリジンが1件だけのとき"
run 'cp $CFG/02-allowlist-1.php \
 config/cors.php'
wait_cfg
show 'curl -s -o /dev/null -D - -X OPTIONS \
 -H "Origin: $NG_ORIGIN" \
 -H "Access-Control-Request-Method: \
POST" \
 -H "Access-Control-Request-Headers: \
content-type" \
 "$API"'

sub "4d. cors.paths に入らないパスへ"
show 'curl -s -o /dev/null -D - -X OPTIONS \
 -H "Origin: $OK_ORIGIN" \
 -H "Access-Control-Request-Method: \
POST" \
 "$WEB"'

# =================================================================
sec "5. Origin: null"
run 'cp $CFG/03-allowlist-2.php \
 config/cors.php'
wait_cfg

sub "5a. null を許可リストに入れていない"
show 'curl -s -o /dev/null -D - \
 -H "Origin: null" \
 "$API"'

sub "5b. null を許可リストに入れた"
run 'cp $CFG/04-allowlist-null.php \
 config/cors.php'
wait_cfg
run "php artisan config:show cors"
show 'curl -s -o /dev/null -D - \
 -H "Origin: null" \
 "$API"'

# =================================================================
sec "6. '*' と credentials を同時に"
run 'cp $CFG/05-star-credentials.php \
 config/cors.php'
wait_cfg
run "php artisan config:show cors"

sub "6a. Origin を付けたGET"
show 'curl -s -o /dev/null -D - \
 -H "Origin: $NG_ORIGIN" \
 "$API"'

sub "6b. Origin を付けないGET"
show 'curl -s -o /dev/null -D - "$API"'

sub "6c. preflight"
show 'curl -s -o /dev/null -D - -X OPTIONS \
 -H "Origin: $NG_ORIGIN" \
 -H "Access-Control-Request-Method: \
POST" \
 -H "Access-Control-Request-Headers: \
content-type" \
 "$API"'

# =================================================================
sec "7. config:cache の罠"
run 'cp $CFG/02-allowlist-1.php \
 config/cors.php'
wait_cfg
run "php artisan config:cache"

sub "7a. キャッシュ後に設定を書き換える"
run 'cp $CFG/03-allowlist-2.php \
 config/cors.php'
run "php artisan config:show cors"
show 'curl -s -o /dev/null -D - \
 -H "Origin: https://app.example.com" \
 "$API"'

sub "7b. config:clear のあと"
run "php artisan config:clear"
wait_cfg
show 'curl -s -o /dev/null -D - \
 -H "Origin: https://app.example.com" \
 "$API"'

sec "おわり"
stop_server
echo "サーバーを止めました"
