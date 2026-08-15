# TiDB を最初に触る — 検証一式

TiDB v8.5.7 と MySQL 8.0.46 を同じマシンで並べて起動し、
同じ SQL を両方に流して差を測った記録。実行日 2026-08-15。

## 実行環境

| 対象 | 版 |
|---|---|
| TiDB | v8.5.7 (tiup playground, 127.0.0.1:4000) |
| MySQL | 8.0.46-0ubuntu0.24.04.3 (127.0.0.1:3306) |
| PHP | 8.4.19 (pdo_mysql) |
| Laravel | 13.25.0 |
| Python | 3.11.15 |
| Node | v22.22.2 |
| Chromium | 141.0.7390.37 |

TiDB クライアントは pdo_mysql のみ（mysql CLI は使っていない）。

## 準備

TiDB:

```
export PATH=$PATH:/root/.tiup/bin
tiup playground --db 1 --kv 1 --pd 1 --tiflash 0 --without-monitor &
```

比較用の MySQL（この環境には最初から無いので入れた）:

```
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq mysql-server
/usr/sbin/mysqld --initialize-insecure --user=root --datadir=/var/lib/mysql-lab
/usr/sbin/mysqld --user=root --datadir=/var/lib/mysql-lab --port=3306 \
  --socket=/var/lib/mysql-lab/m.sock --mysqlx=0 \
  --pid-file=/var/lib/mysql-lab/m.pid &
```

systemd が無いので `mysqld` は直接起動する。datadir を `/tmp` 配下に置くと
`MY-013455 ... data directory is unusable` で初期化に失敗したため `/var/lib` に置いた。

Laravel:

```
composer create-project laravel/laravel tidbapp
# .env を DB_CONNECTION=mysql / DB_PORT=4000 に書き換える
```

## 動かし方

両方起動した状態で:

```
bash run_all.sh          # 01〜11 を実行して out_*.txt を作る
```

TiDB だけ起動した状態で:

```
php 12_wrongport.php     # 3306 に繋いで失敗させる
bash 16_ddl_fix.sh       # 8256 の直し方を4通り
bash 17_laravel.sh       # Laravel を TiDB に通す
php 18_quota.php
php 19_laravel_coll.php
bash 22_disk.sh          # 8256 の条件を記録
```

両方起動した状態で（公開前の再検証で追加した分）:

```
php 20_check.php > out_20_check.txt      # CHECK 制約
php 21_cost.php  > out_21_cost.txt       # estCost の比較
```

`21_cost.php` は `EXPLAIN FORMAT='verbose'` の `estCost` を使う。
既定の計画（TableFullScan）と、`USE_INDEX` ヒントで索引を強制した計画の
全体コストを並べて、オプティマイザが安いほうを選んでいることを確かめる。

## 測っていないこと（記事にもそう書いてある）

- `tidb_enable_check_constraint` を ON にしたあとの CHECK の挙動
- ギャップロックの挙動差（公式ドキュメントの記述として紹介するに留めた）
- AUTO_RANDOM への移行、複数 TiDB server での ID 採番、TiFlash の性能
- エラー8256 が出た瞬間の `/tmp` の空き容量。記録し損ねたので、
  同日に測り直した値を `out_22_disk.txt` に残した（追試不能）

## ファイル

| ファイル | 何を測るか |
|---|---|
| `lib.php` | 共通ヘルパ。表示幅40桁で折り返す |
| `01_versions.php` | version() / tidb_version() |
| `02_ddl_dml.php` | 同じ DDL / INSERT 1000件 / SELECT |
| `03_explain.php` | EXPLAIN の列と中身の違い |
| `03b_stats.php` | 全表スキャンが統計不足のせいか確認 |
| `04_bigtable.php` | 10万行での EXPLAIN |
| `05_autoinc.php` | AUTO_INCREMENT の採番 |
| `05b_gap.php` | 採番の飛びを実際に出す |
| `06_compat.php` | 11種類の構文が通るか |
| `07_silent.php` | 通るが効かない DDL |
| `08_vars.php` | 既定のシステム変数 |
| `09_collation.php` | 既定照合順序と表名の大小 |
| `09b_coll_meta.php` | 照合順序のメタ情報 |
| `10_ddl_txn.php` | トランザクション中の DDL |
| `11_explain_analyze.php` | EXPLAIN ANALYZE の形 |
| `12_wrongport.php` | 3306 に繋ぐ失敗 |
| `16_ddl_fix.sh` | エラー 8256 の直し方 |
| `17_laravel.sh` | Laravel のマイグレーション |
| `18_quota.php` | disk_quota は下げられるか |
| `19_laravel_coll.php` | Laravel の DDL は照合順序を明示する |
| `20_check.php` | CHECK 制約は実際に効くか（TiDB は既定 OFF） |
| `21_cost.php` | 1000行で全表スキャンを選ぶ理由を estCost で確認 |
| `22_disk.sh` | エラー8256の条件（/tmp の空きと disk_quota）を記録 |

`out_<名前>.txt` が各スクリプトの出力（記事に貼ったものと同一、無加工）。
`out_13_laravel_fail.txt` `out_14_laravel_nodb.txt` `out_15_laravel_ok.txt`
`out_18b_users_ddl.txt` は artisan の出力を `fold -w 40` で折り返したもの
（文字は削っていない）。

## この検証で TiDB の設定を2つ変えた

```
SET GLOBAL tidb_enable_dist_task = OFF;
SET GLOBAL tidb_ddl_enable_fast_reorg = OFF;
```

出荷時はどちらも ON。戻すなら `ON` を入れ直す。
