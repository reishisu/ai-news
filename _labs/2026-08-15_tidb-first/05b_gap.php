<?php
// 30001 は本当に使われるのか。キャッシュを作り直させて確かめる。
require __DIR__ . '/lib.php';
$p = tidb();
$p->exec('USE shop');
$p->exec('DROP TABLE IF EXISTS gap_t');
$p->exec('CREATE TABLE gap_t (id BIGINT AUTO_INCREMENT'
    . ' PRIMARY KEY, v INT)');

hr('TiDB 既定キャッシュ');
$ids = [];
for ($i = 0; $i < 3; $i++) {
    $p->exec("INSERT INTO gap_t (v) VALUES ($i)");
    $ids[] = $p->lastInsertId();
}
kv('採番', implode(',', $ids));

hr('ALTER で採番器を作り直す');
$p->exec('ALTER TABLE gap_t AUTO_ID_CACHE 100');
$ids = [];
for ($i = 0; $i < 3; $i++) {
    $p->exec("INSERT INTO gap_t (v) VALUES ($i)");
    $ids[] = $p->lastInsertId();
}
kv('採番', implode(',', $ids));

hr('中身は歯抜けのまま');
$rows = q($p, 'SELECT id FROM gap_t ORDER BY id');
kv('全id', implode(',', array_column($rows, 'id')));
kv('行数', (string)count($rows));
