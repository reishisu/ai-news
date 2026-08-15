<?php
require __DIR__ . '/lib.php';
$t = tidb('shop'); $m = mysql('shop');
hr('新照合フレームワーク(TiDB)');
foreach (q($t, "SELECT variable_name v, variable_value x FROM mysql.tidb WHERE variable_name='new_collation_enabled'") as $r) {
    kv($r['v'], $r['x']);
}
hr('users_t.email の照合順序');
$sql = "SELECT collation_name c FROM information_schema.columns"
     . " WHERE table_schema='shop' AND table_name='users_t'"
     . " AND column_name='email'";
kv('TiDB ', (string)$t->query($sql)->fetchColumn(), 2);
kv('MySQL', (string)$m->query($sql)->fetchColumn(), 2);
