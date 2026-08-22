#!/usr/bin/env bash
# 記事に貼った出力を、そのまま作り直すスクリプト。
# 幅は CLAUDE.md 第4節（幅380pxで横スクロールしない長さ）に合わせてある。
cd "$(dirname "$0")"
export COLUMNS=40

echo "# $(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M') JST"
echo "# $(php artisan --version)"
echo "# PHP $(php -r 'echo PHP_VERSION;')"
echo "# QUEUE=database(sqlite) CACHE=file"
echo
echo '$ php artisan demo:debounce plain'
php artisan demo:debounce plain 2>&1
echo
echo '$ php artisan demo:debounce debounce'
php artisan demo:debounce debounce 2>&1
echo
echo '$ php artisan demo:conflict'
php artisan demo:conflict 2>&1
