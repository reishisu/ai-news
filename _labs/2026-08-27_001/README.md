# 2026-08-27_001 の検証記録

## 何を確かめたか

Terraform 1.16.0 で入った `lifecycle { destroy = false }` が、実際には何をするのか。

きっかけは、CHANGELOG と公式ドキュメントで**書きぶりが食い違って見えた**こと。

| 出どころ | 書きぶり |
|---|---|
| CHANGELOG 1.16.0 | Resource `lifecycle` blocks now support `destroy = false` to prevent a resource from being destroyed. |
| 公式ドキュメント(lifecycle) | Set to `false` to remove a resource from state without destroying the actual infrastructure resource. |

CHANGELOG だけを読むと `prevent_destroy` の別名に見えるが、
ドキュメントは「**実体を消さずに state から外す**」と書いている。**まるで別の機能**なので、実際に動かして確かめた。

## 結論（実測）

**ドキュメントのほうが正しい。** `destroy = false` は「破棄を止める」のではなく
「**実体は残したまま、Terraform の管理下から外す**」。

- `terraform destroy` は成功する（エラーにならない）
- 実体（`hello.txt`）は**残る**
- state からは**消える**（`terraform state list` が空になる）
- 実行時に "Some objects will no longer be managed by Terraform" という警告が出る

`prevent_destroy = true` は destroy を**エラーで止める**ので、挙動が逆に近い。
取り違えると、消えたと思っていたリソースが**クラウド側に残って課金され続ける**。

## 動かし方

```bash
curl -sSLO https://releases.hashicorp.com/terraform/1.16.0/terraform_1.16.0_linux_amd64.zip
unzip terraform_1.16.0_linux_amd64.zip
export COLUMNS=40
./terraform init
./terraform apply -auto-approve     # hello.txt ができる
# main.tf の lifecycle { destroy = false } を有効にしたまま
./terraform destroy -auto-approve   # 0 destroyed、hello.txt は残る
./terraform state list              # 空
```

`local_file` を使っているので**クラウドの認証情報は要らない**。
実体がローカルのファイルなので、「消えたか / 残ったか」を `ls` で直接確認できる。

## 環境

- Terraform v1.16.0 (linux_amd64、公式zip)
- provider: hashicorp/local
- 実行日時: 2026-08-27 01:29 UTC (10:29 JST)
- 出力は `COLUMNS=40` `-no-color` で取得（CLAUDE.md 第4節）

## ファイル

- `main.tf` — 検証に使った構成（`lifecycle { destroy = false }` を含む）
- `output.txt` — 実行結果。記事に貼ったものと同一
