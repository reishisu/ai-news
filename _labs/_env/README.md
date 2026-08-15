# 実行環境で何が動くか（実測）

記事の裏付けに使える範囲を、実際に動かして確かめた記録です。
**「動かせない」ものを動かしたように書かないため**の一覧でもあります。

最終確認: 2026年8月15日

| 対象 | 版 | 実行 | 備考 |
|---|---|---|---|
| PHP | 8.4.19 | ✅ | pdo_mysql / mysqli / pdo_sqlite / mbstring / intl などLaravelに必要な拡張は全部あり |
| Composer | 導入済 | ✅ | `composer create-project laravel/laravel` が通る |
| Laravel | 13.25.0 | ✅ | `php artisan test` まで実行可 |
| TiUP | 1.17.0 | ✅ | `tiup playground` でローカルクラスタを起動 |
| TiDB | v8.5.7 | ✅ | PHPのpdo_mysqlで 127.0.0.1:4000 に接続確認済み |
| Terraform | v1.14.3 | ⚠️ 一部 | `init` / `validate` / `plan` は可。`apply` は不可 |
| AWS CLI | 1.46.0 | ⚠️ 一部 | 認証情報なし。`--generate-cli-skeleton` と `help` のみ |
| Docker CLI | 29.3.1 | ❌ | **デーモンが動いていない。** コンテナは起動できない |
| Chromium | 141.0.7390.37 | ✅ | 表示検証・図版レンダリングに使用 |
| Python | 3.11.15 | ✅ | pytest 9.1.1 |

## Laravel の初回テスト（実出力）

```
$ php artisan test
Tests\Feature\ExampleTest::test_the_application_returns_a_successful_response
  No application encryption key has been specified.
```

`php artisan key:generate` を忘れると必ずこうなります。超基礎記事の題材に使えます。

## TiDB への接続（実出力）

```
接続       : OK
version()  : 8.0.11-TiDB-v8.5.7
tidb_version:
  Release Version: v8.5.7
  Edition: Community
  Store: tikv
```

`version()` が `8.0.11-TiDB-...` を返す点が重要です。
TiDBはMySQL 8.0互換として振る舞うので、既存のMySQLクライアントがそのまま繋がります。

## Terraform を認証情報なしで plan まで動かす

`terraform-plan-without-credentials.tf` を参照。ダミーの認証情報と検証スキップを渡すと
`plan` まで通り、差分の実出力が取れます。

```
Plan: 1 to add, 0 to change, 0 to destroy.
```

`data` ソースなど既存リソースの読み取りが要る構成は plan でも失敗します。
`apply` は実行しません。
