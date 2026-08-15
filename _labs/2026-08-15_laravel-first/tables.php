<?php
// アプリ側(.env の SQLite ファイル)に実在するテーブル名を並べるだけ。
$pdo = new PDO('sqlite:database/database.sqlite');
$sql = "select name from sqlite_master where type='table' order by name";
foreach ($pdo->query($sql) as $row) { echo $row[0], ' '; }
echo "\n";
