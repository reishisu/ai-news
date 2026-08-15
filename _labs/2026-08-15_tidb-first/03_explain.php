<?php
// 同じ SELECT の EXPLAIN を両方で取る。列の顔ぶれから違う。
require __DIR__ . '/lib.php';

$SQL = 'SELECT id, amount FROM orders'
     . ' WHERE user_id = 7 ORDER BY amount DESC LIMIT 3';

function ex(PDO $p, string $name, string $sql): void {
    hr($name);
    $rows = q($p, 'EXPLAIN ' . $sql);
    line('列: ' . implode(', ', array_keys($rows[0])));
    hr();
    foreach ($rows as $i => $r) {
        echo '[', $i + 1, "]\n";
        rowv($r, array_keys($r));
    }
}

$t = tidb('shop');
$m = mysql('shop');
ex($t, 'TiDB  EXPLAIN', $SQL);
ex($m, 'MySQL EXPLAIN', $SQL);
