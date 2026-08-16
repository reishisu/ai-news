#!/bin/bash
# --all オプション側と、別名の同一性を確認
cd "$(dirname "$0")/laravel-queue-test" || exit 1
export COLUMNS=40

A() { echo; echo "\$ $*"; }
LOG=storage/done.log

rm -f "$LOG"
php artisan queue:clear database --no-interaction --no-ansi >/dev/null 2>&1
php artisan queue:resume --all --no-ansi >/dev/null 2>&1

A "php artisan queue:pause --all"
php artisan queue:pause --all --no-ansi 2>&1

A "tinker (dispatch job B)"
php artisan tinker --execute \
  'App\Jobs\RecordJob::dispatch("B"); echo "dispatched\n";' --no-ansi 2>&1

A "queue:work --stop-when-empty (paused)"
timeout 8 php artisan queue:work database \
  --stop-when-empty --no-ansi 2>&1
A "cat storage/done.log"
if [ -s "$LOG" ]; then cat "$LOG"; else echo "(空 = 未処理)"; fi

A "php artisan queue:resume --all"
php artisan queue:resume --all --no-ansi 2>&1

A "queue:work --stop-when-empty (resumed)"
timeout 8 php artisan queue:work database \
  --stop-when-empty --no-ansi 2>&1
A "cat storage/done.log"
if [ -s "$LOG" ]; then cat "$LOG"; else echo "(空 = 未処理)"; fi
