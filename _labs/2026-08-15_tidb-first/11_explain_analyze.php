<?php
// EXPLAIN ANALYZE は両方にあるが、返ってくる形が違う。
require __DIR__ . '/lib.php';

$SQL = 'SELECT COUNT(*) FROM orders_big WHERE user_id = 7';

hr('TiDB EXPLAIN ANALYZE');
$t = tidb('shop');
$rows = q($t, 'EXPLAIN ANALYZE ' . $SQL);
line('列: ' . implode(', ', array_keys($rows[0])));
hr();
foreach ($rows as $r) {
    kv('id', $r['id']);
    kv(' estRows', (string)$r['estRows'], 2);
    kv(' actRows', (string)$r['actRows'], 2);
}

hr('MySQL EXPLAIN ANALYZE');
$m = mysql('shop');
$rows = q($m, 'EXPLAIN ANALYZE ' . $SQL);
line('列: ' . implode(', ', array_keys($rows[0])));
hr();
foreach ($rows as $r) {
    foreach (explode("\n", reset($r)) as $l) line(rtrim($l), 0);
}
