#!/usr/bin/env bash
# LaravelのCORS検証用アプリを作る。
#
#   bash setup.sh [作る場所]
#
# 既定の作る場所は /tmp/cors-lab。リポジトリの中には作らないこと。
set -eu

APP="${1:-/tmp/cors-lab}"
LAB="$(cd "$(dirname "$0")" && pwd)"

export COMPOSER_ALLOW_SUPERUSER=1

echo "== 1. Laravel を新規作成: $APP"
composer create-project laravel/laravel "$APP" --no-interaction

cd "$APP"

echo "== 2. routes/api.php を作る"
# Laravel 11以降の骨格には routes/api.php が無い。
# install:api が routes/api.php を作り、bootstrap/app.php に api: を足す。
php artisan install:api --no-interaction

echo "== 3. 検証用ルートを置く"
cat > routes/api.php <<'PHP'
<?php

use Illuminate\Support\Facades\Route;

// 検証用: cors.paths の 'api/*' に入るGET
Route::get('/hello', function () {
    return ['msg' => 'hello'];
});

// 検証用: preflight のあとに飛ぶ本番リクエスト
Route::post('/hello', function () {
    return ['msg' => 'posted'];
});

// 検証用: サーバー自身に「いま見えている設定」を言わせる。
// php artisan serve は cli-server SAPI で動き、そこでは OPcache が
// 有効(opcache.revalidate_freq=2秒)。config/cors.php を書き換えても
// 最大2秒は古いままなので、測る前にここで反映を待つ。
Route::get('/corsconfig', function () {
    return response()->json([
        config('cors.allowed_origins'),
        config('cors.supports_credentials'),
    ]);
});

// 検証用: 上の「OPcacheが効いている」ことを示すための値。
// 1行が長くならないよう、行ごとの配列で返す。
Route::get('/sapi', function () {
    return response()->json([
        'sapi=' . php_sapi_name(),
        'opcache.enable_cli=' . ini_get('opcache.enable_cli'),
        'opcache.revalidate_freq=' . ini_get('opcache.revalidate_freq'),
        'opcache_get_status=' . var_export((bool) @opcache_get_status(false), true),
    ]);
});
PHP

cat > routes/web.php <<'PHP'
<?php

use Illuminate\Support\Facades\Route;

// 検証用: cors.paths に入らないパス(api/ で始まらない)
Route::get('/hello', function () {
    return ['msg' => 'hello from web'];
});
PHP

echo "== 4. 出来たもの"
php artisan --version
php -v | head -1
ls config/ | tr '\n' ' '; echo

echo
echo "できました。次: bash $LAB/run_tests.sh $APP 8123"
