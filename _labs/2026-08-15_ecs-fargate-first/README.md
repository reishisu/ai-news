# ECS on Fargate の登場人物 — 実証メモ

実行日: 2026年8月15日

## 前提: このテーマは「実行できない」

AWSアカウントも認証情報も無い。Dockerデーモンも動いていない。
そのため **ECSにデプロイする一連の操作は一切実行していない。**

| やったこと | 実行 |
|---|---|
| `aws ecs *-generate-cli-skeleton` | した |
| AWS CLI のクライアント側パラメータ検証 | した |
| AWS CLI 同梱の ECS APIモデル(列挙値・説明文)の読み出し | した |
| `terraform init` / `validate` / `plan` | した |
| `docker build` | **していない**(デーモン無し。エラーだけ記録) |
| `terraform apply` | **していない** |
| `aws ecs create-cluster` / `register-task-definition` / `create-service` | **していない** |
| タスクの起動、ALB経由のHTTPアクセス、ヘルスチェックの確認 | **していない** |

`aws ecs list-clusters` と `register-task-definition`(td-2.json) は
実際にAWSのエンドポイントへ到達したが、認証情報が無効なため
`UnrecognizedClientException` で失敗した。**書き込みは発生していない。**

## 動かし方

```bash
./run-all.sh > output.txt 2>&1
```

`tf/` と `tf-bad/` は `terraform init` 済みの前提。未実行なら:

```bash
(cd tf && terraform init && terraform plan -out=plan.bin)
(cd tf-bad && terraform init)
```

## ファイル

| ファイル | 何をするか |
|---|---|
| `run-all.sh` | 下記を全部実行して `output.txt` を作る |
| `versions.sh` | 版の一覧 |
| `cluster-shape.sh` | `create-cluster` の雛形 |
| `taskdef-shape.sh` | `register-task-definition` の雛形 |
| `shape.sh` | `create-service` の雛形から ALB/NW 部分 |
| `enums.sh` | APIモデルの NetworkMode / Compatibility / LaunchType |
| `model-doc.sh` | APIモデルの networkMode 説明文 |
| `skeleton-random.sh` | 雛形の enum を10回出して分布を見る |
| `skeleton-src.sh` | その値を決めている AWS CLI のソース行 |
| `step.sh` | td-1/2/3.json を順に投げてエラーを見る |
| `td-1.json` | family だけ |
| `td-2.json` | family + containerDefinitions(name なし) |
| `td-3.json` | containerPort を文字列 `"80"` にした版 |
| `tf/main.tf` | クラスタ/タスク定義/サービス/ALB を一式書いたもの |
| `tf/summarize.sh` | plan が作るリソース一覧 |
| `tf/wiring.sh` | plan から配線の値を抜く |
| `tf/mismatch.sh` | コンテナ名をずらして plan する |
| `tf-bad/main.tf` | `container_name` を消した版 |
| `silent.sh` | 誤り4種を validate/plan が捕まえるか |
| `Dockerfile` | `docker build` が失敗することの確認用 |
| `output.txt` | 上記の実出力(記事に貼るのはこれ) |

## 分かったこと

1. **`--generate-cli-skeleton` の enum 値は毎回ランダムに変わる。**
   `awscli/botocore/utils.py` の L1243 が `random.choice(shape.enum)`。
   雛形の `"networkMode": "host"` は既定値ではない。
   APIモデルの説明文では既定は `bridge`、Fargate では `awsvpc` が必須。

2. **クラスタは名前だけで作れる。** `create-cluster` の雛形に
   必須らしきものは `clusterName` しかない。「箱」でしかないことが形に出ている。

3. **タスク定義に最低限必要なのは `family` と `containerDefinitions`。**
   これはクライアント側で検証されるので、認証情報が無くても確かめられる。

4. **サービスとALBは `containerName` と `containerPort` で結ばれる。**
   `create-service` の `loadBalancers[]` に `targetGroupArn` /
   `containerName` / `containerPort` が並ぶ。

5. **Terraform はその結び目を検証しない。**
   タスク定義のコンテナ名 `web` に対してサービス側を `wev` にしても
   `validate` も `plan` も通る。`network_mode = "bridge"` + FARGATE、
   `target_type = "instance"`、`cpu = "300"` も同様に通る。
   4件すべて「通過」。これらは ECS 側がデプロイ時に弾く。

## 版

`output.txt` の先頭を参照。
aws 1.46.0 / botocore 1.43.62 / terraform 1.14.3 /
hashicorp/aws 6.60.0 / python 3.11.15 / docker CLI 29.3.1(デーモン無し)。
