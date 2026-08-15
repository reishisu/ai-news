<?php
// トランザクションの途中で DDL を打つとどうなるか。
require __DIR__ . '/lib.php';

function t1(PDO $p, string $name): void {
    hr($name);
    $p->exec('USE shop');
    $p->exec('DROP TABLE IF EXISTS tx_t');
    $p->exec('CREATE TABLE tx_t (id INT PRIMARY KEY, v INT)');
    $p->exec('INSERT INTO tx_t VALUES (1,1)');

    // BEGIN → INSERT → DDL → ROLLBACK
    $p->exec('BEGIN');
    $p->exec('INSERT INTO tx_t VALUES (2,2)');
    $p->exec('ALTER TABLE tx_t ADD COLUMN w INT');
    try { $p->exec('ROLLBACK'); } catch (PDOException $e) {}

    kv('ROLLBACK後の行数', (string)$p->query(
        'SELECT COUNT(*) FROM tx_t')->fetchColumn());
    kv('id=2 は残るか', (string)$p->query(
        'SELECT COUNT(*) FROM tx_t WHERE id=2')->fetchColumn());
}

t1(tidb(),  'TiDB  8.5.7');
t1(mysql(), 'MySQL 8.0.46');
