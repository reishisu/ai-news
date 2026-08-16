#!/bin/bash
# Laravel 13.25 queue pause/resume 実証
cd "$(dirname "$0")/laravel-queue-test" || exit 1
export COLUMNS=40

A() { echo; echo "\$ $*"; }
LOG=storage/done.log

# --- 後始末して初期状態へ ---
rm -f "$LOG"
php artisan queue:clear database --no-interaction --no-ansi >/dev/null 2>&1
php artisan queue:resume --all --no-ansi >/dev/null 2>&1

A "php artisan queue:pause database:default"
php artisan queue:pause database:default --no-ansi 2>&1

A "php artisan tinker (dispatch job A)"
php artisan tinker --execute \
  'App\Jobs\RecordJob::dispatch("A"); echo "dispatched\n";' --no-ansi 2>&1

A "queue:work --stop-when-empty (paused)"
timeout 8 php artisan queue:work database \
  --stop-when-empty --no-ansi 2>&1
echo "[exit=$?]"

A "cat storage/done.log"
if [ -s "$LOG" ]; then cat "$LOG"; else echo "(空 = 未処理)"; fi

A "php artisan queue:continue database:default"
php artisan queue:continue database:default --no-ansi 2>&1

A "queue:work --stop-when-empty (resumed)"
timeout 8 php artisan queue:work database \
  --stop-when-empty --no-ansi 2>&1
echo "[exit=$?]"

A "cat storage/done.log"
if [ -s "$LOG" ]; then cat "$LOG"; else echo "(空 = 未処理)"; fi
