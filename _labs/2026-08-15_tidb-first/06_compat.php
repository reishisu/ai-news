<?php
// MySQL で通る構文が TiDB で通るかを1つずつ叩く。
require __DIR__ . '/lib.php';

$cases = [
  'ビュー作成' => [
    'CREATE VIEW v_o AS SELECT id FROM orders',
  ],
  '外部キー' => [
    'CREATE TABLE fk_p (id INT PRIMARY KEY)',
    'CREATE TABLE fk_c (id INT PRIMARY KEY, p INT,'
      . ' FOREIGN KEY (p) REFERENCES fk_p(id))',
  ],
  '生成列' => [
    'CREATE TABLE gen_t (a INT, b INT AS (a+1) STORED)',
  ],
  'CHECK制約' => [
    'CREATE TABLE chk_t (a INT CHECK (a > 0))',
  ],
  'SAVEPOINT' => [
    'BEGIN', 'SAVEPOINT s1', 'ROLLBACK TO s1', 'COMMIT',
  ],
  'ストアド' => [
    'CREATE PROCEDURE pr1() BEGIN SELECT 1; END',
  ],
  'トリガー' => [
    'CREATE TRIGGER tg1 BEFORE INSERT ON orders'
      . ' FOR EACH ROW SET @x = 1',
  ],
  'イベント' => [
    'CREATE EVENT ev1 ON SCHEDULE EVERY 1 DAY'
      . ' DO SELECT 1',
  ],
  '全文索引' => [
    'CREATE TABLE ft_t (t TEXT, FULLTEXT KEY (t))',
  ],
  'ENGINE=MyISAM' => [
    'CREATE TABLE my_t (a INT) ENGINE=MyISAM',
  ],
  'GET_LOCK' => [
    "DO GET_LOCK('l1', 1)", "DO RELEASE_LOCK('l1')",
  ],
];

function drops(PDO $p): void {
    foreach (['VIEW v_o'] as $x) {
        try { $p->exec("DROP $x"); } catch (PDOException $e) {}
    }
    foreach (['fk_c','fk_p','gen_t','chk_t','ft_t','my_t'] as $t) {
        try { $p->exec("DROP TABLE IF EXISTS $t"); }
        catch (PDOException $e) {}
    }
    foreach (['PROCEDURE pr1','TRIGGER tg1','EVENT ev1'] as $x) {
        try { $p->exec("DROP $x"); } catch (PDOException $e) {}
    }
}

$t = tidb('shop'); $m = mysql('shop');
drops($t); drops($m);

$res = [];
foreach ($cases as $name => $stmts) {
    foreach (['T' => $t, 'M' => $m] as $k => $p) {
        $ok = 'OK'; $err = '';
        foreach ($stmts as $s) {
            try { $p->exec($s); }
            catch (PDOException $e) {
                $ok = 'NG';
                $err = $e->getMessage();
                break;
            }
        }
        $res[$name][$k] = $ok;
        $res[$name][$k . 'e'] = $err;
    }
}
drops($t); drops($m);

hr('T=TiDB8.5.7 M=MySQL8.0.46');
foreach ($res as $name => $r) {
    printf("%-2s %-2s  %s\n", $r['T'], $r['M'], $name);
}

hr('NG の中身');
foreach ($res as $name => $r) {
    foreach (['T' => 'TiDB', 'M' => 'MySQL'] as $k => $lbl) {
        if ($r[$k] === 'NG') {
            echo "$lbl / $name\n";
            line($r[$k . 'e'], 2);
        }
    }
}
