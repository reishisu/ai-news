#!/bin/bash
# 公式の記述「--all で再開しても個別に一時停止した
# キューは再開しない」を検証する
cd "$(dirname "$0")/laravel-queue-test" || exit 1
export COLUMNS=40

A() { echo; echo "\$ $*"; }
LOG=storage/done.log

rm -f "$LOG"
php artisan queue:clear database --no-interaction --no-ansi >/dev/null 2>&1
php artisan queue:resume --all --no-ansi >/dev/null 2>&1
php artisan queue:resume database:default --no-ansi >/dev/null 2>&1

A "queue:pause database:default (個別)"
php artisan queue:pause database:default --no-ansi 2>&1

A "tinker (dispatch job C)"
php artisan tinker --execute \
  'App\Jobs\RecordJob::dispatch("C"); echo "dispatched\n";' --no-ansi 2>&1

A "queue:resume --all (全体で再開)"
php artisan queue:resume --all --no-ansi 2>&1

A "queue:work --stop-when-empty"
timeout 8 php artisan queue:work database \
  --stop-when-empty --no-ansi 2>&1

A "cat storage/done.log"
if [ -s "$LOG" ]; then cat "$LOG"; else echo "(空 = 未処理)"; fi

A "queue:resume database:default (個別に再開)"
php artisan queue:resume database:default --no-ansi 2>&1

A "queue:work --stop-when-empty"
timeout 8 php artisan queue:work database \
  --stop-when-empty --no-ansi 2>&1

A "cat storage/done.log"
if [ -s "$LOG" ]; then cat "$LOG"; else echo "(空 = 未処理)"; fi
