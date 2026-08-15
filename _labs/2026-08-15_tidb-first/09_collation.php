<?php
// 既定照合順序と表名の大文字小文字。移行で一番刺さる差。
require __DIR__ . '/lib.php';

function check(PDO $p, string $name): void {
    hr($name);
    $p->exec('CREATE DATABASE IF NOT EXISTS shop');
    $p->exec('USE shop');
    $p->exec('DROP TABLE IF EXISTS users_t');
    $p->exec('CREATE TABLE users_t (email VARCHAR(190)'
        . ' UNIQUE)');
    $p->exec("INSERT INTO users_t VALUES ('taro@example.com')");

    // 大文字で検索してヒットするか
    $n = $p->query("SELECT COUNT(*) FROM users_t"
        . " WHERE email='TARO@EXAMPLE.COM'")->fetchColumn();
    kv('大文字で検索', (string)$n . ' 件');

    // 大文字違いを UNIQUE が弾くか
    tryx($p, "INSERT INTO users_t VALUES"
        . " ('TARO@EXAMPLE.COM')", '大文字を重複挿入');

    // 表名の大文字小文字
    try {
        $p->query('SELECT COUNT(*) FROM USERS_T')->fetchColumn();
        echo "OK   表名 USERS_T で参照\n";
    } catch (PDOException $e) {
        echo "NG   表名 USERS_T で参照\n";
        line($e->getMessage(), 4);
    }
}

check(tidb(),  'TiDB  8.5.7');
check(mysql(), 'MySQL 8.0.46');
