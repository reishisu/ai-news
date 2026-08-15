<?php
// CHECK制約は「DDLが通る」だけなのか、値の検査までされるのか。
// TiDB は tidb_enable_check_constraint が既定 OFF。MySQL 8.0 は常に有効。
require __DIR__ . '/lib.php';

foreach ([['TiDB ', 4000], ['MySQL', 3306]] as [$name, $port]) {
    hr("$name $port");
    try {
        $p = conn('127.0.0.1', $port);
    } catch (PDOException $e) {
        line('接続不可', 0);
        continue;
    }
    if ($port === 4000) {
        $v = $p->query("SELECT @@global.tidb_enable_check_constraint")->fetchColumn();
        line("tidb_enable_check_constraint=$v");
    }
    $p->exec("CREATE DATABASE IF NOT EXISTS chk");
    $p->exec("USE chk");
    $p->exec("DROP TABLE IF EXISTS c1");
    $p->exec("CREATE TABLE c1 (a INT CHECK (a > 0))");
    line("CREATE TABLE: OK");
    try {
        $p->exec("INSERT INTO c1 VALUES (-1)");
        $n = $p->query("SELECT COUNT(*) FROM c1")->fetchColumn();
        line("違反行が入った rows=$n");
    } catch (PDOException $e) {
        $m = $e->getMessage();
        $m = substr($m, strpos($m, 'violation:') !== false ? strpos($m, 'violation:') + 11 : 0);
        line('弾かれた', 0);
        line($m, 2);
    }
    $p->exec("DROP TABLE c1");
    $p->exec("DROP DATABASE chk");
}
