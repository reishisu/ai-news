<?php
// 1000行では全表スキャンだった。行を増やすとインデックスを使うのか。
require __DIR__ . '/lib.php';

const N     = 100000;
const BATCH = 1000;

function build(PDO $p, string $name): void {
    hr($name);
    $p->exec('CREATE DATABASE IF NOT EXISTS shop');
    $p->exec('USE shop');
    $p->exec('DROP TABLE IF EXISTS orders_big');
    $p->exec('CREATE TABLE orders_big ('
        . ' id BIGINT AUTO_INCREMENT PRIMARY KEY,'
        . ' user_id INT NOT NULL, amount INT NOT NULL,'
        . ' KEY idx_user (user_id))');

    $ph  = '(?,?)';
    $sql = 'INSERT INTO orders_big (user_id, amount) VALUES '
         . implode(',', array_fill(0, BATCH, $ph));
    $st  = $p->prepare($sql);
    $t0  = microtime(true);
    for ($b = 0; $b < N / BATCH; $b++) {
        $args = [];
        for ($i = 0; $i < BATCH; $i++) {
            $n = $b * BATCH + $i;
            $args[] = $n % 5000;   // 1ユーザーあたり20行
            $args[] = 100 + $n;
        }
        $st->execute($args);
    }
    kv('INSERT 100000 秒', sprintf('%.1f', microtime(true) - $t0));
    // MySQL の ANALYZE は結果セットを返す。読み捨てないと次が撃たれる
    $st2 = $p->query('ANALYZE TABLE orders_big');
    $st2->fetchAll();
    $st2->closeCursor();
    kv('COUNT(*)', (string)$p->query(
        'SELECT COUNT(*) FROM orders_big')->fetchColumn());
}

function ex(PDO $p, string $name, string $sql, array $cols): void {
    hr($name);
    foreach (q($p, 'EXPLAIN ' . $sql) as $r) rowv($r, $cols);
}

$SQL = 'SELECT id, amount FROM orders_big WHERE user_id = 7';

$t = tidb(); $m = mysql();
build($t, 'TiDB  4000');
build($m, 'MySQL 3306');

ex($t, 'TiDB  EXPLAIN', $SQL,
   ['id', 'estRows', 'task', 'access object']);
ex($m, 'MySQL EXPLAIN', $SQL,
   ['table', 'type', 'key', 'rows']);
