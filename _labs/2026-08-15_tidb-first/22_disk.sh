#!/bin/bash
# エラー8256の条件を記録する。/tmp の空きと tidb_ddl_disk_quota を並べて出す。
# 注意: 8256 が最初に出た瞬間の空き容量は記録し損ねている。これは測り直した値。
set -u
echo "-- date"
date -u +'%Y-%m-%d %H:%MZ'
echo "-- df -h /tmp"
df -h /tmp | tail -1 | awk '{print "size="$2" used="$3" avail="$4}'
echo "-- tidb_ddl_disk_quota"
php -r '$d=new PDO("mysql:host=127.0.0.1;port=4000","root","");
        echo $d->query("select @@global.tidb_ddl_disk_quota")->fetchColumn()," bytes\n";'
