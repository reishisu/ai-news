<?php
// tidb_ddl_disk_quota は下げられるのか。警告をそのまま見る。
require __DIR__ . '/lib.php';
$p = tidb();
kv('変更前', (string)$p->query('select @@tidb_ddl_disk_quota')->fetchColumn());
$p->exec('SET GLOBAL tidb_ddl_disk_quota = 1073741824');
foreach (q($p, 'SHOW WARNINGS') as $w) { echo "warn:\n"; line($w['Message'], 2); }
kv('変更後', (string)$p->query('select @@tidb_ddl_disk_quota')->fetchColumn());
hr('users の AUTO_INCREMENT');
$l = conn('127.0.0.1', 4000, 'laravel_tidb');
$ddl = q($l, 'SHOW CREATE TABLE users')[0]['Create Table'];
preg_match('/AUTO_INCREMENT=(\d+)/', $ddl, $m);
kv('値', $m[1] ?? '(表示なし)');
kv('実データ MAX(id)', (string)$l->query('SELECT MAX(id) FROM users')->fetchColumn());
