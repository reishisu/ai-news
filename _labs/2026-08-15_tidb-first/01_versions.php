<?php
require __DIR__ . '/lib.php';

hr('TiDB 127.0.0.1:4000');
$t = tidb();
kv('version()', $t->query('select version()')->fetchColumn());
echo "tidb_version():\n";
foreach (explode("\n", trim($t->query('select tidb_version()')->fetchColumn())) as $l) {
    $l = trim($l);
    if ($l === '') continue;
    line($l, 2);
}

hr('MySQL 127.0.0.1:3306');
$m = mysql();
kv('version()', $m->query('select version()')->fetchColumn());
kv('comment', $m->query('select @@version_comment')->fetchColumn());
