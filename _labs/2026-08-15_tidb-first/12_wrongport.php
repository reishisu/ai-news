<?php
// 最初に必ずやる失敗: MySQL のつもりで 3306 に繋ぐ
require __DIR__ . '/lib.php';
foreach ([3306 => 'MySQL の既定', 4000 => 'TiDB の既定'] as $port => $note) {
    hr("port $port ($note)");
    try {
        $p = conn('127.0.0.1', $port);
        kv('OK version', $p->query('select version()')->fetchColumn());
    } catch (PDOException $e) {
        echo "NG\n";
        line($e->getMessage(), 2);
    }
}
