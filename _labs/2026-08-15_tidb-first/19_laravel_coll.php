<?php
// Laravel は DDL で照合順序を明示する。TiDB 既定は効かない。
require __DIR__ . '/lib.php';

hr('Laravel が作った users.email');
$l = conn('127.0.0.1', 4000, 'laravel_tidb');
kv('照合順序', (string)$l->query(
  "SELECT collation_name FROM information_schema.columns"
  . " WHERE table_schema='laravel_tidb' AND table_name='users'"
  . " AND column_name='email'")->fetchColumn());
kv('登録済み', (string)$l->query(
  'SELECT email FROM users')->fetchColumn());
kv('大文字で検索', (string)$l->query(
  "SELECT COUNT(*) FROM users WHERE email='TARO@EXAMPLE.COM'")
  ->fetchColumn() . ' 件');

hr('照合順序を書かない手書きDDL');
$s = conn('127.0.0.1', 4000, 'shop');
$s->exec('DROP TABLE IF EXISTS coll_t');
$s->exec('CREATE TABLE coll_t (email VARCHAR(190))');
$s->exec("INSERT INTO coll_t VALUES ('taro@example.com')");
kv('照合順序', (string)$s->query(
  "SELECT collation_name FROM information_schema.columns"
  . " WHERE table_schema='shop' AND table_name='coll_t'"
  . " AND column_name='email'")->fetchColumn());
kv('登録済み', (string)$s->query(
  'SELECT email FROM coll_t')->fetchColumn());
kv('大文字で検索', (string)$s->query(
  "SELECT COUNT(*) FROM coll_t WHERE email='TARO@EXAMPLE.COM'")
  ->fetchColumn() . ' 件');
