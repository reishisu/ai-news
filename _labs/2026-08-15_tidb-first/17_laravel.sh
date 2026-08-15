#!/bin/bash
# Laravel を TiDB に繋いでマイグレーションを通すまで。
set -u
D="$(cd "$(dirname "$0")" && pwd)"
APP="$D/tidbapp"

echo "-- .env の DB 設定"
grep "^DB_" "$APP/.env"

echo
echo "-- TiDB 側の準備"
php -r '
$p = new PDO("mysql:host=127.0.0.1;port=4000","root","",
  [PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
$p->exec("SET GLOBAL tidb_enable_dist_task = OFF");
$p->exec("SET GLOBAL tidb_ddl_enable_fast_reorg = OFF");
$p->exec("DROP DATABASE IF EXISTS laravel_tidb");
$p->exec("CREATE DATABASE laravel_tidb");
echo "dist_task  : ", $p->query("select @@tidb_enable_dist_task")->fetchColumn(), "\n";
echo "fast_reorg : ", $p->query("select @@tidb_ddl_enable_fast_reorg")->fetchColumn(), "\n";'

echo
echo "-- php artisan migrate"
( cd "$APP" && php artisan migrate --force -n --no-ansi 2>&1 ) | fold -w 40

echo "-- できた表"
php -r '
$p = new PDO("mysql:host=127.0.0.1;port=4000;dbname=laravel_tidb","root","");
foreach ($p->query("SHOW TABLES") as $r) echo "  ", $r[0], "\n";'

echo
echo "-- Eloquent で1件入れて読む"
( cd "$APP" && php artisan tinker --no-ansi --execute '
$u = App\Models\User::create([
  "name" => "taro",
  "email" => "taro@example.com",
  "password" => bcrypt("secret"),
]);
echo "id=", $u->id, "\n";
echo "count=", App\Models\User::count(), "\n";
echo "engine=", DB::selectOne("select version() v")->v, "\n";
' 2>&1 ) | fold -w 40
