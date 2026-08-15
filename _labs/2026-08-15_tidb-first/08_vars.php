<?php
// 既定のシステム変数を並べる。移行時に効いてくるもの。
require __DIR__ . '/lib.php';

$vars = [
  'transaction_isolation', 'autocommit', 'sql_mode',
  'lower_case_table_names', 'max_allowed_packet',
  'character_set_server', 'collation_server',
  'foreign_key_checks',
];

$t = tidb(); $m = mysql();
foreach ($vars as $v) {
    hr($v);
    foreach (['TiDB ' => $t, 'MySQL' => $m] as $n => $p) {
        try {
            $val = (string)$p->query("SELECT @@$v")->fetchColumn();
        } catch (PDOException $e) { $val = 'NG:未対応'; }
        if ($val === '') $val = '(空)';
        kv($n, $val, 2);
    }
}
