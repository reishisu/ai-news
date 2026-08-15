#!/usr/bin/env bash
# テストDBが .env ではなく phpunit.xml の :memory: を見ていることの実証。
# 使い方: bash dbtest.sh <example-app のパス>
set -u
APP="${1:?usage: bash dbtest.sh <app dir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
export COLUMNS=40 NO_COLOR=1
run() { env -u CLAUDECODE -u AI_AGENT "$@"; }
narrow() { python3 "$HERE/narrow.py" 40; }

write_test() {  # $1 = RefreshDatabase の行
cat > "$APP/tests/Feature/UserCountTest.php" <<PHP
<?php

namespace Tests\Feature;

$1
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

class UserCountTest extends TestCase
{
$2
    public function test_users_table_is_readable(): void
    {
        \$this->assertSame(0, DB::table('users')->count());
    }
}
PHP
}

echo "===== 0. .env 側のDBのテーブル ====="
grep '^DB_CONNECTION' "$APP/.env"
( cd "$APP" && php "$HERE/tables.php" ) | narrow
echo
echo "===== 1. RefreshDatabase なし ====="
write_test "// use Illuminate\\Foundation\\Testing\\RefreshDatabase;" ""
( cd "$APP" && run php artisan test --filter=UserCountTest 2>&1 ) \
  | head -6 | narrow
echo "exit=${PIPESTATUS[0]}"

echo
echo "===== 2. RefreshDatabase あり ====="
write_test "use Illuminate\\Foundation\\Testing\\RefreshDatabase;" "    use RefreshDatabase;
"
( cd "$APP" && run php artisan test --filter=UserCountTest 2>&1 ) \
  | head -6 | narrow
echo "exit=${PIPESTATUS[0]}"
