<?php
// 同じ DDL / DML を TiDB と MySQL の両方に流す。
require __DIR__ . '/lib.php';

$DDL = <<<SQL
CREATE TABLE orders (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  amount INT NOT NULL,
  created_at DATETIME NOT NULL,
  KEY idx_user (user_id)
)
SQL;

function setup(PDO $p, string $name): void {
    global $DDL;
    hr($name);
    $p->exec('CREATE DATABASE IF NOT EXISTS shop');
    $p->exec('USE shop');
    $p->exec('DROP TABLE IF EXISTS orders');
    $p->exec($DDL);
    echo "CREATE TABLE : OK\n";

    $ins = $p->prepare(
        'INSERT INTO orders (user_id, amount, created_at)'
        . ' VALUES (?, ?, ?)');
    $p->beginTransaction();
    for ($i = 1; $i <= 1000; $i++) {
        $ins->execute([$i % 50, 100 + $i, '2026-08-15 09:00:00']);
    }
    $p->commit();
    echo "INSERT 1000  : OK\n";

    kv('COUNT(*)', (string)$p->query(
        'SELECT COUNT(*) FROM orders')->fetchColumn());
    kv('user_id=7 件数', (string)$p->query(
        'SELECT COUNT(*) FROM orders WHERE user_id=7')->fetchColumn());
    $r = q($p, 'SELECT id,user_id,amount FROM orders'
        . ' WHERE user_id=7 ORDER BY id LIMIT 2');
    foreach ($r as $row) {
        echo "  id={$row['id']} user={$row['user_id']}"
            . " amount={$row['amount']}\n";
    }
    // 統計情報を更新（EXPLAIN の見積り行数を安定させる）
    try { $p->exec('ANALYZE TABLE orders'); } catch (PDOException $e) {}
}

setup(tidb(),  'TiDB  4000');
setup(mysql(), 'MySQL 3306');
