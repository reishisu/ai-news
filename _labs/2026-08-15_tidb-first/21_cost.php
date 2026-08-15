<?php
// 1000行のテーブルで TiDB が全表スキャンを選ぶのは「コストがそう出たから」か。
// EXPLAIN FORMAT='verbose' で、既定の計画とヒントで索引を強制した計画の
// estCost を並べて比べる。
require __DIR__ . '/lib.php';

$t = conn('127.0.0.1', 4000);
$t->exec("CREATE DATABASE IF NOT EXISTS costlab");
$t->exec("USE costlab");
$t->exec("DROP TABLE IF EXISTS orders");
$t->exec("CREATE TABLE orders (id BIGINT PRIMARY KEY, user_id INT,
          amount INT, KEY idx_user (user_id))");
$st = $t->prepare("INSERT INTO orders VALUES (?,?,?)");
for ($i = 1; $i <= 1000; $i++) $st->execute([$i, $i % 50, 100 + $i]);
$t->exec("ANALYZE TABLE orders");

$where = "WHERE user_id = 7 ORDER BY amount DESC LIMIT 3";

// 根ノード(1行目)の estCost が、その計画全体の見積もりコスト。
function plan(PDO $t, string $sql): void {
    $rows = q($t, "EXPLAIN FORMAT='verbose' $sql");
    line('根: ' . trim($rows[0]['id']));
    line('全体コスト: ' . $rows[0]['estCost']);
    foreach ($rows as $r) {
        $id = trim(str_replace(['└─', '├─', '│ '], '', $r['id']));
        if (str_contains($id, 'Scan')) line('  ' . $id);
    }
}

hr('既定の計画 (1000行)');
plan($t, "SELECT id, amount FROM orders $where");

hr('索引を強制した計画');
plan($t, "SELECT /*+ USE_INDEX(orders, idx_user) */
          id, amount FROM orders $where");

$t->exec("DROP TABLE orders");
$t->exec("DROP DATABASE costlab");
