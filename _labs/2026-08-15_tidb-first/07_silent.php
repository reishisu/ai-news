<?php
// 「通った」が「効いている」とは限らない。DDLの黙殺を確かめる。
require __DIR__ . '/lib.php';

function look(PDO $p, string $name): void {
    hr($name);
    $p->exec('USE shop');
    foreach (['ft_t','my_t'] as $t) {
        $p->exec("DROP TABLE IF EXISTS $t");
    }
    $p->exec('CREATE TABLE ft_t (id INT PRIMARY KEY,'
        . ' t TEXT, FULLTEXT KEY ft_idx (t))');
    $p->exec("INSERT INTO ft_t VALUES (1,'tidb is mysql compatible')");
    $p->exec('CREATE TABLE my_t (a INT) ENGINE=MyISAM');

    // 索引が本当に登録されたか
    $n = $p->query("SELECT COUNT(*) FROM information_schema.statistics"
        . " WHERE table_schema='shop' AND table_name='ft_t'"
        . " AND index_name='ft_idx'")->fetchColumn();
    kv('ft_idx の行数', (string)$n);

    // 実際に MATCH できるか
    try {
        $r = $p->query("SELECT COUNT(*) FROM ft_t WHERE"
            . " MATCH(t) AGAINST('mysql')")->fetchColumn();
        kv('MATCH 結果', (string)$r);
    } catch (PDOException $e) {
        echo "MATCH: NG\n";
        line($e->getMessage(), 2);
    }

    // MyISAM と言ったのに何になったか
    $e = $p->query("SELECT engine FROM information_schema.tables"
        . " WHERE table_schema='shop' AND table_name='my_t'")
        ->fetchColumn();
    kv('MyISAM 指定の実体', (string)$e);
}

look(tidb(),  'TiDB  8.5.7');
look(mysql(), 'MySQL 8.0.46');
