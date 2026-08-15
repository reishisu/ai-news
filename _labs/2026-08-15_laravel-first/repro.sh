#!/usr/bin/env bash
# Laravel を最初に動かすまで — 実証スクリプト
#
# 使い方:  bash repro.sh <作業ディレクトリ>
# 出力幅は narrow.py で 40 桁に丸めています(記事掲載用)。
# 中身は一切書き換えていません。折り返しのみです。
set -u

WORK="${1:?usage: bash repro.sh <workdir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
APP="$WORK/example-app"
PORT="${PORT:-8902}"

export COMPOSER_ALLOW_SUPERUSER=1
# COLUMNS を渡すと Symfony Console が狭い幅で整形する
export COLUMNS=40
export NO_COLOR=1

# laravel/agent-detector が CLAUDECODE / AI_AGENT を見て
# 出力を JSON に切り替えるため、人間と同じ表示にするには外す
run() { env -u CLAUDECODE -u AI_AGENT "$@"; }
narrow() { python3 "$HERE/narrow.py" 40; }
sec() { printf '\n===== %s =====\n' "$1"; }

mkdir -p "$WORK"

sec "0. 環境"
php -v | head -1 | narrow
composer -V 2>/dev/null | grep '^Composer' | narrow

sec "1. composer create-project"
( cd "$WORK" && run composer create-project laravel/laravel example-app \
    > "$WORK/create.log" 2>&1 )
echo "exit=$?"
echo "--- ログ末尾(post-create-project) ---"
grep -E 'key:generate|Application key|migrate --graceful' "$WORK/create.log" \
  | narrow

sec "2. .env の APP_KEY を見る"
grep '^APP_KEY' "$APP/.env"     | cut -c1-40
echo "^ create-project が自動生成済み"
grep '^APP_KEY' "$APP/.env.example" | cut -c1-40
echo "^ .env.example は空のまま"

sec "3. ここで php artisan test"
( cd "$APP" && run php artisan test 2>&1 ) | narrow
echo "exit=${PIPESTATUS[0]}"

sec "4. git clone 直後を再現"
echo "(.env.example をコピー = APP_KEY 空)"
cp "$APP/.env.example" "$APP/.env"
grep '^APP_KEY' "$APP/.env"

sec "5. APP_KEY 空で test"
( cd "$APP" && run php artisan test 2>&1 ) > "$WORK/fail.log" 2>&1
echo "exit=$?"
head -9 "$WORK/fail.log" | narrow

sec "6. php artisan key:generate"
( cd "$APP" && run php artisan key:generate 2>&1 ) | narrow

sec "7. もう一度 php artisan test"
( cd "$APP" && run php artisan test 2>&1 ) | narrow
echo "exit=${PIPESTATUS[0]}"

sec "8. ルートを1本足す"
cat >> "$APP/routes/web.php" <<'PHP'

Route::get('/hello', function () {
    return ['message' => 'hello', 'laravel' => app()->version()];
});
PHP
tail -4 "$APP/routes/web.php" | narrow

sec "9. serve して確認"
( cd "$APP" && run php artisan serve --host=127.0.0.1 --port="$PORT" \
    > "$WORK/serve.log" 2>&1 & echo $! > "$WORK/serve.pid" )
for _ in $(seq 1 40); do
  curl -s -o /dev/null -m 1 "http://127.0.0.1:$PORT/hello" && break
  sleep 0.5
done
curl -s -o /dev/null -w 'GET /      HTTP %{http_code}\n' "http://127.0.0.1:$PORT/"
curl -s -o /dev/null -w 'GET /hello HTTP %{http_code}\n' "http://127.0.0.1:$PORT/hello"
curl -s "http://127.0.0.1:$PORT/hello" | narrow
echo

sec "10. APP_KEY を空に戻す"
sed -i 's|^APP_KEY=.*|APP_KEY=|' "$APP/.env"
sleep 1
curl -s -o /dev/null -w 'GET /      HTTP %{http_code}\n' "http://127.0.0.1:$PORT/"
curl -s -o /dev/null -w 'GET /hello HTTP %{http_code}\n' "http://127.0.0.1:$PORT/hello"

sec "11. key:generate で復旧"
( cd "$APP" && run php artisan key:generate 2>&1 ) | narrow
sleep 1
curl -s -o /dev/null -w 'GET /      HTTP %{http_code}\n' "http://127.0.0.1:$PORT/"
curl -s -o /dev/null -w 'GET /hello HTTP %{http_code}\n' "http://127.0.0.1:$PORT/hello"

kill "$(cat "$WORK/serve.pid")" 2>/dev/null
echo
echo "===== 終了 ====="
