<?php
// AUTO_INCREMENT の採番を両方で観察する。
require __DIR__ . '/lib.php';

function autoIncOf(PDO $p, string $tbl): string {
    $row = q($p, "SHOW CREATE TABLE $tbl")[0];
    $ddl = $row['Create Table'];
    if (preg_match('/AUTO_INCREMENT=(\d+)/', $ddl, $m)) return $m[1];
    return '(表示なし)';
}

function run(PDO $p, string $name, callable $mk): void {
    hr($name);
    $p->exec('CREATE DATABASE IF NOT EXISTS shop');
    $p->exec('USE shop');
    $p->exec('DROP TABLE IF EXISTS seq_t');
    $mk($p);

    // 1) 素直に4行入れる
    $ids = [];
    for ($i = 0; $i < 4; $i++) {
        $p->exec("INSERT INTO seq_t (v) VALUES ($i)");
        $ids[] = $p->lastInsertId();
    }
    kv('連番 4件', implode(',', $ids));
    kv('SHOW CREATE の値', autoIncOf($p, 'seq_t'));

    // 2) 別コネクションから1行
    $p2 = conn('127.0.0.1', (int)$p->query('select @@port')
        ->fetchColumn(), 'shop');
    $p2->exec('INSERT INTO seq_t (v) VALUES (99)');
    kv('別接続の id', (string)$p2->lastInsertId());

    // 3) 大きい id を明示指定してから自動採番
    $p->exec('INSERT INTO seq_t (id, v) VALUES (1000000, 7)');
    $p->exec('INSERT INTO seq_t (v) VALUES (8)');
    kv('明示100万の次', (string)$p->lastInsertId());

    kv('最終 MAX(id)', (string)$p->query(
        'SELECT MAX(id) FROM seq_t')->fetchColumn());
}

$plain = function (PDO $p) {
    $p->exec('CREATE TABLE seq_t (id BIGINT AUTO_INCREMENT'
        . ' PRIMARY KEY, v INT)');
};

run(tidb(),  'TiDB  既定',  $plain);
run(mysql(), 'MySQL 既定', $plain);

// TiDB だけの構文: AUTO_ID_CACHE 1 で MySQL 互換の連番にする
$cache1 = function (PDO $p) {
    $p->exec('CREATE TABLE seq_t (id BIGINT AUTO_INCREMENT'
        . ' PRIMARY KEY, v INT) AUTO_ID_CACHE 1');
};
run(tidb(), 'TiDB  CACHE 1', $cache1);

hr('MySQL に AUTO_ID_CACHE');
$m = mysql('shop');
$m->exec('DROP TABLE IF EXISTS cache_t');
tryx($m, 'CREATE TABLE cache_t (id BIGINT AUTO_INCREMENT'
    . ' PRIMARY KEY) AUTO_ID_CACHE 1', 'AUTO_ID_CACHE 1');
