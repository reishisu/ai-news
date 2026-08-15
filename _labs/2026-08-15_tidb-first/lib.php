<?php
// 共通ヘルパ。出力は「表示幅」40桁以内に収める（全角は2桁として数える）。
const W = 40;

function conn(string $host, int $port, string $db = ''): PDO {
    $dsn = "mysql:host=$host;port=$port";
    if ($db !== '') $dsn .= ";dbname=$db";
    return new PDO($dsn, 'root', '', [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]);
}

function tidb(string $db = ''): PDO  { return conn('127.0.0.1', 4000, $db); }
function mysql(string $db = ''): PDO { return conn('127.0.0.1', 3306, $db); }

function w(string $s): int { return mb_strwidth($s, 'UTF-8'); }

// 表示幅で分割する（全角を2桁として数える）
function chunks(string $s, int $width): array {
    $out = []; $cur = ''; $cw = 0;
    $len = mb_strlen($s, 'UTF-8');
    for ($i = 0; $i < $len; $i++) {
        $c  = mb_substr($s, $i, 1, 'UTF-8');
        $cc = mb_strwidth($c, 'UTF-8');
        if ($cw + $cc > $width) { $out[] = $cur; $cur = ''; $cw = 0; }
        $cur .= $c; $cw += $cc;
    }
    if ($cur !== '') $out[] = $cur;
    return $out ?: [''];
}

function hr(string $title = ''): void {
    if ($title === '') { echo str_repeat('-', W), "\n"; return; }
    $t = "-- $title ";
    echo $t, str_repeat('-', max(0, W - w($t))), "\n";
}

// ラベル付きの値。長ければ次行に折り返す
function kv(string $k, string $v, int $indent = 2): void {
    $head = "$k: ";
    if (w($head) + w($v) <= W) { echo $head, $v, "\n"; return; }
    echo rtrim($head), "\n";
    foreach (chunks($v, W - $indent) as $c) {
        echo str_repeat(' ', $indent), $c, "\n";
    }
}

// ただの文字列を幅に合わせて折り返す
function line(string $s, int $indent = 0): void {
    $pad = str_repeat(' ', $indent);
    foreach (chunks($s, W - $indent) as $c) echo $pad, $c, "\n";
}

// EXPLAIN 等の1行を、列ごとに縦に並べて出す
function rowv(array $row, array $cols, int $indent = 2): void {
    foreach ($cols as $c) {
        if (!array_key_exists($c, $row)) continue;
        $v = (string)($row[$c] ?? '');
        if ($v === '') $v = '(空)';
        kv($c, $v, $indent);
    }
}

function q(PDO $p, string $sql): array {
    return $p->query($sql)->fetchAll(PDO::FETCH_ASSOC);
}

// 失敗をそのまま見せる
function tryx(PDO $p, string $sql, string $label): void {
    try {
        $p->exec($sql);
        echo "OK   $label\n";
    } catch (PDOException $e) {
        echo "NG   $label\n";
        line($e->getMessage(), 4);
    }
}
