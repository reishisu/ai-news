<?php
// TableFullScan は統計不足のせいか？ ANALYZE を明示的に走らせて確認する。
require __DIR__ . '/lib.php';
$t = tidb('shop');

hr('ANALYZE 実行');
try { $t->exec('ANALYZE TABLE orders'); echo "ANALYZE: OK\n"; }
catch (PDOException $e) { echo "ANALYZE: NG\n"; kv(' err', $e->getMessage(), 2); }

foreach (q($t, 'SHOW WARNINGS') as $w) {
    kv('warn', $w['Message'], 2);
}

hr('SHOW STATS_HEALTHY');
foreach (q($t, "SHOW STATS_HEALTHY WHERE Db_name='shop'") as $r) {
    kv('table', $r['Table_name']);
    kv('healthy', (string)$r['Healthy']);
}

hr('再 EXPLAIN (user_id=7)');
$sql = 'SELECT id, amount FROM orders WHERE user_id = 7'
     . ' ORDER BY amount DESC LIMIT 3';
foreach (q($t, 'EXPLAIN ' . $sql) as $r) {
    kv('id', $r['id']);
    kv(' est', (string)$r['estRows'], 2);
    kv(' task', $r['task'], 2);
}
