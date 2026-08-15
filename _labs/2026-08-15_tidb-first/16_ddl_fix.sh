#!/bin/bash
# 8256 をどう直すか。素直な手から順に試して、全部の結果を残す。
set -u
D="$(cd "$(dirname "$0")" && pwd)"
APP="$D/tidbapp"

setv() {  # setv 変数 値
  php -r '$p=new PDO("mysql:host=127.0.0.1;port=4000","root","",
    [PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
  $p->exec("SET GLOBAL '"$1"' = '"$2"'");
  // 警告は次の文を投げると消える。先に読む
  $ws = [];
  foreach ($p->query("SHOW WARNINGS") as $w) {
    if (strpos($w[2], "plan-cache") !== false) continue;
    $ws[] = $w[2];
  }
  printf("%-26s %s\n", "'"$1"'",
    $p->query("select @@'"$1"'")->fetchColumn());
  foreach ($ws as $m) foreach (str_split($m, 36) as $c)
    echo "  ! ", $c, "\n";'
}

migrate() {
  php -r '$p=new PDO("mysql:host=127.0.0.1;port=4000","root","");
    $p->exec("DROP DATABASE IF EXISTS laravel_tidb");
    $p->exec("CREATE DATABASE laravel_tidb");'
  ( cd "$APP" && php artisan migrate --force -n --no-ansi 2>&1 ) \
    | grep -E "DONE$|FAIL$|General error" | fold -w 40
}

echo "== 出荷時の設定に戻す =="
setv tidb_enable_dist_task ON
setv tidb_ddl_enable_fast_reorg ON
echo "-- migrate"
migrate

echo
echo "== 手1: fast_reorg を切る =="
setv tidb_ddl_enable_fast_reorg OFF
echo "-- migrate"
migrate

echo
echo "== 手2: disk_quota を 1GiB に下げる =="
setv tidb_ddl_enable_fast_reorg ON
setv tidb_ddl_disk_quota 1073741824
echo "-- migrate"
migrate

echo
echo "== 手3: dist_task も一緒に切る =="
setv tidb_enable_dist_task OFF
setv tidb_ddl_enable_fast_reorg OFF
echo "-- migrate"
migrate
